#!/usr/bin/env python3
"""
Markdown to DOCX Converter

==============================================================================
INSTRUCTIONS FOR CLAUDE AGENTS
==============================================================================

This script converts Markdown files to Word documents (.docx) with clean
formatting. Use this when the user needs a .docx export of markdown content.

REQUIREMENTS:
    - Python 3.6+
    - pypandoc: pip install pypandoc
    - pandoc: Must be installed on the system
        - macOS: brew install pandoc
        - Ubuntu/Debian: apt-get install pandoc
        - Windows: choco install pandoc (or download from pandoc.org)

USAGE (Command Line):
    python convert_md_to_docx.py input.md output.docx
    python convert_md_to_docx.py input.md  # outputs to input.docx

USAGE (Programmatic - import in another script):
    from convert_md_to_docx import convert_md_to_docx
    convert_md_to_docx("input.md", "output.docx")

WHAT THIS SCRIPT DOES:
    1. Converts markdown to DOCX using pandoc
    2. Post-processes the DOCX to fix default pandoc styling issues:
       - Changes all header colors from blue to black
       - Changes font from Cambria to Latin Modern Roman (matches LaTeX/PDF style)
       - Removes Word theme color references that cause inconsistent styling

WHAT THIS SCRIPT DOES NOT DO (intentionally):
    - No Table of Contents generation (causes issues with empty TOC headers)
    - No section numbering (breaks formatting)
    - No PDF conversion (use pandoc directly with xelatex for that)

OUTPUT CHARACTERISTICS:
    - All text is black (no blue headers)
    - Font: Latin Modern Roman (clean, professional, matches academic PDF style)
    - Code blocks: Pygments syntax highlighting
    - Images: 96 DPI resolution

TROUBLESHOOTING:
    - "pypandoc not found": Run `pip install pypandoc`
    - "pandoc not found": Install pandoc on your system (see requirements above)
    - Weird characters in output: Ensure input file is UTF-8 encoded
    - Font not rendering: Latin Modern Roman may need to be installed on the
      system viewing the document, or Word will substitute a similar font

==============================================================================
"""
import sys
import os
import re
import tempfile
import zipfile
import io
from pathlib import Path

try:
    import pypandoc
except ImportError:
    print("Error: pypandoc is required. Install with: pip install pypandoc")
    sys.exit(1)


def convert_md_to_docx(input_path: str, output_path: str) -> None:
    """
    Convert a Markdown file to DOCX format.

    Args:
        input_path: Path to the input .md file
        output_path: Path for the output .docx file
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_input = os.path.join(tmpdir, "input.md")
        temp_output = os.path.join(tmpdir, "output.docx")

        with open(temp_input, "w", encoding="utf-8") as f:
            f.write(content)

        pypandoc.convert_file(
            temp_input,
            "docx",
            outputfile=temp_output,
            extra_args=["--standalone", "--highlight-style=pygments", "--dpi=96"]
        )

        # Post-process to fix styling (black headers, Latin Modern Roman font)
        output_bytes = _postprocess_docx(temp_output)

        with open(output_path, "wb") as f:
            f.write(output_bytes)


def _postprocess_docx(docx_path: str) -> bytes:
    """
    Post-process DOCX to fix pandoc's default styling.

    DOCX files are ZIP archives containing XML. This function modifies:
    - word/styles.xml: Style definitions (header colors, fonts)
    - word/document.xml: Actual document content (inline colors)
    - word/theme/theme1.xml: Theme definitions (font defaults)
    """
    with open(docx_path, 'rb') as f:
        docx_bytes = f.read()

    with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as zin:
        output_buffer = io.BytesIO()
        with zipfile.ZipFile(output_buffer, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == 'word/styles.xml':
                    content = data.decode('utf-8')
                    # Remove explicit color values (e.g., blue headers)
                    content = re.sub(r'<w:color\s+w:val="[0-9A-Fa-f]{6}"\s*/>', '', content)
                    # Remove theme color references
                    content = re.sub(r'<w:color[^>]*w:themeColor="[^"]*"[^>]*/>', '', content)
                    # Replace Cambria font with Latin Modern Roman
                    content = re.sub(r'w:ascii="Cambria"', 'w:ascii="Latin Modern Roman"', content)
                    content = re.sub(r'w:hAnsi="Cambria"', 'w:hAnsi="Latin Modern Roman"', content)
                    content = re.sub(r'w:eastAsia="Cambria"', 'w:eastAsia="Latin Modern Roman"', content)
                    content = re.sub(r'w:cs="Cambria"', 'w:cs="Latin Modern Roman"', content)
                    # Replace theme font references with explicit Latin Modern Roman
                    content = re.sub(r'w:asciiTheme="[^"]*"', 'w:ascii="Latin Modern Roman"', content)
                    content = re.sub(r'w:hAnsiTheme="[^"]*"', 'w:hAnsi="Latin Modern Roman"', content)
                    content = re.sub(r'w:eastAsiaTheme="[^"]*"', 'w:eastAsia="Latin Modern Roman"', content)
                    content = re.sub(r'w:cstheme="[^"]*"', 'w:cs="Latin Modern Roman"', content)
                    data = content.encode('utf-8')

                elif item.filename == 'word/document.xml':
                    content = data.decode('utf-8')
                    # Remove inline color styling
                    content = re.sub(r'<w:color\s+w:val="[0-9A-Fa-f]{6}"\s*/>', '', content)
                    content = re.sub(r'<w:color[^>]*w:themeColor="[^"]*"[^>]*/>', '', content)
                    data = content.encode('utf-8')

                elif item.filename == 'word/theme/theme1.xml':
                    content = data.decode('utf-8')
                    # Update theme font
                    content = re.sub(r'typeface="Cambria"', 'typeface="Latin Modern Roman"', content)
                    data = content.encode('utf-8')

                zout.writestr(item, data)

        output_buffer.seek(0)
        return output_buffer.read()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_md_to_docx.py input.md [output.docx]")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = str(Path(input_file).with_suffix(".docx"))

    convert_md_to_docx(input_file, output_file)
    print(f"Converted: {input_file} -> {output_file}")
