"""Task 1: compare whitespace and Unicode word-like tokenization."""
import re

SAMPLES = [
    "AI, search!",
    "I can't log in.",
    "help@example.com",
    "CS4944",
    "",
    "یہ ایک مثال ہے",
]

def compare(text):
    whitespace = text.split()
    word_like = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    print("Original:", repr(text))
    print("Whitespace:", whitespace, "count=", len(whitespace))
    print("Word-like:", word_like, "count=", len(word_like))

if __name__ == "__main__":
    for sample in SAMPLES:
        compare(sample)
    print("\nOptional model subword comparison (requires sentence-transformers):")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
        for sample in SAMPLES[:2]:
            print(repr(sample), model.tokenizer.tokenize(sample))
    except ImportError:
        print("Skipped: install sentence-transformers and download the model to inspect subwords.")
