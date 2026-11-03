
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


# DBSCAN settings: 5 km neighbourhood and minimum 5 observations
EPS_KM = 5
MIN_SAMPLES = 5
EARTH_RADIUS_KM = 6371
EPS_RAD = EPS_KM / EARTH_RADIUS_KM  # Haversine requires distance in radians

CLUSTER_COLUMNS = [
    "cluster",
    "detection_count",
    "centroid_latitude",
    "centroid_longitude",
    "average_frp",
    "maximum_frp",
    "dominant_confidence"
]


def perform_clustering(data):
    # Handle empty input
    if data.empty:
        result = data.copy()
        result["cluster"] = pd.Series(dtype=int)
        return result

    # Check required geographical columns
    required = ["latitude", "longitude"]

    for column in required:
        if column not in data.columns:
            raise ValueError("Missing clustering column: " + column)

    result = data.copy()

    # Convert coordinates to numeric values
    for column in required:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    # Keep only valid geographical coordinates
    valid = (result["latitude"].between(-90, 90) & result["longitude"].between(-180, 180))

    result = result.loc[valid].reset_index(drop=True)

    if result.empty:
        result["cluster"] = pd.Series(dtype=int)
        return result

    # Convert latitude and longitude from degrees to radians
    coordinates = np.radians(result[required].to_numpy())

    # Apply DBSCAN using geographical distance
    model = DBSCAN(
        eps=EPS_RAD,
        min_samples=MIN_SAMPLES,
        metric="haversine",
        algorithm="ball_tree"
    )

    # Assign cluster IDs; -1 represents noise
    result["cluster"] = model.fit_predict(coordinates)

    return result


def calculate_cluster_statistics(data):
    if data.empty:
        return pd.DataFrame(columns=CLUSTER_COLUMNS)

    if "cluster" not in data.columns:
        raise ValueError("Cluster column not found. Perform DBSCAN clustering first.")

    # Exclude noise observations from cluster statistics
    clustered = data[data["cluster"] != -1].copy()

    if clustered.empty:
        return pd.DataFrame(columns=CLUSTER_COLUMNS)

    # Group observations by cluster
    grouped = clustered.groupby("cluster")

    # Calculate detection count and geographical centroid
    statistics = grouped.agg(
        detection_count=("cluster", "size"),
        centroid_latitude=("latitude", "mean"),
        centroid_longitude=("longitude", "mean")
    )

    # Calculate average and maximum Fire Radiative Power
    if "frp" in clustered.columns:
        frp_stats = grouped["frp"].agg(
            average_frp="mean",
            maximum_frp="max"
        )
        statistics = statistics.join(frp_stats)
    else:
        statistics["average_frp"] = np.nan
        statistics["maximum_frp"] = np.nan

    # Select the available confidence column
    confidence_column = next(
        (
            column for column in [
                "predicted_confidence_label",
                "predicted_confidence"
            ]
            if column in clustered.columns
        ),
        None
    )

    # Find the most frequently occurring confidence class
    if confidence_column:
        statistics["dominant_confidence"] = (
            grouped[confidence_column]
            .agg(
                lambda values: (
                    values.mode().iloc[0]
                    if not values.mode().empty
                    else "Unknown"
                )
            )
        )
    else:
        statistics["dominant_confidence"] = "Unknown"

    # Sort clusters by detection count
    return (
        statistics
        .sort_values("detection_count", ascending=False)
        .reset_index()
        [CLUSTER_COLUMNS]
    )


def calculate_clustering_summary(data):
    # Return zero values when no observations are available
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
            "Cluster column not found. Perform DBSCAN clustering first."
        )

    total = len(data)

    # Count clustered and noise observations
    noise = int(data["cluster"].eq(-1).sum())
    clustered = total - noise

    # Return overall clustering statistics
    return {
        "total_detections": total,
        "number_of_clusters": int(
            data.loc[data["cluster"] != -1, "cluster"].nunique()
        ),
        "clustered_detections": clustered,
        "noise_detections": noise,
        "clustered_percentage": round(clustered / total * 100, 2),
        "noise_percentage": round(noise / total * 100, 2)
    }
