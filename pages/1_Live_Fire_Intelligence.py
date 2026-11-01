
import streamlit as st
import pandas as pd

from utils.nasa_api import fetch_nasa_data, get_api_information
from utils.preprocessing import filter_selected_countries, prepare_live_data
from utils.classification import classify_live_data
from utils.clustering import (
    perform_clustering,
    calculate_clustering_summary,
    EPS_KM,
    MIN_SAMPLES
)
from utils.visualisations import (
    plot_cluster_map,
    plot_cluster_sizes,
    plot_temporal_trend
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Live Fire Monitoring",
    page_icon="🔥",
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

st.title("Live Fire Monitoring")

st.caption(
    "Recent satellite detections, geographical clusters "
    "and daily fire activity."
)


# ------------------------------------------------------------
# Sidebar: Data Selection
# ------------------------------------------------------------

st.sidebar.header("Data Settings")

day_range = st.sidebar.selectbox(
    "Observation Period",
    [1, 2, 3, 4, 5],
    index=4,
    format_func=lambda x: f"Last {x} day(s)"
)

refresh = st.sidebar.button(
    "Refresh Fire Data",
    use_container_width=True
)


# ------------------------------------------------------------
# Fetch and Process Data
# ------------------------------------------------------------

if (
    refresh
    or "live_fire_data" not in st.session_state
    or st.session_state.get("selected_period") != day_range
):

    with st.spinner("Fetching and processing NASA fire data..."):

        try:
            raw_data = fetch_nasa_data(day_range)

            if raw_data.empty:
                st.warning("No fire detections were returned by NASA FIRMS.")
                st.stop()

            # Keep detections inside the selected countries
            country_data = filter_selected_countries(raw_data)

            if country_data.empty:
                st.warning("No detections were found in the selected countries.")
                st.stop()

            # Prepare features required by the ML model
            prepared_data, X_live = prepare_live_data(country_data)

            if prepared_data.empty:
                st.warning("No valid observations remain after preprocessing.")
                st.stop()

            # Predict confidence classes
            classified_data = classify_live_data(
                prepared_data,
                X_live
            )

            # Perform geographical clustering independently
            clustered_data = perform_clustering(classified_data)

            # Store processed data
            st.session_state["live_fire_data"] = clustered_data
            st.session_state["selected_period"] = day_range
            st.session_state["last_updated"] = pd.Timestamp.now()

        except Exception as error:
            st.error(f"Unable to load fire data: {error}")
            st.stop()


data = st.session_state["live_fire_data"]


# ------------------------------------------------------------
# Data Summary
# ------------------------------------------------------------

summary = calculate_clustering_summary(data)

total_detections = summary["total_detections"]
total_clusters = summary["number_of_clusters"]
clustered_detections = summary["clustered_detections"]
noise_detections = summary["noise_detections"]

clustered_percentage = summary["clustered_percentage"]
noise_percentage = summary["noise_percentage"]


# ------------------------------------------------------------
# Data Source and Update Information
# ------------------------------------------------------------

api_info = get_api_information()

col1, col2 = st.columns(2)

with col1:
    st.caption(f"Source: {api_info['source']}")

with col2:
    st.caption(
        f"Last updated: "
        f"{st.session_state['last_updated'].strftime('%d %b %Y, %H:%M:%S')}"
    )


st.divider()


# ------------------------------------------------------------
# Detection Summary
# ------------------------------------------------------------

st.subheader("Detection Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Detections",
        f"{total_detections:,}"
    )

with col2:
    st.metric(
        "Spatial Clusters",
        f"{total_clusters:,}"
    )

with col3:
    st.metric(
        "Clustered Detections",
        f"{clustered_detections:,}",
        f"{clustered_percentage:.2f}%"
    )

with col4:
    st.metric(
        "Noise Detections",
        f"{noise_detections:,}",
        f"{noise_percentage:.2f}%"
    )


st.divider()


# ------------------------------------------------------------
# Fire Cluster Map
# ------------------------------------------------------------

st.subheader("Fire Cluster Map")

st.caption(
    "Geographical distribution of the 10 largest DBSCAN clusters. "
    "Hover over detections for observation details."
)

cluster_map = plot_cluster_map(data)

st.plotly_chart(
    cluster_map,
    use_container_width=True
)


st.divider()


# ------------------------------------------------------------
# Cluster and Daily Detection Charts
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Largest Clusters")

    st.caption("Clusters ranked by number of detections.")

    cluster_chart = plot_cluster_sizes(data)

    st.plotly_chart(
        cluster_chart,
        use_container_width=True
    )


with col2:

    st.subheader("Daily Detections")

    st.caption("Detection counts across the selected period.")

    trend_chart = plot_temporal_trend(data)

    st.plotly_chart(
        trend_chart,
        use_container_width=True
    )


st.divider()


# ------------------------------------------------------------
# DBSCAN Information
# ------------------------------------------------------------

with st.expander("DBSCAN Information"):

    st.markdown("#### Clustering Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Distance Metric", "Haversine")

    with col2:
        st.metric("EPS Radius", f"{EPS_KM} km")

    with col3:
        st.metric("Minimum Samples", MIN_SAMPLES)

    st.caption("Earth radius used: 6371 km")

    st.markdown("#### Cluster Interpretation")

    st.write(
        f"**Clustered detections:** {clustered_detections:,} "
        f"({clustered_percentage:.2f}%) belong to a DBSCAN cluster."
    )

    st.write(
        f"**Noise detections:** {noise_detections:,} "
        f"({noise_percentage:.2f}%) were not assigned to a cluster."
    )

    st.write(
        "Noise does not mean that a detection is invalid or low priority. "
        "It means that the observation did not satisfy the DBSCAN "
        "density criteria."
    )

    st.write(
        "DBSCAN forms clusters through connected neighbouring observations. "
        "Therefore, not every pair of detections in the same cluster "
        "must be within the EPS distance."
    )

    st.write(
        "Cluster IDs are algorithm-assigned labels. They do not represent "
        "geographical names, severity levels or priority rankings."
    )


# ------------------------------------------------------------
# Observation Data
# ------------------------------------------------------------

with st.expander("Observation Data"):

    display_columns = [
        "latitude",
        "longitude",
        "country",
        "acq_date",
        "frp",
        "predicted_confidence",
        "cluster"
    ]

    available_columns = [
        column for column in display_columns
        if column in data.columns
    ]

    st.dataframe(
        data[available_columns],
        use_container_width=True,
        hide_index=True
    )

    csv_data = data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download All Fire Observations",
        data=csv_data,
        file_name="live_fire_observations.csv",
        mime="text/csv"
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
    "NASA FIRMS VIIRS-SNPP NRT observations may be revised "
    "as NASA updates its data."
)
