
"""
File Name: nasa_api.py
Purpose: Fetch recent fire hotspot data from NASA FIRMS.
"""

import requests
import pandas as pd
import streamlit as st
from io import StringIO


# NASA FIRMS settings
SOURCE = "VIIRS_SNPP_NRT"
AREA = "68,5,106,36"

API_URL = (
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
)


def fetch_nasa_data(day_range=5):
    """
    Fetch fire hotspot data for the selected number of days.
    The NASA Area API supports a maximum of 5 days per request.
    """

    # Check selected period
    if day_range not in [1, 2, 3, 4, 5]:
        raise ValueError("Select a period between 1 and 5 days.")

    # Read NASA API key from Streamlit secrets
    try:
        api_key = st.secrets["NASA_FIRMS_MAP_KEY"]
    except Exception:
        raise ValueError(
            "NASA API key not found. Check .streamlit/secrets.toml."
        )

    # Build API request URL
    url = (
        API_URL
        + str(api_key) + "/"
        + SOURCE + "/"
        + AREA + "/"
        + str(day_range)
    )

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        raise ConnectionError(
            "Unable to fetch data from NASA FIRMS: " + str(error)
        )

    # Convert CSV response into a DataFrame
    try:
        data = pd.read_csv(StringIO(response.text))
    except Exception:
        raise ValueError("NASA returned invalid CSV data.")

    # Check whether data is available
    if data.empty:
        return pd.DataFrame()

    # Standardise column names
    data.columns = data.columns.str.strip().str.lower()

    # Rename NASA confidence to avoid confusion with model predictions
    if "confidence" in data.columns:
        data.rename(
            columns={"confidence": "api_confidence"},
            inplace=True
        )
    # Check NASA confidence reference labels
    if "api_confidence" not in data.columns:
        raise ValueError(
            "NASA confidence column is missing. "
            "Live model evaluation cannot be performed."
        )

    # Standardise NASA confidence labels
    data["api_confidence"] = (
        data["api_confidence"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    # Required columns
    required_columns = [
        "latitude",
        "longitude",
        "bright_ti4",
        "bright_ti5",
        "scan",
        "track",
        "frp",
        "daynight",
        "acq_date",
        "acq_time"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing NASA data columns: "
            + ", ".join(missing_columns)
        )

    # Convert numerical columns
    numeric_columns = [
        "latitude",
        "longitude",
        "bright_ti4",
        "bright_ti5",
        "scan",
        "track",
        "frp"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Remove invalid observations
    data.dropna(
        subset=numeric_columns + ["daynight", "acq_date"],
        inplace=True
    )

    # Validate geographic coordinates
    data = data[
        (data["latitude"].between(-90, 90)) &
        (data["longitude"].between(-180, 180))
    ]

    # FRP cannot be negative
    data = data[data["frp"] >= 0]

    # Standardise day/night values
    data["daynight"] = (
        data["daynight"].astype(str).str.upper().str.strip()
    )

    data = data[data["daynight"].isin(["D", "N"])]

    # Convert acquisition date
    data["acq_date"] = pd.to_datetime(
        data["acq_date"],
        errors="coerce"
    )

    data.dropna(subset=["acq_date"], inplace=True)

    # Reset row numbers
    data.reset_index(drop=True, inplace=True)

    return data


def get_api_information():
    """
    Return information about the NASA data source.
    """

    return {
        "source": SOURCE,
        "area": AREA,
        "description": "NASA VIIRS-SNPP Near Real-Time Fire Data",
        "period_limit": "1 to 5 days per request",
        "countries": [
            "India",
            "Bangladesh",
            "Nepal",
            "Thailand",
            "Myanmar"
        ]
    }
