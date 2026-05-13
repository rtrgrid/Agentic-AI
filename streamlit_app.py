import time
import streamlit as st

from app.agent import ask_agent


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Autonomous AI Agent",
    page_icon="🤖",
    layout="centered"
)


# ---------------------------------------------------
# CSS
# ---------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0b0f19;
    color: white;
    font-family: Inter, sans-serif;
}

/* Main width */
.block-container {
    max-width: 850px;
    padding-top: 2rem;
}

/* Title */
.title {
    font-size: 42px;
    font-weight: 800;
    color: #7c3aed;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 2rem;
}

/* Chat bubbles */
.user-box {
    background: #1e293b;
    padding: 16px;
    border-radius: 18px;
    margin-top: 20px;
    margin-bottom: 10px;
    border: 1px solid #334155;
}

.assistant-box {
    background: #111827;
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 25px;
    border: 1px solid #1f2937;
    line-height: 1.8;
}

/* Code */
pre {
    background-color: #020617 !important;
    border-radius: 14px;
    padding: 18px;
    overflow-x: auto;
    border: 1px solid #334155;
}

code {
    color: #60a5fa !important;
}

/* Headers */
h1, h2, h3 {
    color: #a78bfa;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Input */
.stChatInputContainer {
    background-color: #0b0f19;
}

/* Remove toolbar */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown(
    """
    <div class="title">
        🤖 Autonomous Multi-Agent Research Agent
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Gemini 2.0 Flash • RAG • Critique Loop • Multi-Agent System
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("⚡ Features")

    st.markdown("""
    ✅ RAG Pipeline  
    ✅ FAISS Retrieval  
    ✅ Web Search  
    ✅ Financial Tool  
    ✅ News Agent (A2A)  
    ✅ Critique Loop  
    ✅ Canvas Generation  
    """)

    st.write("---")

    max_iterations = st.slider(
        "Critique Iterations",
        1,
        5,
        2
    )

    st.write("---")

    st.subheader("💡 Suggested Queries")

    st.markdown("""
    - Latest AI news today  
    - Generate markdown report on AI trends  
    - What are Bitcoin risks?  
    - Compare Amazon and AI startup culture  
    - Write scalable scheduler in Python  
    """)


# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------
# DISPLAY CHAT
# ---------------------------------------------------

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class="user-box">
            🧑 <b>You</b><br><br>
            {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        with st.container():

            st.markdown(
                """
                <div class="assistant-box">
                🤖 <b>Agent</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(msg["content"])


# ---------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------

query = st.chat_input(
    "Ask your autonomous AI agent..."
)


# ---------------------------------------------------
# GENERATE RESPONSE
# ---------------------------------------------------

if query:

    # Save user msg
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    # Show user
    st.markdown(
        f"""
        <div class="user-box">
        🧑 <b>You</b><br><br>
        {query}
        </div>
        """,
        unsafe_allow_html=True
    )

    response_container = st.empty()

    full_response = ""

    with st.spinner("Running autonomous research workflow..."):

        try:

            response = ask_agent(
                query,
                max_iterations=max_iterations
            )

            # Stream response
            for chunk in response.split():

                full_response += chunk + " "

                response_container.markdown(
                    f"""
                    <div class="assistant-box">
                    🤖 <b>Agent</b><br><br>
                    {full_response}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                time.sleep(0.015)

            # Final markdown render
            response_container.markdown(response)

            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as e:

            st.error(str(e))