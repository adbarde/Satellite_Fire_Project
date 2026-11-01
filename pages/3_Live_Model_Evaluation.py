
import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Model Evaluation",
    page_icon="📈",
    layout="wide"
)


# ------------------------------------------------------------
# UI Styling
# ------------------------------------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #101827;
    color: #F1F5F9;
}

/* Content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Headings */
h1, h2, h3 {
    color: #F1F5F9 !important;
}

/* Paragraphs */
p {
    color: #CBD5E1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #182538;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #182538;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 12px;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #94A3B8;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #F1F5F9;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #182538;
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #94A3B8;
    font-size: 13px;
    padding-top: 22px;
    padding-bottom: 10px;
    border-top: 1px solid #334155;
    margin-top: 40px;
}

.footer-subtitle {
    color: #64748B;
    font-size: 12px;
}

hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Page Header
# ------------------------------------------------------------

st.title("Model Evaluation")

st.caption(
    "Examine Decision Tree predictions and their agreement "
    "with NASA-provided confidence labels."
)


# ------------------------------------------------------------
# Retrieve Data from Page 1
# ------------------------------------------------------------

if "live_fire_data" not in st.session_state:

    st.warning(
        "Fire data is not available. Open Live Fire Monitoring "
        "first to fetch and process the latest observations."
    )

    st.stop()


data = st.session_state["live_fire_data"].copy()

if data.empty:

    st.warning("The live dataset is empty.")
    st.stop()


# ------------------------------------------------------------
# Check Required Prediction Column
# ------------------------------------------------------------

if "predicted_confidence" not in data.columns:

    st.error("Decision Tree predictions are missing.")
    st.stop()


# ------------------------------------------------------------
# Prediction Summary
# ------------------------------------------------------------

st.subheader("Prediction Summary")

prediction_labels = {
    "h": "High",
    "n": "Nominal",
    "l": "Low"
}

prediction_counts = (
    data["predicted_confidence"]
    .value_counts()
)

high_count = int(prediction_counts.get("h", 0))
nominal_count = int(prediction_counts.get("n", 0))
low_count = int(prediction_counts.get("l", 0))

total_predictions = len(data)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Predictions",
        f"{total_predictions:,}"
    )

with col2:
    st.metric(
        "High Confidence",
        f"{high_count:,}"
    )

with col3:
    st.metric(
        "Nominal Confidence",
        f"{nominal_count:,}"
    )

with col4:
    st.metric(
        "Low Confidence",
        f"{low_count:,}"
    )


st.divider()


# ------------------------------------------------------------
# Prediction Distribution
# ------------------------------------------------------------

st.subheader("Prediction Distribution")

prediction_data = (
    data["predicted_confidence"]
    .map(prediction_labels)
    .value_counts()
    .rename_axis("Confidence Class")
    .reset_index(name="Count")
)

fig = px.pie(
    prediction_data,
    names="Confidence Class",
    values="Count",
    hole=0.45,
    color="Confidence Class",
    color_discrete_map={
        "High": "#EF4444",
        "Nominal": "#F59E0B",
        "Low": "#22C55E"
    }
)

fig.update_layout(
    margin={"r": 20, "t": 30, "l": 20, "b": 20},
    legend_title_text="Confidence Class"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    "This distribution describes the model's live predictions. "
    "It is not an evaluation accuracy score."
)


st.divider()


# ------------------------------------------------------------
# NASA Label Agreement
# ------------------------------------------------------------

st.subheader("NASA Label Agreement")

st.caption(
    "Agreement is measured against NASA-provided confidence labels."
)


if "api_confidence" not in data.columns:

    st.warning(
        "NASA reference confidence labels are unavailable. "
        "Only the live prediction distribution can be analysed. "
        "Accuracy, precision, recall, F1-score and confusion "
        "matrix cannot be calculated."
    )

else:

    evaluation_data = data[
        ["api_confidence", "predicted_confidence"]
    ].copy()

    # Standardise class labels
    evaluation_data["api_confidence"] = (
        evaluation_data["api_confidence"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    evaluation_data["predicted_confidence"] = (
        evaluation_data["predicted_confidence"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    valid_classes = ["h", "l", "n"]

    # Keep only valid reference and predicted labels
    evaluation_data = evaluation_data[
        evaluation_data["api_confidence"].isin(valid_classes)
        &
        evaluation_data["predicted_confidence"].isin(valid_classes)
    ]

    if evaluation_data.empty:

        st.warning(
            "No valid matching NASA and Decision Tree confidence "
            "labels were found."
        )

    else:

        y_true = evaluation_data["api_confidence"]
        y_pred = evaluation_data["predicted_confidence"]

        labels = ["h", "l", "n"]
        class_names = ["High", "Low", "Nominal"]

        # Calculate evaluation metrics
        accuracy = accuracy_score(y_true, y_pred)

        precision, recall, f1, support = (
            precision_recall_fscore_support(
                y_true,
                y_pred,
                labels=labels,
                zero_division=0
            )
        )

        macro_precision = precision.mean()
        macro_recall = recall.mean()
        macro_f1 = f1.mean()

        agreement_count = int((y_true == y_pred).sum())

        # ----------------------------------------------------
        # Overall Agreement Metrics
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Agreement Accuracy",
                f"{accuracy * 100:.2f}%"
            )

        with col2:
            st.metric(
                "Macro Precision",
                f"{macro_precision * 100:.2f}%"
            )

        with col3:
            st.metric(
                "Macro Recall",
                f"{macro_recall * 100:.2f}%"
            )

        with col4:
            st.metric(
                "Macro F1-Score",
                f"{macro_f1 * 100:.2f}%"
            )


        # ----------------------------------------------------
        # Agreement Counts
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Compared Observations",
                f"{len(evaluation_data):,}"
            )

        with col2:
            st.metric(
                "Matching Predictions",
                f"{agreement_count:,}"
            )

        with col3:
            st.metric(
                "Non-matching Predictions",
                f"{len(evaluation_data) - agreement_count:,}"
            )


        st.divider()


        # ----------------------------------------------------
        # Class-wise Evaluation
        # ----------------------------------------------------

        st.subheader("Class Performance")

        class_metrics = pd.DataFrame({
            "Confidence Class": class_names,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Support": support
        })

        st.dataframe(
            class_metrics.style.format({
                "Precision": "{:.3f}",
                "Recall": "{:.3f}",
                "F1-Score": "{:.3f}"
            }),
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # Class Performance and Confusion Matrix
        # ----------------------------------------------------

        chart_data = class_metrics.melt(
            id_vars="Confidence Class",
            value_vars=[
                "Precision",
                "Recall",
                "F1-Score"
            ],
            var_name="Metric",
            value_name="Score"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Class Performance")

            performance_chart = px.bar(
                chart_data,
                x="Confidence Class",
                y="Score",
                color="Metric",
                barmode="group",
                range_y=[0, 1],
                color_discrete_sequence=[
                    "#60A5FA",
                    "#F59E0B",
                    "#22C55E"
                ]
            )

            performance_chart.update_layout(
                margin={"r": 10, "t": 30, "l": 10, "b": 10},
                legend_title_text="Metric"
            )

            st.plotly_chart(
                performance_chart,
                use_container_width=True
            )


        with col2:

            st.subheader("Confusion Matrix")

            matrix = confusion_matrix(
                y_true,
                y_pred,
                labels=labels
            )

            matrix_data = pd.DataFrame(
                matrix,
                index=class_names,
                columns=class_names
            )

            matrix_data.index.name = "Actual NASA Confidence"
            matrix_data.columns.name = "Predicted Confidence"

            confusion_chart = px.imshow(
                matrix_data,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                labels={
                    "x": "Predicted Confidence",
                    "y": "Actual NASA Confidence",
                    "color": "Observations"
                }
            )

            confusion_chart.update_layout(
                margin={"r": 10, "t": 30, "l": 10, "b": 10}
            )

            st.plotly_chart(
                confusion_chart,
                use_container_width=True
            )


        # ----------------------------------------------------
        # Download Evaluation Results
        # ----------------------------------------------------

        st.divider()

        st.subheader("Download Evaluation Data")

        download_options = {
            "Class-wise Metrics": (
                class_metrics.to_csv(index=False),
                "live_model_evaluation.csv"
            ),

            "Compared Observations": (
                evaluation_data.to_csv(index=False),
                "live_prediction_comparison.csv"
            )
        }

        selected_download = st.selectbox(
            "Select report",
            list(download_options.keys())
        )

        download_data, download_filename = download_options[
            selected_download
        ]

        st.download_button(
            label="Download CSV",
            data=download_data,
            file_name=download_filename,
            mime="text/csv",
            use_container_width=True
        )


# ------------------------------------------------------------
# Evaluation Notes
# ------------------------------------------------------------

with st.expander("Evaluation Notes"):

    st.markdown("#### Evaluation Method")

    st.markdown(
        """
        - **Reference labels:** NASA-provided confidence (`api_confidence`).
        - **Predictions:** Decision Tree output (`predicted_confidence`).
        - **Agreement accuracy:** Percentage of predictions matching
          NASA labels.
        - **Precision:** Proportion of predicted class observations
          that match the reference class.
        - **Recall:** Proportion of reference class observations
          correctly identified by the model.
        - **F1-score:** Harmonic mean of precision and recall.
        - **Macro average:** Average metric across the three classes,
          giving each class equal weight.
        """
    )

    st.markdown("#### Limitations")

    st.warning(
        "NASA confidence labels are used as reference labels in this "
        "comparison. The results measure agreement between the "
        "Decision Tree and NASA's confidence classification. They "
        "do not independently establish actual fire severity or fire risk."
    )

    st.write(
        "These live agreement metrics should not be confused with "
        "the model's historical test-set evaluation."
    )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        <div>AI Mini Project | Anshika (2601) · Kiran (2605)</div>
        <div class="footer-subtitle">
            Satellite Fire Hotspot Intelligence
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
