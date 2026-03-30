#!/usr/bin/env python3
"""DOCX → PDF → PNG preview pipeline.

Requires:
- LibreOffice (for DOCX→PDF): brew install --cask libreoffice
- poppler (for PDF→PNG): brew install poppler
"""
import os
import sys
import glob
import subprocess


def docx_to_pdf(docx_path, output_dir):
    """Convert DOCX to PDF using LibreOffice headless."""
    # Try common LibreOffice paths on macOS
    soffice_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/local/bin/soffice",
        "soffice",
    ]

    soffice = None
    for p in soffice_paths:
        if os.path.exists(p) or p == "soffice":
            soffice = p
            break

    if soffice is None:
        print("⚠ LibreOffice not found. Install: brew install --cask libreoffice")
        return None

    try:
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf",
             "--outdir", output_dir, docx_path],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            basename = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
            return os.path.join(output_dir, basename)
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
    """Convert all DOCX files in output_dir to PDF and PNG previews."""
    preview_dir = os.path.join(output_dir, "preview")
    os.makedirs(preview_dir, exist_ok=True)

    docx_files = sorted(glob.glob(os.path.join(output_dir, "*.docx")))
    if not docx_files:
        print("No .docx files found in output/")
        return

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


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    main(output_dir)
