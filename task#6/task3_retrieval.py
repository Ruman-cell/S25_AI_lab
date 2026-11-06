"""Task 3: controlled retrieval evaluation and CSV evidence log."""
import csv, json, time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from task2_chunks import make_chunks


def evaluate(score_rows, chunks, items):
    hits, reciprocal = [], []
    for row, q in zip(score_rows, items):
        if q["doc"] is None:
            continue
        top = np.argsort(-row, kind="stable")[:3]
        good = [rank for rank, i in enumerate(top, 1)
                if chunks[i]["doc"] == q["doc"] and q["evidence"] in chunks[i]["text"]]
        hits.append(bool(good))
        reciprocal.append(1 / good[0] if good else 0)
    return (float(np.mean(hits)), float(np.mean(reciprocal))) if hits else (None, None)


def main():
    with open("corpus.json", encoding="utf-8") as f: docs = json.load(f)
    with open("queries.json", encoding="utf-8") as f: items = json.load(f)
    assert len(docs) >= 5 and len([q for q in items if q["doc"]]) == 8
    for q in items:
        assert q["split"] in {"dev", "test"}
        if q["doc"] is not None:
            assert q["evidence"] in docs[q["doc"]]
    query_texts = [q["query"] for q in items]
    logs = []
    try:
        from sentence_transformers import SentenceTransformer
        load_start = time.perf_counter()
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
        print("Embedding model load seconds:", round(time.perf_counter()-load_start, 4))
        embedding_available = True
    except Exception as exc:
        model = None
        embedding_available = False
        print("EMBEDDING BACKEND SKIPPED:", str(exc))
        print("Install sentence-transformers and download all-MiniLM-L6-v2 to run it.")

    for strategy in ["0", "10", "sentence"]:
        chunks = make_chunks(docs, strategy)
        texts = [c["text"] for c in chunks]
        for method in (["tfidf", "embedding"] if embedding_available else ["tfidf"]):
            start = time.perf_counter()
            if method == "tfidf":
                vectorizer = TfidfVectorizer()
                C = vectorizer.fit_transform(texts)
                Q = vectorizer.transform(query_texts)
                encode_seconds = time.perf_counter() - start
                start = time.perf_counter()
                scores = (Q @ C.T).toarray()
            else:
                lengths = [len(model.tokenizer(t, truncation=False)["input_ids"]) for t in texts + query_texts]
                if max(lengths) > model.max_seq_length:
                    raise ValueError("Model token limit exceeded; rechunk or shorten inputs")
                C = model.encode(texts, normalize_embeddings=True)
                Q = model.encode(query_texts, normalize_embeddings=True)
                encode_seconds = time.perf_counter() - start
                start = time.perf_counter()
                scores = Q @ C.T
            search_seconds = time.perf_counter() - start
            print("\nCONFIG", strategy, method, "chunks", len(chunks),
                  "encode/index sec", round(encode_seconds, 6),
                  "search sec", round(search_seconds, 6))
            for split in ["dev", "test"]:
                indices = [i for i, q in enumerate(items) if q["split"] == split]
                metric = evaluate(scores[indices], chunks, [items[i] for i in indices])
                print(split, "Hit@3/MRR@3", tuple(None if x is None else round(x, 3) for x in metric))
            for row, q in zip(scores, items):
                for rank, i in enumerate(np.argsort(-row, kind="stable")[:3], 1):
                    c = chunks[i]
                    record = dict(strategy=strategy, method=method, query=q["query"], split=q["split"],
                                  answerable=q["doc"] is not None, rank=rank, score=round(float(row[i]), 6),
                                  chunk_id=c["id"], doc=c["doc"], start=c["start"], end=c["end"], text=c["text"])
                    logs.append(record)
                    print("TOP", rank, record["chunk_id"], "score", record["score"],
                          "offsets", (record["start"], record["end"]), "evidence:", record["text"][:180])
    if logs:
        with open("retrieval_log.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(logs[0]))
            writer.writeheader(); writer.writerows(logs)
    print("\nSaved retrieval_log.csv with", len(logs), "ranked rows")

if __name__ == "__main__":
    main()
