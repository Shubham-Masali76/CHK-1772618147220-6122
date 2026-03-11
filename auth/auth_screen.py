"""
auth/auth_screen.py
────────────────────
Login and registration UI for AutoML Studio.

Renders a centred auth card with Sign In / Create Account tabs.
Calls firebase_auth for credential validation and session_manager
to restore saved progress on successful login.
"""

import streamlit as st

from auth.firebase_auth   import login_user, register_user
from auth.session_manager import load_user_session
from styles.theme         import T


def render_auth_screen() -> None:
    """Render the full authentication screen (login + register)."""
    _, centre, _ = st.columns([1, 1.2, 1])

    with centre:
        # ── Logo + Title ──────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:2.5rem;">
            <div style="
                display:inline-flex;align-items:center;justify-content:center;
                width:56px;height:56px;
                background:linear-gradient(135deg,{T['cyan']},{T['violet']});
                border-radius:16px;
                box-shadow:0 4px 20px rgba(37,99,235,0.22);
                font-family:'IBM Plex Mono',monospace;font-weight:500;
                font-size:1rem;color:#fff;margin-bottom:1rem;
            ">ML</div>
            <div style="
                font-family:'Plus Jakarta Sans',sans-serif;font-size:2.1rem;font-weight:800;
                background:linear-gradient(90deg,{T['text']} 20%,{T['cyan']} 65%,{T['violet']} 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                letter-spacing:-.02em;line-height:1.1;
            ">AutoML Studio</div>
            <div style="color:{T['muted']};font-size:.925rem;
                font-family:'Plus Jakarta Sans',sans-serif;margin-top:.4rem;">
                Your personal machine learning workspace
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tab switcher ──────────────────────────────────────────────────
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
            <div style="background:{T['card']};border:1.5px solid {T['border']};
                border-radius:16px;padding:1.8rem 2rem 1.6rem;
                box-shadow:0 1px 3px rgba(15,23,42,0.06);">
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;
                    color:{T['text']};font-size:1.15rem;margin-bottom:1.4rem;">
                    Welcome back
                </div>
            """, unsafe_allow_html=True)

            login_username = st.text_input(
                "Username", key="login_user", placeholder="Enter your username"
            )
            login_password = st.text_input(
                "Password", key="login_pass",
                placeholder="Enter your password", type="password"
            )
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

            if st.button("Sign In", key="do_login", type="primary", use_container_width=True):
                ok, msg = login_user(login_username, login_password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username  = login_username.strip()
                    load_user_session(login_username.strip())
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown(f"""
                <div style="text-align:center;margin-top:1.2rem;
                    font-family:'Plus Jakarta Sans',sans-serif;font-size:.9rem;color:{T['muted']};">
                    No account yet?
                    <span style="color:{T['cyan']};font-weight:600;">
                        Use the Create Account tab above.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Register Form ─────────────────────────────────────────────────
        else:
            st.markdown(f"""
            <div style="background:{T['card']};border:1.5px solid {T['border']};
                border-radius:16px;padding:1.8rem 2rem 1.6rem;
                box-shadow:0 1px 3px rgba(15,23,42,0.06);">
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;
                    color:{T['text']};font-size:1.15rem;margin-bottom:1.4rem;">
                    Create your account
                </div>
            """, unsafe_allow_html=True)

            reg_username  = st.text_input(
                "Username", key="reg_user",
                placeholder="Choose a username (min 3 chars)"
            )
            reg_password  = st.text_input(
                "Password", key="reg_pass",
                placeholder="Choose a password (min 6 chars)", type="password"
            )
            reg_password2 = st.text_input(
                "Confirm Password", key="reg_pass2",
                placeholder="Re-enter your password", type="password"
            )
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

            if st.button(
                "Create Account", key="do_register",
                type="primary", use_container_width=True
            ):
                if reg_password != reg_password2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(reg_username, reg_password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username  = reg_username.strip()
                        load_user_session(reg_username.strip())
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown(f"""
                <div style="text-align:center;margin-top:1.2rem;
                    font-family:'Plus Jakarta Sans',sans-serif;font-size:.9rem;color:{T['muted']};">
                    Already have an account?
                    <span style="color:{T['cyan']};font-weight:600;">
                        Use the Sign In tab above.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;margin-top:2rem;
            font-family:'IBM Plex Mono',monospace;font-size:.82rem;color:{T['border']};">
            AutoML Studio · All rights reserved
        </div>
        """, unsafe_allow_html=True)