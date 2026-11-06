import re

def word_spans(text):
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]

def windows(text, size=40, overlap=10, offset=0):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    spans = word_spans(text)
    result = []
    step = size - overlap
    for i in range(0, len(spans), step):
        j = min(i + size, len(spans))
        result.append((offset + spans[i][0], offset + spans[j-1][1]))
        if j == len(spans):
            break
    return result

def sentence_chunks(text, size=40):
    if size <= 0:
        raise ValueError("size must be positive")
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?]\s+", text)] + [len(text)]
    out, pending, count = [], None, 0
    for a, b in zip(cuts, cuts[1:]):
        segment = text[a:b]
        n = len(segment.split())
        if not n:
            continue
        if n > size:
            if pending is not None:
                out.append(pending)
            out.extend(windows(segment, size, 0, a))
            pending, count = None, 0
        elif pending is not None and count + n <= size:
            pending, count = (pending[0], b), count + n
        else:
            if pending is not None:
                out.append(pending)
            pending, count = (a, b), n
    if pending is not None:
        out.append(pending)
    return out

def make_chunks(docs, strategy, size=40):
    result = []
    for doc_id, text in docs.items():
        if strategy == "sentence":
            spans = sentence_chunks(text, size)
        elif strategy in {"0", "10"}:
            spans = windows(text, size, int(strategy))
        else:
            raise ValueError("strategy must be '0', '10', or 'sentence'")
        for i, (a, b) in enumerate(spans):
            result.append({"id": f"{doc_id}:{i}", "doc": doc_id,
                           "start": a, "end": b, "text": text[a:b]})
    return result

if __name__ == "__main__":
    assert windows("") == []
    assert windows("short text") == [(0, 10)]
    try:
        windows("a b", 2, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid overlap was accepted")
    long = " ".join(["word"] * 95) + "."
    assert all(len(long[a:b].split()) <= 40 for a, b in sentence_chunks(long))
    demo = {"example": "Reset your password. Keep recovery codes private."}
    for strategy in ["0", "10", "sentence"]:
        for c in make_chunks(demo, strategy):
            assert c["text"] == demo[c["doc"]][c["start"]:c["end"]]
            print(strategy, c)
    print("Chunk boundary tests passed")
