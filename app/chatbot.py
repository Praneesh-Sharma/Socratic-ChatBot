import random
import streamlit as st
from langchain_groq import ChatGroq

def get_system_prompt(topic: str) -> str:
    return f"""
        You are EchoDeepak, a Socratic mentor on the topic of {topic}.
        You never give direct answers. You guide the student through probing, layered questions.

        Style:
        - Responses should be brief (1–3 lines max)
        - Friendly and encouraging
        - Avoids jargon and complexity
        - Ends each message with 1 question
        - After each response, display the statement: "If you don’t understand something, feel free to ask for an explanation."
        - If the user types "I don't understand" or similar, provide a simple, clear description of the concept in an approachable way, helping the user grasp the core idea.

        Goals:
        - Challenge assumptions
        - Ask for real-world examples
        - Encourage clarity and reasoning
        - Explore consequences, comparisons, counterpoints
        
        If the user starts to drift off-topic, gently steer them back to the topic of {topic}.
        If the user provides a vague or unclear response, ask them to clarify or elaborate.
    """

class SocraticChatManager:
    def __init__(self, topic: str, category: str = None, max_use_case_length: int = 500):
        self.topic = topic
        self.category = category
        self.max_use_case_length = max_use_case_length  # Max length of the generated use case
        self.history = []  # List of dicts: {"user": ..., "bot": ...}
        self.llm = ChatGroq(
            api_key=st.secrets["GROQ_API_KEY"],
            model_name=st.secrets["MODEL_NAME"]
        )
        self.system_prompt = get_system_prompt(self.topic)
        self.use_case = None  # Will store the hypothetical use case for Critical Thinking topics

    def _format_chat(self):
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        return messages

    def generate_use_case(self) -> str:
        prompt = f"""
        First, you display the definition of the {self.topic}, then write what kind of answers you expect from the user.

        Generate a brief hypothetical scenario (under 100 words) where critical thinking is essential in the context of "{self.topic}".
        The scenario should:
        - Involve real-world decision-making
        - Highlight multiple possible approaches or trade-offs
        - Be concise, engaging, and easy to follow
        Format as a conversation starter. Keep word count to 100
        """
        messages = [{"role": "system", "content": prompt}]
        response = self.llm.invoke(messages).content.strip()
        return response

    def bot_start(self) -> str:
        if not self.history:
            self.use_case = self.generate_use_case()
            bot_msg = self.use_case
            self.history.append({"user": "", "bot": bot_msg})  # store the first question
            return bot_msg
        return ""

    def user_reply(self, user_input: str) -> str:
        messages = self._format_chat()
        messages.append({"role": "user", "content": user_input})
        response = self.llm.invoke(messages).content.strip()
        self.history.append({"user": user_input, "bot": response})
        return response

    def get_full_conversation(self) -> str:
        return "\n\n".join(
            [f"Turn {i+1}:\nYou: {turn['user']}\nEchoDeepak: {turn['bot']}" for i, turn in enumerate(self.history)]
        )

    def get_conversation_turns(self):
        return self.history
