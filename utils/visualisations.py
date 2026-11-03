
"""
File Name: visualisations.py
Purpose: Create maps and charts for the fire hotspot dashboard.
"""

import plotly.express as px


# --------------------------------------------------
# CHART CONFIGURATION
# --------------------------------------------------

CHART_HEIGHT = 420

# Fire priority colours
HIGH_COLOR = "#E0523A"
MEDIUM_COLOR = "#E8B65A"
LOW_COLOR = "#65B985"

# General chart colours
PRIMARY_COLOR = "#F07836"
SECONDARY_COLOR = "#FF9A55"
TREND_COLOR = "#E8B65A"

# Distinct colours for DBSCAN clusters
CLUSTER_COLORS = [
    "#F07836",
    "#E0523A",
    "#E8B65A",
    "#65B985",
    "#45A9C5",
    "#A78BFA",
    "#F472B6",
    "#B6A28E",
    "#8BC5A5",
    "#D4A5FF"
]

# Shared chart appearance
CHART_TEMPLATE = "plotly_dark"

CHART_LAYOUT = dict(
    template=CHART_TEMPLATE,
    paper_bgcolor="#1B2025",
    plot_bgcolor="#1B2025",
    font=dict(
        family="Arial, sans-serif",
        color="#F2F0EC",
        size=12
    ),
    title=dict(
        font=dict(
            size=17,
            color="#FF9A55"
        ),
        x=0.02,
        xanchor="left"
    ),
    margin=dict(l=20, r=20, t=65, b=35),
    hoverlabel=dict(
        bgcolor="#232A30",
        bordercolor="#F07836",
        font=dict(
            color="#F2F0EC",
            size=12
        )
    ),
    xaxis=dict(
        gridcolor="#30383F",
        zerolinecolor="#46505A",
        linecolor="#30383F"
    ),
    yaxis=dict(
        gridcolor="#30383F",
        zerolinecolor="#46505A",
        linecolor="#30383F"
    )
)


def apply_chart_theme(fig, height=CHART_HEIGHT):
    """Apply consistent styling to dashboard charts."""

    fig.update_layout(
        **CHART_LAYOUT,
        height=height
    )

    return fig


# --------------------------------------------------
# 1. DBSCAN CLUSTER MAP
# --------------------------------------------------

def plot_cluster_map(data):
    """Display the 10 largest non-noise DBSCAN clusters."""

    if data.empty:
        return None

    required = [
        "latitude", "longitude", "cluster",
        "country", "frp"
    ]

    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    data = data[data["cluster"] != -1].copy()

    if data.empty:
        return None

    top_ids = data["cluster"].value_counts().head(10).index
    data = data[data["cluster"].isin(top_ids)].copy()

    data["cluster_size"] = (
        data.groupby("cluster")["cluster"].transform("size")
    )

    data["cluster_label"] = (
        "Cluster " + data["cluster"].astype(str)
    )

    fig = px.scatter_map(
        data,
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
            "cluster_size": "Detections",
            "frp": "FRP (MW)"
        },
        color_discrete_sequence=CLUSTER_COLORS,
        zoom=3,
        center={"lat": 20, "lon": 82},
        map_style="carto-darkmatter",
        title="Top 10 Largest DBSCAN Clusters"
    )

    fig.update_traces(
        marker=dict(
            size=9,
            opacity=0.85
        )
    )

    fig.update_layout(
        height=650,
        paper_bgcolor="#1B2025",
        font=dict(color="#F2F0EC"),
        title=dict(
            font=dict(size=17, color="#FF9A55"),
            x=0.02
        ),
        legend_title_text="DBSCAN Cluster",
        margin=dict(l=0, r=0, t=55, b=0),
        legend=dict(
            orientation="v",
            y=1,
            x=1.01,
            bgcolor="rgba(27,32,37,0.85)",
            bordercolor="#30383F",
            borderwidth=1
        )
    )

    return fig


# --------------------------------------------------
# 2. CLUSTER SIZE CHART
# --------------------------------------------------

def plot_cluster_sizes(data):
    """Display the 10 largest non-noise clusters."""

    if data.empty:
        return None

    counts = (
        data[data["cluster"] != -1]
        .groupby("cluster")
        .size()
        .reset_index(name="detection_count")
        .sort_values("detection_count", ascending=False)
        .head(10)
    )

    if counts.empty:
        return None

    counts["cluster_label"] = (
        "Cluster " + counts["cluster"].astype(str)
    )

    fig = px.bar(
        counts,
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
        marker=dict(
            color=PRIMARY_COLOR,
            line=dict(color="#FF9A55", width=0.5)
        ),
        textposition="outside",
        textfont=dict(color="#F2F0EC")
    )

    apply_chart_theme(fig)

    fig.update_layout(
        yaxis=dict(categoryorder="total ascending")
    )

    return fig


# --------------------------------------------------
# 3. DAILY FIRE DETECTION TREND
# --------------------------------------------------

def plot_temporal_trend(data):
    """Display daily fire detection counts."""

    if data.empty:
        return None

    counts = (
        data.groupby("acq_date")
        .size()
        .reset_index(name="detection_count")
        .sort_values("acq_date")
    )

    if counts.empty:
        return None

    fig = px.line(
        counts,
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
            color=PRIMARY_COLOR,
            width=3
        ),
        marker=dict(
            color=TREND_COLOR,
            size=7,
            line=dict(
                color=PRIMARY_COLOR,
                width=1.5
            )
        ),
        fill="tozeroy",
        fillcolor="rgba(240,120,54,0.10)"
    )

    apply_chart_theme(fig)

    return fig


# --------------------------------------------------
# 4. PRIORITY DISTRIBUTION
# --------------------------------------------------

def plot_priority_distribution(data):
    """Display Low, Medium and High priority counts."""

    if data.empty:
        return None

    counts = (
        data["priority_category"]
        .value_counts()
        .reindex(["Low", "Medium", "High"], fill_value=0)
        .rename_axis("Priority")
        .reset_index(name="Count")
    )

    fig = px.bar(
        counts,
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
        textposition="outside",
        textfont=dict(color="#F2F0EC"),
        marker_line_width=0
    )

    apply_chart_theme(fig)

    fig.update_layout(
        showlegend=False,
        xaxis_title="Priority Category",
        yaxis_title="Number of Detections"
    )

    return fig


# --------------------------------------------------
# 5. CLUSTER PRIORITY CHART
# --------------------------------------------------

def plot_cluster_priority(summary):
    """Display the 10 highest-priority non-noise clusters."""

    if summary.empty:
        return None

    required = [
        "cluster",
        "average_priority",
        "detection_count"
    ]

    missing = [col for col in required if col not in summary.columns]

    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    summary = summary[summary["cluster"] != -1].copy()

    if summary.empty:
        return None

    summary = summary.nlargest(10, "average_priority")

    summary["cluster_label"] = (
        "Cluster " + summary["cluster"].astype(str)
    )

    hover = [
        col for col in [
            "detection_count",
            "average_frp",
            "maximum_frp",
            "maximum_priority"
        ]
        if col in summary.columns
    ]

    fig = px.bar(
        summary,
        x="average_priority",
        y="cluster_label",
        orientation="h",
        color="average_priority",
        color_continuous_scale=[
            "#E8B65A",
            "#F07836",
            "#E0523A"
        ],
        hover_data=hover,
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

    apply_chart_theme(fig)

    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        coloraxis_showscale=False
    )

    return fig


def plot_priority_map(data):
    """Display priority categories on a geographical map."""

    if data.empty:
        return None

    map_data = data.dropna(
        subset=["latitude", "longitude", "priority_category"]
    )

    if map_data.empty:
        return None

    fig = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        color="priority_category",
        color_discrete_map={
            "High": HIGH_COLOR,
            "Medium": MEDIUM_COLOR,
            "Low": LOW_COLOR
        },
        hover_data={
            "latitude": False,
            "longitude": False,
            "country": True,
            "frp": ":.2f",
            "priority_score": ":.2f",
            "cluster": True
        },
        zoom=3.5,
        center={"lat": 22.5, "lon": 82.5},
        height=600,
        map_style="carto-darkmatter",
        title="Geographical Distribution of Fire Priority"
    )

    fig.update_traces(
        marker=dict(
            size=9,
            opacity=0.85
        )
    )

    fig.update_layout(
        paper_bgcolor="#1B2025",
        font=dict(color="#F2F0EC"),
        margin=dict(l=0, r=0, t=55, b=0),
        legend_title_text="Priority",
        legend=dict(
            bgcolor="rgba(27,32,37,0.85)"
        )
    )

    return fig


# ==================================================
# MODEL EVALUATION VISUALISATIONS
# ==================================================

def plot_prediction_distribution(prediction_data):
    """
    Display the distribution of predicted confidence classes.
    """

    if prediction_data.empty:
        return None

    fig = px.pie(
        prediction_data,
        names="Confidence Class",
        values="Count",
        hole=0.45,
        color="Confidence Class",
        color_discrete_map={
            "High": HIGH_COLOR,
            "Nominal": MEDIUM_COLOR,
            "Low": LOW_COLOR
        },
        title="Decision Tree Prediction Distribution"
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(
            line=dict(
                color="#1B2025",
                width=2
            )
        )
    )

    fig.update_layout(
        paper_bgcolor="#1B2025",
        plot_bgcolor="#1B2025",
        font=dict(color="#F2F0EC"),
        title=dict(
            font=dict(size=17, color="#FF9A55"),
            x=0.02
        ),
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Confidence Class"
    )

    return fig


def plot_class_performance(chart_data):
    """
    Display precision, recall and F1-score for each confidence class.
    """

    if chart_data.empty:
        return None

    fig = px.bar(
        chart_data,
        x="Confidence Class",
        y="Score",
        color="Metric",
        barmode="group",
        range_y=[0, 1],
        color_discrete_map={
            "Precision": "#F07836",
            "Recall": "#E8B65A",
            "F1-Score": "#65B985"
        },
        title="Class-wise Evaluation Metrics"
    )

    fig.update_layout(
        paper_bgcolor="#1B2025",
        plot_bgcolor="#1B2025",
        font=dict(color="#F2F0EC"),
        title=dict(
            font=dict(size=17, color="#FF9A55"),
            x=0.02
        ),
        margin=dict(l=15, r=15, t=55, b=15),
        xaxis_title="Confidence Class",
        yaxis_title="Score",
        yaxis=dict(
            range=[0, 1],
            tickformat=".0%",
            gridcolor="#30383F",
            zeroline=False
        ),
        xaxis=dict(
            gridcolor="#30383F"
        ),
        legend_title_text="Metric",
        legend=dict(
            bgcolor="rgba(27,32,37,0.85)"
        ),
        bargap=0.25
    )

    return fig


def plot_confusion_matrix(matrix_data):
    """
    Display the confusion matrix as a heatmap.
    Rows represent actual labels and columns represent predicted labels.
    """

    if matrix_data.empty:
        return None

    fig = px.imshow(
        matrix_data,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[
            "#1B2025",
            "#75452F",
            "#F07836",
            "#FF9A55"
        ],
        labels={
            "x": "Predicted Confidence",
            "y": "Actual NASA Confidence",
            "color": "Observations"
        },
        title="NASA Label Agreement - Confusion Matrix"
    )

    fig.update_layout(
        paper_bgcolor="#1B2025",
        plot_bgcolor="#1B2025",
        font=dict(color="#F2F0EC"),
        title=dict(
            font=dict(size=17, color="#FF9A55"),
            x=0.02
        ),
        margin=dict(l=15, r=15, t=55, b=15),
        xaxis_title="Predicted Confidence",
        yaxis_title="Actual NASA Confidence"
    )

    fig.update_traces(
        textfont=dict(
            color="#FFFFFF",
            size=13
        )
    )

    return fig
