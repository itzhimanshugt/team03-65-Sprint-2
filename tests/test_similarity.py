import pytest

from embeddings.similarity import cosine, dot, euclidean, rank


def test_cosine_basics():
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([1, 0], [-1, 0]) == pytest.approx(-1.0)
    assert cosine([2, 0], [5, 0]) == pytest.approx(1.0)  # length does not matter
    assert cosine([0, 0], [1, 0]) == 0.0  # zero vector is safe


def test_dot_and_euclidean():
    assert dot([1, 2], [3, 4]) == 11
    assert euclidean([0, 0], [3, 4]) == pytest.approx(5.0)


def test_rank_orders_most_similar_first_for_each_metric():
    q, vs = [1, 0], [[0, 1], [0.9, 0.1], [1, 0]]
    assert [i for i, _ in rank(q, vs)] == [2, 1, 0]
    assert [i for i, _ in rank(q, vs, euclidean)] == [2, 1, 0]
