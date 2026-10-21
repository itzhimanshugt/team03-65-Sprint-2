"""Show that similar meanings get nearby vectors: embed 14 sentences, project to 2-D with PCA.

Run: python -m scripts.embedding_map  (writes outputs/c16/embedding_map.png and .md)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from embeddings.embedder import embed_texts  # noqa: E402

TOPICS = {
    "Exit load": [
        "A 1% exit load applies if units are redeemed within 365 days.",
        "Redeeming early costs a fee deducted from the payout.",
        "No charge is levied on redemptions after two years.",
        "The fund charges investors for selling units too soon.",
    ],
    "NAV": [
        "NAV is the per-unit value of a fund's assets minus liabilities.",
        "The scheme's net asset value is published every business day.",
        "Units are bought and sold at the day's NAV.",
        "Total assets divided by units outstanding gives the unit price.",
    ],
    "Riskometer": [
        "The riskometer shows the scheme's risk level, from Low to Very High.",
        "This fund is rated Very High risk on the riskometer.",
        "SEBI requires every scheme to display its risk level.",
        "Investors should match the risk label to their own risk appetite.",
    ],
    "Unrelated": [
        "The cricket match was stopped because of rain.",
        "Add two cups of flour and stir the batter well.",
    ],
}
labels = [t for t, ss in TOPICS.items() for _ in ss]
texts = [s for ss in TOPICS.values() for s in ss]
X = np.array(embed_texts(texts))

# PCA by SVD on centred vectors: the two directions with the most variance.
Xc = X - X.mean(axis=0)
_, s, vt = np.linalg.svd(Xc, full_matrices=False)
xy = Xc @ vt[:2].T
explained = (s[:2] ** 2).sum() / (s**2).sum()

fig, ax = plt.subplots(figsize=(8, 6))
for topic, color in zip(TOPICS, ["#785926", "#2C694E", "#1F5EDB", "#BA1A1A"], strict=True):
    idx = [i for i, t in enumerate(labels) if t == topic]
    ax.scatter(xy[idx, 0], xy[idx, 1], s=70, color=color, label=topic)
    for i in idx:
        ax.annotate(
            texts[i][:28] + "…", xy[i], fontsize=7, xytext=(4, 4), textcoords="offset points"
        )
ax.set_title(
    f"14 sentences: 768-D embeddings projected to 2-D\n(PCA keeps {explained:.0%} of the variance)",
    fontsize=11,
)
ax.legend()
ax.set_xticks([])
ax.set_yticks([])
fig.tight_layout()
fig.savefig("outputs/c16/embedding_map.png", dpi=150)

sim = X @ X.T  # vectors are unit-length, so dot product = cosine similarity
names = list(TOPICS)


def avg(a, b):
    ia = [i for i, t in enumerate(labels) if t == a]
    ib = [i for i, t in enumerate(labels) if t == b]
    vals = [sim[i, j] for i in ia for j in ib if i != j]
    return sum(vals) / len(vals)


rows = ["| | " + " | ".join(names) + " |", "|---" * (len(names) + 1) + "|"]
rows += [f"| **{a}** | " + " | ".join(f"{avg(a, b):.2f}" for b in names) + " |" for a in names]
md = [
    "# C16 — Embeddings: similar meaning, nearby vectors",
    "",
    "![map](embedding_map.png)",
    "",
    "Average cosine similarity between sentences (diagonal = same topic):",
    "",
    *rows,
]
# Self-check: each real topic is closer to itself than to any other topic.
for t in names[:-1]:
    assert avg(t, t) > max(avg(t, o) for o in names if o != t), t
Path("outputs/c16/embedding_map.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
