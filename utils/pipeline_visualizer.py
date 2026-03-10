import streamlit as st


def show_pipeline():

    st.subheader("AutoML Pipeline")

    st.markdown("""
    **Your data will go through the following steps:**

    **Dataset Analysis**  
    The system inspects the dataset structure.

    **Dataset Readiness Check**  
    The system evaluates if the data is ready for training.

    **Data Preparation Advice**  
    Recommendations are provided for cleaning and preparing the data.

    **Preprocessing**  
    Missing values, encoding, and scaling are applied.

    **Feature Selection**  
    Highly similar features are removed.

    **Model Training**  
    Multiple machine learning models are trained.

    **Evaluation**  
    Models are compared and the best one is selected.

    **Export Model**  
    The trained model can be downloaded.
    """)