import random
import streamlit as st
from langchain_groq import ChatGroq

# Hypothetical use cases for Critical Thinking topics
USE_CASES = {
    "Data Abstraction": "Imagine you're working with a large dataset of customer reviews. How would you approach abstracting relevant features for further analysis?",
    "Model Testing": "You have trained a machine learning model for classifying emails as spam or not. What steps would you take to test the model's performance and ensure it's accurate?",
    "Data Cleaning": "You're analyzing a dataset with missing values and outliers. What strategies would you employ to clean this data before analysis?",
    "Validation": "You're about to deploy an AI model in production. How do you validate that it will perform well in real-world scenarios?",
    "Data Transformation": "Consider a scenario where raw data needs to be transformed into a suitable format for analysis. What steps would you take to transform the data effectively?",
    "Model Deployment": "You're tasked with deploying a machine learning model into a live environment. What considerations must you take into account during deployment?",
    "Data Integration": "You're combining data from multiple sources to create a comprehensive dataset. What challenges do you foresee in data integration and how would you tackle them?",
    "Feature Engineering": "You're developing a machine learning model and need to select the best features. How do you decide which features are the most important for the model?",
}

def get_system_prompt(topic: str) -> str:
    return f"""
        You are EchoDeepak, a Socratic mentor on the topic of {topic}.
        You never give direct answers. You guide the student through probing, layered questions.

        Style:
        - Responses should be brief (1–3 lines max)
        - Friendly and encouraging
        - Avoids jargon and complexity
        - Ends each message with 1 question

        Goals:
        - Challenge assumptions
        - Ask for real-world examples
        - Encourage clarity and reasoning
        - Explore consequences, comparisons, counterpoints
        
        If the user starts to drift off-topic, gently steer them back to the topic of {topic}.
        If the user provides a vague or unclear response, ask them to clarify or elaborate.
        """

class SocraticChatManager:
    def __init__(self, topic: str, max_turns: int = 6):
        self.topic = topic
        self.max_turns = max_turns
        self.history = []  # List of dicts: {"user": ..., "bot": ...}
        self.turn = 0
        self.llm = ChatGroq(
            api_key=st.secrets["GROQ_API_KEY"],
            model_name=st.secrets["MODEL_NAME"]
        )
        self.system_prompt = get_system_prompt(topic)
        self.use_case = None  # Will store the hypothetical use case for Critical Thinking topics

    def _format_chat(self):
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        return messages

    def bot_start(self) -> str:
        if self.turn == 0:
            self.turn += 1

            # Check if it's a Critical Thinking topic
            if self.topic == "Critical Thinking":
                # Select a random use case related to Critical Thinking
                self.use_case = random.choice(list(USE_CASES.values()))
                bot_msg = f"Let's explore a hypothetical scenario related to Critical Thinking:\n\n{self.use_case}\n\nWhat would be your approach to tackle this problem?"
            else:
                # For other topics, continue with the usual Socratic questioning
                bot_msg = f"Let's begin our exploration of {self.topic}. What comes to your mind when you hear this topic?"
            
            self.history.append({"user": "", "bot": bot_msg})  # store the first question
            return bot_msg
        return ""

    def user_reply(self, user_input: str) -> str:
        if self.turn >= self.max_turns:
            return "This concludes our discussion. You can now review your responses."

        messages = self._format_chat()
        messages.append({"role": "user", "content": user_input})

        response = self.llm.invoke(messages).content.strip()
        self.history.append({"user": user_input, "bot": response})
        self.turn += 1
        return response

    def is_finished(self) -> bool:
        return self.turn >= self.max_turns

    def get_full_conversation(self) -> str:
        return "\n\n".join(
            [f"Turn {i+1}:\nYou: {turn['user']}\nEchoDeepak: {turn['bot']}" for i, turn in enumerate(self.history)]
        )

    def get_conversation_turns(self):
        return self.history
