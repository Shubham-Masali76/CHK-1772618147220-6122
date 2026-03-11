# AutoML Assistant

A Streamlit-based AutoML web application designed for beginners. The project was originally developed as part of a hackathon to provide an interactive, end-to-end machine learning workflow.

## Features

- **Dataset Upload**: Drag-and-drop CSV/Excel files with live preview and summary statistics.
- **Exploratory Data Analysis**: Plot distributions, correlation heatmaps, and evaluate dataset readiness.
- **Automated Preprocessing**: AI-driven suggestions for handling missing values, encoding categoricals, and scaling numeric features; allows manual override.
- **Model Training**: Trains multiple models (Logistic Regression, Random Forest, Decision Tree, and their regression variants) with leaderboard ranking and training time measurement.
- **Result Visualization**: Interactive charts comparing model performance and a clean display of scores.
- **Explainability**: Generates plain-English reasoning for the selected best model.
- **Theme Support**: Light and dark themes with consistent CSS styling.
- **Session Management**: User authentication with Firebase, session persistence, and export of configuration and reference data.

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd automl-assistant-hackathon
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the application:
   ```powershell
   python -m streamlit run appui.py
   ```
5. Open your browser at the URL shown in the terminal (usually `http://localhost:8501`).

## Project Structure

- `appui.py` – Main Streamlit application with UI and workflow logic.
- `auth/` – Firebase authentication helpers.
- `preprocessing/` – Data cleaning, encoding, scaling, and feature selection.
- `ml_engine/` – Model training, evaluation, and problem type detection.
- `explainability/` – Logic for generating model explanations and plots.
- `styles/` – CSS injection and theme tokens for light/dark modes.
- `export/` – Model export utilities.
- `utils/` – Miscellaneous helpers such as session visualization.

## Notes & Tips

- Categorical targets (e.g., `gender`) are supported and preserved during preprocessing.
- The target column is excluded from encoding/scaling and cannot be dropped.
- Use the "Toggle Theme" button to switch between light and dark modes; the title and UI elements adapt automatically.
- The app is intended for educational purposes and may need adjustments for production use.

Feel free to explore, modify, and extend the application!

## Maintenance

To keep the workspace lean and fast, run the cleanup utility before committing or sharing:

```bash
git pull
python clean.py  # deletes __pycache__ and export artifacts
```
