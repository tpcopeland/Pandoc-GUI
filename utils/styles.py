"""
Custom CSS styles for Jony Ive aesthetic.
"""

def get_custom_css() -> str:
    """Return custom CSS for the Streamlit app."""
    return """
    <style>
    /* Main app background */
    .stApp {
        background-color: #FAFAFA;
    }

    /* Main container */
    .main .block-container {
        max-width: 800px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* Headers */
    h1 {
        color: #1D1D1F;
        font-weight: 600;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    h2, h3 {
        color: #1D1D1F;
        font-weight: 600;
    }

    /* Subtitle/description text */
    .subtitle {
        color: #86868B;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Card-like containers for expanders */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    div[data-testid="stExpander"] details {
        border: none;
    }

    div[data-testid="stExpander"] summary {
        padding: 1rem 1.25rem;
        font-weight: 500;
        color: #1D1D1F;
    }

    /* File uploader styling */
    div[data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #D2D2D7;
        border-radius: 12px;
        padding: 2rem;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: #0071E3;
        transition: border-color 0.2s ease;
    }

    div[data-testid="stFileUploader"] section {
        padding: 0;
    }

    /* Primary button styling */
    .stButton > button {
        background-color: #0071E3;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 1rem;
        width: 100%;
        transition: background-color 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #0077ED;
        border: none;
    }

    .stButton > button:active {
        background-color: #006ACC;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #FFFFFF;
        color: #0071E3;
        border: 1px solid #0071E3;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 1rem;
        width: 100%;
        transition: all 0.2s ease;
    }

    .stDownloadButton > button:hover {
        background-color: #0071E3;
        color: white;
    }

    /* Radio buttons as format selector */
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 1rem;
    }

    div[data-testid="stRadio"] label {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        flex: 1;
        text-align: center;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: #0071E3;
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        border-color: #0071E3;
        background-color: #F0F7FF;
    }

    /* Slider styling */
    div[data-testid="stSlider"] {
        padding-top: 0.5rem;
    }

    /* Select box styling */
    div[data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 8px;
    }

    /* Number input styling */
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 8px;
    }

    /* Toggle/checkbox styling */
    div[data-testid="stCheckbox"] label span {
        color: #1D1D1F;
    }

    /* Success message */
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #E5E5E7;
        margin: 2rem 0;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Spinner */
    .stSpinner > div {
        border-color: #0071E3;
    }
    </style>
    """

def get_format_card_css() -> str:
    """Return CSS for format selection cards."""
    return """
    <style>
    .format-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .format-card:hover {
        border-color: #0071E3;
        box-shadow: 0 2px 8px rgba(0,113,227,0.1);
    }

    .format-card.selected {
        border-color: #0071E3;
        background-color: #F0F7FF;
    }

    .format-card h3 {
        margin: 0;
        color: #1D1D1F;
        font-size: 1.25rem;
    }

    .format-card p {
        margin: 0.5rem 0 0 0;
        color: #86868B;
        font-size: 0.875rem;
    }
    </style>
    """
