import os
import joblib
import streamlit as st

MODEL_PATH = os.path.join("models", "decision_tree_tuned.pkl")


@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model file not found: " + MODEL_PATH)

    return joblib.load(MODEL_PATH)


def classify_live_data(data, X_live):
    if data.empty:
        return data.copy()

    result = data.copy()
    result["predicted_confidence"] = load_model().predict(X_live)

    labels = {"h": "High", "n": "Nominal", "l": "Low"}
    result["predicted_confidence_label"] = result["predicted_confidence"].map(labels)

    if result["predicted_confidence_label"].isna().any():
        raise ValueError("Model returned an unexpected confidence class.")

    return result