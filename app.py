import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
import json
import pickle
# hashlib no longer needed — Firebase handles password hashing
import gzip
import base64

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

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoML Studio",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon=None
)

# ─── Design Tokens (Dark Theme) ───────────────────────────────────────────────
T = {
    "bg":         "#080d1a",
    "bg2":        "#0d1425",
    "surface":    "#111c30",
    "card":       "#152038",
    "border":     "#1e3050",
    "cyan":       "#00d4ff",
    "cyan_dim":   "#00d4ff22",
    "violet":     "#8b5cf6",
    "violet_dim": "#8b5cf620",
    "green":      "#10d494",
    "green_dim":  "#10d49420",
    "amber":      "#f59e0b",
    "red":        "#f43f5e",
    "text":       "#e2ecff",
    "muted":      "#6b82a8",
    "grid_line":  "rgba(0,212,255,0.03)",
    "plot_bg":    "#0d1425",
    "plot_paper": "#111c30",
    "plot_tmpl":  "plotly_dark",
    "hero_bg":    "linear-gradient(135deg,#0d1425 0%,#111c30 60%,#0a0f1e 100%)",
    "hero_border":"#1e3050",
}

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

:root {{
    --bg:          {T['bg']};
    --bg2:         {T['bg2']};
    --surface:     {T['surface']};
    --card:        {T['card']};
    --border:      {T['border']};
    --cyan:        {T['cyan']};
    --cyan-dim:    {T['cyan_dim']};
    --violet:      {T['violet']};
    --violet-dim:  {T['violet_dim']};
    --green:       {T['green']};
    --green-dim:   {T['green_dim']};
    --amber:       {T['amber']};
    --red:         {T['red']};
    --text:        {T['text']};
    --muted:       {T['muted']};
    --font-body:   'Outfit', sans-serif;
    --font-mono:   'DM Mono', monospace;
    --font-head:   'Syne', sans-serif;
    --glow-cyan:   0 0 24px {T['cyan']}44, 0 0 48px {T['cyan']}18;
    --glow-violet: 0 0 24px {T['violet']}44;
    --ease:        cubic-bezier(0.4,0,0.2,1);
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}}

[data-testid="stAppViewContainer"]::before {{
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image:
        linear-gradient({T['grid_line']} 1px, transparent 1px),
        linear-gradient(90deg, {T['grid_line']} 1px, transparent 1px);
    background-size: 48px 48px;
}}
[data-testid="stMain"] > div:first-child,
[data-testid="block-container"] {{
    position:relative; z-index:1;
    padding-top:2rem !important;
}}

#MainMenu, footer, header, [data-testid="stToolbar"] {{ display:none !important; }}

[data-testid="stTextInput"] input {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: .9rem !important;
    padding: .6rem 1rem !important;
    transition: border-color .2s, box-shadow .2s !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 2px var(--cyan-dim) !important;
    outline: none !important;
}}
[data-testid="stTextInput"] label {{
    color: var(--muted) !important;
    font-size: .8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .07em !important;
    font-family: var(--font-body) !important;
}}

[data-testid="stFileUploader"] {{
    background:var(--card) !important;
    border:2px dashed var(--border) !important;
    border-radius:16px !important;
    padding:1rem !important;
    transition:border-color .3s, box-shadow .3s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color:var(--cyan) !important;
    box-shadow:var(--glow-cyan) !important;
}}

[data-testid="stTabs"] > div:first-child {{
    background:var(--surface) !important; border-radius:12px !important;
    padding:4px !important; border:1px solid var(--border) !important;
}}
button[data-baseweb="tab"] {{
    background:transparent !important; color:var(--muted) !important;
    font-family:var(--font-body) !important; font-weight:500 !important;
    font-size:.88rem !important; border-radius:9px !important;
    border:none !important; padding:.55rem 1.4rem !important;
    transition:all .25s !important; letter-spacing:.02em !important;
}}
button[data-baseweb="tab"]:hover {{
    color:var(--cyan) !important; background:var(--cyan-dim) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background:linear-gradient(135deg,var(--cyan-dim),var(--violet-dim)) !important;
    color:var(--cyan) !important; font-weight:600 !important;
    box-shadow:inset 0 0 0 1px var(--cyan) !important;
}}
[data-testid="stTabPanel"] {{
    background:transparent !important; border:none !important;
    padding-top:1.5rem !important;
}}

.stButton > button {{
    background:var(--surface) !important; color:var(--cyan) !important;
    border:1px solid var(--cyan) !important; border-radius:10px !important;
    font-family:var(--font-body) !important; font-weight:600 !important;
    font-size:.875rem !important; padding:.6rem 1.6rem !important;
    transition:all .25s !important; letter-spacing:.03em !important;
}}
.stButton > button:hover {{
    background:var(--cyan) !important; color:var(--bg) !important;
    box-shadow:var(--glow-cyan) !important; transform:translateY(-1px) !important;
}}
.stButton > button[kind="primary"] {{
    background:linear-gradient(135deg,var(--cyan) 0%,var(--violet) 100%) !important;
    color:#fff !important; border:none !important;
    font-weight:700 !important; font-size:.925rem !important;
    padding:.7rem 2rem !important;
    box-shadow:0 4px 20px {T['cyan']}30, 0 4px 20px {T['violet']}30 !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform:translateY(-2px) !important;
    box-shadow:0 6px 30px {T['cyan']}50, 0 6px 30px {T['violet']}50 !important;
}}

[data-testid="stDataFrame"] {{
    background:var(--card) !important; border-radius:12px !important;
    border:1px solid var(--border) !important; overflow:hidden !important;
}}
[data-testid="stDataFrame"] table {{ font-family:var(--font-mono) !important; font-size:.82rem !important; }}
[data-testid="stDataFrame"] thead tr th {{
    background:var(--surface) !important; color:var(--cyan) !important;
    font-weight:500 !important; border-bottom:1px solid var(--border) !important;
    text-transform:uppercase !important; letter-spacing:.06em !important;
    font-size:.72rem !important;
}}
[data-testid="stDataFrame"] tbody tr:hover td {{ background:var(--cyan-dim) !important; }}

[data-testid="stMetric"] {{
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:14px !important; padding:1.2rem 1.4rem !important;
    transition:all .3s !important; position:relative !important; overflow:hidden !important;
}}
[data-testid="stMetric"]::before {{
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,var(--cyan),var(--violet));
}}
[data-testid="stMetric"]:hover {{
    border-color:var(--cyan) !important; transform:translateY(-2px) !important;
    box-shadow:var(--glow-cyan) !important;
}}
[data-testid="stMetricLabel"] {{
    color:var(--muted) !important; font-size:.78rem !important;
    text-transform:uppercase !important; letter-spacing:.08em !important; font-weight:500 !important;
}}
[data-testid="stMetricValue"] {{
    color:var(--text) !important; font-family:var(--font-mono) !important;
    font-size:1.8rem !important; font-weight:400 !important;
}}

[data-testid="stAlert"] {{
    border-radius:12px !important; border-left-width:3px !important;
    font-size:.875rem !important; font-family:var(--font-body) !important;
    background:var(--card) !important;
}}

[data-testid="stSelectbox"] > div > div {{
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:10px !important; color:var(--text) !important;
    font-family:var(--font-body) !important; transition:border-color .2s !important;
}}
[data-testid="stSelectbox"] > div > div:focus-within {{
    border-color:var(--cyan) !important; box-shadow:0 0 0 2px var(--cyan-dim) !important;
}}

[data-testid="stRadio"] label {{
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:9px !important; padding:.45rem 1.1rem !important;
    cursor:pointer !important; color:var(--muted) !important;
    font-size:.85rem !important; font-weight:500 !important; transition:all .2s !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background:var(--cyan-dim) !important; border-color:var(--cyan) !important;
    color:var(--cyan) !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color:var(--cyan) !important; color:var(--cyan) !important;
}}

[data-testid="stCheckbox"] label {{
    color:var(--muted) !important; font-size:.875rem !important; font-weight:500 !important;
}}
[data-testid="stCheckbox"] label:hover {{ color:var(--cyan) !important; }}
[data-testid="stCheckbox"] span[role="checkbox"] {{
    background:var(--card) !important; border:2px solid var(--border) !important;
    border-radius:5px !important;
}}
[data-testid="stCheckbox"] span[role="checkbox"][aria-checked="true"] {{
    background:var(--cyan) !important; border-color:var(--cyan) !important;
}}

[data-testid="stSlider"] > div > div > div > div {{
    background:linear-gradient(90deg,var(--cyan),var(--violet)) !important;
}}
[data-testid="stSlider"] [role="slider"] {{
    background:var(--cyan) !important; box-shadow:0 0 10px var(--cyan) !important;
    border:2px solid var(--surface) !important;
}}

[data-testid="stNumberInput"] input {{
    background:var(--card) !important; border:1px solid var(--border) !important;
    color:var(--text) !important; font-family:var(--font-mono) !important;
    border-radius:8px !important;
}}

[data-testid="stDownloadButton"] > button {{
    background:linear-gradient(135deg,var(--violet-dim),var(--cyan-dim)) !important;
    color:var(--text) !important; border:1px solid var(--violet) !important;
    border-radius:10px !important; font-weight:600 !important;
    font-size:.875rem !important; width:100% !important;
    padding:.7rem 1.2rem !important; transition:all .25s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background:linear-gradient(135deg,var(--violet),var(--cyan)) !important;
    color:#fff !important; box-shadow:var(--glow-violet) !important;
    transform:translateY(-2px) !important;
}}

[data-testid="stForm"] {{
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:16px !important; padding:1.5rem !important;
}}
[data-testid="stFormSubmitButton"] > button {{
    background:linear-gradient(135deg,var(--cyan) 0%,var(--violet) 100%) !important;
    color:#fff !important; border:none !important; font-weight:700 !important;
    padding:.65rem 2rem !important; border-radius:10px !important;
    font-size:.9rem !important; transition:all .25s !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform:translateY(-2px) !important; box-shadow:0 6px 30px {T['cyan']}50 !important;
}}

hr {{
    border:none !important; height:1px !important; margin:1.5rem 0 !important;
    background:linear-gradient(90deg,transparent,var(--border),transparent) !important;
}}
h1,h2,h3,h4,h5,h6 {{ font-family:var(--font-head) !important; color:var(--text) !important; }}
p,li,span,label,.stMarkdown {{ font-family:var(--font-body) !important; color:var(--text) !important; }}
[data-testid="stVegaLiteChart"] {{
    background:var(--card) !important; border-radius:12px !important;
    border:1px solid var(--border) !important; padding:1rem !important;
}}
[data-testid="stJson"] {{
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:12px !important; font-family:var(--font-mono) !important;
    font-size:.8rem !important;
}}
[data-testid="stSpinner"] {{ color:var(--cyan) !important; }}
.js-plotly-plot .plotly {{ border-radius:12px !important; }}
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:var(--bg2); }}
::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:var(--cyan); }}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# AUTH — FIREBASE
# ─────────────────────────────────────────────────────────────────────────────
# Uses Firebase Authentication (Email/Password provider) via pyrebase4.
# No user data is stored locally — Firebase handles everything.
#
# Setup (one-time):
#   1. Go to https://console.firebase.google.com → create a project
#   2. Authentication → Sign-in method → enable Email/Password
#   3. Project Settings → General → scroll to "Your apps" → Web app → copy config
#   4. Paste your values into FIREBASE_CONFIG below
#   5. pip install pyrebase4
#
# Username UX is preserved: we store username as a display name in Firebase
# and use <username>@automlstudio.app as the internal email — users never
# see or type an email address.
# ═════════════════════════════════════════════════════════════════════════════

SESSIONS_DIR = "sessions"

# ── Paste your Firebase project config here ───────────────────────────────────
FIREBASE_CONFIG = {
  "apiKey": "AIzaSyC8iVVGmR5DQ8RZzn8uU47w4jLf6-_0ANk",
  "authDomain": "automl-assistant.firebaseapp.com",
  "projectId": "automl-assistant",
  "storageBucket": "automl-assistant.firebasestorage.app",
  "messagingSenderId": "493105345729",
  "appId": "1:493105345729:web:bc41e0ce267d521f1f9040",
  "measurementId": "G-SBFTKXMFKH"
};

@st.cache_resource
def _get_firebase():
    """
    Initialise pyrebase once and cache it for the lifetime of the app.
    pyrebase4 requires databaseURL — we point it to a dummy placeholder
    since we only use Firebase Auth, not the Realtime Database.
    """
    import pyrebase
    config = {**FIREBASE_CONFIG, "databaseURL": f"https://{FIREBASE_CONFIG['projectId']}-default-rtdb.firebaseio.com"}
    fb = pyrebase.initialize_app(config)
    return fb.auth()

def _to_email(username: str) -> str:
    """Map a plain username to a deterministic internal email for Firebase."""
    safe = "".join(c for c in username.lower() if c.isalnum() or c in "-_.")
    return f"{safe}@automlstudio.app"

def _register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    try:
        auth = _get_firebase()
        user = auth.create_user_with_email_and_password(_to_email(username), password)
        # Store the display name so we can show it back to the user
        auth.update_profile(user["idToken"], display_name=username)
        return True, "Account created successfully."
    except Exception as e:
        msg = str(e)
        if "EMAIL_EXISTS" in msg:
            return False, "Username already exists. Please choose another."
        if "WEAK_PASSWORD" in msg:
            return False, "Password must be at least 6 characters."
        return False, f"Registration failed: {msg}"

def _login_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Please enter both username and password."
    try:
        auth = _get_firebase()
        auth.sign_in_with_email_and_password(_to_email(username), password)
        return True, "Login successful."
    except Exception as e:
        msg = str(e)
        if "EMAIL_NOT_FOUND" in msg or "USER_NOT_FOUND" in msg:
            return False, "No account found with that username."
        if "INVALID_PASSWORD" in msg or "INVALID_LOGIN_CREDENTIALS" in msg:
            return False, "Incorrect password."
        return False, f"Login failed: {msg}"


# ═════════════════════════════════════════════════════════════════════════════
# PER-USER SESSION PERSISTENCE
# ═════════════════════════════════════════════════════════════════════════════

def _session_path(username: str) -> str:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    # .pkl.gz — gzip-compressed pickle, typically 60-80 % smaller than raw pickle
    return os.path.join(SESSIONS_DIR, f"{username}.pkl.gz")

def _slim_result(result: dict) -> dict:
    """
    Return a lightweight copy of the result dict.
    The full result contains EVERY trained model (Random Forest, XGBoost, SVM …).
    We only need the best one to power the Live Prediction tester.
    Leaderboard, scores, training times and feature importance are plain Python
    objects and stay as-is.
    """
    if result is None:
        return None
    return {
        "leaderboard":        result.get("leaderboard"),
        "model_scores":       result.get("model_scores"),
        "training_time":      result.get("training_time"),
        "best_model_name":    result.get("best_model_name"),
        "best_model":         result.get("best_model"),   # only the winner
        "feature_importance": result.get("feature_importance"),
        # intentionally omit "all_models" / any other bulky keys
    }

def _save_user_session(username: str):
    """
    Persist all progress to sessions/<username>.pkl.gz (gzip-compressed).

    What is stored and why it stays small:
      • df_csv          — raw CSV text, compressed well by gzip
      • processed_df_csv— same
      • analysis        — plain Python dict, tiny
      • result (slim)   — only the BEST model, not every trained model
      • preprocessing_config — small JSON-style dict
    """
    if not username:
        return
    payload = {
        "df_csv":           st.session_state.session_df.to_csv(index=False).encode("utf-8")
                            if st.session_state.session_df is not None else None,
        "df_filename":      st.session_state.session_df_filename,
        "analysis":         st.session_state.analysis,
        "result":           _slim_result(st.session_state.result),
        "processed_df_csv": st.session_state.processed_df.to_csv(index=False).encode("utf-8")
                            if st.session_state.processed_df is not None else None,
        "preprocessing_config": st.session_state.preprocessing_config,
    }
    try:
        import gzip
        with gzip.open(_session_path(username), "wb", compresslevel=6) as f:
            pickle.dump(payload, f)
    except Exception:
        pass  # never crash the app on a save failure

def _load_user_session(username: str):
    """
    Restore a previously saved session into st.session_state on login.
    Handles both the new .pkl.gz format and the old .pkl format gracefully.
    """
    import gzip
    gz_path  = _session_path(username)                              # new format
    pkl_path = gz_path.replace(".pkl.gz", ".pkl")                   # legacy format

    if os.path.exists(gz_path):
        open_fn, path = gzip.open, gz_path
    elif os.path.exists(pkl_path):
        open_fn, path = open, pkl_path
    else:
        return  # brand-new user — nothing to restore

    try:
        with open_fn(path, "rb") as f:
            payload = pickle.load(f)

        # Restore raw dataframe
        st.session_state.session_df = (
            pd.read_csv(io.BytesIO(payload["df_csv"]))
            if payload.get("df_csv") is not None else None
        )
        st.session_state.session_df_filename = payload.get("df_filename", "")

        # Restore downstream objects
        st.session_state.analysis    = payload.get("analysis")
        st.session_state.result      = payload.get("result")

        # Restore processed dataframe
        st.session_state.processed_df = (
            pd.read_csv(io.BytesIO(payload["processed_df_csv"]))
            if payload.get("processed_df_csv") is not None else None
        )

        # Restore preprocessing config
        st.session_state.preprocessing_config = payload.get("preprocessing_config")

        # Rebuild the export reference files so Live Prediction works immediately
        if st.session_state.session_df is not None and st.session_state.preprocessing_config:
            os.makedirs("export", exist_ok=True)
            st.session_state.session_df.to_csv("export/reference_data.csv", index=False)
            with open("export/preprocessing_config.json", "w") as f:
                json.dump(st.session_state.preprocessing_config, f)

    except Exception:
        pass  # corrupt or old session file — start fresh silently


# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ═════════════════════════════════════════════════════════════════════════════

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "result" not in st.session_state:
    st.session_state.result = None
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None
# Holds the uploaded df across logout/login cycles (populated from disk on login)
if "session_df" not in st.session_state:
    st.session_state.session_df = None
if "session_df_filename" not in st.session_state:
    st.session_state.session_df_filename = ""
if "preprocessing_config" not in st.session_state:
    st.session_state.preprocessing_config = None


# ═════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ═════════════════════════════════════════════════════════════════════════════

def render_auth_screen():
    _, centre, _ = st.columns([1, 1.2, 1])

    with centre:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:2.5rem;">
            <div style="
                display:inline-flex;align-items:center;justify-content:center;
                width:56px;height:56px;
                background:linear-gradient(135deg,{T['cyan']},{T['violet']});
                border-radius:16px;
                box-shadow:0 0 32px {T['cyan']}44;
                font-family:'DM Mono',monospace;font-weight:500;
                font-size:1rem;color:#fff;margin-bottom:1rem;
            ">ML</div>
            <div style="
                font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;
                background:linear-gradient(90deg,{T['text']} 20%,{T['cyan']} 65%,{T['violet']} 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                letter-spacing:-.02em;line-height:1.1;
            ">AutoML Studio</div>
            <div style="color:{T['muted']};font-size:.85rem;
                font-family:'Outfit',sans-serif;margin-top:.4rem;">
                Your personal machine learning workspace
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login_style = (
            f"background:linear-gradient(135deg,{T['cyan_dim']},{T['violet_dim']});"
            f"color:{T['cyan']};border:1px solid {T['cyan']}66;font-weight:700;"
            if st.session_state.auth_tab == "login"
            else f"background:{T['surface']};color:{T['muted']};border:1px solid {T['border']};"
        )
        tab_reg_style = (
            f"background:linear-gradient(135deg,{T['cyan_dim']},{T['violet_dim']});"
            f"color:{T['cyan']};border:1px solid {T['cyan']}66;font-weight:700;"
            if st.session_state.auth_tab == "register"
            else f"background:{T['surface']};color:{T['muted']};border:1px solid {T['border']};"
        )

        sw_col1, sw_col2 = st.columns(2)
        with sw_col1:
            if st.button("Sign In", key="switch_login", use_container_width=True):
                st.session_state.auth_tab = "login"
                st.rerun()
        with sw_col2:
            if st.button("Create Account", key="switch_register", use_container_width=True):
                st.session_state.auth_tab = "register"
                st.rerun()

        st.markdown("<div style='height:.2rem'></div>", unsafe_allow_html=True)

        # ── Login Form ────────────────────────────────────────────────────
        if st.session_state.auth_tab == "login":
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};
                border-radius:16px;padding:1.8rem 2rem 1.6rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:800;
                    color:{T['text']};font-size:1.05rem;margin-bottom:1.4rem;">
                    Welcome back
                </div>
            """, unsafe_allow_html=True)

            login_username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            login_password = st.text_input("Password", key="login_pass", placeholder="Enter your password", type="password")
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

            if st.button("Sign In", key="do_login", type="primary", use_container_width=True):
                ok, msg = _login_user(login_username, login_password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username  = login_username.strip()
                    # ── Restore all saved progress from disk ──
                    _load_user_session(login_username.strip())
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown(f"""
                <div style="text-align:center;margin-top:1.2rem;
                    font-family:'Outfit',sans-serif;font-size:.8rem;color:{T['muted']};">
                    No account yet?
                    <span style="color:{T['cyan']};font-weight:600;">Use the Create Account tab above.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Register Form ─────────────────────────────────────────────────
        else:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};
                border-radius:16px;padding:1.8rem 2rem 1.6rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:800;
                    color:{T['text']};font-size:1.05rem;margin-bottom:1.4rem;">
                    Create your account
                </div>
            """, unsafe_allow_html=True)

            reg_username  = st.text_input("Username", key="reg_user",  placeholder="Choose a username (min 3 chars)")
            reg_password  = st.text_input("Password", key="reg_pass",  placeholder="Choose a password (min 6 chars)", type="password")
            reg_password2 = st.text_input("Confirm Password", key="reg_pass2", placeholder="Re-enter your password", type="password")
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

            if st.button("Create Account", key="do_register", type="primary", use_container_width=True):
                if reg_password != reg_password2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = _register_user(reg_username, reg_password)
                    if ok:
                        # Auto-login + try loading any existing session (empty for new users)
                        st.session_state.logged_in = True
                        st.session_state.username  = reg_username.strip()
                        _load_user_session(reg_username.strip())
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown(f"""
                <div style="text-align:center;margin-top:1.2rem;
                    font-family:'Outfit',sans-serif;font-size:.8rem;color:{T['muted']};">
                    Already have an account?
                    <span style="color:{T['cyan']};font-weight:600;">Use the Sign In tab above.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin-top:2rem;
            font-family:'DM Mono',monospace;font-size:.72rem;color:{T['border']};">
            AutoML Studio · All rights reserved
        </div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# GATE
# ═════════════════════════════════════════════════════════════════════════════

if not st.session_state.logged_in:
    render_auth_screen()
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═════════════════════════════════════════════════════════════════════════════

hero_left, hero_right = st.columns([6, 1])

with hero_left:
    st.markdown(f"""
    <div style="
        display:flex; align-items:center; gap:18px;
        padding:1.6rem 2rem;
        background:{T['hero_bg']};
        border:1px solid {T['hero_border']};
        border-radius:20px; margin-bottom:.4rem;
        position:relative; overflow:hidden;
    ">
        <div style="position:absolute;inset:0;pointer-events:none;
            background:
                radial-gradient(ellipse 60% 80% at 80% 50%, {T['cyan']}08, transparent),
                radial-gradient(ellipse 40% 60% at 10% 50%, {T['violet']}08, transparent);
        "></div>
        <div style="
            width:52px; height:52px; flex-shrink:0;
            background:linear-gradient(135deg,{T['cyan']},{T['violet']});
            border-radius:14px; display:flex; align-items:center;
            justify-content:center; font-size:1rem;
            font-family:'DM Mono',monospace; font-weight:500; color:#fff;
            box-shadow:0 0 24px {T['cyan']}44;
        ">ML</div>
        <div>
            <div style="
                font-family:'Syne',sans-serif; font-size:1.85rem; font-weight:800;
                background:linear-gradient(90deg,{T['text']} 20%,{T['cyan']} 65%,{T['violet']} 100%);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                line-height:1.1; letter-spacing:-.02em;
            ">AutoML Studio</div>
            <div style="color:{T['muted']};font-size:.85rem;
                font-family:'Outfit',sans-serif;margin-top:4px;">
                Upload a dataset · Preprocess · Train models · Explain results
            </div>
        </div>
        <div style="margin-left:auto;display:flex;gap:8px;align-items:center;
            font-family:'DM Mono',monospace;font-size:.72rem;">
            <span style="background:{T['green']}1a;border:1px solid {T['green']}44;
                border-radius:20px;padding:4px 12px;color:{T['green']};">LIVE</span>
            <span style="background:{T['cyan']}0d;border:1px solid {T['cyan']}30;
                border-radius:20px;padding:4px 12px;color:{T['cyan']};">v2.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_right:
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        background:{T['card']};border:1px solid {T['border']};
        border-radius:12px;padding:.7rem 1rem;text-align:center;
        font-family:'Outfit',sans-serif;
    ">
        <div style="font-size:.7rem;color:{T['muted']};
            text-transform:uppercase;letter-spacing:.08em;margin-bottom:.2rem;">
            Signed in as
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:.88rem;
            color:{T['cyan']};font-weight:500;">
            {st.session_state.username}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

    if st.button("Sign Out", key="logout", use_container_width=True):
        # ── Save all progress to disk first, THEN wipe memory ──
        _save_user_session(st.session_state.username)
        st.session_state.logged_in             = False
        st.session_state.username              = ""
        st.session_state.auth_tab              = "login"
        st.session_state.analysis              = None
        st.session_state.result                = None
        st.session_state.processed_df          = None
        st.session_state.session_df            = None
        st.session_state.session_df_filename   = ""
        st.session_state.preprocessing_config  = None
        st.rerun()


# ─── Upload / Resume ─────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:.6rem;
    font-family:'Outfit',sans-serif;font-weight:600;font-size:.9rem;
    color:{T['muted']};letter-spacing:.06em;text-transform:uppercase;">
    <span style="color:{T['cyan']};">+</span> Dataset Upload
</div>
""", unsafe_allow_html=True)

# ── Resume banner: shown when a previous dataset was restored from disk ──
if st.session_state.session_df is not None:
    fname = st.session_state.session_df_filename or "your dataset"
    resume_col, clear_col = st.columns([5, 1])
    with resume_col:
        progress_parts = []
        if st.session_state.analysis   is not None: progress_parts.append("Analysis ✓")
        if st.session_state.result     is not None: progress_parts.append("Model ✓")
        progress_str = "  ·  ".join(progress_parts) if progress_parts else "No steps completed yet"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;
            background:linear-gradient(135deg,{T['green_dim']},{T['cyan_dim']});
            border:1px solid {T['green']}40;border-radius:12px;
            padding:.75rem 1.2rem;margin-bottom:.8rem;
            font-family:'Outfit',sans-serif;font-size:.875rem;">
            <span style="font-size:1.1rem;">↩</span>
            <div>
                <span style="color:{T['muted']};">Resuming session · </span>
                <span style="color:{T['green']};font-weight:700;
                    font-family:'DM Mono',monospace;">{fname}</span>
                <span style="color:{T['muted']};font-size:.78rem;">
                    &nbsp;·&nbsp;{st.session_state.session_df.shape[0]:,} rows
                    × {st.session_state.session_df.shape[1]} cols</span>
                <br>
                <span style="font-size:.78rem;color:{T['cyan']};
                    font-family:'DM Mono',monospace;">{progress_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with clear_col:
        if st.button("Upload New", key="clear_session_df", use_container_width=True):
            st.session_state.session_df            = None
            st.session_state.session_df_filename   = ""
            st.session_state.analysis              = None
            st.session_state.result                = None
            st.session_state.processed_df          = None
            st.session_state.preprocessing_config  = None
            _save_user_session(st.session_state.username)
            st.rerun()

uploaded_file = st.file_uploader(
    "Drop your CSV or Excel file here, or click to browse",
    type=["csv", "xlsx", "xls"],
    label_visibility="visible"
)

# ── Resolve which dataframe to work with ──────────────────────────────────────
if uploaded_file is not None:
    file_name = uploaded_file.name
    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file format")
        st.stop()

    # Persist newly uploaded file; reset downstream state if it's a different file
    if st.session_state.session_df_filename != file_name or st.session_state.session_df is None:
        st.session_state.session_df            = df.copy()
        st.session_state.session_df_filename   = file_name
        st.session_state.analysis              = None
        st.session_state.result                = None
        st.session_state.processed_df          = None
        st.session_state.preprocessing_config  = None
        _save_user_session(st.session_state.username)

elif st.session_state.session_df is not None:
    # No new upload — resume from the saved session
    df        = st.session_state.session_df
    file_name = st.session_state.session_df_filename
else:
    df        = None
    file_name = None

if df is None:
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.5rem;">
        <div style="background:{T['card']};border:1px solid {T['border']};border-radius:14px;padding:1.2rem 1.4rem;">
            <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:{T['cyan']};
                text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;">01</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:{T['text']};font-size:.9rem;margin-bottom:.3rem;">Smart Analysis</div>
            <div style="font-family:'Outfit',sans-serif;color:{T['muted']};font-size:.8rem;line-height:1.5;">Auto-detects column types, missing values, and ML problem type</div>
        </div>
        <div style="background:{T['card']};border:1px solid {T['border']};border-radius:14px;padding:1.2rem 1.4rem;">
            <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:{T['cyan']};
                text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;">02</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:{T['text']};font-size:.9rem;margin-bottom:.3rem;">AI Preprocessing</div>
            <div style="font-family:'Outfit',sans-serif;color:{T['muted']};font-size:.8rem;line-height:1.5;">Recommends encoding, scaling, and imputation strategies</div>
        </div>
        <div style="background:{T['card']};border:1px solid {T['border']};border-radius:14px;padding:1.2rem 1.4rem;">
            <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:{T['cyan']};
                text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;">03</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:{T['text']};font-size:.9rem;margin-bottom:.3rem;">Model Tournament</div>
            <div style="font-family:'Outfit',sans-serif;color:{T['muted']};font-size:.8rem;line-height:1.5;">Trains multiple models and ranks them by performance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:8px;
    background:{T['cyan_dim']};border:1px solid {T['cyan']}30;
    border-radius:30px;padding:6px 16px;
    font-family:'DM Mono',monospace;font-size:.78rem;color:{T['cyan']};
    margin-bottom:1.2rem;">
    <span>File:</span> {file_name}
    <span style="color:{T['muted']};">·</span>
    <span style="color:{T['muted']};">{df.shape[0]:,} rows x {df.shape[1]} cols</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Data & EDA", "Preprocessing", "Results & Testing"])

# =========================================================================
# TAB 1 — DATA & EDA
# =========================================================================
with tab1:

    def section_label(num, title):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;
            margin:1.6rem 0 .8rem;
            font-family:'Syne',sans-serif;font-weight:700;
            font-size:1.05rem;color:{T['text']};">
            <span style="background:linear-gradient(135deg,{T['cyan_dim']},{T['violet_dim']});
                border:1px solid {T['cyan']}44;border-radius:8px;
                padding:4px 10px;font-family:'DM Mono',monospace;
                font-size:.78rem;color:{T['cyan']};letter-spacing:.04em;">{num}</span>
            {title}
        </div>""", unsafe_allow_html=True)

    section_label("01", "Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    section_label("02", "Dataset Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())

    valid_columns = [
        col for col in df.columns
        if df[col].nunique() > 1 and "id" not in col.lower()
    ]
    suggested_targets = [
        col for col in valid_columns
        if df[col].nunique() <= 20 or df[col].dtype != "object"
    ]

    section_label("03", "Target Column Selection")
    st.markdown(f"""<p style="color:{T['muted']};font-size:.85rem;margin-bottom:.5rem;">
        Choose the column the model should learn to predict.</p>""",
        unsafe_allow_html=True)

    # Restore previously chosen target if available
    saved_target = (
        st.session_state.preprocessing_config.get("target")
        if st.session_state.preprocessing_config else None
    )
    target_index = (
        suggested_targets.index(saved_target)
        if saved_target and saved_target in suggested_targets else 0
    )
    target = st.selectbox(
        "Select Target Column", suggested_targets,
        index=target_index, key="target_col"
    )

    st.divider()
    section_label("04", "Exploratory Data Analysis")

    eda_col1, eda_col2 = st.columns(2)
    with eda_col1:
        if st.checkbox("Show Distribution of Target Variable"):
            fig_hist = px.histogram(
                df, x=target,
                title=f"Distribution — {target}",
                color_discrete_sequence=[T["cyan"]],
                template=T["plot_tmpl"]
            )
            fig_hist.update_layout(
                paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
                font_family="Outfit", font_color=T["muted"],
                title_font_size=13, title_font_color=T["muted"],
                margin=dict(l=16, r=16, t=40, b=16),
            )
            fig_hist.update_traces(marker_line_color=T["plot_bg"], marker_line_width=1)
            st.plotly_chart(fig_hist, use_container_width=True)

    with eda_col2:
        if st.checkbox("Show Correlation Heatmap (Numerical Features)"):
            numeric_df = df.select_dtypes(include=["number"])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr().round(2)
                fig_corr = px.imshow(
                    corr_matrix, text_auto=True, aspect="auto",
                    color_continuous_scale="RdBu_r",
                    title="Feature Correlation Heatmap",
                    template=T["plot_tmpl"]
                )
                fig_corr.update_layout(
                    paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
                    font_family="DM Mono", font_color=T["muted"],
                    title_font_size=13, title_font_color=T["muted"],
                    margin=dict(l=16, r=16, t=40, b=16),
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("No numerical features available to calculate correlations.")

# =========================================================================
# TAB 2 — PREPROCESSING
# =========================================================================
with tab2:

    def step_header(number, title, subtitle=""):
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:14px;
            background:{T['card']};border:1px solid {T['border']};
            border-radius:14px;padding:1rem 1.4rem;margin:1.4rem 0 .8rem;">
            <div style="width:32px;height:32px;flex-shrink:0;
                background:linear-gradient(135deg,{T['cyan']},{T['violet']});
                border-radius:9px;display:flex;align-items:center;
                justify-content:center;font-family:'DM Mono',monospace;
                font-size:.78rem;font-weight:500;color:#fff;">{number}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;
                    color:{T['text']};font-size:.95rem;">{title}</div>
                {f'<div style="color:{T["muted"]};font-size:.8rem;margin-top:2px;">{subtitle}</div>' if subtitle else ''}
            </div>
        </div>""", unsafe_allow_html=True)

    step_header("01", "Analyze Your Dataset", "Click the button to scan for issues and column types")
    if st.button("Analyze Dataset"):
        st.session_state.analysis = analyze_dataset(df)
        _save_user_session(st.session_state.username)   # ← auto-save after analysis

    if st.session_state.analysis is not None:
        analysis = st.session_state.analysis

        rows, cols_count = analysis["dataset_shape"]
        st.markdown(f"""
        <div style="background:{T['card']};border:1px solid {T['border']};
            border-radius:12px;padding:1rem 1.4rem;margin:.5rem 0;
            font-family:'Outfit',sans-serif;font-size:.875rem;color:{T['muted']};">
            Dataset contains
            <span style="color:{T['cyan']};font-weight:700;">{rows:,} rows</span>
            and
            <span style="color:{T['cyan']};font-weight:700;">{cols_count} columns</span>.
        </div>""", unsafe_allow_html=True)

        missing = sum(analysis["missing_values"].values())
        if missing == 0:
            st.success("No missing values detected.")
        else:
            st.warning(f"{missing} missing values detected.")

        col_cat, col_num = st.columns(2)
        with col_cat:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};
                border-radius:12px;padding:1rem 1.2rem;">
                <div style="color:{T['muted']};font-size:.72rem;text-transform:uppercase;
                    letter-spacing:.1em;font-weight:600;margin-bottom:.6rem;
                    font-family:'Outfit',sans-serif;">Categorical Columns</div>
            """, unsafe_allow_html=True)
            if analysis["categorical_columns"]:
                for c in analysis["categorical_columns"]:
                    st.markdown(f"""
                    <span style="display:inline-block;background:{T['violet_dim']};
                        border:1px solid {T['violet']}40;border-radius:6px;
                        padding:2px 10px;font-family:'DM Mono',monospace;
                        font-size:.78rem;color:{T['violet']};margin:2px 3px;">{c}</span>
                    """, unsafe_allow_html=True)
            else:
                st.success("None detected")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_num:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};
                border-radius:12px;padding:1rem 1.2rem;">
                <div style="color:{T['muted']};font-size:.72rem;text-transform:uppercase;
                    letter-spacing:.1em;font-weight:600;margin-bottom:.6rem;
                    font-family:'Outfit',sans-serif;">Numerical Columns</div>
            """, unsafe_allow_html=True)
            for n in analysis["numerical_columns"]:
                st.markdown(f"""
                <span style="display:inline-block;background:{T['cyan_dim']};
                    border:1px solid {T['cyan']}30;border-radius:6px;
                    padding:2px 10px;font-family:'DM Mono',monospace;
                    font-size:.78rem;color:{T['cyan']};margin:2px 3px;">{n}</span>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if analysis["duplicate_rows"] == 0:
            st.success("No duplicate rows detected.")
        else:
            st.warning(f"{analysis['duplicate_rows']} duplicate rows detected.")

        problem_type = detect_problem_type(df[target])
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:10px;
            background:linear-gradient(135deg,{T['cyan_dim']},{T['violet_dim']});
            border:1px solid {T['cyan']}40;border-radius:30px;
            padding:8px 20px;margin:.8rem 0;font-family:'Outfit',sans-serif;">
            <span style="color:{T['muted']};font-size:.85rem;">Detected ML Problem:</span>
            <span style="color:{T['cyan']};font-weight:700;font-size:.9rem;
                text-transform:uppercase;letter-spacing:.06em;">{problem_type}</span>
        </div>""", unsafe_allow_html=True)

        readiness = dataset_readiness(analysis)
        score = readiness["score"]
        score_color = T["green"] if score >= 80 else T["amber"] if score >= 50 else T["red"]
        st.markdown(f"""
        <div style="background:{T['card']};border:1px solid {T['border']};
            border-radius:14px;padding:1.2rem 1.5rem;margin:.8rem 0;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.7rem;">
                <span style="font-family:'Syne',sans-serif;font-weight:700;color:{T['text']};">Dataset Readiness</span>
                <span style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{score_color};">
                    {score}<span style="font-size:.75rem;color:{T['muted']};">/100</span></span>
            </div>
            <div style="background:{T['bg2']};border-radius:30px;height:8px;overflow:hidden;">
                <div style="width:{score}%;height:100%;border-radius:30px;
                    background:linear-gradient(90deg,{score_color}88,{score_color});"></div>
            </div>
            <div style="margin-top:.5rem;font-family:'Outfit',sans-serif;
                font-size:.78rem;color:{score_color};">{readiness['status']}</div>
        </div>""", unsafe_allow_html=True)

        if readiness["issues"]:
            for issue in readiness["issues"]:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;color:{T['amber']};
                    font-size:.83rem;font-family:'Outfit',sans-serif;margin:.2rem 0;">
                    {issue}</div>""", unsafe_allow_html=True)

        show_pipeline()

       

        step_header("02", "Preprocessing Recommendations", "Review AI suggestions or customise each step")
        rec      = recommend_preprocessing(df)
        _saved   = st.session_state.preprocessing_config or {}

        def rec_section(title):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:1.2rem 0 .5rem;
                font-family:'Outfit',sans-serif;font-weight:600;font-size:.88rem;
                color:{T['muted']};letter-spacing:.04em;text-transform:uppercase;">
                <span style="display:inline-block;width:18px;height:1px;
                    background:{T['cyan']};"></span>
                {title}
            </div>""", unsafe_allow_html=True)

        # ── Missing Values ────────────────────────────────────────────
        rec_section("Missing Values")
        mv_rec = rec["missing_values"]
        if mv_rec["recommended"] is not None:
            rec_val  = str(mv_rec["recommended"]).lower()
            valid_mv = ["mean", "median", "mode", "drop"]
            if rec_val not in valid_mv:
                rec_val = "mean"
            mv_explanations = {
                "mean":   "Replaces empty spots with the column average — keeps data rows intact without skewing numbers.",
                "median": "Replaces empty spots with the middle value — robust to extreme outliers.",
                "mode":   "Fills empty spots with the most frequent value — great for categories.",
                "drop":   "Removes incomplete rows entirely — safest when guessing could mislead the model.",
            }
            st.info(f"Recommendation: `{rec_val}` — {mv_explanations.get(rec_val, '')}")
            mv_choice = st.radio("Action", ["Accept Recommendation", "Modify"], key="mv_radio", horizontal=True)
            if mv_choice == "Accept Recommendation":
                missing_option = rec_val
                st.success(f"Applied **{rec_val}** strategy.")
            else:
                saved_mv = _saved.get("missing_strategy", rec_val)
                mv_idx   = valid_mv.index(saved_mv) if saved_mv in valid_mv else valid_mv.index(rec_val)
                missing_option = st.selectbox("Choose strategy", valid_mv, index=mv_idx)
                if missing_option == rec_val:
                    st.success("Sticking with the recommendation.")
                elif missing_option == "drop":
                    st.warning("Dropping rows reduces dataset size — imputation usually works better.")
                elif rec_val == "drop" and missing_option != "drop":
                    st.success(f"Better choice! **{missing_option}** preserves data rows.")
                elif missing_option in ["mean", "median"] and rec_val == "mode":
                    st.success(f"Smart choice — **{missing_option}** is statistically robust for numerical variables.")
                else:
                    st.info(f"Using **{missing_option}** strategy.")
        else:
            st.success("No missing values — no action needed.")
            missing_option = None

        # ── Encoding ─────────────────────────────────────────────────
        rec_section("Categorical Encoding")
        enc_rec   = rec["encoding"]
        rec_enc   = str(enc_rec.get("recommended", "onehot")).lower()
        valid_enc = ["label", "onehot"]
        if rec_enc not in valid_enc:
            rec_enc = "onehot"
        enc_explanations = {
            "onehot": "Creates separate Yes/No columns per category — prevents the model from assuming a false numeric order.",
            "label":  "Converts categories to integers — suitable when categories have a natural order.",
        }
        st.info(f"Recommendation: `{rec_enc}` — {enc_explanations.get(rec_enc, '')}")
        enc_choice = st.radio("Action", ["Accept Recommendation", "Modify"], key="enc_radio", horizontal=True)
        if enc_choice == "Accept Recommendation":
            encoding_option = rec_enc
            st.success(f"Applied **{rec_enc}** encoding.")
        else:
            saved_enc = _saved.get("encoding", rec_enc)
            enc_idx   = valid_enc.index(saved_enc) if saved_enc in valid_enc else valid_enc.index(rec_enc)
            encoding_option = st.selectbox("Choose encoding", valid_enc, index=enc_idx)
            if encoding_option == rec_enc:
                st.success("Sticking with the recommendation.")
            elif encoding_option == "label" and rec_enc == "onehot":
                st.warning("Label encoding may introduce false ordering among categories.")
            elif encoding_option == "onehot" and rec_enc == "label":
                st.success("One-hot encoding is more robust — good choice.")

        # ── Scaling ──────────────────────────────────────────────────
        rec_section("Feature Scaling")
        rec_scale   = "standard"
        valid_scale = ["standard", "minmax"]
        scale_explanations = {
            "standard": "Centers all values around zero — prevents large-magnitude features from dominating.",
            "minmax":   "Squishes all values to [0, 1] — preserves original data shape but sensitive to outliers.",
        }
        st.info(f"Recommendation: `{rec_scale}` — {scale_explanations.get(rec_scale, '')}")
        scale_choice = st.radio("Action", ["Accept Recommendation", "Modify"], key="scale_radio", horizontal=True)
        if scale_choice == "Accept Recommendation":
            scaling_option = rec_scale
            st.success(f"Applied **{rec_scale}** scaling.")
        else:
            saved_scale = _saved.get("scaling", rec_scale)
            sc_idx      = valid_scale.index(saved_scale) if saved_scale in valid_scale else 0
            scaling_option = st.selectbox("Choose scaling", valid_scale, index=sc_idx)
            if scaling_option == rec_scale:
                st.success("Sticking with the recommendation.")
            elif scaling_option == "minmax":
                st.warning("MinMax is sensitive to extreme outliers.")
            else:
                st.info(f"Using **{scaling_option}** scaling.")

        st.divider()
        if st.button("Run AutoML", type="primary"):
            with st.spinner("Preparing data and training models..."):
                processed_df = preprocess_data(
                    df,
                    missing_strategy=missing_option,
                    encoding=encoding_option,
                    scaling=scaling_option,
                )
                processed_df, removed_features = remove_highly_correlated_features(processed_df)
                if removed_features:
                    st.markdown(f"""
                    <div style="color:{T['amber']};font-size:.85rem;
                        font-family:'Outfit',sans-serif;margin:.4rem 0;">
                        Removed highly correlated features:</div>""",
                        unsafe_allow_html=True)
                    for r in removed_features:
                        st.markdown(f"""
                        <span style="display:inline-block;background:{T['amber']}15;
                            border:1px solid {T['amber']}40;border-radius:6px;
                            padding:2px 10px;font-family:'DM Mono',monospace;
                            font-size:.78rem;color:{T['amber']};margin:2px;">{r}</span>
                        """, unsafe_allow_html=True)

                st.session_state.processed_df = processed_df
                st.session_state.result       = train_models(processed_df, target)

                os.makedirs("export", exist_ok=True)
                df.to_csv("export/reference_data.csv", index=False)
                config = {
                    "missing_strategy": missing_option,
                    "encoding":         encoding_option,
                    "scaling":          scaling_option,
                    "target":           target,
                }
                with open("export/preprocessing_config.json", "w") as f:
                    json.dump(config, f)

                # Save config to session state and persist everything ──
                st.session_state.preprocessing_config = config
                _save_user_session(st.session_state.username)  # ← auto-save after training

            st.success("Training complete! Head to the **Results & Testing** tab.")

# =========================================================================
# TAB 3 — RESULTS & TESTING
# =========================================================================
with tab3:
    if st.session_state.result is None:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
            justify-content:center;padding:4rem 2rem;text-align:center;
            background:{T['card']};border:1px dashed {T['border']};border-radius:16px;">
            <div style="font-family:'DM Mono',monospace;font-size:2rem;
                color:{T['cyan']};margin-bottom:1rem;letter-spacing:.1em;">[ ]</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;
                color:{T['text']};font-size:1.1rem;margin-bottom:.5rem;">No results yet</div>
            <div style="color:{T['muted']};font-size:.875rem;font-family:'Outfit',sans-serif;">
                Go to <strong style="color:{T['cyan']};">Preprocessing</strong>,
                configure your pipeline, and click
                <strong style="color:{T['cyan']};">Run AutoML</strong>.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        result = st.session_state.result

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""<div style="font-family:'Syne',sans-serif;font-weight:800;
                font-size:1rem;color:{T['text']};margin-bottom:.8rem;">Model Leaderboard</div>
            """, unsafe_allow_html=True)
            leaderboard = pd.DataFrame(result["leaderboard"], columns=["Model", "Score"])
            st.dataframe(leaderboard, use_container_width=True)

            fig_lb = px.bar(
                leaderboard, x="Model", y="Score",
                color="Score",
                color_continuous_scale=[T["border"], T["cyan"]],
                template=T["plot_tmpl"],
                title="Model Comparison"
            )
            fig_lb.update_layout(
                paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
                font_family="Outfit", font_color=T["muted"],
                title_font_size=13, title_font_color=T["muted"],
                coloraxis_showscale=False,
                margin=dict(l=16, r=16, t=40, b=16),
            )
            fig_lb.update_traces(marker_line_width=0)
            st.plotly_chart(fig_lb, use_container_width=True)

            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:10px;
                background:linear-gradient(135deg,{T['green_dim']},{T['cyan_dim']});
                border:1px solid {T['green']}40;border-radius:30px;padding:8px 20px;
                font-family:'Outfit',sans-serif;">
                <span style="font-family:'DM Mono',monospace;font-size:.78rem;
                    color:{T['green']};letter-spacing:.06em;">No.1</span>
                <span style="color:{T['muted']};font-size:.85rem;">Best Model:</span>
                <span style="color:{T['green']};font-weight:700;font-size:.95rem;">
                    {result['best_model_name']}</span>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""<div style="font-family:'Syne',sans-serif;font-weight:800;
                font-size:1rem;color:{T['text']};margin-bottom:.8rem;">Model Scores</div>
            """, unsafe_allow_html=True)
            st.json(result["model_scores"])

            st.markdown(f"""<div style="font-family:'Syne',sans-serif;font-weight:800;
                font-size:1rem;color:{T['text']};margin:.8rem 0;">Training Time</div>
            """, unsafe_allow_html=True)
            time_df = pd.DataFrame(
                list(result["training_time"].items()),
                columns=["Model", "Time (seconds)"]
            )
            st.dataframe(time_df, hide_index=True, use_container_width=True)

        st.divider()
        explanation = explain_model_choice(result["best_model_name"], result["model_scores"])
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{T['card']},{T['surface']});
            border:1px solid {T['border']};border-radius:16px;
            padding:1.5rem 1.8rem;margin:.5rem 0;">
            <div style="font-family:'Syne',sans-serif;font-weight:800;
                color:{T['text']};font-size:1.05rem;margin-bottom:.5rem;">{explanation['title']}</div>
            <div style="font-family:'Outfit',sans-serif;color:{T['muted']};
                font-size:.875rem;line-height:1.65;margin-bottom:.8rem;">{explanation['message']}</div>
            <div style="background:{T['cyan_dim']};border:1px solid {T['cyan']}20;
                border-radius:10px;padding:.7rem 1rem;font-size:.83rem;color:{T['cyan']};
                font-family:'Outfit',sans-serif;line-height:1.5;">{explanation['reason']}</div>
        </div>""", unsafe_allow_html=True)

        if result["feature_importance"] is not None:
            st.divider()
            st.markdown(f"""
            <div style="font-family:'Syne',sans-serif;font-weight:800;
                font-size:1rem;color:{T['text']};margin-bottom:.5rem;">Feature Importance</div>
            <p style="color:{T['muted']};font-size:.85rem;margin-bottom:.8rem;
                font-family:'Outfit',sans-serif;">
                These features had the strongest influence on the model's predictions.</p>
            """, unsafe_allow_html=True)
            fig_imp = plot_feature_importance(result["feature_importance"])
            fig_imp.update_layout(
                paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
                font_family="Outfit", font_color=T["muted"],
                margin=dict(l=16, r=16, t=40, b=16),
            )
            st.plotly_chart(fig_imp, use_container_width=True)

        st.divider()
        st.markdown(f"""
        <div style="font-family:'Syne',sans-serif;font-weight:800;
            font-size:1.05rem;color:{T['text']};margin-bottom:.3rem;">Live Prediction Tester</div>
        <p style="color:{T['muted']};font-size:.85rem;margin-bottom:1rem;
            font-family:'Outfit',sans-serif;">
            Adjust the sliders and dropdowns to test the model with your own values in real-time.</p>
        """, unsafe_allow_html=True)

        if os.path.exists("export/reference_data.csv") and os.path.exists("export/preprocessing_config.json"):
            ref_df = pd.read_csv("export/reference_data.csv")
            with open("export/preprocessing_config.json", "r") as f:
                saved_config = json.load(f)

            with st.form("interactive_prediction_form"):
                user_input = {}
                original_features = [col for col in ref_df.columns if col != saved_config["target"]]
                form_cols = st.columns(3)
                for i, col in enumerate(original_features):
                    with form_cols[i % 3]:
                        if pd.api.types.is_numeric_dtype(ref_df[col]):
                            col_min  = float(ref_df[col].min())
                            col_max  = float(ref_df[col].max())
                            col_mean = float(ref_df[col].mean())
                            step = 1.0 if pd.api.types.is_integer_dtype(ref_df[col]) else (col_max - col_min) / 100.0
                            if col_min == col_max:
                                user_input[col] = st.number_input(f"{col}", value=col_min)
                            else:
                                user_input[col] = st.slider(
                                    f"{col}",
                                    min_value=col_min, max_value=col_max,
                                    value=col_mean, step=step,
                                )
                        else:
                            unique_categories = ref_df[col].dropna().unique().tolist()
                            user_input[col] = st.selectbox(f"{col}", options=unique_categories)

                submit_prediction = st.form_submit_button("Run Prediction", type="primary")

                if submit_prediction:
                    input_df = pd.DataFrame([user_input])
                    input_df[saved_config["target"]] = ref_df[saved_config["target"]].iloc[0]
                    combined_df = pd.concat([ref_df, input_df], ignore_index=True)
                    processed_combined = preprocess_data(
                        combined_df,
                        missing_strategy=saved_config["missing_strategy"],
                        encoding=saved_config["encoding"],
                        scaling=saved_config["scaling"],
                    )
                    final_processed_row = processed_combined.tail(1)
                    expected_model_columns = [
                        c for c in st.session_state.processed_df.columns
                        if c != saved_config["target"]
                    ]
                    for c in expected_model_columns:
                        if c not in final_processed_row.columns:
                            final_processed_row[c] = 0
                    final_processed_row = final_processed_row[expected_model_columns]

                    best_model = result["best_model"]
                    prediction = best_model.predict(final_processed_row)[0]

                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,{T['green_dim']},{T['cyan_dim']});
                        border:2px solid {T['green']}40;border-radius:14px;
                        padding:1.2rem 1.6rem;text-align:center;margin-top:.8rem;">
                        <div style="color:{T['muted']};font-size:.78rem;text-transform:uppercase;
                            letter-spacing:.1em;font-family:'Outfit',sans-serif;margin-bottom:.4rem;">
                            Predicted {saved_config['target']}</div>
                        <div style="font-family:'DM Mono',monospace;font-size:2rem;
                            font-weight:500;color:{T['green']};
                            text-shadow:0 0 20px {T['green']}60;">{prediction}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.warning("Reference files not found. Please click **Run AutoML** again to generate them.")

        st.divider()
        st.markdown(f"""
        <div style="font-family:'Syne',sans-serif;font-weight:800;
            font-size:1.05rem;color:{T['text']};margin-bottom:1rem;">Export & Download</div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};
                border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:.8rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;
                    color:{T['text']};font-size:.9rem;margin-bottom:.35rem;">Cleaned Dataset</div>
                <div style="font-family:'Outfit',sans-serif;color:{T['muted']};
                    font-size:.82rem;margin-bottom:.8rem;line-height:1.5;">
                    Dataset after missing value handling, encoding, and scaling.</div>
            </div>""", unsafe_allow_html=True)
            csv_data = st.session_state.processed_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cleaned Data (.csv)",
                data=csv_data,
                file_name="cleaned_dataset.csv",
                mime="text/csv",
            )

        with col_d2:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};
                border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:.8rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;
                    color:{T['text']};font-size:.9rem;margin-bottom:.35rem;">Trained Model</div>
                <div style="font-family:'Outfit',sans-serif;color:{T['muted']};
                    font-size:.82rem;margin-bottom:.8rem;line-height:1.5;">
                    Download <strong style="color:{T['violet']};">{result['best_model_name']}</strong>
                    as a pickle file for use in your own apps.</div>
            </div>""", unsafe_allow_html=True)
            model_bytes     = pickle.dumps(result["best_model"])
            safe_model_name = result["best_model_name"].replace(" ", "_").lower()
            st.download_button(
                label="Download Best Model (.pkl)",
                data=model_bytes,
                file_name=f"{safe_model_name}.pkl",
                mime="application/octet-stream",
            )