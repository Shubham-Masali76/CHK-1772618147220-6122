"""
auth/session_manager.py
────────────────────────
Per-user session persistence for AutoML Studio.

Saves and restores user progress (uploaded dataset, analysis results,
trained model) to/from a gzip-compressed pickle file on disk so that
users can pick up where they left off after logging back in.
"""

import gzip
import io
import json
import os
import pickle

import pandas as pd
import streamlit as st

SESSIONS_DIR = "sessions"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _session_path(username: str) -> str:
    """Return the .pkl.gz path for a given username, creating the dir if needed."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return os.path.join(SESSIONS_DIR, f"{username}.pkl.gz")


def _slim_result(result: dict) -> dict | None:
    """
    Return a lightweight copy of the result dict.
    The full result contains EVERY trained model (Random Forest, XGBoost, SVM …).
    We only keep the best one to power the Live Prediction tester.
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
        # intentionally omit "all_models" and other bulky keys
    }


# ─── Public API ──────────────────────────────────────────────────────────────

def init_session_state() -> None:
    """Initialise all required session_state keys with safe defaults."""
    defaults = {
        "logged_in":             False,
        "username":              "",
        "auth_tab":              "login",
        "analysis":              None,
        "result":                None,
        "processed_df":          None,
        "session_df":            None,
        "session_df_filename":   "",
        "preprocessing_config":  None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_user_session(username: str) -> None:
    """
    Persist all progress to sessions/<username>.pkl.gz (gzip-compressed).

    What is stored and why it stays small:
      • df_csv               — raw CSV text, compresses well with gzip
      • processed_df_csv     — same
      • analysis             — plain Python dict, tiny
      • result (slim)        — only the BEST model, not every trained model
      • preprocessing_config — small JSON-style dict
    """
    if not username:
        return
    payload = {
        "df_csv": (
            st.session_state.session_df.to_csv(index=False).encode("utf-8")
            if st.session_state.session_df is not None else None
        ),
        "df_filename":      st.session_state.session_df_filename,
        "analysis":         st.session_state.analysis,
        "result":           _slim_result(st.session_state.result),
        "processed_df_csv": (
            st.session_state.processed_df.to_csv(index=False).encode("utf-8")
            if st.session_state.processed_df is not None else None
        ),
        "preprocessing_config": st.session_state.preprocessing_config,
    }
    try:
        with gzip.open(_session_path(username), "wb", compresslevel=6) as f:
            pickle.dump(payload, f)
    except Exception:
        pass  # never crash the app on a save failure


def load_user_session(username: str) -> None:
    """
    Restore a previously saved session into st.session_state on login.
    Handles both the new .pkl.gz format and the old .pkl format gracefully.
    """
    gz_path  = _session_path(username)
    pkl_path = gz_path.replace(".pkl.gz", ".pkl")

    if os.path.exists(gz_path):
        open_fn, path = gzip.open, gz_path
    elif os.path.exists(pkl_path):
        open_fn, path = open, pkl_path
    else:
        return  # brand-new user — nothing to restore

    try:
        with open_fn(path, "rb") as f:
            payload = pickle.load(f)

        st.session_state.session_df = (
            pd.read_csv(io.BytesIO(payload["df_csv"]))
            if payload.get("df_csv") is not None else None
        )
        st.session_state.session_df_filename  = payload.get("df_filename", "")
        st.session_state.analysis             = payload.get("analysis")
        st.session_state.result               = payload.get("result")
        st.session_state.processed_df = (
            pd.read_csv(io.BytesIO(payload["processed_df_csv"]))
            if payload.get("processed_df_csv") is not None else None
        )
        st.session_state.preprocessing_config = payload.get("preprocessing_config")

        # Rebuild the export reference files so Live Prediction works immediately
        if st.session_state.session_df is not None and st.session_state.preprocessing_config:
            os.makedirs("export", exist_ok=True)
            st.session_state.session_df.to_csv("export/reference_data.csv", index=False)
            with open("export/preprocessing_config.json", "w") as fh:
                json.dump(st.session_state.preprocessing_config, fh)

    except Exception:
        pass  # corrupt or old session file — start fresh silently