from types import SimpleNamespace

import pytest

from embeddings.embedder import EmbeddingError, embed_texts


class FakeEmbeddings:
    def __init__(self, dims=768, drop=False, shuffle=False, no_index=False):
        self.dims, self.drop, self.shuffle, self.sent = dims, drop, shuffle, None
        self.no_index = no_index
        self.embeddings = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.sent = kwargs
        n = len(kwargs["input"])
        data = [SimpleNamespace(index=i, embedding=[float(i)] * self.dims) for i in range(n)]
        if self.no_index:
            for d in data:
                d.index = None
        if self.drop:
            data = data[:-1]
        if self.shuffle:
            data = data[::-1]
        return SimpleNamespace(data=data)


def test_one_vector_per_text_in_order(monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")
    client = FakeEmbeddings(shuffle=True)
    vectors = embed_texts(["exit load", "expense ratio", "NAV"], client=client)
    assert [round(v[0] * 768**0.5) for v in vectors] == [0, 1, 1]
    assert client.sent["dimensions"] == 768 and client.sent["model"] == "gemini-embedding-001"


def test_empty_input_makes_no_call():
    client = FakeEmbeddings()
    assert embed_texts([], client=client) == [] and client.sent is None


def test_wrong_count_or_dimension_raises(monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")
    with pytest.raises(EmbeddingError, match="vectors"):
        embed_texts(["a", "b"], client=FakeEmbeddings(drop=True))
    with pytest.raises(EmbeddingError, match="dimensions"):
        embed_texts(["a"], client=FakeEmbeddings(dims=3072))


def test_missing_index_keeps_response_order():
    vectors = embed_texts(["a", "b", "c"], client=FakeEmbeddings(no_index=True))
    assert [v[0] for v in vectors[:1]] == [0.0] and vectors[1] == vectors[2]


def test_vectors_are_unit_length():
    import math

    (v,) = embed_texts(["a"], client=FakeEmbeddings(no_index=True))
    v2 = embed_texts(["a", "b"], client=FakeEmbeddings())[1]
    assert math.isclose(sum(x * x for x in v2), 1.0)
    assert v == [0.0] * 768  # zero vector stays zero instead of dividing by 0
