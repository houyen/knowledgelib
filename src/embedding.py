#!/usr/bin/env python3
"""
Multilingual embedding for KnowledgeLib (ONNX, no torch).

Chroma's default embedder (all-MiniLM-L6-v2) is English-only, while a large share of queries and
self-docs are Vietnamese. This module runs `intfloat/multilingual-e5-base` (768 dims, ~100 languages)
through onnxruntime + tokenizers, which chromadb already depends on.

Model choice, measured with src/retrieval_eval.py on tests/retrieval_eval (hybrid search, 2026-11):
  model                   golden_selfdocs R@1 / R@5   golden_general R@1 / R@5   size    full embed
  all-MiniLM-L6 (old)     0.63 / 0.82                 not measured *             90 MB   -
  multilingual-e5-small   0.95 / 1.00                 0.55 / 0.75                465 MB  ~55 s
  multilingual-e5-base    0.95 / 1.00                 0.70 / 0.85                1.0 GB  ~90 s
  (* the old ranking code scored R@1 0.00 on the first 10 general queries before the set was extended)
golden_general is small (20 queries) and half of it was written together with the units it targets,
so treat its numbers as optimistic.
The small model fails on Vietnamese questions about English units, so base is the default.
Override with KNOWLEDGELIB_EMBED_MODEL; each model gets its own collection.

E5 models expect a role prefix: "query: " for search queries, "passage: " for indexed documents.

The model is downloaded once from Hugging Face into the local cache. If it cannot be loaded
(offline first run, missing libs), `load_embedder()` returns None and callers fall back to the
legacy collection with Chroma's default embedder.
"""

import os

MODEL_REPO = os.environ.get("KNOWLEDGELIB_EMBED_MODEL", "intfloat/multilingual-e5-base")
MODEL_FILE = os.environ.get("KNOWLEDGELIB_EMBED_ONNX", "onnx/model.onnx")
MAX_TOKENS = 512
BATCH_SIZE = 32

# Collection names. The legacy collection keeps Chroma's default embedder; vectors of different
# models must never share a collection.
LEGACY_COLLECTION = "knowledgelib_units"
ML_COLLECTION = "knowledgelib_units_" + "".join(ch if ch.isalnum() else "_" for ch in MODEL_REPO.split("/")[-1].lower())

_EMBEDDER = None
_LOAD_FAILED = False


class E5Embedder:
    def __init__(self, model_path: str, tokenizer_path: str):
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self._np = np
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.enable_truncation(max_length=MAX_TOKENS)
        self.tokenizer.enable_padding(pad_id=1, pad_token="<pad>")
        opts = ort.SessionOptions()
        opts.log_severity_level = 3
        self.session = ort.InferenceSession(model_path, sess_options=opts, providers=["CPUExecutionProvider"])
        self.input_names = {i.name for i in self.session.get_inputs()}

    def _embed(self, texts: list[str]) -> list[list[float]]:
        np = self._np
        out = []
        for start in range(0, len(texts), BATCH_SIZE):
            enc = self.tokenizer.encode_batch(texts[start:start + BATCH_SIZE])
            ids = np.array([e.ids for e in enc], dtype=np.int64)
            mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in self.input_names:
                feed["token_type_ids"] = np.zeros_like(ids)
            hidden = self.session.run(None, feed)[0]  # (batch, seq, dim)
            m = mask[..., None].astype(hidden.dtype)
            pooled = (hidden * m).sum(axis=1) / np.clip(m.sum(axis=1), 1e-9, None)
            pooled = pooled / np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-12, None)
            out.extend(pooled.astype(np.float32).tolist())
        return out

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return self._embed(["passage: " + (t or "") for t in texts])

    def embed_queries(self, texts: list[str]) -> list[list[float]]:
        return self._embed(["query: " + (t or "") for t in texts])


def load_embedder():
    """Return a cached E5Embedder, or None when the model cannot be loaded."""
    global _EMBEDDER, _LOAD_FAILED
    if _EMBEDDER is not None:
        return _EMBEDDER
    if _LOAD_FAILED or os.environ.get("KNOWLEDGELIB_EMBED_DISABLE") == "1":
        return None
    try:
        from huggingface_hub import hf_hub_download

        model_path = hf_hub_download(MODEL_REPO, MODEL_FILE)
        tokenizer_path = hf_hub_download(MODEL_REPO, "tokenizer.json")
        _EMBEDDER = E5Embedder(model_path, tokenizer_path)
        return _EMBEDDER
    except BaseException as e:  # incl. onnxruntime/pyo3 panics; never take the caller down
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _LOAD_FAILED = True
        print(f"Warning: multilingual embedder unavailable ({e}). Falling back to default embedder.")
        return None
