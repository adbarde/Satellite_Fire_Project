
"""
File Name: visualisations.py
Purpose: Create geographical maps and analytical charts
         for the satellite fire hotspot dashboard.
"""

import pandas as pd
import plotly.express as px


# --------------------------------------------------
# Common Chart Settings
# --------------------------------------------------

CHART_HEIGHT = 420

HIGH_COLOR = "#EF4444"
MEDIUM_COLOR = "#F59E0B"
LOW_COLOR = "#22C55E"


# --------------------------------------------------
# 1. Geographical Map of Top 10 DBSCAN Clusters
# --------------------------------------------------

def plot_cluster_map(data):
    """
    Display the 10 largest non-noise DBSCAN clusters.

    Each cluster has a separate colour.
    Hover shows only detection count, country and FRP.
    """

    if data.empty:
        return None

    required_columns = [
        "latitude",
        "longitude",
        "cluster",
        "country",
        "frp"
    ]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Missing columns for cluster map: "
            + ", ".join(missing)
        )

    # Exclude DBSCAN noise
    clustered_data = data[
        data["cluster"] != -1
    ].copy()

    if clustered_data.empty:
        return None

    # Find the 10 largest clusters
    cluster_counts = (
        clustered_data["cluster"]
        .value_counts()
        .head(10)
    )

    top_10_ids = cluster_counts.index

    # Keep observations from the selected clusters
    map_data = clustered_data[
        clustered_data["cluster"].isin(top_10_ids)
    ].copy()

    # Calculate the number of detections in each cluster
    map_data["cluster_size"] = (
        map_data.groupby("cluster")["cluster"]
        .transform("size")
    )

    # Create readable cluster labels
    map_data["cluster_label"] = (
        "Cluster "
        + map_data["cluster"].astype(str)
    )

    fig = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        color="cluster_label",
        hover_name="country",
        hover_data={
            "latitude": False,
            "longitude": False,
            "cluster": False,
            "cluster_label": False,
            "cluster_size": True,
            "frp": ":.2f"
        },
        labels={
            "cluster_size": "Number of Detections",
            "frp": "FRP (MW)"
        },
        color_discrete_sequence=(
            px.colors.qualitative.Dark24
        ),
        zoom=3,
        center={
            "lat": 20,
            "lon": 82
        },
        map_style="open-street-map",
        title="Top 10 Largest DBSCAN Clusters"
    )

    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.8
        )
    )

    fig.update_layout(
        height=650,
        legend_title_text="DBSCAN Cluster",
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01
        )
    )

    return fig


# --------------------------------------------------
# 2. Top 10 Largest DBSCAN Clusters
# --------------------------------------------------

def plot_cluster_sizes(data):
    """
    Display the 10 largest non-noise DBSCAN clusters.
    """

    if data.empty:
        return None

    cluster_counts = (
        data[data["cluster"] != -1]
        .groupby("cluster")
        .size()
        .reset_index(name="detection_count")
    )

    if cluster_counts.empty:
        return None

    # Select the 10 largest clusters
    cluster_counts = (
        cluster_counts
        .sort_values(
            "detection_count",
            ascending=False
        )
        .head(10)
    )

    cluster_counts["cluster_label"] = (
        "Cluster "
        + cluster_counts["cluster"].astype(str)
    )

    fig = px.bar(
        cluster_counts,
        x="detection_count",
        y="cluster_label",
        orientation="h",
        text="detection_count",
        title="Top 10 Largest DBSCAN Clusters",
        labels={
            "cluster_label": "DBSCAN Cluster",
            "detection_count": "Number of Detections"
        }
    )

    fig.update_traces(
        marker_color="#3B82F6",
        textposition="outside"
    )

    fig.update_layout(
        height=CHART_HEIGHT,
        yaxis={
            "categoryorder": "total ascending"
        },
        showlegend=False
    )

    return fig


# --------------------------------------------------
# 3. Daily Fire Detection Trend
# --------------------------------------------------

def plot_temporal_trend(data):
    """
    Display the number of fire detections per day.
    """

    if data.empty:
        return None

    daily_counts = (
        data.groupby("acq_date")
        .size()
        .reset_index(name="detection_count")
        .sort_values("acq_date")
    )

    if daily_counts.empty:
        return None

    fig = px.line(
        daily_counts,
        x="acq_date",
        y="detection_count",
        markers=True,
        title="Daily Fire Detection Trend",
        labels={
            "acq_date": "Date",
            "detection_count": "Number of Detections"
        }
    )

    fig.update_traces(
        line=dict(
            color="#38BDF8",
            width=3
        ),
        marker=dict(size=8)
    )

    fig.update_layout(
        height=CHART_HEIGHT
    )

    return fig


# --------------------------------------------------
# 4. Individual Detection Priority Distribution
# --------------------------------------------------

def plot_priority_distribution(data):
    """
    Display the number of detections in each
    investigation-priority category.
    """

    if data.empty:
        return None

    priority_counts = (
        data["priority_category"]
        .value_counts()
        .reindex(
            ["Low", "Medium", "High"],
            fill_value=0
        )
        .rename_axis("Priority")
        .reset_index(name="Count")
    )

    fig = px.bar(
        priority_counts,
        x="Priority",
        y="Count",
        color="Priority",
        text="Count",
        title="Fire Detections by Priority Category",
        color_discrete_map={
            "Low": LOW_COLOR,
            "Medium": MEDIUM_COLOR,
            "High": HIGH_COLOR
        }
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=CHART_HEIGHT,
        showlegend=False
    )

    return fig


# --------------------------------------------------
# 5. Top 10 Clusters by Average Priority
# --------------------------------------------------

def plot_cluster_priority(summary):
    """
    Display the 10 DBSCAN clusters with the highest
    average investigation-priority scores.

    Noise is excluded.
    """

    if summary.empty:
        return None

    required_columns = [
        "cluster",
        "average_priority",
        "detection_count"
    ]

    missing = [
        column for column in required_columns
        if column not in summary.columns
    ]

    if missing:
        raise ValueError(
            "Missing columns for cluster priority chart: "
            + ", ".join(missing)
        )

    # Exclude noise
    summary = summary[
        summary["cluster"] != -1
    ].copy()

    if summary.empty:
        return None

    # Select the 10 highest-priority clusters
    summary = (
        summary
        .sort_values(
            "average_priority",
            ascending=False
        )
        .head(10)
    )

    summary["cluster_label"] = (
        "Cluster "
        + summary["cluster"].astype(str)
    )

    hover_columns = [
        column for column in [
            "detection_count",
            "average_frp",
            "maximum_frp",
            "maximum_priority"
        ]
        if column in summary.columns
    ]

    fig = px.bar(
        summary,
        x="average_priority",
        y="cluster_label",
        orientation="h",
        color="average_priority",
        color_continuous_scale="YlOrRd",
        hover_data=hover_columns,
        title="Top 10 Clusters by Average Priority",
        labels={
            "cluster_label": "DBSCAN Cluster",
            "average_priority": "Average Priority Score",
            "detection_count": "Number of Detections",
            "average_frp": "Average FRP (MW)",
            "maximum_frp": "Maximum FRP (MW)",
            "maximum_priority": "Maximum Priority Score"
        }
    )

    fig.update_layout(
        height=CHART_HEIGHT,
        yaxis={
            "categoryorder": "total ascending"
        },
        coloraxis_showscale=False
    )

    return fig
