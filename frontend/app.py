import os
import uuid

import requests
import streamlit as st

DEFAULT_API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)


st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="🎧",
    layout="centered",
)


# ── Session state ─────────────────────────────────────────────────────────────

def initialize_session_state() -> None:
    if "token" not in st.session_state:
        st.session_state.token = None

    if "username" not in st.session_state:
        st.session_state.username = None

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "waiting_for_human" not in st.session_state:
        st.session_state.waiting_for_human = False

    if "interrupt_data" not in st.session_state:
        st.session_state.interrupt_data = None


# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def fetch_thread_history(api_url: str, thread_id: str) -> dict:
    try:
        response = requests.get(
            f"{api_url}/support/{thread_id}/history",
            headers=get_auth_headers(),
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return {
        "messages": [],
        "waiting_for_human": False,
        "interrupt_data": None,
    }


def load_thread(api_url: str, thread_id: str) -> None:
    st.session_state.thread_id = thread_id
    history = fetch_thread_history(api_url, thread_id)
    st.session_state.messages = history.get("messages", [])
    st.session_state.waiting_for_human = history.get("waiting_for_human", False)
    st.session_state.interrupt_data = history.get("interrupt_data")

def fetch_user_threads(api_url: str) -> list[dict]:
    try:
        response = requests.get(
            f"{api_url}/support/threads",
            headers=get_auth_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    default_tid = f"customer-{st.session_state.username}"
    return [{"thread_id": default_tid, "title": "Main Conversation"}]

def do_login(api_url: str, username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.session_state.username = username
            load_thread(api_url, f"customer-{username}")
            return True
        return False
    except requests.RequestException:
        return False


def do_register(api_url: str, username: str, password: str) -> tuple[bool, str]:
    try:
        response = requests.post(
            f"{api_url}/auth/register",
            json={"username": username, "password": password},
            timeout=10,
        )
        if response.status_code == 201:
            st.session_state.token = response.json()["access_token"]
            st.session_state.username = username
            load_thread(api_url, f"customer-{username}")
            return True, "Registered successfully."
        detail = response.json().get("detail", "Registration failed.")
        return False, detail
    except requests.RequestException as e:
        return False, f"Connection error: {e}"


def do_logout() -> None:
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.thread_id = None
    st.session_state.messages = []
    st.session_state.waiting_for_human = False
    st.session_state.interrupt_data = None


def start_new_conversation(api_url: str) -> None:
    prefix = st.session_state.username or "user"
    new_id = f"customer-{prefix}-{uuid.uuid4().hex[:6]}"
    load_thread(api_url, new_id)

# ── API calls ─────────────────────────────────────────────────────────────────

def submit_support_request(
    api_url: str,
    thread_id: str,
    message: str,
) -> dict:
    response = requests.post(
        f"{api_url}/support",
        json={
            "thread_id": thread_id,
            "message": message,
        },
        headers=get_auth_headers(),
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def resume_support_request(
    api_url: str,
    thread_id: str,
    human_response: str,
) -> dict:
    response = requests.post(
        f"{api_url}/support/resume",
        json={
            "thread_id": thread_id,
            "human_response": human_response,
        },
        headers=get_auth_headers(),
        timeout=60,
    )

    response.raise_for_status()

    return response.json()

    
# ── Login page ────────────────────────────────────────────────────────────────

def show_login_page(api_url: str) -> None:
    st.title("🔐 Customer Support Agent")
    st.caption("Please log in or create an account to continue.")
    st.divider()

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.form_submit_button("Login", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Enter both username and password.")
                elif do_login(api_url, username, password):
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_register:
        with st.form("register_form"):
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
            if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Fill out all fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = do_register(api_url, new_user, new_pass)
                    if ok:
                        st.rerun()
                    else:
                        st.error(msg)

# ── Main app ──────────────────────────────────────────────────────────────────

initialize_session_state()

# Sidebar — always visible
with st.sidebar:
    api_url = st.text_input(
        "API URL",
        value=DEFAULT_API_URL,
    )

    if st.session_state.token:
        st.divider()

        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            start_new_conversation(api_url)
            st.rerun()

        st.caption("RECENT CHATS")

        user_threads = fetch_user_threads(api_url)
        thread_ids = [t["thread_id"] for t in user_threads]

        # If in a brand new chat, show it at the top instead of resetting
        if st.session_state.thread_id and st.session_state.thread_id not in thread_ids:
            user_threads.insert(0, {
                "thread_id": st.session_state.thread_id,
                "title": "New Chat",
            })
            thread_ids.insert(0, st.session_state.thread_id)
        elif not st.session_state.thread_id and thread_ids:
            st.session_state.thread_id = thread_ids[0]

        for t in user_threads:
            tid = t["thread_id"]
            title = t.get("title") or "Conversation"
            is_active = (tid == st.session_state.thread_id)
            label = f"{'👉 ' if is_active else '💬 '}{title}"
            if st.button(
                label,
                key=f"chat_btn_{tid}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                load_thread(api_url, tid)
                st.rerun()

        st.divider()

        st.caption(f"Logged in as **{st.session_state.username}**")
        if st.button("Logout", use_container_width=True):
            do_logout()
            st.rerun()


# Route: login or app
if not st.session_state.token:
    show_login_page(api_url)

else:
    st.title("🎧 Customer Support Agent")
    st.caption(
        "LangGraph-powered customer support with hybrid routing, "
        "specialized workflows, persistence, and human escalation."
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.waiting_for_human:
        interrupt_data = st.session_state.interrupt_data or {}

        st.warning("This request requires human support review.")

        with st.expander(
            "View escalation details",
            expanded=True,
        ):
            st.write(
                "Customer Message:",
                interrupt_data.get("customer_message", "Unknown"),
            )

            st.write(
                "Intent:",
                interrupt_data.get("intent", "unknown"),
            )

            st.write(
                "Escalation Reason:",
                interrupt_data.get("escalation_reason", "unknown"),
            )

            diagnostic_result = interrupt_data.get("diagnostic_result")

            if diagnostic_result:
                st.write(
                    "Diagnostic Result:",
                    diagnostic_result,
                )

        st.subheader("Human Support Review")

        human_response = st.text_area(
            "Human Support Response",
            placeholder="Enter the human support response...",
        )

        if st.button(
            "Resume Workflow",
            type="primary",
            use_container_width=True,
        ):
            if not human_response.strip():
                st.warning("Enter a human support response.")
            else:
                try:
                    with st.spinner("Resuming workflow..."):
                        result = resume_support_request(
                            api_url=api_url,
                            thread_id=st.session_state.thread_id,
                            human_response=human_response.strip(),
                        )

                    response_text = result.get("response")

                    if response_text:
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response_text,
                            }
                        )

                    st.session_state.waiting_for_human = False
                    st.session_state.interrupt_data = None

                    st.rerun()

                except requests.RequestException as exc:
                    st.error(f"API request failed: {exc}")

    if not st.session_state.waiting_for_human:
        customer_message = st.chat_input(
            "Describe your support issue..."
        )

        if customer_message:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": customer_message,
                }
            )

            try:
                with st.spinner("Processing support request..."):
                    result = submit_support_request(
                        api_url=api_url,
                        thread_id=st.session_state.thread_id,
                        message=customer_message,
                    )

                if result["status"] == "completed":
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": result["response"],
                        }
                    )

                elif result["status"] == "human_review_required":
                    st.session_state.waiting_for_human = True
                    st.session_state.interrupt_data = result["interrupt_data"]

                st.rerun()

            except requests.RequestException as exc:
                st.error(f"API request failed: {exc}")