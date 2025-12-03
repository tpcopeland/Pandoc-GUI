import streamlit as st
import tempfile
import os
from pathlib import Path

from utils.converter import (
    convert_md_to_docx,
    convert_md_to_pdf,
    get_highlight_styles,
    get_pdf_engines,
    get_paper_sizes,
    get_font_sizes,
    get_document_classes
)
from utils.styles import get_custom_css


# Page Configuration
st.set_page_config(
    page_title="Pandoc GUI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def main():
    # Header Section
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Pandoc GUI</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #86868B; margin-top: 0.5rem; margin-bottom: 3rem;'>Convert Markdown with ease</p>",
                unsafe_allow_html=True)

    # File Upload Section
    uploaded_file = st.file_uploader(
        "Upload your Markdown file",
        type=["md"],
        help="Select a Markdown file (.md) to convert"
    )

    if uploaded_file is not None:
        # Get the input filename without extension
        input_filename = Path(uploaded_file.name).stem

        # Cache file content to allow multiple conversions
        if "file_content" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
            st.session_state.file_content = uploaded_file.read().decode("utf-8")
            st.session_state.current_file = uploaded_file.name

        # Format Selection
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        output_format = st.radio(
            "Select output format",
            options=["Word Document (.docx)", "PDF Document (.pdf)"],
            horizontal=True,
            key="output_format"
        )

        # Determine if DOCX or PDF
        is_docx = "docx" in output_format.lower()

        # Options Section
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

        # Document Options (common to both formats)
        with st.expander("📄 Document Options", expanded=False):
            toc = st.checkbox("Generate Table of Contents", value=False)

            toc_depth = 3
            if toc:
                toc_depth = st.slider(
                    "Table of Contents Depth",
                    min_value=1,
                    max_value=6,
                    value=3,
                    help="Maximum heading level to include in TOC"
                )

            number_sections = st.checkbox("Number Sections", value=False)

            highlight_style = st.selectbox(
                "Syntax Highlighting Style",
                options=get_highlight_styles(),
                index=get_highlight_styles().index("pygments") if "pygments" in get_highlight_styles() else 0,
                help="Style for code blocks"
            )

        # Format-specific options
        reference_doc_path = None
        dpi = 96
        pdf_engine = None
        paper_size = None
        font_size = None
        margin = None
        line_stretch = None
        document_class = None

        if is_docx:
            # DOCX Options
            with st.expander("📝 Word Document Options", expanded=False):
                reference_doc = st.file_uploader(
                    "Reference Document (Optional)",
                    type=["docx"],
                    help="Upload a .docx template to apply custom styles",
                    key="reference_doc"
                )

                if reference_doc is not None:
                    # Save reference doc to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_ref:
                        tmp_ref.write(reference_doc.read())
                        reference_doc_path = tmp_ref.name

                dpi = st.number_input(
                    "DPI (Dots Per Inch)",
                    min_value=72,
                    max_value=300,
                    value=96,
                    step=1,
                    help="Resolution for embedded images"
                )
        else:
            # PDF Options
            with st.expander("📕 PDF Document Options", expanded=False):
                pdf_engine = st.selectbox(
                    "PDF Engine",
                    options=get_pdf_engines(),
                    index=0,
                    help="LaTeX engine to use for PDF generation"
                )

                paper_size = st.selectbox(
                    "Paper Size",
                    options=get_paper_sizes(),
                    index=get_paper_sizes().index("letter") if "letter" in get_paper_sizes() else 0,
                    help="Page size for the PDF document"
                )

                font_size = st.selectbox(
                    "Font Size",
                    options=get_font_sizes(),
                    index=get_font_sizes().index("11pt") if "11pt" in get_font_sizes() else 0,
                    help="Base font size for the document"
                )

                margin = st.text_input(
                    "Margin",
                    value="1in",
                    help="Page margins (e.g., '1in', '2cm', '20mm')"
                )

                line_stretch = st.slider(
                    "Line Spacing",
                    min_value=1.0,
                    max_value=2.0,
                    value=1.15,
                    step=0.05,
                    help="Line height multiplier"
                )

                document_class = st.selectbox(
                    "Document Class",
                    options=get_document_classes(),
                    index=get_document_classes().index("article") if "article" in get_document_classes() else 0,
                    help="LaTeX document class"
                )

        # Convert Button
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            convert_button = st.button("Convert File", type="primary", use_container_width=True)

        # Conversion Logic
        if convert_button:
            try:
                # Use cached file content
                input_content = st.session_state.file_content

                # Show spinner during conversion
                with st.spinner("Converting..."):
                    if is_docx:
                        # Convert to DOCX
                        output_filename = f"{input_filename}.docx"
                        output_bytes = convert_md_to_docx(
                            input_content=input_content,
                            output_filename=output_filename,
                            toc=toc,
                            toc_depth=toc_depth,
                            number_sections=number_sections,
                            highlight_style=highlight_style,
                            reference_doc=reference_doc_path,
                            dpi=dpi
                        )
                        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    else:
                        # Convert to PDF
                        output_filename = f"{input_filename}.pdf"
                        output_bytes = convert_md_to_pdf(
                            input_content=input_content,
                            output_filename=output_filename,
                            toc=toc,
                            toc_depth=toc_depth,
                            number_sections=number_sections,
                            highlight_style=highlight_style,
                            pdf_engine=pdf_engine,
                            paper_size=paper_size,
                            font_size=font_size,
                            margin=margin,
                            line_stretch=line_stretch,
                            document_class=document_class
                        )
                        mime_type = "application/pdf"

                # Clean up temporary reference doc if it exists
                if reference_doc_path and os.path.exists(reference_doc_path):
                    try:
                        os.unlink(reference_doc_path)
                    except Exception:
                        pass  # Ignore cleanup errors

                # Success message
                st.success("✓ Conversion successful!")

                # Download button
                st.download_button(
                    label=f"Download {output_filename}",
                    data=output_bytes,
                    file_name=output_filename,
                    mime=mime_type,
                    use_container_width=True
                )

            except Exception as e:
                # Clean up temporary reference doc if it exists
                if reference_doc_path and os.path.exists(reference_doc_path):
                    try:
                        os.unlink(reference_doc_path)
                    except Exception:
                        pass  # Ignore cleanup errors

                # Error handling
                error_message = str(e)

                # Check if it's a PDF/LaTeX error
                if not is_docx and ("latex" in error_message.lower() or
                                   "pdflatex" in error_message.lower() or
                                   "xelatex" in error_message.lower() or
                                   "lualatex" in error_message.lower()):
                    st.error(
                        "⚠️ PDF conversion failed. This might be due to missing LaTeX installation or LaTeX syntax errors.\n\n"
                        "**Suggestions:**\n"
                        "- Try converting to Word Document (.docx) instead\n"
                        "- Ensure you have a LaTeX distribution installed (TeX Live, MiKTeX, etc.)\n"
                        "- Check your Markdown for special characters or LaTeX commands\n\n"
                        f"**Error details:** {error_message}"
                    )
                else:
                    st.error(
                        f"⚠️ Conversion failed.\n\n"
                        f"**Error details:** {error_message}\n\n"
                        "Please check your Markdown file and try again."
                    )
    else:
        # Show placeholder when no file is uploaded
        st.markdown(
            "<div style='text-align: center; padding: 4rem 2rem; color: #999;'>"
            "<p style='font-size: 1.2rem;'>Upload a Markdown file to get started</p>"
            "</div>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
