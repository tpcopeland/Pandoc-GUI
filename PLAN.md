# Pandoc GUI — Streamlit App Plan

## Overview

A minimal, elegant Streamlit application for converting Markdown files to Word (.docx) or PDF documents. The interface follows Jony Ive's design philosophy: reduction to essence, intuitive interaction, and visual calm.

---

## Design Philosophy — Jony Ive Aesthetic

### Core Principles

1. **Reduction** — Remove everything that isn't essential. Each element must earn its place.
2. **White Space** — Generous breathing room. Let the interface feel open and uncluttered.
3. **Typography** — Clean sans-serif fonts. Clear hierarchy. Subtle weight differences.
4. **Quiet Confidence** — No flashy colors. Soft grays, whites, and one restrained accent color.
5. **Obvious Interaction** — Controls should explain themselves. No manual needed.
6. **Progressive Disclosure** — Show basic options first. Advanced settings tucked away but accessible.

### Visual Specifications

| Element | Specification |
|---------|---------------|
| Background | `#FAFAFA` (off-white) |
| Card/Container | `#FFFFFF` with subtle `rgba(0,0,0,0.04)` shadow |
| Primary Text | `#1D1D1F` (near-black) |
| Secondary Text | `#86868B` (medium gray) |
| Accent Color | `#0071E3` (Apple blue) — used sparingly |
| Border Radius | `12px` for containers, `8px` for inputs |
| Font Stack | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` |

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     Pandoc GUI                              │
│              Convert Markdown with ease                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │            [ Drop your .md file here ]              │   │
│  │                   or click to browse                │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Output Format                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    .docx     │  │     .pdf     │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│  ▼ Document Options                                        │
│    [ collapsed accordion with conversion options ]          │
│                                                             │
│  ▼ Advanced Options                                        │
│    [ collapsed accordion with advanced settings ]           │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│           ┌────────────────────────────┐                   │
│           │       Convert File         │                   │
│           └────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Functionality

### Supported Conversions

| Input | Output | Engine |
|-------|--------|--------|
| `.md` | `.docx` | Pandoc native |
| `.md` | `.pdf` | Pandoc via LaTeX (pdflatex/xelatex) |

### Conversion Options

#### Common Options (Both Formats)

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| Table of Contents | Toggle | Generate TOC | Off |
| TOC Depth | Slider (1-6) | Heading levels in TOC | 3 |
| Number Sections | Toggle | Add section numbers | Off |
| Highlight Style | Select | Code syntax highlighting | `pygments` |
| Standalone | Toggle | Complete document with headers | On |

**Highlight Style Options:**
- `pygments` (default)
- `tango`
- `espresso`
- `zenburn`
- `kate`
- `monochrome`
- `breezedark`
- `haddock`

#### DOCX-Specific Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| Reference Document | File Upload | Custom .docx template | None |
| DPI | Number Input | Image resolution | 96 |

#### PDF-Specific Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| PDF Engine | Select | LaTeX engine | `pdflatex` |
| Paper Size | Select | Document dimensions | `letter` |
| Font Size | Select | Base font size | `11pt` |
| Margin | Number Input | Page margins | `1in` |
| Line Stretch | Slider | Line spacing multiplier | 1.0 |
| Document Class | Select | LaTeX document class | `article` |

**PDF Engine Options:**
- `pdflatex` — Standard, fast, good for English
- `xelatex` — Unicode support, system fonts
- `lualatex` — Modern, programmable

**Paper Size Options:**
- `letter` (8.5" × 11")
- `a4` (210mm × 297mm)
- `legal` (8.5" × 14")

**Font Size Options:**
- `10pt`
- `11pt`
- `12pt`

**Document Class Options:**
- `article`
- `report`
- `book`

---

## File Structure

```
Pandoc-GUI/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── packages.txt           # System dependencies (for Streamlit Cloud)
├── .streamlit/
│   └── config.toml        # Streamlit theme configuration
├── utils/
│   ├── __init__.py
│   ├── converter.py       # Pandoc conversion logic
│   └── styles.py          # CSS styling functions
├── templates/
│   └── reference.docx     # Default DOCX reference template (optional)
├── PLAN.md                # This file
├── README.md              # Project documentation
└── LICENSE                # MIT License
```

---

## Dependencies

### requirements.txt

```
streamlit>=1.28.0
pypandoc>=1.11
```

### packages.txt (Streamlit Cloud System Dependencies)

```
pandoc
texlive-latex-base
texlive-latex-recommended
texlive-latex-extra
texlive-fonts-recommended
texlive-xetex
lmodern
```

---

## Implementation Steps

### Phase 1: Foundation

1. **Set up Streamlit configuration**
   - Create `.streamlit/config.toml` with Jony Ive color scheme
   - Configure page title, favicon, layout

2. **Create basic app structure**
   - File uploader for `.md` files
   - Output format selector (radio buttons styled as cards)
   - Convert button

3. **Implement core conversion**
   - Set up pypandoc wrapper
   - Handle MD → DOCX conversion
   - Handle MD → PDF conversion
   - Provide download button for output

### Phase 2: Options Interface

4. **Add common options**
   - TOC toggle and depth slider
   - Section numbering toggle
   - Highlight style selector

5. **Add format-specific options**
   - DOCX: Reference document upload, DPI
   - PDF: Engine, paper size, font size, margins, line spacing

6. **Implement progressive disclosure**
   - Use `st.expander` for option groups
   - "Document Options" expander (common settings)
   - "Advanced Options" expander (technical settings)

### Phase 3: Polish

7. **Apply Jony Ive styling**
   - Custom CSS for containers, buttons, inputs
   - Generous padding and margins
   - Subtle animations/transitions
   - Clean typography hierarchy

8. **Add user feedback**
   - Conversion progress indicator
   - Success/error messages with appropriate styling
   - File preview (optional)

9. **Error handling**
   - Graceful handling of conversion failures
   - Clear error messages
   - Validation of uploaded files

### Phase 4: Deployment

10. **Prepare for Streamlit Cloud**
    - Verify `packages.txt` includes all system dependencies
    - Test on Streamlit Cloud environment
    - Optimize for performance

---

## Streamlit Theme Configuration

### `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#0071E3"
backgroundColor = "#FAFAFA"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1D1D1F"
font = "sans serif"

[server]
maxUploadSize = 50
```

---

## Custom CSS Approach

Inject custom CSS via `st.markdown` to achieve the Jony Ive aesthetic:

```css
/* Container styling */
.stApp {
    background-color: #FAFAFA;
}

/* Card-like containers */
div[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Button styling */
.stButton > button {
    background-color: #0071E3;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 500;
    transition: background-color 0.2s ease;
}

.stButton > button:hover {
    background-color: #0077ED;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border: 2px dashed #E5E5E7;
    border-radius: 12px;
    padding: 40px;
}

/* Typography */
h1, h2, h3 {
    color: #1D1D1F;
    font-weight: 600;
}

p, label {
    color: #1D1D1F;
}

small {
    color: #86868B;
}
```

---

## Pandoc Command Construction

### Example: MD → DOCX

```bash
pandoc input.md \
  -o output.docx \
  --standalone \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --highlight-style=pygments \
  --reference-doc=template.docx \
  --dpi=96
```

### Example: MD → PDF

```bash
pandoc input.md \
  -o output.pdf \
  --standalone \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --highlight-style=pygments \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V papersize=letter \
  -V linestretch=1.15 \
  -V documentclass=article
```

---

## User Flow

```
1. User lands on page
   └─→ Clean interface with file uploader prominent

2. User uploads .md file
   └─→ File name displayed, format selector becomes active

3. User selects output format (.docx or .pdf)
   └─→ Format-specific options appear in expandable sections

4. User adjusts options (optional)
   └─→ Options organized in logical groups
   └─→ Sensible defaults pre-selected

5. User clicks "Convert"
   └─→ Progress indicator shows conversion status

6. Conversion completes
   └─→ Download button appears with output file
   └─→ Option to convert another file
```

---

## Error Handling Strategy

| Error Type | User Message | Action |
|------------|--------------|--------|
| Invalid file type | "Please upload a Markdown (.md) file" | Reject upload |
| Pandoc not found | "Conversion engine unavailable" | Show setup instructions |
| LaTeX missing (PDF) | "PDF generation requires LaTeX" | Suggest DOCX alternative |
| Conversion failure | "Conversion failed: [specific error]" | Show error details |
| File too large | "File exceeds 50MB limit" | Reject with size info |

---

## Testing Checklist

- [ ] MD → DOCX basic conversion
- [ ] MD → DOCX with TOC
- [ ] MD → DOCX with reference document
- [ ] MD → PDF basic conversion
- [ ] MD → PDF with all LaTeX engines
- [ ] MD → PDF with custom margins/fonts
- [ ] Error handling for invalid files
- [ ] Error handling for missing dependencies
- [ ] Mobile responsive layout
- [ ] File download functionality
- [ ] Streamlit Cloud deployment

---

## Future Considerations (Out of Scope)

The following are explicitly **not** included in this version:

- Other input formats (HTML, RST, etc.)
- Other output formats (EPUB, HTML, etc.)
- Batch conversion
- Cloud storage integration
- User accounts/history
- Custom LaTeX templates
- Equation rendering preview

---

## Summary

This plan outlines a focused, elegant Markdown conversion tool. By limiting scope to MD → DOCX/PDF and applying Jony Ive's design principles, we create an app that does one thing exceptionally well: converting Markdown documents with thoughtful options and a beautiful interface.

The key is restraint — in features, in visual elements, in complexity. Everything present should be purposeful. The result: a tool that feels inevitable, as if it couldn't have been designed any other way.
