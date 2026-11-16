import os

# Keep the suite hermetic and fast: never download or load the multilingual ONNX model in tests.
# Code paths then use the legacy collection / keyword search, which is what the fixtures build.
os.environ.setdefault("KNOWLEDGELIB_EMBED_DISABLE", "1")
