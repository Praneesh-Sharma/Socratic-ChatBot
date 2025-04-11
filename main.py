import streamlit as st
from app.chatbot import SocraticChatManager
from app.evaluation import ConversationEvaluator

# 1. Page setup
st.set_page_config(page_title="EchoDeepak: Socratic Approach", layout="centered")
st.title("EchoDeepak: Socratic Approach")

# 2. Categories and Topics
categories = {
    "Generative AI": [
        "Prompt Engineering",
        "Few-shot / One-shot / Chain-of-Thought",
        "LangChain / LlamaIndex",
        "Retrieval-Augmented Generation (RAG)",
        "Hallucinations in LLMs",
        "Responsible AI",
        "Agents and Automation",
        "GenAI Use Cases",
        "Ethics and Risks"
    ],
    "Professional Development": [
        "Positive Attitude at Work",
        "Professionalism in the Workplace",
        "Time Management & Meeting Deadlines",
        "Effective Team Collaboration",
        "Handling Feedback and Talking to Seniors",
        "Behavior and Communication in a Company",
        "Owning and Contributing to Projects"
    ]
}

# 3. Session state initialization
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "conversation_active" not in st.session_state:
    st.session_state.conversation_active = False
if "bot_intro" not in st.session_state:
    st.session_state.bot_intro = ""
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None

# 4. Select category first
selected_category = st.selectbox("Choose a category:", list(categories.keys()))

# 5. Then select topic based on category
selected_topic = st.selectbox("Now choose a topic:", categories[selected_category])

# 6. Start conversation
if st.button("Start Conversation"):
    st.session_state.chatbot = SocraticChatManager(topic=selected_topic)
    st.session_state.conversation_active = True
    st.session_state.bot_intro = st.session_state.chatbot.bot_start()
    st.session_state.evaluation_result = None  # Reset previous eval

# 7. Conversation flow
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
        st.success("The conversation is complete. EchoDeepak has no further questions.")
        st.markdown("Have a look at your **evaluation summary below** 👇")

        if not st.session_state.evaluation_result:
            evaluator = ConversationEvaluator()
            convo_text = st.session_state.chatbot.get_full_conversation()
            st.session_state.evaluation_result = evaluator.evaluate(convo_text)
            st.rerun()

    else:
        # Only show input if conversation still active
        user_input = st.text_area("Your response:", key="user_input", height=100)

        if user_input.strip():
            bot_reply = st.session_state.chatbot.user_reply(user_input)

            # Display current turn immediately
            st.markdown(f"**You:** {user_input}")
            st.markdown("---")
            st.markdown(f"**EchoDeepak:** {bot_reply}")

            # Clear input manually
            del st.session_state["user_input"]
            st.rerun()

# 8. Evaluation
if st.session_state.evaluation_result:
    st.markdown("### Evaluation Summary")
    st.markdown(st.session_state.evaluation_result)
