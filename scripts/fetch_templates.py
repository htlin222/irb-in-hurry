#!/usr/bin/env python3
"""Download the official blank KFSYSCC IRB forms for layout validation.

Scrapes https://www.kfsyscc.org/human/common_files/{1..11}, downloads every
linked IRB_SFxxx form from Google Drive into templates/official/, and converts
legacy .doc files to .docx (LibreOffice) so validate_layout.py can read them.

Usage: uv run python scripts/fetch_templates.py [--force]
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.request

BASE_URL = "https://www.kfsyscc.org/human/common_files/{}"
PAGES = range(1, 12)
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "templates", "official")
INDEX_FILE = "index.json"

LINK_RE = re.compile(r'<a[^>]*href="([^"]*(?:drive|docs)\.google\.com[^"]*)"[^>]*>(.*?)</a>', re.S)
FORM_RE = re.compile(r"SF\s*0*(\d{1,3})")
DRIVE_ID_RE = re.compile(r"(?:id=|/d/)([A-Za-z0-9_-]{20,})")


# Official forms without an SF number, keyed to the id our generators use
NAMED_FORMS = {"中文計畫摘要": "PROPOSAL"}


def normalize_form_id(text):
    """'IRB_SF90 藥品…' → 'SF090'; '中文計畫摘要' → 'PROPOSAL'; else None."""
    m = FORM_RE.search(text)
    if m:
        return f"SF{int(m.group(1)):03d}"
    return next((fid for name, fid in NAMED_FORMS.items() if text.strip() == name), None)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "irb-in-hurry"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def scrape_links():
    """Return {form_id: {"title", "drive_id", "page"}} from all common_files pages."""
    found = {}
    for page in PAGES:
        try:
            body = fetch(BASE_URL.format(page)).decode("utf-8", "replace")
        except Exception as e:
            print(f"  ⚠ page {page}: {e}")
            continue
        for href, label in LINK_RE.findall(body):
            title = " ".join(re.sub(r"<[^>]+>", "", html.unescape(label)).split())
            fid = normalize_form_id(title)
            m = DRIVE_ID_RE.search(html.unescape(href))
            if fid and m and fid not in found:
                found[fid] = {"title": title, "drive_id": m.group(1), "page": page}
    return found


def sniff_ext(data):
    if data[:4] == b"PK\x03\x04":
        return ".docx"
    if data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return ".doc"
    if data[:4] == b"%PDF":
        return ".pdf"
    return None


def to_docx(doc_path):
    """Convert legacy .doc → .docx next to it. Returns new path or None."""
    from scripts.convert import find_soffice, soffice_cmd
    soffice = find_soffice()
    if not soffice:
        return None
    out_dir = os.path.dirname(doc_path)
    try:
        subprocess.run(soffice_cmd(soffice, "--convert-to", "docx", "--outdir", out_dir, doc_path),
                       capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return None
    docx = os.path.splitext(doc_path)[0] + ".docx"
    return docx if os.path.exists(docx) else None


def main(force=False):
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    print("Scraping KFSYSCC common_files pages...")
    links = scrape_links()
    print(f"Found {len(links)} official forms\n")

    index = {}
    for fid, info in sorted(links.items()):
        existing = [f for f in os.listdir(TEMPLATE_DIR) if f.startswith(fid + ".")]
        if existing and not force:
            raw = next((f for f in existing if not f.endswith(".docx")), existing[0])
            print(f"  ■ {fid} cached")
        else:
            try:
                data = fetch(f"https://drive.google.com/uc?export=download&id={info['drive_id']}")
            except Exception as e:
                print(f"  ✗ {fid} download failed: {e}")
                continue
            ext = sniff_ext(data)
            if ext is None:
                print(f"  ✗ {fid} not a Word/PDF file (Drive returned HTML?)")
                continue
            raw = fid + ext
            with open(os.path.join(TEMPLATE_DIR, raw), "wb") as f:
                f.write(data)
            print(f"  ■ {fid} {info['title']} ({ext})")

        raw_path = os.path.join(TEMPLATE_DIR, raw)
        docx = raw_path if raw.endswith(".docx") else os.path.join(TEMPLATE_DIR, fid + ".docx")
        if raw.endswith(".doc") and (force or not os.path.exists(docx)):
            docx = to_docx(raw_path)
            if docx is None:
                print(f"    ⚠ {fid}: .doc→.docx conversion failed (LibreOffice missing?)")
        index[fid] = {**info, "source": raw,
                      "docx": os.path.basename(docx) if docx and os.path.exists(docx) else None}

    with open(os.path.join(TEMPLATE_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"\n■ {len(index)} templates indexed → {os.path.relpath(TEMPLATE_DIR)}/{INDEX_FILE}")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main(force="--force" in sys.argv)
