
"""
File Name: app.py
Project: Satellite Fire Hotspot Intelligence
Purpose: Main dashboard configuration and Home page.
"""

import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Fire Intelligence Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# COMMON UI STYLING
# --------------------------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #101827;
    color: #F1F5F9;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Headings */
h1, h2, h3 {
    color: #F1F5F9 !important;
}

/* Paragraph text */
p {
    color: #CBD5E1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #182538;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #182538;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 12px;
}

/* Buttons */
.stButton > button {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1rem;
}

.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}

/* Navigation cards */
.nav-card {
    background-color: #182538;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 22px;
    min-height: 175px;
    margin-bottom: 12px;
}

.nav-card h3 {
    color: #F1F5F9;
    margin-bottom: 10px;
    font-size: 20px;
}

.nav-card p {
    color: #94A3B8;
    font-size: 14px;
}

/* Workflow cards */
.workflow-card {
    background-color: #182538;
    border-left: 4px solid #60A5FA;
    border-radius: 10px;
    padding: 18px;
    min-height: 130px;
}

.workflow-card h3 {
    font-size: 17px;
    margin-bottom: 8px;
}

.workflow-card p {
    color: #94A3B8;
    font-size: 14px;
}

/* Footer */
.footer {
    text-align: center;
    color: #94A3B8;
    font-size: 13px;
    padding-top: 22px;
    padding-bottom: 10px;
    border-top: 1px solid #334155;
    margin-top: 45px;
}

.footer-subtitle {
    color: #64748B;
    font-size: 12px;
}

/* Remove excess divider spacing */
hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HOME PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div style="margin-bottom: 8px;">
        <span style="
            background-color: #1E3A5F;
            color: #93C5FD;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;">
            SATELLITE FIRE MONITORING
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Fire Intelligence Dashboard")

st.markdown(
    """
    Monitor satellite-based fire detections through
    machine learning, spatial clustering and priority analysis.
    """
)

st.caption("Data source: NASA FIRMS · VIIRS-SNPP NRT")

st.divider()


# --------------------------------------------------
# SYSTEM WORKFLOW
# --------------------------------------------------

st.subheader("System Workflow")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="workflow-card">
            <h3>01 · Classification</h3>
            <p>
                Decision Tree predicts the confidence
                class of fire detections.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="workflow-card">
            <h3>02 · Spatial Clustering</h3>
            <p>
                DBSCAN identifies geographical
                clusters and noise detections.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="workflow-card">
            <h3>03 · Priority Analysis</h3>
            <p>
                Weighted priority scores rank
                detections for further investigation.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# --------------------------------------------------
# DASHBOARD NAVIGATION
# --------------------------------------------------

st.subheader("Explore Dashboard")

st.markdown(
    "Select a section to explore the fire intelligence results."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="nav-card">
            <h3>Live Fire Monitoring</h3>
            <p>
                View recent fire detections, geographical
                clusters and daily detection trends.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/1_Live_Fire_Intelligence.py",
        label="Open Live Monitoring",
        icon=":material/map:"
    )

with col2:
    st.markdown(
        """
        <div class="nav-card">
            <h3>Priority Analysis</h3>
            <p>
                Explore priority categories, high-priority
                clusters and individual detections.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/2_Regional_Priority_Analysis.py",
        label="Open Priority Analysis",
        icon=":material/priority_high:"
    )

with col3:
    st.markdown(
        """
        <div class="nav-card">
            <h3>Model Evaluation</h3>
            <p>
                Examine prediction distribution and
                evaluation results against NASA labels.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/3_Live_Model_Evaluation.py",
        label="Open Model Evaluation",
        icon=":material/analytics:"
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        <div>AI Mini Project | Anshika (2601) · Kiran (2605)</div>
        <div class="footer-subtitle">
            Satellite Fire Hotspot Intelligence
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
