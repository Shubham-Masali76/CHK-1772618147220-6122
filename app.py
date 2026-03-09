import streamlit as st
import pandas as pd

from data_analysis.analyzer import analyze_dataset
from preprocessing.preprocessing_engine import preprocess_data
from ml_engine.train_models import train_models, detect_problem_type
from export.export_model import export_model


st.title("AutoML Assistant for Beginners")

st.info(
"This AutoML assistant automatically analyzes datasets, "
"preprocesses data, trains multiple models, compares them, "
"and selects the best performing model."
)


uploaded_file = st.file_uploader("Upload CSV Dataset")


if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # Dataset Summary
    st.subheader("Dataset Summary")

    st.write("Rows:", df.shape[0])
    st.write("Columns:", df.shape[1])
    st.write("Total Missing Values:", df.isnull().sum().sum())

    # Target Selection
    target = st.selectbox("Select Target Column", df.columns)

    # Dataset Analysis
    if st.button("Analyze Dataset"):
        
        st.info("The system is analyzing the dataset to understand its structure before training models.")

        analysis = analyze_dataset(df)

        st.subheader("Dataset Analysis")

        rows, cols = analysis["dataset_shape"]

        st.write(f"The dataset contains **{rows} rows** and **{cols} columns**.")

        # Missing values explanation
        total_missing = sum(analysis["missing_values"].values())

        if total_missing == 0:
            st.success("Good news! No missing values were found in the dataset.")
        else:
            st.warning(f"The dataset contains {total_missing} missing values that will need handling.")

        # Categorical columns explanation
        cat_cols = analysis["categorical_columns"]

        st.subheader("Categorical Features")

        st.write(
        "These columns contain categories instead of numbers "
        "(for example: male/female or yes/no)."
        )

        for col in cat_cols:
            st.write(f"• {col}")

        # Numerical columns explanation
        num_cols = analysis["numerical_columns"]

        st.subheader("Numerical Features")

        st.write(
        "These columns contain numbers that machine learning models can directly analyze."
        )

        for col in num_cols:
            st.write(f"• {col}")

        # Duplicate rows explanation
        duplicates = analysis["duplicate_rows"]

        if duplicates == 0:
            st.success("No duplicate rows were found.")
        else:
            st.warning(f"The dataset contains {duplicates} duplicate rows.")


        # Detect problem type
        problem_type = detect_problem_type(df[target])

        st.success(f"Detected ML Problem Type: {problem_type}")


    # Run AutoML
    if st.button("Run AutoML"):

        with st.spinner("Training models..."):

            processed_df = preprocess_data(df)

            st.session_state.result = train_models(processed_df, target)

        result = st.session_state.result

        st.success("Model training completed!")

        # Model Scores
        st.subheader("Model Scores")

        st.write(result["model_scores"])

        # Best Model
        best_model = result["best_model_name"]

        st.success(f"Best Performing Model: {best_model}")


        # Leaderboard
        st.subheader("Model Leaderboard")

        leaderboard_df = pd.DataFrame(
            result["leaderboard"],
            columns=["Model", "Score"]
        )

        st.dataframe(leaderboard_df)


        # Performance Chart
        st.subheader("Model Performance Chart")

        st.bar_chart(leaderboard_df.set_index("Model"))


        # Training Time
        st.subheader("Training Time")

        training_time_df = pd.DataFrame(
            list(result["training_time"].items()),
            columns=["Model", "Time (seconds)"]
        )

        st.dataframe(training_time_df)


        # Model Comparison Table
        comparison_df = pd.DataFrame({
            "Model": list(result["model_scores"].keys()),
            "Score": list(result["model_scores"].values()),
            "Training Time": list(result["training_time"].values())
        })

        st.subheader("Model Comparison")

        st.dataframe(comparison_df)


        # Feature Importance
        if result["feature_importance"] is not None:

            st.subheader("Feature Importance")

            st.dataframe(result["feature_importance"])

            top_features = result["feature_importance"].head(3)["feature"].tolist()

            st.info(
                f"The model prediction is mostly influenced by: {', '.join(top_features)}"
            )

            st.info(
            "The AutoML assistant has trained multiple models and selected the best performing one."
            )


        # Download Clean Dataset
        csv = processed_df.to_csv(index=False)

        st.download_button(
            label="Download Clean Dataset",
            data=csv,
            file_name="clean_dataset.csv",
            mime="text/csv"
        )


        # Download Model
        if st.button("Download Trained Model"):

            export_model(result["best_model"])

            st.success("Model exported successfully")