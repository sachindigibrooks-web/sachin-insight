"""Import Google Search Console performance data (clicks, impressions per page).

In Search Console: Performance > Search results > Pages tab > Export > Download CSV.
That gives a .zip with Pages.csv inside; either the .zip or the Pages.csv works.
"""

import csv
import io
import zipfile

from crawler import normalize


def _number(text):
    text = (text or "").strip().replace(",", "")
    if text.endswith("%"):
        return float(text[:-1] or 0) / 100
    try:
        return float(text)
    except ValueError:
        return None


def read_rows(data, filename=""):
    """[(url, clicks, impressions, ctr, position)] from a GSC export (.zip or .csv bytes)."""
    if filename.lower().endswith(".zip") or data[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name = next((n for n in z.namelist() if n.lower().endswith("pages.csv")), None)
            if not name:
                raise ValueError("The zip has no Pages.csv - export from the Pages tab.")
            data = z.read(name)
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text))
    header = [h.strip().lower() for h in next(reader, [])]

    def col(*names):
        for n in names:
            if n in header:
                return header.index(n)
        return None
    i_url = col("top pages", "page", "pages", "url", "landing page")
    i_clicks, i_impr = col("clicks"), col("impressions")
    i_ctr, i_pos = col("ctr"), col("position", "average position")
    if i_url is None or i_clicks is None:
        raise ValueError("This doesn't look like a Search Console Pages export "
                         "(needs 'Top pages' and 'Clicks' columns).")
    rows = []
    for r in reader:
        if len(r) <= i_url:
            continue
        url = normalize(r[i_url])
        if not url:
            continue
        get = lambda i: _number(r[i]) if i is not None and i < len(r) else None  # noqa: E731
        clicks, impr = get(i_clicks), get(i_impr)
        rows.append((url, int(clicks or 0), int(impr or 0), get(i_ctr), get(i_pos)))
    return rows


def import_into(db, data, filename=""):
    rows = read_rows(data, filename)
    db.execute("DELETE FROM gsc")
    db.executemany("INSERT OR REPLACE INTO gsc VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()
    return len(rows)
