
"""
File Name: app.py
Project: Satellite Fire Hotspot Intelligence
Purpose: Main dashboard configuration and Home page.
"""

import streamlit as st
from utils.theme import apply_theme


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Fire Intelligence Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown(
    """
    <div class="hero-section">
        <div class="hero-label">NASA SATELLITE DATA · AI-POWERED ANALYSIS</div>
        <h1>Satellite Fire Hotspot Intelligence</h1>
        <p>
            An integrated system for fire hotspot classification,
            spatial clustering and priority analysis.
        </p>
        <div class="hero-source">
            DATA SOURCE: NASA FIRMS | VIIRS-SNPP NRT
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# PROJECT OVERVIEW
# --------------------------------------------------

st.subheader("Project Overview")

st.markdown(
    """
    This platform analyses satellite-based fire hotspot detections
    using machine learning and spatial analysis techniques.

    It combines three major processes: predicting detection
    confidence, identifying geographical clusters and assigning
    investigation-priority scores to individual observations.
    """
)

st.divider()


# --------------------------------------------------
# SYSTEM WORKFLOW
# --------------------------------------------------

st.subheader("How the System Works")

st.caption(
    "Three integrated stages transform satellite observations "
    "into structured fire intelligence."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="workflow-card">
            <div class="card-number">01</div>
            <div class="card-icon">🎯</div>
            <h3>Fire Classification</h3>
            <p>
                A trained Decision Tree model classifies
                satellite detections into Low, Nominal
                and High confidence categories.
            </p>
            <div class="card-tag">MACHINE LEARNING</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="workflow-card">
            <div class="card-number">02</div>
            <div class="card-icon">📍</div>
            <h3>Spatial Clustering</h3>
            <p>
                DBSCAN groups geographically nearby
                fire detections and identifies
                observations that do not belong
                to dense clusters.
            </p>
            <div class="card-tag">SPATIAL ANALYSIS</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="workflow-card">
            <div class="card-number">03</div>
            <div class="card-icon">🔥</div>
            <h3>Priority Analysis</h3>
            <p>
                A weighted scoring method combines
                FRP, nearby detection density and
                predicted confidence to rank
                observations for investigation.
            </p>
            <div class="card-tag">PRIORITY SCORING</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# --------------------------------------------------
# DASHBOARD NAVIGATION
# --------------------------------------------------

st.subheader("Explore the Dashboard")

st.caption(
    "Select a module to explore the corresponding analysis."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="nav-card">
            <div class="nav-icon">🛰️</div>
            <h3>Live Fire Monitoring</h3>
            <p>
                Retrieve recent satellite fire detections,
                view classification results, explore
                geographical clusters and examine
                detection trends.
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
            <div class="nav-icon">🔥</div>
            <h3>Priority Analysis</h3>
            <p>
                Explore High, Medium and Low priority
                observations, examine priority scores
                and identify important spatial clusters.
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
            <div class="nav-icon">📊</div>
            <h3>Model Evaluation</h3>
            <p>
                Examine prediction distributions,
                compare model predictions with
                NASA confidence labels and review
                evaluation metrics.
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


st.divider()


# --------------------------------------------------
# TECHNOLOGY AND METHODOLOGY
# --------------------------------------------------

st.subheader("Technology Behind the Platform")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown(
        """
        **Data and Machine Learning**

        - NASA FIRMS VIIRS-SNPP satellite observations
        - Python and Pandas for data processing
        - Scikit-learn Decision Tree classification
        - DBSCAN spatial clustering
        """
    )

with tech_col2:
    st.markdown(
        """
        **Analysis and Visualisation**

        - BallTree and Haversine distance calculations
        - FRP-based priority scoring
        - Plotly interactive maps and charts
        - Streamlit dashboard interface
        """
    )


# --------------------------------------------------
# PROJECT SCOPE
# --------------------------------------------------

with st.expander("Project Scope and Important Notes"):

    st.markdown(
        """
        - The system analyses satellite-based fire detections.
        - The Decision Tree predicts detection confidence classes.
        - DBSCAN identifies spatially dense groups of detections.
        - Priority scores rank observations for further investigation.
        - The platform does not predict future fires.
        - Priority scores are project-defined investigation
          indices, not probabilities of fire risk or severity.
        """
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        <div class="footer-title">
            SATELLITE FIRE HOTSPOT INTELLIGENCE
        </div>
        <div>
            AI Mini Project | Anshika (2601) · Kiran (2605)
        </div>
        <div class="footer-subtitle">
            Powered by NASA FIRMS satellite observations
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
