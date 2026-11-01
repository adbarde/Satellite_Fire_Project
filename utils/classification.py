
"""
File Name: classification.py
Purpose: Predict fire hotspot confidence using a trained Decision Tree.
"""

import os
import joblib
import streamlit as st


MODEL_PATH = os.path.join(
    "models",
    "decision_tree_tuned.pkl"
)


@st.cache_resource
def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model file not found: " + MODEL_PATH
        )

    model = joblib.load(MODEL_PATH)

    return model



def classify_live_data(data, X_live):

    if data.empty:
        return data.copy()

    model = load_model()

    result = data.copy()

    predictions = model.predict(X_live)

    result["predicted_confidence"] = predictions

    confidence_labels = {
        "h": "High",
        "n": "Nominal",
        "l": "Low"
    }

    result["predicted_confidence_label"] = (
        result["predicted_confidence"].map(confidence_labels)
    )

    if result["predicted_confidence_label"].isna().any():
        raise ValueError(
            "Model returned an unexpected confidence class."
        )

    return result
