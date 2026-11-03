
import streamlit as st
import pandas as pd
from utils.theme import apply_theme
from utils.nasa_api import fetch_nasa_data, get_api_information
from utils.preprocessing import filter_selected_countries, prepare_live_data
from utils.classification import classify_live_data
from utils.clustering import (
    perform_clustering, calculate_clustering_summary,
    EPS_KM, MIN_SAMPLES
)
from utils.visualisations import (
    plot_cluster_map, plot_cluster_sizes, plot_temporal_trend
)


# Page configuration
st.set_page_config(
    page_title="Live Fire Monitoring",
    page_icon="🔥",
    layout="wide"
)
apply_theme()

# Page header
st.title("Live Fire Monitoring")
st.caption("Recent satellite detections, geographical clusters and daily fire activity.")


# Sidebar settings
st.sidebar.header("Data Settings")

day_range = st.sidebar.selectbox(
    "Observation Period", [1, 2, 3, 4, 5],
    index=4, format_func=lambda x: f"Last {x} day(s)"
)

refresh = st.sidebar.button("Refresh Fire Data", use_container_width=True)


# Fetch and process data
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

            country_data = filter_selected_countries(raw_data)

            if country_data.empty:
                st.warning("No detections were found in the selected countries.")
                st.stop()

            prepared_data, X_live = prepare_live_data(country_data)

            if prepared_data.empty:
                st.warning("No valid observations remain after preprocessing.")
                st.stop()

            classified_data = classify_live_data(prepared_data, X_live)
            clustered_data = perform_clustering(classified_data)

            st.session_state["live_fire_data"] = clustered_data
            st.session_state["selected_period"] = day_range
            st.session_state["last_updated"] = pd.Timestamp.now()

        except Exception as error:
            st.error(f"Unable to load fire data: {error}")
            st.stop()


data = st.session_state["live_fire_data"]


# Detection summary
summary = calculate_clustering_summary(data)

total_detections = summary["total_detections"]
total_clusters = summary["number_of_clusters"]
clustered_detections = summary["clustered_detections"]
noise_detections = summary["noise_detections"]
clustered_percentage = summary["clustered_percentage"]
noise_percentage = summary["noise_percentage"]


# Data source information
api_info = get_api_information()
col1, col2 = st.columns(2)

col1.caption(f"Source: {api_info['source']}")
col2.caption(
    f"Last updated: {st.session_state['last_updated'].strftime('%d %b %Y, %H:%M:%S')}"
)

st.divider()


# Detection metrics
st.subheader("Detection Summary")

metrics = st.columns(4)
values = [
    ("Total Detections", f"{total_detections:,}", None),
    ("Spatial Clusters", f"{total_clusters:,}", None),
    ("Clustered Detections", f"{clustered_detections:,}", f"{clustered_percentage:.2f}%"),
    ("Noise Detections", f"{noise_detections:,}", f"{noise_percentage:.2f}%")
]

for col, (label, value, delta) in zip(metrics, values):
    col.metric(label, value, delta)

st.divider()


# Cluster map
st.subheader("Fire Cluster Map")
st.caption("Geographical distribution of the 10 largest DBSCAN clusters.")

cluster_map = plot_cluster_map(data)

if cluster_map is not None:
    st.plotly_chart(cluster_map, use_container_width=True)
else:
    st.info("No spatial clusters available to display.")

st.divider()


# Cluster size and daily trend charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Largest Clusters")
    st.caption("Clusters ranked by number of detections.")
    chart = plot_cluster_sizes(data)

    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No clusters available.")

with col2:
    st.subheader("Daily Detections")
    st.caption("Detection counts across the selected period.")
    chart = plot_temporal_trend(data)

    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No daily detection data available.")

st.divider()


# DBSCAN information
with st.expander("DBSCAN Information"):
    st.markdown("#### Clustering Parameters")

    col1, col2, col3 = st.columns(3)
    col1.metric("Distance Metric", "Haversine")
    col2.metric("EPS Radius", f"{EPS_KM} km")
    col3.metric("Minimum Samples", MIN_SAMPLES)

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
        "Noise does not mean a detection is invalid or low priority. "
        "It means it did not satisfy DBSCAN density criteria."
    )
    st.write(
        "DBSCAN forms clusters through connected neighbouring observations. "
        "Not every pair of detections in a cluster must be within the EPS distance."
    )
    st.write(
        "Cluster IDs are algorithm-assigned labels, not geographical names, "
        "severity levels or priority rankings."
    )


# Observation data and download
with st.expander("Observation Data"):
    columns = [
        "latitude", "longitude", "country", "acq_date",
        "frp", "predicted_confidence", "cluster"
    ]
    available = [col for col in columns if col in data.columns]

    st.dataframe(data[available], use_container_width=True, hide_index=True)

    st.download_button(
        "Download All Fire Observations",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="live_fire_observations.csv",
        mime="text/csv"
    )


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
