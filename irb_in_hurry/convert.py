"""DOCX → PDF → PNG preview pipeline.

Requires:
- LibreOffice (for DOCX→PDF): brew install --cask libreoffice  (Windows: winget)
- poppler (for PDF→PNG): brew install poppler  (Windows: conda/scoop poppler)
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOFFICE_CANDIDATES = [
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",          # macOS
    r"C:\Program Files\LibreOffice\program\soffice.exe",          # Windows
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]
FONTS_CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts.conf")


def find_soffice():
    """Locate LibreOffice on macOS / Windows / Linux. Returns path or None."""
    for p in SOFFICE_CANDIDATES:
        if os.path.exists(p):
            return p
    return shutil.which("soffice") or shutil.which("libreoffice")


def soffice_env():
    """On Linux, map 標楷體/DFKai-SB to an installed Kai font so renders keep metrics."""
    env = dict(os.environ)
    if sys.platform.startswith("linux") and os.path.exists(FONTS_CONF):
        env["FONTCONFIG_FILE"] = FONTS_CONF
    return env


def soffice_cmd(soffice, *args):
    """soffice argv with a private profile, so conversion works while LibreOffice is open."""
    profile = Path(tempfile.gettempdir(), "irb-in-hurry-lo-profile").as_uri()
    return [soffice, f"-env:UserInstallation={profile}", "--headless", *args]


def docx_to_pdf(docx_path, output_dir):
    """Convert DOCX to PDF using LibreOffice headless."""
    soffice = find_soffice()
    if soffice is None:
        print("⚠ LibreOffice not found. Install: brew install --cask libreoffice "
              "(macOS) / winget install TheDocumentFoundation.LibreOffice (Windows)")
        return None

    try:
        result = subprocess.run(
            soffice_cmd(soffice, "--convert-to", "pdf", "--outdir", output_dir, docx_path),
            capture_output=True, text=True, timeout=120, env=soffice_env(),
        )
        pdf_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
        # soffice exits 0 even when it cannot load the file, so check the output exists
        if result.returncode == 0 and os.path.exists(pdf_path):
            return pdf_path
        else:
            print(f"  ✗ PDF conversion failed for {os.path.basename(docx_path)}: {result.stderr}")
            return None
    except FileNotFoundError:
        print("⚠ LibreOffice not found. Install: brew install --cask libreoffice")
        return None
    except subprocess.TimeoutExpired:
        print(f"  ✗ PDF conversion timed out for {os.path.basename(docx_path)}")
        return None


def pdf_to_png(pdf_path, preview_dir, dpi=150):
    """Convert first page of PDF to PNG using pdf2image."""
    try:
        from pdf2image import convert_from_path
        os.makedirs(preview_dir, exist_ok=True)
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=dpi)
        if images:
            basename = os.path.splitext(os.path.basename(pdf_path))[0] + ".png"
            png_path = os.path.join(preview_dir, basename)
            images[0].save(png_path, "PNG")
            return png_path
    except ImportError:
        print("⚠ pdf2image not installed. Run: pip install pdf2image")
    except Exception as e:
        print(f"  ✗ PNG conversion failed for {os.path.basename(pdf_path)}: {e}")
    return None


def main(output_dir="output"):
    """Convert all DOCX files in output_dir to PDF and PNG previews. Returns an exit code."""
    preview_dir = os.path.join(output_dir, "preview")
    os.makedirs(preview_dir, exist_ok=True)

    docx_files = sorted(glob.glob(os.path.join(output_dir, "*.docx")))
    if not docx_files:
        print(f"No .docx files found in {output_dir}/")
        return 0
    if find_soffice() is None:
        print("⚠ LibreOffice not found — skipping PDF conversion. Install: brew install --cask libreoffice "
              "(macOS) / winget install TheDocumentFoundation.LibreOffice (Windows)")
        return 0

    print(f"Converting {len(docx_files)} DOCX files...")
    print()

    pdf_count = 0
    png_count = 0

    for docx_path in docx_files:
        basename = os.path.basename(docx_path)

        # DOCX → PDF
        pdf_path = docx_to_pdf(docx_path, output_dir)
        if pdf_path:
            print(f"  ■ PDF: {basename}")
            pdf_count += 1

            # PDF → PNG preview
            png_path = pdf_to_png(pdf_path, preview_dir)
            if png_path:
                print(f"  ■ PNG: {os.path.basename(png_path)}")
                png_count += 1
        else:
            print(f"  □ PDF: {basename} — skipped")

    print(f"\n{'═' * 40}")
    print(f"  PDFs:     {pdf_count}/{len(docx_files)}")
    print(f"  Previews: {png_count}/{len(docx_files)}")
    print(f"{'═' * 40}")
    return 0 if pdf_count == len(docx_files) else 1


if __name__ == "__main__":
    from irb_in_hurry.cli import main as cli
    sys.exit(cli(["pdf", *sys.argv[1:]]))
