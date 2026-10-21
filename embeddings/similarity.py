"""Similarity and distance between embedding vectors."""

import numpy as np


def cosine(a, b) -> float:
    """Angle-based similarity in [-1, 1]; ignores vector length."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denom) if denom else 0.0


def dot(a, b) -> float:
    return float(np.asarray(a, dtype=float) @ np.asarray(b, dtype=float))


def euclidean(a, b) -> float:
    return float(np.linalg.norm(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)))


def rank(query, vectors, metric=cosine) -> list[tuple[int, float]]:
    """Indexes of `vectors` ordered from most to least similar to `query`."""
    scores = [(i, metric(query, v)) for i, v in enumerate(vectors)]
    reverse = metric is not euclidean  # smaller distance = more similar
    return sorted(scores, key=lambda s: s[1], reverse=reverse)
