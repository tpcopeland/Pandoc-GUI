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

def preprocess_markdown(content: str, toc: bool = False) -> str:
    """
    Preprocess markdown content to fix common issues.

    Args:
        content: Raw markdown content
        toc: Whether TOC is enabled

    Returns:
        Processed markdown content
    """
    # Fix bullet list formatting
    content = fix_bullet_lists(content)

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
        highlight_style: Code syntax highlighting style
        reference_doc: Path to reference DOCX template
        dpi: Image resolution

    Returns:
        bytes: The DOCX file content
    """
    # Preprocess markdown content
    input_content = preprocess_markdown(input_content, toc=toc)

    extra_args = ["--standalone"]

    if toc:
        extra_args.append("--toc")
        extra_args.append(f"--toc-depth={toc_depth}")

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

        # Post-process DOCX to fix styling (colors, fonts) and remove field codes
        output_bytes = _postprocess_docx(output_path)
        return output_bytes


def _postprocess_docx(docx_path: str) -> bytes:
    """
    Post-process DOCX file to fix styling issues.

    - Makes all header colors black (removes blue styling)
    - Sets font to Latin Modern Roman to match PDF output
    - Removes field codes that cause 'update fields' warning
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

                # Process styles.xml to fix header colors and fonts
                if item.filename == 'word/styles.xml':
                    content = data.decode('utf-8')
                    # Remove any blue color from heading styles (color value 2E74B5 or similar blues)
                    # This targets <w:color w:val="XXXXXX"/> inside heading style definitions
                    content = re.sub(r'<w:color\s+w:val="[0-9A-Fa-f]{6}"\s*/>', '', content)
                    # Also remove themeColor references that cause blue headers
                    content = re.sub(r'<w:color[^>]*w:themeColor="[^"]*"[^>]*/>', '', content)

                    # Change default font from Cambria to Latin Modern Roman
                    # Replace Cambria font references
                    content = re.sub(r'w:ascii="Cambria"', 'w:ascii="Latin Modern Roman"', content)
                    content = re.sub(r'w:hAnsi="Cambria"', 'w:hAnsi="Latin Modern Roman"', content)
                    content = re.sub(r'w:eastAsia="Cambria"', 'w:eastAsia="Latin Modern Roman"', content)
                    content = re.sub(r'w:cs="Cambria"', 'w:cs="Latin Modern Roman"', content)

                    # Also handle the theme font settings
                    content = re.sub(r'w:asciiTheme="[^"]*"', 'w:ascii="Latin Modern Roman"', content)
                    content = re.sub(r'w:hAnsiTheme="[^"]*"', 'w:hAnsi="Latin Modern Roman"', content)
                    content = re.sub(r'w:eastAsiaTheme="[^"]*"', 'w:eastAsia="Latin Modern Roman"', content)
                    content = re.sub(r'w:cstheme="[^"]*"', 'w:cs="Latin Modern Roman"', content)

                    data = content.encode('utf-8')

                # Process document.xml to fix colors and remove field codes
                elif item.filename == 'word/document.xml':
                    content = data.decode('utf-8')
                    # Remove any inline blue color styling
                    content = re.sub(r'<w:color\s+w:val="[0-9A-Fa-f]{6}"\s*/>', '', content)
                    content = re.sub(r'<w:color[^>]*w:themeColor="[^"]*"[^>]*/>', '', content)

                    # Remove HYPERLINK field codes that reference external files
                    # These patterns match Word field codes like PAGEREF, HYPERLINK \l, etc.
                    content = re.sub(r'<w:fldChar[^>]*w:fldCharType="begin"[^>]*/>', '', content)
                    content = re.sub(r'<w:fldChar[^>]*w:fldCharType="separate"[^>]*/>', '', content)
                    content = re.sub(r'<w:fldChar[^>]*w:fldCharType="end"[^>]*/>', '', content)
                    content = re.sub(r'<w:instrText[^>]*>.*?</w:instrText>', '', content, flags=re.DOTALL)
                    data = content.encode('utf-8')

                # Process theme file to change default fonts
                elif item.filename == 'word/theme/theme1.xml':
                    content = data.decode('utf-8')
                    # Change Cambria to Latin Modern Roman in theme
                    content = re.sub(r'typeface="Cambria"', 'typeface="Latin Modern Roman"', content)
                    data = content.encode('utf-8')

                zout.writestr(item, data)

        output_buffer.seek(0)
        return output_buffer.read()

def convert_md_to_pdf(
    input_content: str,
    output_filename: str,
    toc: bool = False,
    toc_depth: int = 3,
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
    input_content = preprocess_markdown(input_content, toc=toc)

    # Build margin string for geometry package
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
        f"-V fontsize={font_size}",
        f"-V papersize={paper_size}",
        f"-V linestretch={line_stretch}",
        f"-V documentclass={document_class}",
        # Force black color for all text
        "-V colorlinks=false",
        "-V urlcolor=black",
        "-V linkcolor=black",
        "-V toccolor=black",
    ]

    # Add geometry package with proper syntax
    extra_args.append(f"-V geometry={margin_str}")

    # Add header-includes for title spacing and unicode support
    header_includes = []

    # Reduce space between title and content
    header_includes.append(r"\usepackage{titling}")
    header_includes.append(r"\setlength{\droptitle}{-2em}")
    header_includes.append(r"\predate{}")
    header_includes.append(r"\postdate{}")
    header_includes.append(r"\preauthor{}")
    header_includes.append(r"\postauthor{}")

    # Add packages for xelatex unicode support
    if pdf_engine == "xelatex":
        header_includes.append(r"\usepackage{fontspec}")
        header_includes.append(r"\usepackage{unicode-math}")
        # Set default font if not specified
        if font_family:
            extra_args.append(f"-V mainfont={font_family}")
        else:
            header_includes.append(r"\setmainfont{Latin Modern Roman}")
    elif pdf_engine == "pdflatex":
        # For pdflatex, use inputenc and textgreek for unicode
        header_includes.append(r"\usepackage[utf8]{inputenc}")
        header_includes.append(r"\usepackage[T1]{fontenc}")
        header_includes.append(r"\usepackage{textgreek}")
        header_includes.append(r"\usepackage{lmodern}")
    elif pdf_engine == "lualatex":
        header_includes.append(r"\usepackage{fontspec}")
        header_includes.append(r"\usepackage{unicode-math}")
        if font_family:
            extra_args.append(f"-V mainfont={font_family}")
        else:
            header_includes.append(r"\setmainfont{Latin Modern Roman}")

    # Add header includes to extra_args
    for include in header_includes:
        extra_args.append(f"-V header-includes={include}")

    if toc:
        extra_args.append("--toc")
        extra_args.append(f"--toc-depth={toc_depth}")

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
