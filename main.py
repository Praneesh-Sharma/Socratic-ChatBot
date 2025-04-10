import streamlit as st
from app.chatbot import SocraticChatManager

# 1. Page setup
st.set_page_config(page_title="EchoDeepak: Socratic Mentor", layout="centered")
st.title("EchoDeepak: Socratic GenAI Mentor")

# 2. Topic selection
topics = [
    "Prompt Engineering",
    "Few-shot / One-shot / Chain-of-Thought",
    "LangChain / LlamaIndex",
    "Retrieval-Augmented Generation (RAG)",
    "Hallucinations in LLMs",
    "Responsible AI",
    "Agents and Automation",
    "GenAI Use Cases",
    "Ethics and Risks"
]

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "conversation_active" not in st.session_state:
    st.session_state.conversation_active = False
if "bot_intro" not in st.session_state:
    st.session_state.bot_intro = ""

selected_topic = st.selectbox("Select a Generative AI topic to explore:", topics)

# 3. Start conversation only on button click
if st.button("Start Conversation"):
    st.session_state.chatbot = SocraticChatManager(topic=selected_topic)
    st.session_state.conversation_active = True
    st.session_state.bot_intro = st.session_state.chatbot.bot_start()

# 4. Conversation flow
if st.session_state.conversation_active:
    st.markdown("### Conversation")

    # Show the first Socratic question (intro)
    if st.session_state.bot_intro and st.session_state.chatbot.turn == 1:
        st.markdown(f"**EchoDeepak:** {st.session_state.bot_intro}")

    # Show previous turns (if any)
    for turn in st.session_state.chatbot.get_conversation_turns():
        st.markdown(f"**You:** {turn['user']}")
        st.markdown("---")  # Visual separator
        st.markdown(f"**EchoDeepak:** {turn['bot']}")

    # User input
    user_input = st.text_input("Your response:", key="user_input")

    if user_input:
        bot_reply = st.session_state.chatbot.user_reply(user_input)

        # Display the current interaction
        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**EchoDeepak:** {bot_reply}")

        # Safely clear the input field
        st.session_state.pop("user_input", None)
        st.rerun()

    if st.session_state.chatbot.is_finished():
        st.success("Conversation complete. You may now evaluate your responses.")

    if st.button("Evaluate My Understanding"):
        st.info("Evaluation feature coming soon...")
