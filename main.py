import streamlit as st
from app.chatbot import SocraticChatManager
from app.evaluation import ConversationEvaluator
from app.login import login
from app.database import save_conversation

# 1. Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. If not logged in, call the login function
if not st.session_state.logged_in:
    user = login()  # This calls the login function from login.py
    if user:
        # If login is successful, proceed to the chatbot interface
        st.session_state.user = user
else:
    # If logged in, proceed with the chatbot functionality
    st.set_page_config(page_title="EchoDeepak: Socratic Approach", layout="centered")
    st.title("EchoDeepak: Socratic Approach")

    # Categories and Topics (including Critical Thinking)
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
        ],
        "Critical Thinking": [
            "Data Abstraction",
            "Model Testing",
            "Data Cleaning",
            "Validation",
            "Data Transformation",
            "Model Deployment",
            "Data Integration",
            "Feature Engineering"
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
    if "conversation_saved" not in st.session_state:
        st.session_state.conversation_saved = False

    # 4. Select category first
    selected_category = st.selectbox("Choose a category:", list(categories.keys()))

    # 5. Then select topic based on category
    selected_topic = st.selectbox("Now choose a topic:", categories[selected_category])

    # 6. Start conversation
    if st.button("Start Conversation"):
        # For Critical Thinking, we handle it a bit differently
        if selected_category == "Critical Thinking":
            st.session_state.chatbot = SocraticChatManager(topic="Critical Thinking", category=selected_category)
        else:
            st.session_state.chatbot = SocraticChatManager(topic=selected_topic)

        st.session_state.conversation_active = True
        st.session_state.bot_intro = st.session_state.chatbot.bot_start()
        st.session_state.evaluation_result = None
        st.session_state.conversation_saved = False

    # 7. Conversation flow
    if st.session_state.conversation_active:
        st.markdown("### Conversation")

        # Show previous turns
        for turn in st.session_state.chatbot.get_conversation_turns():
            if turn['user']:
                st.markdown(f"**You:** {turn['user']}")
            st.markdown("---")
            st.markdown(f"**EchoDeepak:** {turn['bot']}")

        # Display text input field
        user_input = st.text_area("Your response:", key="user_input", height=100)

        # Display 'Next' button for conversation progression
        if st.button("Next") and user_input.strip():
            bot_reply = st.session_state.chatbot.user_reply(user_input)

            # Display current turn immediately
            st.markdown(f"**You:** {user_input}")
            st.markdown("---")
            st.markdown(f"**EchoDeepak:** {bot_reply}")

            # Clear input manually
            del st.session_state["user_input"]
            st.rerun()

    # 8. Evaluation Button
    if st.session_state.conversation_active and len(st.session_state.chatbot.get_conversation_turns()) > 0:
        if st.button("Evaluate my responses"):
            if not st.session_state.evaluation_result:
                evaluator = ConversationEvaluator()
                convo_text = st.session_state.chatbot.get_full_conversation()
                st.session_state.evaluation_result = evaluator.evaluate(convo_text)
                st.rerun()

    # 9. Evaluation Display
    if st.session_state.evaluation_result:
        st.markdown("### Evaluation Summary")
        st.markdown(st.session_state.evaluation_result)

        if not st.session_state.conversation_saved:
            conversation_data = {
                "turns": st.session_state.chatbot.get_conversation_turns(),
                "topic": selected_topic,
                "category": selected_category,
                "evaluation": st.session_state.evaluation_result
            }

            # Save conversation data
            save_conversation(
                user_id=st.session_state.user,
                selected_topic=selected_topic,
                selected_category=selected_category,
                evaluation_result=st.session_state.evaluation_result
            )

            st.session_state.conversation_saved = True
