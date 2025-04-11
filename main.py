import streamlit as st
from app.chatbot import SocraticChatManager
from app.evaluation import ConversationEvaluator

# 1. Page setup
st.set_page_config(page_title="EchoDeepak: Socratic Approach", layout="centered")
st.title("EchoDeepak: Socratic Approach")

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

# 3. Session state initialization
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "conversation_active" not in st.session_state:
    st.session_state.conversation_active = False
if "bot_intro" not in st.session_state:
    st.session_state.bot_intro = ""
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None

# 4. Topic selection
selected_topic = st.selectbox("Select a Generative AI topic to explore:", topics)

# 5. Start conversation
if st.button("Start Conversation"):
    st.session_state.chatbot = SocraticChatManager(topic=selected_topic)
    st.session_state.conversation_active = True
    st.session_state.bot_intro = st.session_state.chatbot.bot_start()
    st.session_state.evaluation_result = None  # Reset previous eval

# 6. Conversation flow
if st.session_state.conversation_active:
    st.markdown("### Conversation")

    # Previous turns
    for turn in st.session_state.chatbot.get_conversation_turns():
        if turn['user']:  # Only show user input if it exists
            st.markdown(f"**You:** {turn['user']}")
        st.markdown("---")  # Visual separator
        st.markdown(f"**EchoDeepak:** {turn['bot']}")

    # User input
    user_input = st.text_input("Your response:", key="user_input")

    if user_input:
        bot_reply = st.session_state.chatbot.user_reply(user_input)

        # Display current turn immediately
        st.markdown(f"**You:** {user_input}")
        st.markdown("---")
        st.markdown(f"**EchoDeepak:** {bot_reply}")

        st.session_state.pop("user_input", None)  # Clear input safely
        st.rerun()

    # Trigger evaluation after last turn
    if st.session_state.chatbot.is_finished() and not st.session_state.evaluation_result:
        st.success("Conversation complete! Evaluating your responses...")
        evaluator = ConversationEvaluator()
        convo_text = st.session_state.chatbot.get_full_conversation()
        st.session_state.evaluation_result = evaluator.evaluate(convo_text)
        st.rerun()

    # Display evaluation
    if st.session_state.evaluation_result:
        st.markdown("### Evaluation Summary")
        st.markdown(st.session_state.evaluation_result)
