import streamlit as st
import pandas as pd
import plotly.express as px  # Added for EDA visualizations
import os
import json
import pickle

from data_analysis.analyzer import analyze_dataset
from data_analysis.readiness import dataset_readiness

from preprocessing.preprocessing_engine import preprocess_data
from preprocessing.recommendations import recommend_preprocessing
from preprocessing.preprocessing_advisor import preprocessing_advisor
from preprocessing.feature_selection import remove_highly_correlated_features

from ml_engine.train_models import train_models, detect_problem_type

from explainability.model_explainer import explain_model_choice
from explainability.feature_importance_plot import plot_feature_importance

from export.export_model import export_model

from utils.pipeline_visualizer import show_pipeline

# Configure page layout
st.set_page_config(page_title="AutoML Assistant", layout="wide")

st.title("AutoML Assistant for Beginners")

st.info(
    "This assistant analyzes your dataset, suggests preprocessing steps, "
    "trains machine learning models, and explains the results."
)

# Initialize Session State Variables to prevent data loss across tabs
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "result" not in st.session_state:
    st.session_state.result = None
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None


# -----------------------------
# Upload Dataset
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Dataset (CSV or Excel)",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file:

    file_name = uploaded_file.name

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file format")
        st.stop()

    # --- UI Layout (Organizing into Tabs) ---
    tab1, tab2, tab3 = st.tabs(["📊 Data & EDA", "⚙️ Preprocessing", "🚀 Results & Testing"])

    # ==========================================
    # TAB 1: DATA & EXPLORATORY DATA ANALYSIS
    # ==========================================
    with tab1:
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        st.subheader("Dataset Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        # Remove useless columns for target selection
        valid_columns = []
        for col in df.columns:
            if df[col].nunique() <= 1:
                continue
            if "id" in col.lower():
                continue
            valid_columns.append(col)

        suggested_targets = []
        for col in valid_columns:
            unique_values = df[col].nunique()
            if unique_values <= 20 or df[col].dtype != "object":
                suggested_targets.append(col)

        st.subheader("Target Column Selection")
        st.info("Choose the column the model should predict.")
        
        # Save target selection to session state so it persists
        target = st.selectbox(
            "Select Target Column",
            suggested_targets,
            key="target_col"
        )

        # --- Exploratory Data Analysis (EDA) Visualizations ---
        st.divider()
        st.subheader("Exploratory Data Analysis (EDA)")
        
        if st.checkbox("Show Distribution of Target Variable"):
            fig_hist = px.histogram(
                df, x=target, 
                title=f"Distribution of {target}",
                color_discrete_sequence=['#4C78A8']
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        if st.checkbox("Show Correlation Heatmap (Numerical Features)"):
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                # Calculate correlation matrix
                corr_matrix = numeric_df.corr().round(2)
                fig_corr = px.imshow(
                    corr_matrix, 
                    text_auto=True, 
                    aspect="auto",
                    color_continuous_scale='RdBu_r',
                    title="Feature Correlation Heatmap"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("No numerical features available to calculate correlations.")


    # ==========================================
    # TAB 2: PREPROCESSING & TRAINING PIPELINE
    # ==========================================
    with tab2:
        if st.button("Analyze Dataset"):
            st.session_state.analysis = analyze_dataset(df)

        if st.session_state.analysis is not None:
            analysis = st.session_state.analysis

            st.subheader("Dataset Analysis")
            rows, cols = analysis["dataset_shape"]
            st.write(f"The dataset contains **{rows} rows** and **{cols} columns**.")

            missing = sum(analysis["missing_values"].values())
            if missing == 0:
                st.success("Great! No missing values were found.")
            else:
                st.warning(f"{missing} missing values detected.")

            col_cat, col_num = st.columns(2)
            with col_cat:
                st.write("**Categorical Data**")
                if analysis["categorical_columns"]:
                    for c in analysis["categorical_columns"]:
                        st.write("•", c)
                else:
                    st.success("No categorical columns detected.")

            with col_num:
                st.write("**Numerical Data**")
                for n in analysis["numerical_columns"]:
                    st.write("•", n)

            if analysis["duplicate_rows"] == 0:
                st.success("No duplicate rows detected.")
            else:
                st.warning(f"{analysis['duplicate_rows']} duplicate rows detected.")

            # ML Problem Detection
            problem_type = detect_problem_type(df[target])
            st.success(f"Detected Machine Learning Problem: **{problem_type.upper()}**")

            # Dataset Readiness
            readiness = dataset_readiness(analysis)
            st.subheader("Dataset Readiness")

            if readiness["status"] == "READY":
                st.success(f"Dataset ready for training ({readiness['score']}/100)")
            elif readiness["status"] == "WARNING":
                st.warning(f"Dataset has minor issues ({readiness['score']}/100)")
            else:
                st.error(f"Dataset not ready ({readiness['score']}/100)")

            if readiness["issues"]:
                st.write("Issues detected:")
                for issue in readiness["issues"]:
                    st.write("•", issue)

            show_pipeline()

            # Data Preparation Advice
            st.subheader("Data Preparation Advice")
            advice = preprocessing_advisor(df)
            for item in advice:
                st.markdown(f"**{item['title']}**")
                st.write(item["message"])
                st.info(item["recommendation"])

            # ---------------------------------------------------------
            # Preprocessing Options: Interactive AI Recommendations
            # ---------------------------------------------------------
            st.subheader("Preprocessing Recommendations")
            rec = recommend_preprocessing(df)
            
            # --- Missing Values ---
            mv_rec = rec["missing_values"]
            st.write("### Missing Values")
            
            if mv_rec["recommended"] is not None:
                rec_val = str(mv_rec["recommended"]).lower()
                valid_mv = ["mean", "median", "mode", "drop"]
                if rec_val not in valid_mv: rec_val = "mean" # fallback

                mv_explanations = {
                    "mean": "It replaces empty spots with the average value. This safely keeps your data rows intact without skewing the numbers too much.",
                    "median": "It replaces empty spots with the exact middle value. This is very safe if you have extreme 'outliers'.",
                    "mode": "It fills empty spots with the most frequent value. This is great for categories or common recurring items.",
                    "drop": "Guessing the missing values might confuse the model here, so it's safer to just remove those incomplete rows entirely."
                }
                explanation_mv = mv_explanations.get(rec_val, "It is a standard approach to clean up incomplete data.")

                st.info(f"💡 **AI Recommendation:** Use **{rec_val}** to handle missing values.\n\n**Why?** {explanation_mv}")
                
                mv_choice = st.radio("What would you like to do?", ["Accept Recommendation", "Modify"], key="mv_radio", horizontal=True)

                if mv_choice == "Accept Recommendation":
                    missing_option = rec_val
                    st.success(f"✅ Applied **{rec_val}** strategy.")
                else:
                    missing_option = st.selectbox(
                        "How should missing values be handled?",
                        valid_mv,
                        index=valid_mv.index(rec_val)
                    )
                    
                    if missing_option == rec_val:
                        st.success("✅ Good choice! Sticking with the AI's recommendation.")
                    elif missing_option == "drop":
                        st.warning("⚠️ **Weaker Choice:** Dropping rows reduces your dataset size. Imputation (like mean or median) is usually a better approach to preserve data.")
                    elif rec_val == "drop" and missing_option != "drop":
                        st.success(f"🌟 **Better Choice!** You chose **{missing_option}**. This is great because it preserves data rows compared to just dropping them!")
                    elif missing_option in ["mean", "median"] and rec_val == "mode":
                        st.success(f"🌟 **Smart Choice!** Using **{missing_option}** is statistically robust for numerical variables.")
                    else:
                        st.info(f"Applied **{missing_option}** strategy.")
            else:
                st.success("No missing values detected! No action needed.")
                missing_option = None

            # --- Categorical Encoding ---
            enc_rec = rec["encoding"]
            st.write("### Categorical Encoding (Text to Numbers)")
            
            rec_enc = str(enc_rec.get("recommended", "onehot")).lower()
            valid_enc = ["label", "onehot"]
            if rec_enc not in valid_enc: rec_enc = "onehot" # fallback

            enc_explanations = {
                "onehot": "It creates separate Yes/No columns for each category. This stops the model from mistakenly thinking one category is mathematically 'greater' than another.",
                "label": "It converts categories into simple numbers (1, 2, 3...). This is good when your categories have a natural order (like 'Low', 'Medium', 'High')."
            }
            explanation_enc = enc_explanations.get(rec_enc, "It safely converts text into numbers.")

            st.info(f"💡 **AI Recommendation:** Use **{rec_enc}** encoding.\n\n**Why?** {explanation_enc}")
            
            enc_choice = st.radio("What would you like to do?", ["Accept Recommendation", "Modify"], key="enc_radio", horizontal=True)

            if enc_choice == "Accept Recommendation":
                encoding_option = rec_enc
                st.success(f"✅ Applied **{rec_enc}** encoding.")
            else:
                encoding_option = st.selectbox(
                    "Choose encoding method",
                    valid_enc,
                    index=valid_enc.index(rec_enc)
                )

                if encoding_option == rec_enc:
                    st.success("✅ Good choice! Sticking with the AI's recommendation.")
                elif encoding_option == "label" and rec_enc == "onehot":
                    st.warning("⚠️ **Weaker Choice:** Label encoding might cause the model to incorrectly assume an artificial order among your categories.")
                elif encoding_option == "onehot" and rec_enc == "label":
                    st.success("🌟 **Better Choice!** One-hot encoding is more robust and prevents the model from assuming false ordering!")

            # --- Feature Scaling ---
            st.write("### Feature Scaling")
            st.write("Scaling helps the model handle numbers of different ranges.")
            
            rec_scale = "standard" 
            valid_scale = ["standard", "minmax"]
            
            scale_explanations = {
                "standard": "It balances all your numbers so they center around zero like a bell curve. This stops the model from getting distracted by huge numbers.",
                "minmax": "It strictly squishes all your numbers to be between 0 and 1. This is useful when you want to keep the exact original shape of your data."
            }
            explanation_scale = scale_explanations.get(rec_scale, "It ensures the model treats all your columns fairly.")

            st.info(f"💡 **AI Recommendation:** Use **{rec_scale}** scaling.\n\n**Why?** {explanation_scale}")
            
            scale_choice = st.radio("What would you like to do?", ["Accept Recommendation", "Modify"], key="scale_radio", horizontal=True)

            if scale_choice == "Accept Recommendation":
                scaling_option = rec_scale
                st.success(f"✅ Applied **{rec_scale}** scaling.")
            else:
                scaling_option = st.selectbox(
                    "Choose scaling method",
                    valid_scale,
                    index=valid_scale.index(rec_scale)
                )

                if scaling_option == rec_scale:
                    st.success("✅ Good choice! Sticking with the AI's recommendation.")
                elif scaling_option == "minmax":
                    st.warning("⚠️ **Weaker Choice:** MinMax scaling is bounded between 0 and 1, making it highly sensitive to extreme outliers.")
                else:
                    st.info(f"Applied **{scaling_option}** scaling.")

            # Run AutoML
            if st.button("🚀 Run AutoML", type="primary"):
                with st.spinner("Preparing data and training models..."):
                    
                    processed_df = preprocess_data(
                        df,
                        missing_strategy=missing_option,
                        encoding=encoding_option,
                        scaling=scaling_option
                    )

                    processed_df, removed_features = remove_highly_correlated_features(processed_df)

                    if removed_features:
                        st.write("Removed highly correlated features:")
                        for r in removed_features:
                            st.write("•", r)

                    # Save to session state for the UI
                    st.session_state.processed_df = processed_df
                    st.session_state.result = train_models(processed_df, target)
                    
                    # ---------------------------------------------------------
                    # PHYSICAL EXPORTS: Save preprocessing context to files
                    # ---------------------------------------------------------
                    os.makedirs("export", exist_ok=True)
                    
                    # 1. Save reference dataset for transformations
                    df.to_csv("export/reference_data.csv", index=False)
                    
                    # 2. Save configuration parameters
                    config = {
                        "missing_strategy": missing_option,
                        "encoding": encoding_option,
                        "scaling": scaling_option,
                        "target": target
                    }
                    with open("export/preprocessing_config.json", "w") as f:
                        json.dump(config, f)

                st.success("Model training completed! Go to the **🚀 Results & Testing** tab to view the output.")


    # ==========================================
    # TAB 3: RESULTS, TESTING & EXPORTS
    # ==========================================
    with tab3:
        if st.session_state.result is None:
            st.info("👈 Please complete the Preprocessing step and click 'Run AutoML' to see results here.")
        else:
            result = st.session_state.result

            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Model Leaderboard")
                leaderboard = pd.DataFrame(
                    result["leaderboard"],
                    columns=["Model", "Score"]
                )
                st.dataframe(leaderboard, use_container_width=True)
                st.bar_chart(leaderboard.set_index("Model"))
                
                st.success(f"🏆 Best Model: **{result['best_model_name']}**")

            with col2:
                st.subheader("Model Scores")
                st.json(result["model_scores"])
                
                st.subheader("Training Time")
                time_df = pd.DataFrame(
                    list(result["training_time"].items()),
                    columns=["Model", "Time (seconds)"]
                )
                st.dataframe(time_df, hide_index=True)

            # Model Explanation
            st.divider()
            st.subheader("Model Explanation")
            explanation = explain_model_choice(
                result["best_model_name"],
                result["model_scores"]
            )
            st.markdown(f"### {explanation['title']}")
            st.write(explanation["message"])
            st.info(explanation["reason"])

            # Feature Importance
            if result["feature_importance"] is not None:
                st.divider()
                st.subheader("Feature Importance")
                st.write("These features had the strongest influence on the model's predictions.")
                fig_imp = plot_feature_importance(result["feature_importance"])
                st.plotly_chart(fig_imp, use_container_width=True)

            st.divider()
            
            # --- FEATURE 1: Interactive "Test the Model" Form ---
            st.subheader("🧪 Test the Model")
            st.write("Enter normal, everyday values below to see what the best model predicts in real-time.")
            
            # Read state directly from the exported folders instead of hidden memory
            if os.path.exists("export/reference_data.csv") and os.path.exists("export/preprocessing_config.json"):
                ref_df = pd.read_csv("export/reference_data.csv")
                
                with open("export/preprocessing_config.json", "r") as f:
                    saved_config = json.load(f)
                
                with st.form("interactive_prediction_form"):
                    user_input = {}
                    # Extract original features (before preprocessing) excluding the target
                    original_features = [col for col in ref_df.columns if col != saved_config["target"]]
                    
                    # Create input fields dynamically based on ORIGINAL data ranges from the exported file
                    form_cols = st.columns(3)
                    for i, col in enumerate(original_features):
                        with form_cols[i % 3]:
                            if pd.api.types.is_numeric_dtype(ref_df[col]):
                                col_min = float(ref_df[col].min())
                                col_max = float(ref_df[col].max())
                                col_mean = float(ref_df[col].mean())
                                
                                step = 1.0 if pd.api.types.is_integer_dtype(ref_df[col]) else (col_max - col_min) / 100.0
                                
                                if col_min == col_max:
                                    user_input[col] = st.number_input(f"{col}", value=col_min)
                                else:
                                    user_input[col] = st.slider(
                                        f"{col}", 
                                        min_value=col_min, 
                                        max_value=col_max, 
                                        value=col_mean,
                                        step=step
                                    )
                            else:
                                unique_categories = ref_df[col].dropna().unique().tolist()
                                user_input[col] = st.selectbox(f"{col}", options=unique_categories)
                    
                    submit_prediction = st.form_submit_button("Predict", type="primary")
                    
                    if submit_prediction:
                        # 1. Take the user's normal input and make a 1-row DataFrame
                        input_df = pd.DataFrame([user_input])
                        
                        # 2. Add a dummy target value
                        input_df[saved_config["target"]] = ref_df[saved_config["target"]].iloc[0]
                        
                        # 3. Combine original data (from export file) with the 1 new row. 
                        combined_df = pd.concat([ref_df, input_df], ignore_index=True)
                        
                        # 4. Run preprocessing using the exact parameters saved in our export config
                        processed_combined = preprocess_data(
                            combined_df,
                            missing_strategy=saved_config["missing_strategy"],
                            encoding=saved_config["encoding"],
                            scaling=saved_config["scaling"]
                        )
                        
                        # 5. Extract our newly preprocessed 1-row from the bottom
                        final_processed_row = processed_combined.tail(1)
                        
                        # 6. Ensure the columns perfectly match what the model expects
                        expected_model_columns = [c for c in st.session_state.processed_df.columns if c != saved_config["target"]]
                        
                        for c in expected_model_columns:
                            if c not in final_processed_row.columns:
                                final_processed_row[c] = 0
                                
                        final_processed_row = final_processed_row[expected_model_columns]

                        # 7. Predict!
                        best_model = result["best_model"]
                        prediction = best_model.predict(final_processed_row)[0]
                        st.success(f"### Predicted {saved_config['target']}: **{prediction}**")
            else:
                st.warning("⚠️ Reference files not found in the export folder. Please click 'Run AutoML' again to generate them.")

            st.divider()

            # --- FEATURE 2 & EXPORTS: Downloads ---
            st.subheader("📥 Downloads")
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.write("**Download Cleaned Dataset**")
                st.write("Download the dataset after missing values, encoding, and scaling were applied.")
                csv_data = st.session_state.processed_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Cleaned Data (CSV)",
                    data=csv_data,
                    file_name='cleaned_dataset.csv',
                    mime='text/csv',
                )

            with col_d2:
                st.write("**Download Trained Model**")
                st.write("Download the winning model to use in your own applications.")
                
                # Serialize the model into bytes for downloading
                model_bytes = pickle.dumps(result["best_model"])
                
                # Format model name safely for a file
                safe_model_name = result["best_model_name"].replace(" ", "_").lower()
                
                st.download_button(
                    label="Download Best Model (.pkl)",
                    data=model_bytes,
                    file_name=f"{safe_model_name}.pkl",
                    mime="application/octet-stream"
                )