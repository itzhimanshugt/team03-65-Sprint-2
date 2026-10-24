from retrieval.neighbours import add_neighbours
from retrieval.search import Hit


class FakeCollection:
    def __init__(self, rows):
        self.rows = rows
        self.asked = []

    def get(self, ids, include):
        self.asked += ids
        hit = [i for i in ids if i in self.rows]
        return {
            "ids": hit,
            "documents": [self.rows[i][0] for i in hit],
            "metadatas": [self.rows[i][1] for i in hit],
        }


def hit(cid, page, idx, score=0.8):
    return Hit(cid, "t", score, {"doc_id": "d", "chunk_index": idx, "page": page})


def test_same_page_neighbour_follows_its_parent():
    col = FakeCollection(
        {"d-0002": ("Exit load 1%", {"doc_id": "d", "chunk_index": 2, "page": 39})}
    )
    out = add_neighbours([hit("d-0001", 39, 1), hit("x-0005", 52, 5)], col)
    assert [h.chunk_id for h in out] == ["d-0001", "d-0002", "x-0005"]
    assert out[1].score == out[0].score and out[1].text == "Exit load 1%"


def test_other_page_and_duplicates_are_skipped():
    col = FakeCollection({"d-0002": ("next page", {"doc_id": "d", "chunk_index": 2, "page": 40})})
    assert [h.chunk_id for h in add_neighbours([hit("d-0001", 39, 1)], col)] == ["d-0001"]
    hits = [hit("d-0001", 39, 1), hit("d-0002", 39, 2)]
    assert add_neighbours(hits, col) == hits  # neighbour already retrieved: no lookup needed


def test_hits_without_position_metadata_are_untouched():
    hits = [Hit("a", "t", 0.9, {})]
    assert add_neighbours(hits, collection=object()) == hits
