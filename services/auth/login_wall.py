import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_profile_card():
    username = st.session_state.get("username", "User")
    user_id = st.session_state.get("user_id", "")

    st.sidebar.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 8px;
        ">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="
                    width:40px; height:40px;
                    border-radius:50%;
                    background: linear-gradient(135deg, #f5a623, #00d4ff);
                    display:flex; align-items:center; justify-content:center;
                    font-size:18px; font-weight:bold; color:#000;
                    flex-shrink:0;
                ">
                    {username[0].upper()}
                </div>
                <div>
                    <div style="font-weight:600; font-size:15px; color:#eee;">
                        {username}
                    </div>
                    <div style="font-size:11px; color:#666;">
                        ID: {user_id}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    st.markdown(
        """
        <div style="text-align:center; padding: 40px 0 20px;">
            <div style="font-size: 56px;">🏋️‍♂️</div>
            <h1 style="font-size:2rem; margin-bottom:4px;">fitMentor AI</h1>
            <p style="color:#888; font-size:1rem;">
                Real-time AI GYM Coach — enter a username to begin
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="e.g. princekhunt",
                label_visibility="collapsed",
            )
            submit_button = st.form_submit_button(
                "▶  Start Session", use_container_width=True
            )

        if submit_button:
            if not username.strip():
                st.error("Username cannot be empty.")
                return False

            user = get_or_create_user(username.strip())
            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]
            st.rerun()

    return False