
"""
File Name: 3_Live_Model_Evaluation.py
Project: Satellite Fire Hotspot Intelligence
Purpose: Evaluate Decision Tree predictions against
         NASA-provided confidence labels.
"""

import streamlit as st
import pandas as pd

from utils.theme import apply_theme

from utils.visualisations import (
    plot_prediction_distribution,
    plot_class_performance,
    plot_confusion_matrix
)

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Model Evaluation",
    page_icon="📈",
    layout="wide"
)

apply_theme()


# ==================================================
# 2. PAGE HEADER
# ==================================================

st.title("Model Evaluation")

st.caption(
    "Examine Decision Tree predictions and their agreement "
    "with NASA-provided confidence labels."
)

st.divider()


# ==================================================
# 3. RETRIEVE LIVE DATA
# ==================================================

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


if "predicted_confidence" not in data.columns:

    st.error("Decision Tree predictions are missing.")

    st.stop()


# ==================================================
# 4. PREDICTION SUMMARY
# ==================================================

st.subheader("Prediction Summary")


prediction_labels = {
    "h": "High",
    "n": "Nominal",
    "l": "Low"
}


prediction_counts = data["predicted_confidence"].value_counts()

total_predictions = len(data)


summary_metrics = [
    ("Total Predictions", total_predictions),
    ("High Confidence", prediction_counts.get("h", 0)),
    ("Nominal Confidence", prediction_counts.get("n", 0)),
    ("Low Confidence", prediction_counts.get("l", 0))
]


columns = st.columns(4)


for column, (label, value) in zip(columns, summary_metrics):

    column.metric(
        label,
        f"{value:,}"
    )


st.divider()


# ==================================================
# 5. PREDICTION DISTRIBUTION
# ==================================================

st.subheader("Prediction Distribution")


prediction_data = (
    data["predicted_confidence"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map(prediction_labels)
    .value_counts()
    .rename_axis("Confidence Class")
    .reset_index(name="Count")
)


distribution_chart = plot_prediction_distribution(
    prediction_data
)


if distribution_chart is not None:

    st.plotly_chart(
        distribution_chart,
        use_container_width=True
    )

else:

    st.info("No valid prediction classes are available.")


st.caption(
    "This distribution describes the model's live predictions. "
    "It is not an evaluation accuracy score."
)


st.divider()


# ==================================================
# 6. NASA LABEL AGREEMENT
# ==================================================

st.subheader("NASA Label Agreement")

st.caption(
    "Agreement is measured against NASA-provided confidence labels."
)


if "api_confidence" not in data.columns:

    st.warning(
        "NASA reference confidence labels are unavailable. "
        "Only the live prediction distribution can be analysed. "
        "Evaluation metrics and confusion matrix cannot be calculated."
    )


else:

    evaluation_data = data[
        [
            "api_confidence",
            "predicted_confidence"
        ]
    ].copy()


    # ----------------------------------------------
    # Standardise labels
    # ----------------------------------------------

    for column in [
        "api_confidence",
        "predicted_confidence"
    ]:

        evaluation_data[column] = (
            evaluation_data[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )


    labels = ["h", "l", "n"]

    class_names = [
        "High",
        "Low",
        "Nominal"
    ]


    # ----------------------------------------------
    # Remove invalid labels
    # ----------------------------------------------

    evaluation_data = evaluation_data[
        evaluation_data["api_confidence"].isin(labels)
        & evaluation_data["predicted_confidence"].isin(labels)
    ]


    if evaluation_data.empty:

        st.warning(
            "No valid matching NASA and Decision Tree confidence "
            "labels were found."
        )


    else:

        y_true = evaluation_data["api_confidence"]

        y_pred = evaluation_data["predicted_confidence"]


        # ------------------------------------------
        # Calculate evaluation metrics
        # ------------------------------------------

        accuracy = accuracy_score(
            y_true,
            y_pred
        )


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


        agreement_count = int(
            (y_true == y_pred).sum()
        )


        # ------------------------------------------
        # Overall agreement metrics
        # ------------------------------------------

        st.subheader("Overall Evaluation Metrics")


        metrics = [
            ("Agreement Accuracy", accuracy * 100),
            ("Macro Precision", macro_precision * 100),
            ("Macro Recall", macro_recall * 100),
            ("Macro F1-Score", macro_f1 * 100)
        ]


        columns = st.columns(4)


        for column, (label, value) in zip(columns, metrics):

            column.metric(
                label,
                f"{value:.2f}%"
            )


        # ------------------------------------------
        # Agreement counts
        # ------------------------------------------

        st.subheader("Observation Comparison")


        counts = [
            ("Compared Observations", len(evaluation_data)),
            ("Matching Predictions", agreement_count),
            (
                "Non-matching Predictions",
                len(evaluation_data) - agreement_count
            )
        ]


        columns = st.columns(3)


        for column, (label, value) in zip(columns, counts):

            column.metric(
                label,
                f"{value:,}"
            )


        st.divider()


        # ==================================================
        # 7. CLASS-WISE EVALUATION
        # ==================================================

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


        # ----------------------------------------------
        # Prepare class performance chart data
        # ----------------------------------------------

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


        # ==================================================
        # 8. PERFORMANCE CHART AND CONFUSION MATRIX
        # ==================================================

        col1, col2 = st.columns(2)


        with col1:

            st.subheader("Class Performance")


            performance_chart = plot_class_performance(
                chart_data
            )


            if performance_chart is not None:

                st.plotly_chart(
                    performance_chart,
                    use_container_width=True
                )

            else:

                st.info(
                    "Class performance chart is unavailable."
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


            confusion_chart = plot_confusion_matrix(
                matrix_data
            )


            if confusion_chart is not None:

                st.plotly_chart(
                    confusion_chart,
                    use_container_width=True
                )

            else:

                st.info(
                    "Confusion matrix is unavailable."
                )


        # ==================================================
        # 9. DOWNLOAD EVALUATION RESULTS
        # ==================================================

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


        download_data, filename = download_options[
            selected_download
        ]


        st.download_button(
            "Download CSV",
            data=download_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )


# ==================================================
# 10. EVALUATION NOTES
# ==================================================

with st.expander("Evaluation Notes"):

    st.markdown("""
    #### Evaluation Method

    - **Reference labels:** NASA-provided confidence (`api_confidence`).
    - **Predictions:** Decision Tree output (`predicted_confidence`).
    - **Agreement accuracy:** Percentage of predictions matching NASA labels.
    - **Precision:** Proportion of predicted class observations matching the reference class.
    - **Recall:** Proportion of reference class observations correctly identified.
    - **F1-score:** Harmonic mean of precision and recall.
    - **Macro average:** Average metric across the three classes, giving each class equal weight.
    """)


    st.markdown("#### Limitations")


    st.warning(
        "NASA confidence labels are used as reference labels. "
        "These results measure agreement between the Decision Tree "
        "and NASA's confidence classification. They do not independently "
        "establish actual fire severity or fire risk."
    )


    st.write(
        "Live agreement metrics should not be confused with "
        "the model's historical test-set evaluation."
    )


# ==================================================
# 11. FOOTER
# ==================================================

# Footer
st.markdown("""
<div class="footer">
    <div>AI Mini Project | Anshika (2601) · Kiran (2605)</div>
    <div class="footer-subtitle">Satellite Fire Hotspot Intelligence</div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "NASA FIRMS VIIRS-SNPP NRT observations may be revised "
    "as NASA updates its data."
)
