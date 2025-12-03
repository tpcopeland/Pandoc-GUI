"""
Pandoc conversion utilities for MD to DOCX/PDF conversion.
"""
import pypandoc
import tempfile
import os
from typing import Optional, List

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
    return ["pdflatex", "xelatex", "lualatex"]

def get_paper_sizes() -> List[str]:
    """Return available paper sizes."""
    return ["letter", "a4", "legal"]

def get_font_sizes() -> List[str]:
    """Return available font sizes."""
    return ["10pt", "11pt", "12pt"]

def get_document_classes() -> List[str]:
    """Return available LaTeX document classes."""
    return ["article", "report", "book"]

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

        with open(output_path, "rb") as f:
            return f.read()

def convert_md_to_pdf(
    input_content: str,
    output_filename: str,
    toc: bool = False,
    toc_depth: int = 3,
    number_sections: bool = False,
    highlight_style: str = "pygments",
    pdf_engine: str = "pdflatex",
    paper_size: str = "letter",
    font_size: str = "11pt",
    margin: str = "1in",
    line_stretch: float = 1.0,
    document_class: str = "article"
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
        pdf_engine: LaTeX engine (pdflatex, xelatex, lualatex)
        paper_size: Paper size (letter, a4, legal)
        font_size: Base font size (10pt, 11pt, 12pt)
        margin: Page margins
        line_stretch: Line spacing multiplier
        document_class: LaTeX document class

    Returns:
        bytes: The PDF file content
    """
    extra_args = [
        "--standalone",
        f"--pdf-engine={pdf_engine}",
        f"--highlight-style={highlight_style}",
        f"-V geometry:margin={margin}",
        f"-V fontsize={font_size}",
        f"-V papersize={paper_size}",
        f"-V linestretch={line_stretch}",
        f"-V documentclass={document_class}"
    ]

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
