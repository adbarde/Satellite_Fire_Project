
"""
File Name: priority.py
Purpose: Calculate and rank fire hotspot investigation priority.
"""

import numpy as np
import pandas as pd

from sklearn.neighbors import BallTree


# Priority calculation settings
EARTH_RADIUS_KM = 6371
NEIGHBOURHOOD_KM = 5

FRP_WEIGHT = 0.50
DENSITY_WEIGHT = 0.30
CONFIDENCE_WEIGHT = 0.20

CONFIDENCE_SCORES = {
    "h": 1.0,
    "n": 0.7,
    "l": 0.4
}


def calculate_frp_score(data):
    """
    Calculate FRP percentile scores between 0 and 1.
    """

    return data["frp"].rank(pct=True)


def calculate_density_score(data):
    """
    Calculate local detection density within 5 km.
    """

    coordinates = np.radians(
        data[["latitude", "longitude"]].to_numpy()
    )

    tree = BallTree(
        coordinates,
        metric="haversine"
    )

    radius = NEIGHBOURHOOD_KM / EARTH_RADIUS_KM

    # Count nearby observations, including the point itself
    neighbour_counts = tree.query_radius(
        coordinates,
        r=radius,
        count_only=True
    )

    # Log normalisation reduces the effect of very dense areas
    density = np.log1p(neighbour_counts)

    maximum = density.max()

    if maximum == 0:
        return pd.Series(0, index=data.index)

    return pd.Series(
        density / maximum,
        index=data.index
    )


def calculate_confidence_score(data):
    """
    Convert model-predicted confidence into numerical scores.
    """

    return data["predicted_confidence"].map(
        CONFIDENCE_SCORES
    )


def calculate_priority_scores(data):
    """
    Calculate the final priority score for every detection.

    Priority categories:
    High:   70 and above
    Medium: 40 to below 70
    Low:    below 40
    """

    if data.empty:
        return data.copy()

    required_columns = [
        "latitude",
        "longitude",
        "frp",
        "predicted_confidence"
    ]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                "Missing priority input column: " + column
            )

    result = data.copy()

    # Calculate individual components
    result["frp_score"] = calculate_frp_score(result)

    result["density_score"] = calculate_density_score(result)

    result["confidence_score"] = calculate_confidence_score(
        result
    )

    if result["confidence_score"].isna().any():
        raise ValueError(
            "Invalid predicted confidence values found."
        )

    # Calculate weighted priority score
    result["priority_score"] = 100 * (
        FRP_WEIGHT * result["frp_score"]
        + DENSITY_WEIGHT * result["density_score"]
        + CONFIDENCE_WEIGHT * result["confidence_score"]
    )

    # Assign priority categories
    result["priority_category"] = pd.cut(
        result["priority_score"],
        bins=[-0.01, 40, 70, 100],
        labels=["Low", "Medium", "High"],
        include_lowest=True
    )

    return result


def calculate_priority_cluster_summary(data):
    """
    Calculate priority statistics for each DBSCAN cluster.
    Includes noise as cluster -1.
    """

    if data.empty or "cluster" not in data.columns:
        return pd.DataFrame()

    summary = data.groupby("cluster").agg(
        detection_count=("cluster", "size"),
        average_frp=("frp", "mean"),
        maximum_frp=("frp", "max"),
        average_priority=("priority_score", "mean"),
        maximum_priority=("priority_score", "max"),
        centroid_latitude=("latitude", "mean"),
        centroid_longitude=("longitude", "mean")
    ).reset_index()

    # Find the most common predicted confidence
    confidence = (
        data.groupby("cluster")["predicted_confidence_label"]
        .agg(lambda values: values.mode().iloc[0])
        .reset_index(name="dominant_confidence")
    )

    summary = summary.merge(
        confidence,
        on="cluster",
        how="left"
    )

    # Identify noise separately
    summary["cluster_type"] = np.where(
        summary["cluster"] == -1,
        "Noise",
        "Spatial Cluster"
    )

    return summary


def get_top_priority_observations(data, number=10):
    """
    Return the highest-priority individual detections.
    Includes noise points.
    """

    if data.empty:
        return data.copy()

    return data.sort_values(
        by="priority_score",
        ascending=False
    ).head(number).reset_index(drop=True)


def get_top_priority_clusters(data, number=10):
    """
    Return the highest-priority DBSCAN clusters.
    Noise is excluded from this ranking.
    """

    if data.empty:
        return data.copy()

    clusters = data[
        data["cluster"] != -1
    ].copy()

    if clusters.empty:
        return clusters

    summary = calculate_priority_cluster_summary(clusters)

    return summary.sort_values(
        by="average_priority",
        ascending=False
    ).head(number).reset_index(drop=True)
