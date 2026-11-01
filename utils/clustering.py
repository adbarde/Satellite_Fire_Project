
"""
File Name: clustering.py
Purpose: Identify geographical fire hotspot clusters using DBSCAN.
"""

import numpy as np
import pandas as pd

from sklearn.cluster import DBSCAN


# --------------------------------------------------
# DBSCAN Parameters
# --------------------------------------------------

EPS_KM = 15
MIN_SAMPLES = 5
EARTH_RADIUS_KM = 6371

# Convert distance from kilometres to radians
EPS_RAD = EPS_KM / EARTH_RADIUS_KM


# --------------------------------------------------
# 1. Perform DBSCAN Clustering
# --------------------------------------------------

def perform_clustering(data):
    """
    Group geographically close fire hotspot observations
    using DBSCAN with the Haversine distance metric.

    EPS_KM = 15:
        Maximum neighbourhood distance is 15 km.

    MIN_SAMPLES = 5:
        At least 5 observations, including the point itself,
        must be within the neighbourhood for a core point.

    Cluster -1 represents noise.
    """

    if data.empty:

        result = data.copy()
        result["cluster"] = pd.Series(dtype=int)

        return result

    # Check required columns
    required_columns = [
        "latitude",
        "longitude"
    ]

    for column in required_columns:

        if column not in data.columns:

            raise ValueError(
                "Missing clustering column: " + column
            )

    result = data.copy()

    # Convert coordinates to numeric values
    result["latitude"] = pd.to_numeric(
        result["latitude"],
        errors="coerce"
    )

    result["longitude"] = pd.to_numeric(
        result["longitude"],
        errors="coerce"
    )

    # Remove invalid coordinates
    valid_coordinates = (
        result["latitude"].between(-90, 90)
        & result["longitude"].between(-180, 180)
    )

    result = result.loc[
        valid_coordinates
    ].copy()

    result = result.dropna(
        subset=["latitude", "longitude"]
    )

    result.reset_index(drop=True, inplace=True)

    if result.empty:

        result["cluster"] = pd.Series(dtype=int)

        return result

    # Convert latitude and longitude to radians
    coordinates = np.radians(
        result[["latitude", "longitude"]].to_numpy()
    )

    # Apply DBSCAN
    dbscan = DBSCAN(
        eps=EPS_RAD,
        min_samples=MIN_SAMPLES,
        metric="haversine",
        algorithm="ball_tree"
    )

    # Assign cluster labels
    result["cluster"] = dbscan.fit_predict(
        coordinates
    )

    return result


# --------------------------------------------------
# 2. Calculate Cluster Statistics
# --------------------------------------------------

def calculate_cluster_statistics(data):
    """
    Calculate statistics for each non-noise cluster.

    Noise observations are excluded.
    """

    columns = [
        "cluster",
        "detection_count",
        "centroid_latitude",
        "centroid_longitude",
        "average_frp",
        "maximum_frp",
        "dominant_confidence"
    ]

    if data.empty:

        return pd.DataFrame(columns=columns)

    if "cluster" not in data.columns:

        raise ValueError(
            "Cluster column not found. "
            "Perform DBSCAN clustering first."
        )

    # Exclude noise observations
    clustered_data = data[
        data["cluster"] != -1
    ].copy()

    if clustered_data.empty:

        return pd.DataFrame(columns=columns)

    # Calculate cluster statistics
    statistics = (
        clustered_data
        .groupby("cluster")
        .agg(
            detection_count=("cluster", "size"),
            centroid_latitude=("latitude", "mean"),
            centroid_longitude=("longitude", "mean")
        )
        .reset_index()
    )

    # Calculate FRP statistics when available
    if "frp" in clustered_data.columns:

        frp_statistics = (
            clustered_data
            .groupby("cluster")
            .agg(
                average_frp=("frp", "mean"),
                maximum_frp=("frp", "max")
            )
            .reset_index()
        )

        statistics = statistics.merge(
            frp_statistics,
            on="cluster",
            how="left"
        )

    else:

        statistics["average_frp"] = np.nan
        statistics["maximum_frp"] = np.nan

    # Determine dominant predicted confidence
    confidence_column = None

    if "predicted_confidence_label" in clustered_data.columns:

        confidence_column = "predicted_confidence_label"

    elif "predicted_confidence" in clustered_data.columns:

        confidence_column = "predicted_confidence"

    if confidence_column is not None:

        dominant_confidence = (
            clustered_data
            .groupby("cluster")[confidence_column]
            .agg(
                lambda values:
                values.mode().iloc[0]
                if not values.mode().empty
                else "Unknown"
            )
            .reset_index(name="dominant_confidence")
        )

        statistics = statistics.merge(
            dominant_confidence,
            on="cluster",
            how="left"
        )

    else:

        statistics["dominant_confidence"] = "Unknown"

    # Sort clusters by number of detections
    statistics = statistics.sort_values(
        "detection_count",
        ascending=False
    ).reset_index(drop=True)

    return statistics[columns]


# --------------------------------------------------
# 3. Calculate Overall Clustering Summary
# --------------------------------------------------

def calculate_clustering_summary(data):
    """
    Calculate overall DBSCAN clustering statistics.

    Noise is counted separately from actual clusters.
    """

    if data.empty:

        return {
            "total_detections": 0,
            "number_of_clusters": 0,
            "clustered_detections": 0,
            "noise_detections": 0,
            "clustered_percentage": 0,
            "noise_percentage": 0
        }

    if "cluster" not in data.columns:

        raise ValueError(
            "Cluster column not found. "
            "Perform DBSCAN clustering first."
        )

    total_detections = len(data)

    # Count non-noise clusters
    number_of_clusters = (
        data.loc[
            data["cluster"] != -1,
            "cluster"
        ].nunique()
    )

    # Count clustered observations
    clustered_detections = int(
        (data["cluster"] != -1).sum()
    )

    # Count noise observations
    noise_detections = int(
        (data["cluster"] == -1).sum()
    )

    # Calculate percentages
    clustered_percentage = (
        clustered_detections / total_detections
    ) * 100

    noise_percentage = (
        noise_detections / total_detections
    ) * 100

    return {
        "total_detections": total_detections,
        "number_of_clusters": int(number_of_clusters),
        "clustered_detections": clustered_detections,
        "noise_detections": noise_detections,
        "clustered_percentage": round(
            clustered_percentage, 2
        ),
        "noise_percentage": round(
            noise_percentage, 2
        )
    }
