"""
styles/theme.py
───────────────
Design tokens and global CSS for AutoML Studio.
Supports dynamic switching between Light and Dark themes.
"""

import streamlit as st

# ─── Dark Theme Tokens ────────────────────────────────────────────────────────
DARK_THEME = {
    "bg":          "#080d1a",
    "bg2":         "#0d1425",
    "surface":     "#111c30",
    "card":        "#152038",
    "border":      "#1e3050",
    "cyan":        "#00d4ff",
    "cyan_dim":    "#00d4ff22",
    "violet":      "#8b5cf6",
    "violet_dim":  "#8b5cf620",
    "green":       "#10d494",
    "green_dim":   "#10d49420",
    "amber":       "#f59e0b",
    "red":         "#f43f5e",
    "text":        "#e2ecff",
    "muted":       "#6b82a8",
    "grid_line":   "rgba(0,212,255,0.03)",
    "plot_bg":     "#0d1425",
    "plot_paper":  "#111c30",
    "plot_tmpl":   "plotly_dark",
    "hero_bg":     "linear-gradient(135deg,#0d1425 0%,#111c30 60%,#0a0f1e 100%)",
    "hero_border": "#1e3050",
    "shadow_sm":   "0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)",
    "shadow_md":   "0 4px 12px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)",
    "shadow_blue": "0 4px 16px rgba(0,212,255,0.15)",
    "scrollbar":   "#1e3050",
    "scrollbar_hv": "#00d4ff",
}

# ─── Light Theme Tokens ───────────────────────────────────────────────────────
LIGHT_THEME = {
    "bg":          "#F8FAFC",
    "bg2":         "#F1F5F9",
    "surface":     "#EFF6FF",
    "card":        "#FFFFFF",
    "border":      "#E2E8F0",
    "cyan":        "#2563EB",
    "cyan_dim":    "#2563EB12",
    "violet":      "#6366F1",
    "violet_dim":  "#6366F112",
    "green":       "#059669",
    "green_dim":   "#05966912",
    "amber":       "#D97706",
    "red":         "#DC2626",
    "text":        "#0F172A",
    "muted":       "#64748B",
    "grid_line":   "rgba(37,99,235,0.04)",
    "plot_bg":     "#FFFFFF",
    "plot_paper":  "#F8FAFC",
    "plot_tmpl":   "simple_white",
    "hero_bg":     "linear-gradient(135deg,#EFF6FF 0%,#F8FAFC 55%,#EEF2FF 100%)",
    "hero_border": "#BFDBFE",
    "shadow_sm":   "0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04)",
    "shadow_md":   "0 4px 12px rgba(15,23,42,0.08), 0 2px 4px rgba(15,23,42,0.04)",
    "shadow_blue": "0 4px 16px rgba(37,99,235,0.15)",
    "scrollbar":   "#CBD5E1",
    "scrollbar_hv": "#2563EB",
}


def inject_css(theme_mode: str = "dark") -> None:
    """Inject the full global stylesheet mapped to the active theme mode."""
    T = DARK_THEME if theme_mode == "dark" else LIGHT_THEME
    
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── CSS Variables ── */
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
    --font-body:   'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
    --font-mono:   'IBM Plex Mono', 'Cascadia Code', monospace;
    --font-head:   'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    --shadow-sm:   {T['shadow_sm']};
    --shadow-md:   {T['shadow_md']};
    --shadow-blue: {T['shadow_blue']};
    --ease:        cubic-bezier(0.4,0,0.2,1);
}}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 16px !important;
}}
[data-testid="stAppViewContainer"]::before {{
    content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(var(--grid_line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid_line) 1px, transparent 1px);
    background-size: 56px 56px;
}}
[data-testid="stMain"] > div:first-child,
[data-testid="block-container"] {{
    position: relative; z-index: 1;
    padding-top: 2rem !important;
}}
#MainMenu, footer, header, [data-testid="stToolbar"] {{ display: none !important; }}

/* ── Text Inputs ── */
[data-testid="stTextInput"] input {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    padding: .65rem 1rem !important;
    transition: border-color .18s var(--ease), box-shadow .18s var(--ease) !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-dim) !important;
    outline: none !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: #94A3B8 !important; }}
[data-testid="stTextInput"] label {{
    color: var(--text) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: .01em !important;
    font-family: var(--font-body) !important;
    margin-bottom: 6px !important;
}}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {{
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    transition: border-color .2s var(--ease), box-shadow .2s var(--ease) !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: var(--cyan) !important;
    box-shadow: var(--shadow-blue) !important;
}}
[data-testid="stFileUploader"] section {{
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
}}
[data-testid="stFileUploader"] section:hover {{
    border-color: var(--cyan) !important;
    background: var(--cyan-dim) !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] {{
    background: transparent !important;
    color: var(--muted) !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {{
    color: var(--muted) !important;
    font-family: var(--font-body) !important;
}}
[data-testid="stFileUploader"] button {{
    background: var(--cyan) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
[data-testid="stFileUploader"] svg {{
    color: var(--cyan) !important;
    fill: var(--cyan) !important;
}}
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div {{
    background: var(--surface) !important;
    color: var(--muted) !important;
}}
[data-testid="stFileUploaderFile"] {{
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] > div:first-child {{
    background: var(--card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}}
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--muted) !important;
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border-radius: 9px !important;
    border: none !important;
    padding: .55rem 1.4rem !important;
    transition: all .18s var(--ease) !important;
    letter-spacing: .01em !important;
}}
button[data-baseweb="tab"]:hover {{
    color: var(--cyan) !important;
    background: var(--cyan-dim) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background: var(--cyan) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-blue) !important;
}}
[data-testid="stTabPanel"] {{
    background: transparent !important;
    border: none !important;
    padding-top: 1.5rem !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: var(--card) !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: .6rem 1.6rem !important;
    transition: all .18s var(--ease) !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stButton > button:hover {{
    background: var(--surface) !important;
    color: var(--cyan) !important;
    border-color: var(--cyan) !important;
    box-shadow: var(--shadow-blue) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="primary"] {{
    background: var(--cyan) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: .7rem 2rem !important;
    box-shadow: var(--shadow-blue) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: var(--violet) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px var(--violet-dim) !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
    background: var(--card) !important;
    border-radius: 12px !important;
    border: 2px solid var(--border) !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}}
[data-testid="stDataFrame"] table {{
    font-family: var(--font-mono) !important;
    font-size: 13px !important;
}}
[data-testid="stDataFrame"] thead tr th {{
    background: var(--surface) !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--border) !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    font-size: 11px !important;
    padding: 12px 14px !important;
    font-family: var(--font-body) !important;
}}
[data-testid="stDataFrame"] tbody tr td {{
    padding: 11px 14px !important;
    font-size: 13px !important;
    border-bottom: 1px solid var(--bg2) !important;
    color: var(--text) !important;
}}
[data-testid="stDataFrame"] tbody tr:hover td {{
    background: var(--cyan-dim) !important;
}}
[data-testid="stDataFrame"] tbody tr:last-child td {{
    border-bottom: none !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.2rem 1.4rem !important;
    transition: all .2s var(--ease) !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stMetric"]::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
}}
[data-testid="stMetric"]:hover {{
    border-color: var(--cyan) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}}
[data-testid="stMetricLabel"] {{
    color: var(--muted) !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 28px !important;
    font-weight: 500 !important;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border-left-width: 3px !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
    font-family: var(--font-body) !important;
    background: var(--card) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1.2rem 1.4rem !important;
}}
[data-testid="stAlert"] p {{
    margin: 0 !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div {{
    width: 100% !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    padding: .65rem 1rem !important;
    min-height: 42px !important;
    display: flex !important;
    align-items: center !important;
    transition: border-color .18s, box-shadow .18s !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
}}
[data-testid="stSelectbox"] > div > div div {{
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
}}
[data-testid="stSelectbox"] > div > div:hover {{
    border-color: var(--cyan) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
}}
[data-testid="stSelectbox"] > div > div:focus-within {{
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-dim), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    outline: none !important;
}}
[data-testid="stSelectbox"] label {{
    color: var(--text) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: .01em !important;
    font-family: var(--font-body) !important;
    margin-bottom: 8px !important;
    display: block !important;
}}
[data-testid="stSelectbox"] svg {{
    color: var(--text) !important;
    fill: var(--text) !important;
}}

/* ── Radio ── */
[data-testid="stRadio"] label {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 9px !important;
    padding: .5rem 1.2rem !important;
    cursor: pointer !important;
    color: var(--muted) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all .18s var(--ease) !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background: var(--surface) !important;
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    background: var(--surface) !important;
}}

/* ── Checkboxes ── */
[data-testid="stCheckbox"] label {{
    color: var(--text) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    font-family: var(--font-body) !important;
}}
[data-testid="stCheckbox"] label:hover {{ color: var(--cyan) !important; }}
[data-testid="stCheckbox"] span[role="checkbox"] {{
    background: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 5px !important;
}}
[data-testid="stCheckbox"] span[role="checkbox"][aria-checked="true"] {{
    background: var(--cyan) !important;
    border-color: var(--cyan) !important;
}}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div > div {{
    background: linear-gradient(90deg, var(--cyan), var(--violet)) !important;
    height: 4px !important;
    border-radius: 4px !important;
}}
[data-testid="stSlider"] [role="slider"] {{
    background: var(--cyan) !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
    border: 2px solid var(--card) !important;
    width: 18px !important;
    height: 18px !important;
}}
[data-testid="stSlider"] label {{
    color: var(--text) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}}

/* ── Number Input ── */
[data-testid="stNumberInput"] input {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 14px !important;
    border-radius: 9px !important;
    padding: .5rem .8rem !important;
}}

/* ── Download Button ── */
[data-testid="stDownloadButton"] > button {{
    background: var(--surface) !important;
    color: var(--violet) !important;
    border: 1.5px solid var(--violet-dim) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100% !important;
    padding: .7rem 1.2rem !important;
    transition: all .18s var(--ease) !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: var(--violet) !important;
    color: #fff !important;
    border-color: var(--violet) !important;
    box-shadow: var(--shadow-blue) !important;
    transform: translateY(-2px) !important;
}}

/* ── Forms ── */
[data-testid="stForm"] {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stFormSubmitButton"] > button {{
    background: var(--cyan) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 700 !important;
    padding: .65rem 2rem !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    transition: all .18s var(--ease) !important;
    box-shadow: var(--shadow-blue) !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    background: var(--violet) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px var(--violet-dim) !important;
}}

/* ── Dividers ── */
hr {{
    border: none !important;
    height: 2px !important;
    margin: 2rem 0 !important;
    background: linear-gradient(90deg, transparent, var(--border) 10%, var(--border) 90%, transparent) !important;
}}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-head) !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    line-height: 1.25 !important;
}}
h1 {{ font-size: 34px !important; }}
h2 {{ font-size: 28px !important; }}
h3 {{ font-size: 22px !important; }}
h4 {{ font-size: 18px !important; }}
p, li, span, label, .stMarkdown {{
    font-family: var(--font-body) !important;
    color: var(--text) !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}}
.stMarkdown p {{
    color: var(--text) !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}}

/* ── Charts & JSON ── */
[data-testid="stVegaLiteChart"] {{
    background: var(--card) !important;
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    padding: 1rem !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stJson"] {{
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    font-family: var(--font-mono) !important;
    font-size: 13px !important;
    color: #ffffff !important;
}}
[data-testid="stJson"] * {{
    color: #ffffff !important;
}}
[data-testid="stJson"] span {{
    color: #ffffff !important;
}}
[data-testid="stJson"] div {{
    color: #ffffff !important;
}}
[data-testid="stSpinner"] {{ color: var(--cyan) !important; }}
.js-plotly-plot .plotly {{ border-radius: 12px !important; }}

/* ── Scrollbars ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg2); border-radius: 6px; }}
::-webkit-scrollbar-thumb {{ background: {T['scrollbar']}; border-radius: 6px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['scrollbar_hv']}; }}
[data-testid="stAppViewContainer"] *, [data-testid="stMain"] * {{
    scrollbar-color: {T['scrollbar']} var(--bg2);
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: var(--card) !important;
    border-right: 1.5px solid var(--border) !important;
}}

/* ── Dropdown menus ── */
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-md) !important;
}}
[data-baseweb="menu"] li {{
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
}}
[data-baseweb="menu"] li:hover {{
    background: var(--surface) !important;
    color: var(--cyan) !important;
}}

/* ── Expanders ── */
[data-testid="stExpander"] {{
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stExpander"] summary {{
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}}
</style>
""", unsafe_allow_html=True)