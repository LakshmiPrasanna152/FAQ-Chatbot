import streamlit as st
from openai import OpenAI
import uuid
import os
import requests

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

from auth import login, signup
from history import load as load_history, save as save_session
from domains import DOMAINS

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# OPENROUTER CLIENT
# =========================================================

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# =========================================================
# GOOGLE CONFIG
# =========================================================

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8501"

client_config = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="FAQ Chatbot",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f4f8ff;
    }

    section[data-testid="stSidebar"] {
        background-color: #dbeafe;
    }

    .stButton button {
        background-color: #2563eb;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #1d4ed8;
    }

    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
    }

    h1, h2, h3 {
        color: #1e3a8a;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SESSION STATE
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

# =========================================================
# GOOGLE LOGIN FUNCTION
# =========================================================
def google_login():

    flow = Flow.from_client_config(
        client_config,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        redirect_uri=REDIRECT_URI,
    )

    # IMPORTANT FIX
    flow.autogenerate_code_verifier = False

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    st.session_state["oauth_state"] = state

    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0; url={auth_url}">
        """,
        unsafe_allow_html=True
    )
# =========================================================
# HANDLE GOOGLE REDIRECT
# =========================================================

query_params = st.query_params

if "code" in query_params:

    try:

        flow = Flow.from_client_config(
            client_config,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            state=st.session_state.get("oauth_state"),
            redirect_uri=REDIRECT_URI,
        )

        # IMPORTANT FIX
        flow.autogenerate_code_verifier = False

        flow.fetch_token(
            code=query_params["code"]
        )

        credentials = flow.credentials

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={
                "access_token": credentials.token
            }
        ).json()

        st.session_state.user = {
            "email": user_info["email"],
            "name": user_info["name"]
        }

        st.query_params.clear()

        st.success("Google Login Successful!")

        st.rerun()

    except Exception as e:
        st.error(f"Google Login Error: {str(e)}")

# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if not st.session_state.user:

    st.title("🤖 FAQ Chatbot")

    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    # =====================================================
    # SIGN IN
    # =====================================================

    with tab1:

        st.subheader("Sign In")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Sign In"):

            ok, name = login(email, password)

            if ok:

                st.session_state.user = {
                    "email": email,
                    "name": name
                }

                st.success("Login Successful!")

                st.rerun()

            else:
                st.error("Invalid Email or Password")

        st.markdown("### OR")

        if st.button(
            "Continue with Google",
            key="google_signin"
        ):
            google_login()

    # =====================================================
    # SIGN UP
    # =====================================================

    with tab2:

        st.subheader("Create Account")

        fullname = st.text_input(
            "Full Name",
            key="signup_name"
        )

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account"):

            ok, msg = signup(
                fullname,
                signup_email,
                signup_password
            )

            if ok:

                st.success(
                    "Account Created Successfully! Please Sign In."
                )

            else:
                st.error(msg)

        st.markdown("### OR")

        if st.button(
            "Continue with Google ",
            key="google_signup"
        ):
            google_login()

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        f"## 👤 {st.session_state.user['name']}"
    )

    st.caption(
        st.session_state.user["email"]
    )

    if st.button("+ New Chat"):

        st.session_state.sid = str(uuid.uuid4())
        st.session_state.messages = []

        st.rerun()

    if st.button("Sign Out"):

        st.session_state.clear()

        st.rerun()

    st.divider()

    st.subheader("Chat History")

    history = load_history(
        st.session_state.user["email"]
    )

    for sid, chat in sorted(
        history.items(),
        key=lambda x: -x[1]["ts"]
    ):

        title = chat.get(
            "title",
            "New Chat"
        )[:30]

        if st.button(title, key=sid):

            st.session_state.sid = sid
            st.session_state.messages = chat["messages"]
            st.session_state.domain = chat["domain"]

            st.rerun()

# =========================================================
# CHAT SESSION
# =========================================================

if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "domain" not in st.session_state:
    st.session_state.domain = "All Topics"

# =========================================================
# DOMAIN SELECT
# =========================================================

domain = st.selectbox(
    "Select Domain",
    list(DOMAINS.keys()),
    index=list(DOMAINS.keys()).index(
        st.session_state.domain
    )
)

st.session_state.domain = domain

# =========================================================
# DISPLAY MESSAGES
# =========================================================

for msg in st.session_state.messages:

    if msg["role"] != "system":

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask your question..."
)

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = client.chat.completions.create(

                    model="openai/gpt-3.5-turbo",

                    messages=[

                        {
                            "role": "system",
                            "content":
                            f"""
                            You are a professional FAQ chatbot.

                            Use ONLY the following data:

                            {DOMAINS[domain]}

                            Rules:
                            - Answer only what user asked
                            - Keep answer short
                            - Do not show full dictionary
                            - Give natural human answers
                            """
                        }

                    ] + [

                        {
                            "role": m["role"],
                            "content": m["content"]
                        }

                        for m in st.session_state.messages
                        if m["role"] != "system"
                    ],

                    temperature=0.5
                )

                reply = response.choices[0].message.content

            except Exception as e:

                reply = f"Error: {str(e)}"

            st.write(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # =====================================================
    # SAVE CHAT HISTORY
    # =====================================================

    title = prompt[:40]

    save_session(
        st.session_state.user["email"],
        st.session_state.sid,
        st.session_state.messages,
        domain,
        title
    )

    st.rerun()