
import streamlit as st


def apply_theme():

    st.markdown("""
    <style>

    /* =========================================
       1. GLOBAL DESIGN SYSTEM
    ========================================= */

    :root {
        --bg-main: #101316;
        --bg-sidebar: #15191D;
        --bg-card: #1B2025;
        --bg-card-hover: #232A30;

        --accent: #F07836;
        --accent-light: #FF9A55;
        --accent-dark: #C95125;

        --ember-red: #E0523A;
        --gold: #E8B65A;

        --text-main: #F2F0EC;
        --text-secondary: #A7ADB4;
        --text-muted: #737C85;

        --border: #30383F;
        --border-accent: #75452F;

        --success: #65B985;
        --warning: #E8B65A;
        --danger: #E0523A;

        --radius: 12px;
    }


    /* =========================================
       2. APPLICATION BACKGROUND
    ========================================= */

    .stApp {
        background: var(--bg-main);
        color: var(--text-main);
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg-main);
    }

    [data-testid="stMain"] {
        background: var(--bg-main);
    }

    .block-container {
        max-width: 1450px;
        padding: 2rem 2.5rem 2.5rem;
    }


    /* =========================================
       3. SIDEBAR
    ========================================= */

    [data-testid="stSidebar"] {
        background: var(--bg-sidebar);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: var(--bg-sidebar);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-main);
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: var(--text-secondary);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] a {
        border-radius: 8px;
        padding: 9px 12px;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
        background: var(--bg-card-hover);
        color: var(--accent-light);
    }


    /* =========================================
       4. HEADINGS AND TEXT
    ========================================= */

    h1 {
        color: var(--text-main) !important;
        font-size: 2.25rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.8px;
    }

    h2 {
        color: var(--accent-light) !important;
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }

    h3 {
        color: var(--text-main) !important;
        font-size: 1.15rem !important;
        font-weight: 650 !important;
    }

    p, li {
        color: var(--text-secondary);
        line-height: 1.7;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--text-muted);
    }

    a {
        color: var(--accent-light);
    }


    /* =========================================
       5. METRIC CARDS
    ========================================= */

    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #20262B,
            #191E22
        );

        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);

        border-radius: var(--radius);
        padding: 17px 19px;

        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);

        transition: border-color 0.2s ease,
                    transform 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--border-accent);
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.85rem;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-main) !important;
        font-size: 1.8rem;
        font-weight: 750;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }


    /* =========================================
       6. BUTTONS
    ========================================= */

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(
            135deg,
            var(--accent-dark),
            var(--accent)
        );

        color: #FFFFFF;
        border: 1px solid #E8793E;
        border-radius: 8px;

        padding: 0.55rem 1.15rem;
        font-weight: 650;

        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--accent-light);
        color: #171717;
        border-color: var(--accent-light);
        transform: translateY(-1px);
    }

    .stButton > button:focus,
    .stDownloadButton > button:focus {
        box-shadow: 0 0 0 2px rgba(240, 120, 54, 0.3);
    }


    /* =========================================
       7. INPUTS AND SELECT BOXES
    ========================================= */

    [data-baseweb="input"],
    [data-baseweb="select"],
    [data-baseweb="textarea"] {
        background: var(--bg-card);
        border-color: var(--border);
        border-radius: 8px;
    }

    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: var(--text-main);
    }

    [data-baseweb="select"] > div {
        background: var(--bg-card);
        border-color: var(--border);
        color: var(--text-main);
    }

    [data-baseweb="popover"] {
        background: var(--bg-card);
    }

    [data-baseweb="menu"] {
        background: var(--bg-card);
    }


    /* =========================================
       8. DATA TABLES
    ========================================= */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] {
        background: var(--bg-card);
    }


    /* =========================================
       9. CHART CONTAINERS
    ========================================= */

    [data-testid="stPlotlyChart"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 8px;
    }


    /* =========================================
       10. EXPANDERS
    ========================================= */

    [data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    [data-testid="stExpander"] summary {
        color: var(--text-main);
        font-weight: 600;
    }

    [data-testid="stExpander"] summary:hover {
        color: var(--accent-light);
    }


    /* =========================================
       11. TABS
    ========================================= */

    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-secondary);
        font-weight: 600;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--accent-light);
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: var(--accent);
    }


    /* =========================================
       12. ALERTS AND STATUS MESSAGES
    ========================================= */

    [data-testid="stAlert"] {
        background: var(--bg-card);
        border-radius: 9px;
        border: 1px solid var(--border);
    }


    /* =========================================
       13. DIVIDERS AND SPACING
    ========================================= */

    hr {
        border-color: var(--border);
        margin: 1.5rem 0;
    }

    [data-testid="stVerticalBlock"] {
        gap: 1rem;
    }


    /* =========================================
       14. HOME PAGE HERO SECTION
    ========================================= */

    .hero-section {
        background: linear-gradient(
            115deg,
            #211C1A 0%,
            #38231C 55%,
            #54291D 100%
        );

        border: 1px solid #69402D;
        border-radius: 16px;

        padding: 42px 38px;
        margin-bottom: 25px;

        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.2);
    }

    .hero-label {
        color: var(--accent-light);
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 2px;
        margin-bottom: 15px;
    }

    .hero-section h1 {
        color: #FFFFFF !important;
        font-size: 38px !important;
        margin-bottom: 12px;
    }

    .hero-section p {
        color: #D6C8C0;
        font-size: 15px;
        max-width: 750px;
        line-height: 1.8;
    }

    .hero-source {
        color: #EBA66E;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-top: 22px;
    }


    /* =========================================
       15. WORKFLOW CARDS
    ========================================= */

    .workflow-card {
        background: linear-gradient(
            145deg,
            #20262B,
            #191E22
        );

        border: 1px solid var(--border);
        border-top: 3px solid var(--accent);
        border-radius: 12px;

        padding: 23px;
        min-height: 270px;

        transition: all 0.2s ease;
    }

    .workflow-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-3px);
    }

    .card-number {
        color: var(--accent-light);
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1.5px;
    }

    .card-icon {
        font-size: 27px;
        margin: 18px 0 10px;
    }

    .workflow-card h3 {
        color: var(--text-main) !important;
        font-size: 18px;
    }

    .workflow-card p {
        color: var(--text-secondary);
        font-size: 13px;
        line-height: 1.7;
    }

    .card-tag {
        display: inline-block;
        color: var(--accent-light);
        background: rgba(240, 120, 54, 0.10);
        border: 1px solid rgba(240, 120, 54, 0.2);
        border-radius: 5px;

        padding: 5px 8px;
        margin-top: 12px;

        font-size: 9px;
        font-weight: 750;
        letter-spacing: 1px;
    }


    /* =========================================
       16. NAVIGATION CARDS
    ========================================= */

    .nav-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;

        padding: 23px;
        min-height: 235px;
        margin-bottom: 12px;

        transition: all 0.2s ease;
    }

    .nav-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--accent-dark);
        transform: translateY(-3px);
    }

    .nav-icon {
        font-size: 28px;
        margin-bottom: 14px;
    }

    .nav-card h3 {
        color: var(--text-main) !important;
        font-size: 18px;
    }

    .nav-card p {
        color: var(--text-secondary);
        font-size: 13px;
        line-height: 1.7;
    }


    /* =========================================
       17. FOOTER
    ========================================= */

    .footer {
        text-align: center;
        background: #15191D;

        border-top: 1px solid var(--border);
        border-radius: 10px;

        padding: 24px 15px;
        margin-top: 35px;
    }

    .footer-title {
        color: var(--accent-light);
        font-size: 12px;
        font-weight: 750;
        letter-spacing: 1.5px;
        margin-bottom: 9px;
    }

    .footer-subtitle {
        color: var(--text-muted);
        font-size: 11px;
        margin-top: 8px;
    }


    /* =========================================
       18. SCROLLBAR
    ========================================= */

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }

    ::-webkit-scrollbar-thumb {
        background: #46505A;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-dark);
    }


    /* =========================================
       19. RESPONSIVE LAYOUT
    ========================================= */

    @media (max-width: 768px) {

        .block-container {
            padding: 1rem;
        }

        .hero-section {
            padding: 25px 20px;
        }

        .hero-section h1 {
            font-size: 27px !important;
        }

        .workflow-card,
        .nav-card {
            min-height: auto;
        }
    }

    </style>
    """, unsafe_allow_html=True)
