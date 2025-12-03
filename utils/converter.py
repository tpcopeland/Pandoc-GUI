"""
Pandoc conversion utilities for MD to DOCX/PDF conversion.
"""
import pypandoc
import tempfile
import os
import re
from typing import Optional, List, Tuple

def get_highlight_styles() -> List[str]:
    """Return available syntax highlighting styles."""
    return [
        "pygments",
        "tango",
        "espresso",
        "zenburn",
        "kate",
        "monochrome",
        "breezedark",
        "haddock"
    ]

def get_pdf_engines() -> List[str]:
    """Return available PDF engines."""
    return ["xelatex", "pdflatex", "lualatex"]

def get_paper_sizes() -> List[str]:
    """Return available paper sizes."""
    return ["a4", "letter", "legal"]

def get_font_sizes() -> List[str]:
    """Return available font sizes."""
    return ["10pt", "11pt", "12pt"]

def get_document_classes() -> List[str]:
    """Return available LaTeX document classes."""
    return ["article", "report", "book"]

def get_font_families() -> List[str]:
    """Return available font families for xelatex."""
    return [
        "Latin Modern Roman",
        "Times New Roman",
        "Arial",
        "Helvetica",
        "Georgia",
        "Palatino",
        "DejaVu Serif",
        "DejaVu Sans",
        "Liberation Serif",
        "Liberation Sans"
    ]

def strip_manual_numbering(content: str) -> str:
    """
    Remove manual section numbering from markdown headers.

    Converts headers like:
      ## 1. Objectives and Hypotheses
      ### 1.1 Primary Objective
    To:
      ## Objectives and Hypotheses
      ### Primary Objective
    """
    # Pattern matches headers with manual numbering like "# 1.", "## 1.1", "### 1.1.2", etc.
    # Handles both "1." and "1.1" and "1.1.1" style numbering
    pattern = r'^(#{1,6})\s*\d+(?:\.\d+)*\.?\s+'

    lines = content.split('\n')
    processed_lines = []

    for line in lines:
        # Check if this is a header line with manual numbering
        match = re.match(pattern, line)
        if match:
            # Extract the hash marks and the rest of the content after the numbering
            hashes = match.group(1)
            # Remove the matched prefix and keep the rest
            remaining = line[match.end():]
            processed_lines.append(f"{hashes} {remaining}")
        else:
            processed_lines.append(line)

    return '\n'.join(processed_lines)

def fix_bullet_lists(content: str) -> str:
    """
    Ensure proper line breaks before bullet lists.

    Adds blank line before bullet lists that follow text without proper separation.
    """
    lines = content.split('\n')
    processed_lines = []

    for i, line in enumerate(lines):
        # Check if this is a bullet line (starts with - or * after optional whitespace)
        is_bullet = re.match(r'^\s*[-*]\s+', line)

        if is_bullet and i > 0:
            prev_line = lines[i - 1].strip()
            # If previous line is not empty and not a bullet, add blank line
            if prev_line and not re.match(r'^\s*[-*]\s+', lines[i - 1]):
                processed_lines.append('')

        processed_lines.append(line)

    return '\n'.join(processed_lines)

def extract_title_for_toc(content: str) -> Tuple[str, Optional[str]]:
    """
    Extract the first H1 heading to use as document title (appears before TOC).

    Returns:
        Tuple of (processed_content, title)
    """
    lines = content.split('\n')
    title = None
    processed_lines = []
    found_first_h1 = False

    for line in lines:
        # Check if this is an H1 header (single #)
        match = re.match(r'^#\s+(.+)$', line)
        if match and not found_first_h1:
            title = match.group(1).strip()
            found_first_h1 = True
            # Skip this line - it will be added as YAML title
            continue
        processed_lines.append(line)

    return '\n'.join(processed_lines), title

def preprocess_markdown(content: str, number_sections: bool = False, toc: bool = False) -> str:
    """
    Preprocess markdown content to fix common issues.

    Args:
        content: Raw markdown content
        number_sections: Whether auto-numbering is enabled
        toc: Whether TOC is enabled

    Returns:
        Processed markdown content
    """
    # Fix bullet list formatting
    content = fix_bullet_lists(content)

    # Strip manual numbering if auto-numbering is enabled
    if number_sections:
        content = strip_manual_numbering(content)

    # Extract title if TOC is enabled
    if toc:
        content, title = extract_title_for_toc(content)
        if title:
            # Add YAML front matter with title
            yaml_header = f"---\ntitle: \"{title}\"\n---\n\n"
            content = yaml_header + content

    return content

def convert_md_to_docx(
    input_content: str,
    output_filename: str,
    toc: bool = False,
    toc_depth: int = 3,
    number_sections: bool = False,
    highlight_style: str = "pygments",
    reference_doc: Optional[str] = None,
    dpi: int = 96
) -> bytes:
    """
    Convert Markdown content to DOCX format.

    Args:
        input_content: Markdown text content
        output_filename: Desired output filename
        toc: Generate table of contents
        toc_depth: Depth of TOC (1-6)
        number_sections: Add section numbers
        highlight_style: Code syntax highlighting style
        reference_doc: Path to reference DOCX template
        dpi: Image resolution

    Returns:
        bytes: The DOCX file content
    """
    # Preprocess markdown content
    input_content = preprocess_markdown(input_content, number_sections=number_sections, toc=toc)

    extra_args = ["--standalone"]

    if toc:
        extra_args.append("--toc")
        extra_args.append(f"--toc-depth={toc_depth}")

    if number_sections:
        extra_args.append("--number-sections")

    extra_args.append(f"--highlight-style={highlight_style}")
    extra_args.append(f"--dpi={dpi}")

    if reference_doc:
        extra_args.append(f"--reference-doc={reference_doc}")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.md")
        output_path = os.path.join(tmpdir, output_filename)

        with open(input_path, "w", encoding="utf-8") as f:
            f.write(input_content)

        pypandoc.convert_file(
            input_path,
            "docx",
            outputfile=output_path,
            extra_args=extra_args
        )

        # Post-process DOCX to remove field codes that cause the warning
        output_bytes = _remove_docx_field_codes(output_path)
        return output_bytes


def _remove_docx_field_codes(docx_path: str) -> bytes:
    """
    Remove field codes from DOCX that cause 'update fields' warning.

    This modifies the TOC to be static text instead of dynamic fields.
    """
    import zipfile
    import io

    # Read the original docx
    with open(docx_path, 'rb') as f:
        docx_bytes = f.read()

    # DOCX files are ZIP archives
    with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as zin:
        # Create output buffer
        output_buffer = io.BytesIO()
        with zipfile.ZipFile(output_buffer, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                # Process document.xml to remove field codes
                if item.filename == 'word/document.xml':
                    content = data.decode('utf-8')
                    # Remove HYPERLINK field codes that reference external files
                    # These patterns match Word field codes like PAGEREF, HYPERLINK \l, etc.
                    content = re.sub(r'<w:fldChar[^>]*w:fldCharType="begin"[^>]*/>', '', content)
                    content = re.sub(r'<w:fldChar[^>]*w:fldCharType="separate"[^>]*/>', '', content)
                    content = re.sub(r'<w:fldChar[^>]*w:fldCharType="end"[^>]*/>', '', content)
                    content = re.sub(r'<w:instrText[^>]*>.*?</w:instrText>', '', content, flags=re.DOTALL)
                    data = content.encode('utf-8')

                zout.writestr(item, data)

        output_buffer.seek(0)
        return output_buffer.read()

def convert_md_to_pdf(
    input_content: str,
    output_filename: str,
    toc: bool = False,
    toc_depth: int = 3,
    number_sections: bool = False,
    highlight_style: str = "pygments",
    pdf_engine: str = "xelatex",
    paper_size: str = "a4",
    font_size: str = "11pt",
    margin: str = "2.5cm",
    line_stretch: float = 1.0,
    document_class: str = "article",
    font_family: Optional[str] = None,
    margin_top: Optional[str] = None,
    margin_bottom: Optional[str] = None,
    margin_left: Optional[str] = None,
    margin_right: Optional[str] = None
) -> bytes:
    """
    Convert Markdown content to PDF format.

    Args:
        input_content: Markdown text content
        output_filename: Desired output filename
        toc: Generate table of contents
        toc_depth: Depth of TOC (1-6)
        number_sections: Add section numbers
        highlight_style: Code syntax highlighting style
        pdf_engine: LaTeX engine (xelatex, pdflatex, lualatex)
        paper_size: Paper size (a4, letter, legal)
        font_size: Base font size (10pt, 11pt, 12pt)
        margin: Page margins (uniform)
        line_stretch: Line spacing multiplier
        document_class: LaTeX document class
        font_family: Font family (for xelatex)
        margin_top: Top margin override
        margin_bottom: Bottom margin override
        margin_left: Left margin override
        margin_right: Right margin override

    Returns:
        bytes: The PDF file content
    """
    # Preprocess markdown content
    input_content = preprocess_markdown(input_content, number_sections=number_sections, toc=toc)

    # Build margin string
    margin_parts = []
    if margin_top:
        margin_parts.append(f"top={margin_top}")
    if margin_bottom:
        margin_parts.append(f"bottom={margin_bottom}")
    if margin_left:
        margin_parts.append(f"left={margin_left}")
    if margin_right:
        margin_parts.append(f"right={margin_right}")

    if margin_parts:
        margin_str = ",".join(margin_parts)
    else:
        margin_str = f"margin={margin}"

    extra_args = [
        "--standalone",
        f"--pdf-engine={pdf_engine}",
        f"--highlight-style={highlight_style}",
        f"-V geometry:{margin_str}",
        f"-V fontsize={font_size}",
        f"-V papersize={paper_size}",
        f"-V linestretch={line_stretch}",
        f"-V documentclass={document_class}",
        # Force black color for all text
        "-V colorlinks=false",
    ]

    # Add font family for xelatex
    if pdf_engine == "xelatex" and font_family:
        extra_args.append(f"-V mainfont={font_family}")

    if toc:
        extra_args.append("--toc")
        extra_args.append(f"--toc-depth={toc_depth}")

    if number_sections:
        extra_args.append("--number-sections")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.md")
        output_path = os.path.join(tmpdir, output_filename)

        with open(input_path, "w", encoding="utf-8") as f:
            f.write(input_content)

        pypandoc.convert_file(
            input_path,
            "pdf",
            outputfile=output_path,
            extra_args=extra_args
        )

        with open(output_path, "rb") as f:
            return f.read()
