
"""
File Name: 2_Regional_Priority_Analysis.py
Project: Satellite Fire Hotspot Intelligence
Purpose: Analyse individual fire detection priorities,
         spatial cluster priorities and priority distributions.
"""

import streamlit as st

from utils.theme import apply_theme

from utils.priority import (
    calculate_priority_scores,
    calculate_priority_cluster_summary,
    get_top_priority_observations,
    get_top_priority_clusters
)

from utils.visualisations import (
    plot_priority_map,
    plot_priority_distribution,
    plot_cluster_priority
)


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Priority Analysis",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()


# ==================================================
# 2. PAGE HEADER
# ==================================================

st.title("Priority Analysis")

st.caption(
    "Analyse individual fire detection priorities and "
    "identify high-priority geographical clusters."
)

st.divider()


# ==================================================
# 3. RETRIEVE LIVE FIRE DATA
# ==================================================

if "live_fire_data" not in st.session_state:

    st.warning(
        "Open Live Fire Monitoring first to fetch and "
        "process fire observations."
    )

    st.stop()


data = st.session_state["live_fire_data"].copy()


if data.empty:

    st.warning("No live fire observations are available.")

    st.stop()


# ==================================================
# 4. CALCULATE PRIORITY SCORES
# ==================================================

try:

    priority_data = calculate_priority_scores(data)

except Exception as error:

    st.error(f"Unable to calculate priority scores: {error}")

    st.stop()


if priority_data.empty:

    st.warning("No observations are available for priority analysis.")

    st.stop()


# ==================================================
# 5. PRIORITY SUMMARY
# ==================================================

counts = priority_data["priority_category"].value_counts()

high = counts.get("High", 0)
medium = counts.get("Medium", 0)
low = counts.get("Low", 0)

st.subheader("Priority Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "High Priority",
    f"{high:,}"
)

col2.metric(
    "Medium Priority",
    f"{medium:,}"
)

col3.metric(
    "Low Priority",
    f"{low:,}"
)

st.caption(
    f"Total observations analysed: {len(priority_data):,}"
)

st.divider()


# ==================================================
# 6. PRIORITY MAP
# ==================================================

st.subheader("Geographical Priority Distribution")

st.caption(
    "High: Red · Medium: Gold · Low: Green"
)

st.caption(
    "Includes clustered and DBSCAN noise observations."
)

fig = plot_priority_map(priority_data)

if fig is not None:

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "No valid geographical coordinates are available."
    )

st.divider()


# ==================================================
# 7. PRIORITY DISTRIBUTION
#    AND CLUSTER RANKING
# ==================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Priority Distribution")

    chart = plot_priority_distribution(priority_data)

    if chart is not None:

        st.plotly_chart(
            chart,
            use_container_width=True
        )

    else:

        st.info(
            "No priority distribution is available."
        )


with col2:

    st.subheader("Highest-Ranked Clusters")

    st.caption(
        "Ranked by average individual priority score."
    )

    top_clusters = get_top_priority_clusters(
        priority_data,
        number=10
    )

    if not top_clusters.empty:

        chart = plot_cluster_priority(top_clusters)

        if chart is not None:

            st.plotly_chart(
                chart,
                use_container_width=True
            )

        else:

            st.info(
                "Unable to generate the cluster priority chart."
            )

    else:

        st.info(
            "No spatial clusters are available for ranking."
        )

st.divider()


# ==================================================
# 8. CLUSTER DETAILS
# ==================================================

st.subheader("Cluster Details")

if not top_clusters.empty:

    columns = [
        "cluster",
        "detection_count",
        "average_priority",
        "maximum_priority",
        "average_frp",
        "maximum_frp",
        "dominant_confidence"
    ]

    available = [
        col for col in columns
        if col in top_clusters.columns
    ]

    st.dataframe(
        top_clusters[available],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No cluster summary is available."
    )

st.divider()


# ==================================================
# 9. HIGHEST-PRIORITY DETECTIONS
# ==================================================

st.subheader("Highest-Priority Detections")

top_observations = get_top_priority_observations(
    priority_data,
    number=10
)

if not top_observations.empty:

    columns = [
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

    available = [
        col for col in columns
        if col in top_observations.columns
    ]

    st.dataframe(
        top_observations[available],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No high-priority observations are available."
    )

st.divider()


# ==================================================
# 10. PRIORITY METHODOLOGY
# ==================================================

with st.expander("How Priority Is Calculated"):

    st.markdown("#### Individual Priority Score")

    st.latex(
        r"P = 100(0.50F + 0.30D + 0.20C)"
    )

    st.markdown("""
    | Component | Description | Weight |
    |---|---|---:|
    | FRP (F) | FRP percentile rank | 50% |
    | Density (D) | Log-normalised detections within 5 km | 30% |
    | Confidence (C) | Decision Tree predicted confidence | 20% |
    """)

    st.markdown("#### Confidence Mapping")

    st.markdown("""
    | Predicted Class | Score |
    |---|---:|
    | High (`h`) | 1.0 |
    | Nominal (`n`) | 0.7 |
    | Low (`l`) | 0.4 |
    """)

    st.markdown("#### Priority Categories")

    st.markdown("""
    | Score | Category |
    |---|---|
    | 70–100 | High |
    | 40–less than 70 | Medium |
    | Less than 40 | Low |
    """)

    st.markdown("#### Cluster Priority")

    st.write(
        "Individual priority scores are calculated first. "
        "Cluster priority is summarised using the average "
        "score of detections within each cluster."
    )

    st.write(
        "**Average priority:** Overall priority of detections in a cluster."
    )

    st.write(
        "**Maximum priority:** Highest individual score in a cluster."
    )

    st.write(
        "**Detection count:** Number of observations in a cluster."
    )

    st.write(
        "Clusters are ranked by average priority, not detection count."
    )

    st.write(
        "Noise observations are excluded from cluster ranking but remain "
        "included in individual priority analysis and the map."
    )

    st.markdown("#### Notes and Limitations")

    st.warning(
        "The priority score is a project-defined investigation-priority "
        "index. It is not a validated fire-risk probability, fire-severity "
        "measurement or emergency-response classification."
    )

    st.markdown("""
    - FRP, density and predicted confidence are weighted indicators.
    - Confidence is predicted by the Decision Tree model.
    - A high score does not confirm a dangerous fire.
    - DBSCAN clustering and priority scoring are independent.
    - The 5 km density calculation is separate from DBSCAN's neighbourhood radius.
    """)


# ==================================================
# 11. PREPARE DOWNLOAD REPORTS
# ==================================================

st.divider()

st.subheader("Download Data")

cluster_summary = calculate_priority_cluster_summary(
    priority_data
)

downloads = {

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


# ==================================================
# 12. DOWNLOAD SELECTED REPORT
# ==================================================

selected = st.selectbox(
    "Select report",
    list(downloads.keys())
)

csv_data, filename = downloads[selected]

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name=filename,
    mime="text/csv",
    use_container_width=True
)


# ==================================================
# 13. FOOTER
# ==================================================
# Footer
st.markdown("""
<div class="footer">
    <div>AI Mini Project | Anshika (2601) · Kiran (2605)</div>
    <div class="footer-subtitle">Satellite Fire Hotspot Intelligence</div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "NASA FIRMS VIIRS-SNPP NRT observations may be revised "
    "as NASA updates its data."
)
