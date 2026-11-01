
"""
File Name: preprocessing.py
Purpose: Clean and prepare NASA fire hotspot data.
"""

import requests
import pandas as pd
import streamlit as st

from shapely.geometry import shape, Point


# Countries included in the project
COUNTRIES = [
    "India",
    "Bangladesh",
    "Nepal",
    "Thailand",
    "Myanmar"
]

# Features must follow the same order used during model training
MODEL_FEATURES = [
    "bright_ti4",
    "bright_ti5",
    "scan",
    "track",
    "frp",
    "daynight"
]

# Country boundary data
GEOJSON_URL = (
    "https://raw.githubusercontent.com/"
    "datasets/geo-countries/master/data/countries.geojson"
)


@st.cache_data
def load_country_boundaries():
    """
    Download and load country boundary geometries.
    """

    response = requests.get(GEOJSON_URL, timeout=60)
    response.raise_for_status()

    geojson_data = response.json()

    country_shapes = {}

    for feature in geojson_data["features"]:

        properties = feature["properties"]

        country_name = (
            properties.get("ADMIN")
            or properties.get("name")
            or properties.get("NAME")
        )

        # Some datasets use Burma instead of Myanmar
        if country_name == "Burma":
            country_name = "Myanmar"

        if country_name in COUNTRIES:
            country_shapes[country_name] = shape(
                feature["geometry"]
            )

    missing = [
        country for country in COUNTRIES
        if country not in country_shapes
    ]

    if missing:
        raise ValueError(
            "Country boundaries not found: "
            + ", ".join(missing)
        )

    return country_shapes


def filter_selected_countries(data):
    """
    Keep only observations inside the five selected countries.
    """

    if data.empty:
        return data.copy()

    country_shapes = load_country_boundaries()

    country_values = []

    for index, row in data.iterrows():

        point = Point(
            row["longitude"],
            row["latitude"]
        )

        matched_country = None

        for country, geometry in country_shapes.items():

            if geometry.covers(point):
                matched_country = country
                break

        country_values.append(matched_country)

    filtered_data = data.copy()
    filtered_data["country"] = country_values

    filtered_data = filtered_data.dropna(
        subset=["country"]
    )

    return filtered_data.reset_index(drop=True)


def prepare_live_data(data):
    """
    Clean filtered data and prepare model input features.

    Returns:
        prepared_data: Cleaned observations.
        X_live: Features used by the trained model.
    """

    if data.empty:
        return pd.DataFrame(), pd.DataFrame(
            columns=MODEL_FEATURES
        )

    prepared_data = data.copy()

    prepared_data["daynight"] = (
    prepared_data["daynight"]
    .astype(str)
    .str.upper()
    .str.strip()
    )

    prepared_data["daynight_label"] = (
        prepared_data["daynight"]
    )

    prepared_data["daynight"] = (
        prepared_data["daynight"].map({
            "D": 0,
            "N": 1
        })
    )

    # Convert model features into numerical values
    for column in MODEL_FEATURES:
        prepared_data[column] = pd.to_numeric(
            prepared_data[column],
            errors="coerce"
        )

    # Remove observations with missing model features
    prepared_data.dropna(
        subset=MODEL_FEATURES,
        inplace=True
    )

    # Remove invalid negative FRP values
    prepared_data = prepared_data[
        prepared_data["frp"] >= 0
    ]

    prepared_data.reset_index(drop=True, inplace=True)

    # Select features in the exact training order
    X_live = prepared_data[MODEL_FEATURES].copy()

    return prepared_data, X_live
