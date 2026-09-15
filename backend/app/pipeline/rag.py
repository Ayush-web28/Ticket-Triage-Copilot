"""Tiny in-memory retrieval index over the knowledge base.

Real mode embeds KB docs with the configured Nebius embedding model and
ranks by cosine similarity. Mock mode falls back to a local TF-IDF index
so the whole app still runs end-to-end without an API key, without
mis-ranking on generic words like "account" the way raw keyword-overlap
counting would.
"""
import math
import re
from collections import Counter

import numpy as np
from sqlmodel import Session, select

from ..config import settings
from ..models import KBDoc
from .. import nebius_client

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or",
    "in", "on", "for", "with", "my", "i", "it", "this", "that", "how", "do",
    "does", "can", "you", "your", "please", "have", "has", "not", "be",
    "been", "from", "about", "get", "got", "just", "will",
}

_index: dict = {"docs": [], "vectors": None, "vocab": None, "idf": None}


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 2]


def _tfidf_vector(tokens: list[str], vocab: dict[str, int], idf: np.ndarray) -> np.ndarray:
    vec = np.zeros(len(vocab))
    counts = Counter(tokens)
    for token, count in counts.items():
        idx = vocab.get(token)
        if idx is not None:
            # Log-dampened term frequency ("ltc" weighting) so a term repeated
            # many times in one document doesn't dominate the cosine norm and
            # drown out documents with fewer but more relevant matches.
            vec[idx] = (1.0 + math.log(count)) * idf[idx]
    return vec


def _build_tfidf_index(docs: list[KBDoc]) -> None:
    doc_tokens = [_tokenize(f"{d.title} {d.content}") for d in docs]

    vocab: dict[str, int] = {}
    for tokens in doc_tokens:
        for token in set(tokens):
            vocab.setdefault(token, len(vocab))

    n_docs = len(docs)
    doc_freq = np.zeros(len(vocab))
    for tokens in doc_tokens:
        for token in set(tokens):
            doc_freq[vocab[token]] += 1
    idf = np.log((1 + n_docs) / (1 + doc_freq)) + 1.0

    vectors = np.array([_tfidf_vector(tokens, vocab, idf) for tokens in doc_tokens])

    _index["vocab"] = vocab
    _index["idf"] = idf
    _index["vectors"] = vectors


def build_index(session: Session) -> None:
    docs = session.exec(select(KBDoc)).all()
    _index["docs"] = docs
    if not docs:
        _index["vectors"] = None
        return
    if settings.effective_mock_mode:
        _build_tfidf_index(docs)
        return
    texts = [f"{d.title}\n{d.content}" for d in docs]
    vectors = nebius_client.embed(texts)
    _index["vectors"] = np.array(vectors)


def _cosine_top_k(query_vec: np.ndarray, vectors: np.ndarray, k: int) -> list[tuple[int, float]]:
    norms = np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vec)
    norms[norms == 0] = 1e-9
    sims = (vectors @ query_vec) / norms
    top_idx = np.argsort(-sims)[:k]
    return [(int(i), float(sims[i])) for i in top_idx]


def retrieve(query: str, k: int = 3) -> list[dict]:
    docs: list[KBDoc] = _index["docs"]
    if not docs:
        return []

    if settings.effective_mock_mode:
        query_vec = _tfidf_vector(_tokenize(query), _index["vocab"], _index["idf"])
        if not query_vec.any():
            return []
        hits = _cosine_top_k(query_vec, _index["vectors"], k)
        return [
            {"id": docs[i].id, "title": docs[i].title, "content": docs[i].content, "score": round(score, 4)}
            for i, score in hits
            if score > 0
        ]

    query_vec = np.array(nebius_client.embed([query])[0])
    hits = _cosine_top_k(query_vec, _index["vectors"], k)
    return [
        {"id": docs[i].id, "title": docs[i].title, "content": docs[i].content, "score": round(score, 4)}
        for i, score in hits
    ]
