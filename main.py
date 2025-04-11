import streamlit as st
from app.chatbot import SocraticChatManager
from app.evaluation import ConversationEvaluator

print("🚀 Starting Streamlit App")

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

    # Show previous turns
    for turn in st.session_state.chatbot.get_conversation_turns():
        if turn['user']:
            st.markdown(f"**You:** {turn['user']}")
        st.markdown("---")
        st.markdown(f"**EchoDeepak:** {turn['bot']}")

    # Check if conversation is finished
    if st.session_state.chatbot.is_finished():
        st.success(" The conversation is complete. EchoDeepak has no further questions.")
        st.markdown("Have a look at your **evaluation summary below** 👇")

        if not st.session_state.evaluation_result:
            evaluator = ConversationEvaluator()
            convo_text = st.session_state.chatbot.get_full_conversation()
            st.session_state.evaluation_result = evaluator.evaluate(convo_text)
            st.rerun()

    else:
        # Only show input if conversation still active
        user_input = st.text_input("Your response:", key="user_input")

        if user_input.strip():  # Avoid blank submits
            bot_reply = st.session_state.chatbot.user_reply(user_input)

            # Display current turn immediately
            st.markdown(f"**You:** {user_input}")
            st.markdown("---")
            st.markdown(f"**EchoDeepak:** {bot_reply}")

            # Clear input manually to prevent stale value
            del st.session_state["user_input"]
            st.rerun()

# Show evaluation at the bottom (after rerun completes)
if st.session_state.evaluation_result:
    st.markdown("### Evaluation Summary")
    st.markdown(st.session_state.evaluation_result)
