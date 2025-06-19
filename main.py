import streamlit as st
from app.chatbot import SocraticChatManager
from app.evaluation import ConversationEvaluator
from app.login import login
from app.database import save_conversation
import time  # For the timer
from app.leetprompt import LeetPromptSocraticChatManager

from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI()

app.include_router(api_router, prefix="/api")


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
        ],
        "LeetPrompt": [
            "Zero-Shot Basic Conversation",
            "One-Shot Simple Query",
            "Few-Shot Greeting Variations",
            "Zero-Shot Open Ended Question",
            "One-Shot Fact-Based Query",
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
    if "start_time" not in st.session_state:
        st.session_state.start_time = None  # To store the start time
    if "end_time" not in st.session_state:
        st.session_state.end_time = None  # To store the end time

    # 4. Select category first
    selected_category = st.selectbox("Choose a category:", list(categories.keys()))

    # 5. Then select topic based on category
    selected_topic = st.selectbox("Now choose a topic:", categories[selected_category])

    # 6. Start conversation
    if st.button("Start Conversation"):
        # For Critical Thinking, we handle it a bit differently
        if selected_category == "Critical Thinking":
            st.session_state.chatbot = SocraticChatManager(topic="Critical Thinking", category=selected_category)
        elif selected_category == "LeetPrompt":
            st.session_state.chatbot = LeetPromptSocraticChatManager(category=selected_category, topic=selected_topic)
        else:
            st.session_state.chatbot = SocraticChatManager(topic=selected_topic)

        st.session_state.conversation_active = True
        st.session_state.bot_intro = st.session_state.chatbot.bot_start()
        st.session_state.evaluation_result = None
        st.session_state.conversation_saved = False

        # Start the timer
        st.session_state.start_time = time.time()

    # 7. Conversation flow
    if st.session_state.conversation_active:
        # Calculate elapsed time
        elapsed_time = time.time() - st.session_state.start_time

        # Display the timer in the sidebar so it stays visible
        with st.sidebar:
            st.markdown(f"**Time Elapsed:** {elapsed_time:.2f} seconds")

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

                # End the timer when evaluation is clicked
                st.session_state.end_time = time.time()

                # Calculate the duration
                elapsed_time = st.session_state.end_time - st.session_state.start_time
                st.session_state.duration = elapsed_time  # Store the duration

                # Save the conversation along with the time to MongoDB
                conversation_data = {
                    "turns": st.session_state.chatbot.get_conversation_turns(),
                    "topic": selected_topic,
                    "category": selected_category,
                    "evaluation": st.session_state.evaluation_result,
                    "duration": st.session_state.duration  # Add duration here
                }

                save_conversation(
                    user_id=st.session_state.user,
                    selected_topic=selected_topic,
                    selected_category=selected_category,
                    evaluation_result=st.session_state.evaluation_result,
                    duration=st.session_state.duration  # Pass duration to MongoDB
                )

                st.rerun()

    # 9. Evaluation Display
    if st.session_state.evaluation_result:
        st.markdown("### Evaluation Summary")
        st.markdown(st.session_state.evaluation_result)

        # Display the duration of the conversation after evaluation
        st.markdown("### Time Taken")
        st.markdown(f"**Time Taken:** {st.session_state.duration:.2f} seconds")

        if not st.session_state.conversation_saved:
            conversation_data = {
                "turns": st.session_state.chatbot.get_conversation_turns(),
                "topic": selected_topic,
                "category": selected_category,
                "evaluation": st.session_state.evaluation_result,
                "duration": st.session_state.duration  # Store duration
            }

            # Update save_conversation call to include duration
            save_conversation(
                user_id=st.session_state.user,
                selected_topic=selected_topic,
                selected_category=selected_category,
                evaluation_result=st.session_state.evaluation_result,
                duration=st.session_state.duration  # Store duration in DB
            )

            st.session_state.conversation_saved = True
