"""
File Name: preprocessing.py
Purpose: Clean and prepare NASA fire hotspot data.
"""

import requests
import pandas as pd
import streamlit as st

from shapely.geometry import shape, Point


COUNTRIES = ["India", "Bangladesh", "Nepal", "Thailand", "Myanmar"]

MODEL_FEATURES = ["bright_ti4", "bright_ti5", "scan", "track", "frp", "daynight"]

GEOJSON_URL = ("https://raw.githubusercontent.com/"
    "datasets/geo-countries/master/data/countries.geojson")


@st.cache_data
def load_country_boundaries():
    response = requests.get(GEOJSON_URL, timeout=60)
    response.raise_for_status()

    country_shapes = {}

    for feature in response.json()["features"]:
        properties = feature["properties"]
        name = (
            properties.get("ADMIN")
            or properties.get("name")
            or properties.get("NAME")
        )

        name = "Myanmar" if name == "Burma" else name

        if name in COUNTRIES:
            country_shapes[name] = shape(feature["geometry"])

    missing = [c for c in COUNTRIES if c not in country_shapes]
    if missing:
        raise ValueError("Country boundaries not found: " + ", ".join(missing))

    return country_shapes


def filter_selected_countries(data):
    if data.empty:
        return data.copy()

    boundaries = load_country_boundaries()

    data = data.copy()
    data["country"] = [
        next(
            (name for name, geometry in boundaries.items()
             if geometry.covers(Point(row.longitude, row.latitude))),
            None)
        for row in data.itertuples()
    ]

    return data.dropna(subset=["country"]).reset_index(drop=True)


def prepare_live_data(data):
    if data.empty:
        return pd.DataFrame(), pd.DataFrame(columns=MODEL_FEATURES)

    prepared_data = data.copy()
    prepared_data["daynight"] = (prepared_data["daynight"].astype(str).str.upper().str.strip())
    prepared_data["daynight_label"] = prepared_data["daynight"]
    prepared_data["daynight"] = prepared_data["daynight"].map({"D": 0, "N": 1})

    prepared_data[MODEL_FEATURES] = prepared_data[MODEL_FEATURES].apply(pd.to_numeric, errors="coerce")

    prepared_data.dropna(subset=MODEL_FEATURES, inplace=True)
    prepared_data = prepared_data[prepared_data["frp"] >= 0]
    prepared_data.reset_index(drop=True, inplace=True)

    return prepared_data, prepared_data[MODEL_FEATURES].copy()
