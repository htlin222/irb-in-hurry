#!/usr/bin/env python3
"""Cache the institution's official blank forms for layout validation.

Driven by the `templates:` block of the active institution profile:

- `index_url` set   → scrape those pages, download every linked form whose
                      label matches `form_id_pattern` / `named_forms`
                      (Google Drive or direct links) into templates/<id>/
- no `index_url`    → index blanks you dropped into templates/<id>/ by hand,
                      mapped in `templates.files` (written by onboard.py) or
                      named after their form id

Legacy .doc files are converted to .docx (LibreOffice) so validate_layout.py
can read them. The result is templates/<id>/index.json.

Usage: uv run python scripts/fetch_templates.py [--force]
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.institution import current

INDEX_FILE = "index.json"
FORM_EXTS = (".docx", ".doc", ".pdf")

LINK_RE = re.compile(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.S)
DRIVE_ID_RE = re.compile(r"(?:id=|/d/)([A-Za-z0-9_-]{20,})")


def normalize_form_id(text):
    """'IRB_SF90 藥品…' → 'SF090'; '中文計畫摘要' → 'PROPOSAL'; else None."""
    return current().form_id(text)


def index_pages():
    tpl = current().templates
    url = tpl.get("index_url")
    if not url:
        return []
    lo, hi = tpl.get("index_range", [None, None])
    return [url.format(n=n) for n in range(lo, hi + 1)] if lo is not None else [url]


def download_url(href, page_url):
    """Resolve a form link to a direct-download URL (Google Drive aware)."""
    href = html.unescape(href)
    if "google.com" in href:
        m = DRIVE_ID_RE.search(href)
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}" if m else None
    if current().templates.get("link_host") == "google_drive":
        return None
    return urllib.parse.urljoin(page_url, href)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "irb-in-hurry"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def scrape_links():
    """Return {form_id: {"title", "url", "page"}} from the profile's index pages."""
    found = {}
    for page in index_pages():
        try:
            body = fetch(page).decode("utf-8", "replace")
        except Exception as e:
            print(f"  ⚠ {page}: {e}")
            continue
        for href, label in LINK_RE.findall(body):
            title = " ".join(re.sub(r"<[^>]+>", "", html.unescape(label)).split())
            fid = normalize_form_id(title)
            url = download_url(href, page)
            if fid and url and fid not in found:
                found[fid] = {"title": title, "url": url, "page": page}
    return found


def local_forms(template_dir):
    """Blanks placed by hand: {form_id: {"title", "file"}}."""
    mapped = current().templates.get("files", {})
    if mapped:
        return {fid: {"title": os.path.splitext(f)[0], "file": f} for fid, f in mapped.items()}
    found = {}
    for f in sorted(os.listdir(template_dir)):
        stem, ext = os.path.splitext(f)
        fid = normalize_form_id(stem) if ext.lower() in FORM_EXTS else None
        if fid and fid not in found:
            found[fid] = {"title": stem, "file": f}
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
    inst = current()
    template_dir = inst.template_dir
    os.makedirs(template_dir, exist_ok=True)
    if index_pages():
        print(f"Scraping {inst.name} form index ({len(index_pages())} pages)...")
        links = scrape_links()
    else:
        print(f"No templates.index_url for '{inst.id}' — indexing blanks in "
              f"{os.path.relpath(template_dir)}/ (name each file with its form id)")
        links = local_forms(template_dir)
    print(f"Found {len(links)} official forms\n")

    index = {}
    for fid, info in sorted(links.items()):
        existing = [f for f in os.listdir(template_dir) if f.startswith(fid + ".")]
        if "file" in info:
            raw = info["file"]
            print(f"  ■ {fid} {info['title']} (local)")
        elif existing and not force:
            raw = next((f for f in existing if not f.endswith(".docx")), existing[0])
            print(f"  ■ {fid} cached")
        else:
            try:
                data = fetch(info["url"])
            except Exception as e:
                print(f"  ✗ {fid} download failed: {e}")
                continue
            ext = sniff_ext(data)
            if ext is None:
                print(f"  ✗ {fid} not a Word/PDF file (Drive returned HTML?)")
                continue
            raw = fid + ext
            with open(os.path.join(template_dir, raw), "wb") as f:
                f.write(data)
            print(f"  ■ {fid} {info['title']} ({ext})")

        raw_path = os.path.join(template_dir, raw)
        docx = raw_path if raw.endswith(".docx") else os.path.splitext(raw_path)[0] + ".docx"
        if raw.endswith(".doc") and (force or not os.path.exists(docx)):
            docx = to_docx(raw_path)
            if docx is None:
                print(f"    ⚠ {fid}: .doc→.docx conversion failed (LibreOffice missing?)")
        index[fid] = {**info, "source": raw,
                      "docx": os.path.basename(docx) if docx and os.path.exists(docx) else None}

    with open(os.path.join(template_dir, INDEX_FILE), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"\n■ {len(index)} templates indexed → {os.path.relpath(template_dir)}/{INDEX_FILE}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
