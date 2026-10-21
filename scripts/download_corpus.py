"""Download the public corpus listed in data/catalog.csv into data/raw (skips files already there).

Run: python -m scripts.download_corpus
"""

import csv
import re
import sys
import urllib.request
from pathlib import Path

DATA = Path("data")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0 Safari/537.36"}


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
        return r.read()


def resolve(url: str, filename: str) -> str:
    # SEBI circular pages are HTML wrappers; the circular itself is a linked PDF.
    if filename.endswith(".pdf") and "sebi.gov.in/legal/" in url:
        page = fetch(url).decode("utf-8", "ignore")
        match = re.search(r"https://www\.sebi\.gov\.in/sebi_data/attachdocs/[^\"' ]+\.pdf", page)
        if not match:
            raise ValueError("no PDF link on SEBI page")
        return match.group(0)
    return url


def main() -> int:
    (DATA / "raw").mkdir(parents=True, exist_ok=True)
    failed = 0
    for row in csv.DictReader(open("data/catalog.csv", encoding="utf-8")):
        target = DATA / row["filename"]
        if not row["url"] or target.exists():  # internal docs live in git, nothing to fetch
            continue
        try:
            data = fetch(resolve(row["url"], row["filename"]))
            if target.suffix == ".pdf" and not data.startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            target.write_bytes(data)
            print(f"ok    {row['filename']} ({len(data) / 1e6:.1f} MB)")
        except Exception as error:  # report and continue with the rest of the corpus
            failed += 1
            print(f"FAIL  {row['filename']}: {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
