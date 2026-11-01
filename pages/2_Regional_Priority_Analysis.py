
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.priority import (
    calculate_priority_scores,
    calculate_priority_cluster_summary,
    get_top_priority_observations,
    get_top_priority_clusters
)

from utils.visualisations import (
    plot_priority_distribution,
    plot_cluster_priority
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Priority Analysis",
    page_icon="📊",
    layout="wide"
)


# ------------------------------------------------------------
# UI Styling
# ------------------------------------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #101827;
    color: #F1F5F9;
}

/* Content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Headings */
h1, h2, h3 {
    color: #F1F5F9 !important;
}

/* Paragraphs */
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

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #94A3B8;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #F1F5F9;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #182538;
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #94A3B8;
    font-size: 13px;
    padding-top: 22px;
    padding-bottom: 10px;
    border-top: 1px solid #334155;
    margin-top: 40px;
}

.footer-subtitle {
    color: #64748B;
    font-size: 12px;
}

hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Page Header
# ------------------------------------------------------------

st.title("Priority Analysis")

st.caption(
    "Explore individual fire detection priorities "
    "and priority patterns across spatial clusters."
)


# ------------------------------------------------------------
# Retrieve Data from Page 1
# ------------------------------------------------------------

if "live_fire_data" not in st.session_state:

    st.warning(
        "Fire data is not available. Open Live Fire Monitoring "
        "first to fetch and process the latest observations."
    )

    st.stop()


data = st.session_state["live_fire_data"].copy()


# ------------------------------------------------------------
# Calculate Individual Priority Scores
# ------------------------------------------------------------

try:

    priority_data = calculate_priority_scores(data)

except Exception as error:

    st.error(f"Unable to calculate priority scores: {error}")
    st.stop()


if priority_data.empty:

    st.warning("No observations are available for priority analysis.")
    st.stop()


# ------------------------------------------------------------
# Priority Counts
# ------------------------------------------------------------

priority_counts = (
    priority_data["priority_category"]
    .value_counts()
)

high_count = int(priority_counts.get("High", 0))
medium_count = int(priority_counts.get("Medium", 0))
low_count = int(priority_counts.get("Low", 0))


# ------------------------------------------------------------
# Priority Summary
# ------------------------------------------------------------

st.subheader("Priority Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "High Priority",
        f"{high_count:,}"
    )

with col2:
    st.metric(
        "Medium Priority",
        f"{medium_count:,}"
    )

with col3:
    st.metric(
        "Low Priority",
        f"{low_count:,}"
    )

st.caption(
    f"Total observations analysed: {len(priority_data):,}"
)


st.divider()


# ------------------------------------------------------------
# Priority Map
# ------------------------------------------------------------

st.subheader("Priority Map")

st.caption(
    "Geographical distribution of individual fire detections. "
    "Red: High · Orange: Medium · Green: Low"
)

st.caption(
    "Both clustered and DBSCAN noise observations are included."
)

map_data = priority_data.dropna(
    subset=["latitude", "longitude", "priority_category"]
).copy()


if not map_data.empty:

    priority_map = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        color="priority_category",
        color_discrete_map={
            "High": "#EF4444",
            "Medium": "#F59E0B",
            "Low": "#22C55E"
        },
        hover_data={
            "latitude": False,
            "longitude": False,
            "country": True,
            "frp": ":.2f",
            "priority_score": ":.2f",
            "cluster": True
        },
        zoom=4,
        height=600
    )

    priority_map.update_layout(
        map_style="open-street-map",
        margin={"r": 0, "t": 20, "l": 0, "b": 0},
        legend_title_text="Priority"
    )

    st.plotly_chart(
        priority_map,
        use_container_width=True
    )

else:

    st.info("No valid geographical coordinates are available.")


st.divider()


# ------------------------------------------------------------
# Priority Distribution and Cluster Ranking
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Priority Distribution")

    priority_chart = plot_priority_distribution(priority_data)

    st.plotly_chart(
        priority_chart,
        use_container_width=True
    )


with col2:

    st.subheader("Highest-Ranked Clusters")

    st.caption("Ranked by average individual priority score.")

    top_clusters = get_top_priority_clusters(
        priority_data,
        number=10
    )

    if not top_clusters.empty:

        cluster_chart = plot_cluster_priority(top_clusters)

        st.plotly_chart(
            cluster_chart,
            use_container_width=True
        )

    else:

        st.info("No spatial clusters are available for ranking.")


st.divider()


# ------------------------------------------------------------
# Cluster Summary Table
# ------------------------------------------------------------

st.subheader("Cluster Details")

if not top_clusters.empty:

    cluster_columns = [
        "cluster",
        "detection_count",
        "average_priority",
        "maximum_priority",
        "average_frp",
        "maximum_frp",
        "dominant_confidence"
    ]

    available_columns = [
        column for column in cluster_columns
        if column in top_clusters.columns
    ]

    st.dataframe(
        top_clusters[available_columns],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No cluster summary is available.")


st.divider()


# ------------------------------------------------------------
# Highest-Priority Detections
# ------------------------------------------------------------

st.subheader("Highest-Priority Detections")

top_observations = get_top_priority_observations(
    priority_data,
    number=10
)

observation_columns = [
    "latitude",
    "longitude",
    "country",
    "acq_date",
    "frp",
    "predicted_confidence",
    "priority_score",
    "priority_category",
    "cluster"
]

available_columns = [
    column for column in observation_columns
    if column in top_observations.columns
]

st.dataframe(
    top_observations[available_columns],
    use_container_width=True,
    hide_index=True
)


st.divider()


# ------------------------------------------------------------
# Priority Methodology and Limitations
# ------------------------------------------------------------

with st.expander("How Priority Is Calculated"):

    st.markdown("#### Individual Priority Score")

    st.latex(
        r"P = 100(0.50F + 0.30D + 0.20C)"
    )

    st.markdown(
        """
        | Component | Description | Weight |
        |---|---|---:|
        | FRP score (F) | Percentile rank of Fire Radiative Power | 50% |
        | Density score (D) | Log-normalised nearby detection count within 5 km | 30% |
        | Confidence score (C) | Decision Tree predicted confidence mapping | 20% |
        """
    )

    st.markdown("#### Confidence Mapping")

    st.markdown(
        """
        | Predicted class | Score |
        |---|---:|
        | High (`h`) | 1.0 |
        | Nominal (`n`) | 0.7 |
        | Low (`l`) | 0.4 |
        """
    )

    st.markdown("#### Priority Categories")

    st.markdown(
        """
        | Priority score | Category |
        |---|---|
        | 70–100 | High |
        | 40–less than 70 | Medium |
        | Less than 40 | Low |
        """
    )

    st.markdown("#### Cluster Priority")

    st.write(
        "Individual priority scores are calculated first. "
        "Cluster-level priority is summarised using the average "
        "priority score of detections within each cluster."
    )

    st.write(
        "**Average priority:** Overall priority level of detections "
        "within a cluster."
    )

    st.write(
        "**Maximum priority:** Highest individual priority score "
        "within the cluster."
    )

    st.write(
        "**Detection count:** Number of observations belonging "
        "to the cluster."
    )

    st.write(
        "Clusters are ranked by average priority, not by detection count."
    )

    st.write(
        "DBSCAN noise observations are excluded from cluster ranking, "
        "but remain included in individual priority analysis and the map."
    )

    st.markdown("#### Notes and Limitations")

    st.warning(
        "The priority score is a project-defined investigation-priority "
        "index. It is not a validated fire-risk probability, fire-severity "
        "measurement or emergency-response classification."
    )

    st.markdown(
        """
        - FRP, local detection density and predicted confidence are
          weighted indicators used by this project.
        - The confidence component comes from the Decision Tree model
          and is not an independent measurement of fire severity.
        - A high score indicates higher investigation priority under
          the selected formula; it does not confirm a dangerous fire.
        - DBSCAN clustering and priority scoring are independent processes.
          Priority scores do not affect cluster formation.
        - The 5 km density calculation is separate from DBSCAN's
          geographical neighbourhood radius.
        """
    )


# ------------------------------------------------------------
# Download Priority Analysis Data
# ------------------------------------------------------------

st.divider()

st.subheader("Download Data")

cluster_summary = calculate_priority_cluster_summary(
    priority_data
)

download_options = {
    "All Priority Observations": (
        priority_data.to_csv(index=False).encode("utf-8"),
        "all_priority_observations.csv"
    ),

    "Full Cluster Summary": (
        cluster_summary.to_csv(index=False).encode("utf-8"),
        "priority_cluster_summary.csv"
    ),

    "Top 10 Priority Clusters": (
        top_clusters.to_csv(index=False).encode("utf-8"),
        "top_10_priority_clusters.csv"
    ),

    "Top 10 Priority Observations": (
        top_observations.to_csv(index=False).encode("utf-8"),
        "top_10_priority_observations.csv"
    )
}

selected_download = st.selectbox(
    "Select report",
    list(download_options.keys())
)

download_data, download_filename = download_options[selected_download]

st.download_button(
    label="Download CSV",
    data=download_data,
    file_name=download_filename,
    mime="text/csv",
    use_container_width=True
)


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

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

st.caption(
    "Priority scores are intended for exploratory analysis "
    "and should not be interpreted as confirmed fire-risk levels."
)
