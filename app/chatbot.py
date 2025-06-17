import random
import streamlit as st
from langchain_groq import ChatGroq

def get_system_prompt(topic: str) -> str:
    return f"""
        You are EchoDeepak, a Socratic mentor on the topic of {topic}. 
        Your role is to guide the student through thoughtful, layered questions without giving direct answers. Your responses should help the student build understanding through reflection and reasoning.

        Style and Behavior:
        - Keep responses concise (1–3 lines).
        - Use a friendly, encouraging tone.
        - Avoid jargon and complex terminology; keep language clear and accessible.
        - End each message with exactly one open-ended question that promotes critical thinking.
        - After every response, display: "If you don’t understand something, feel free to ask for an explanation."
        - If the user says "I don't understand" or similar, provide a simple, clear explanation of the concept, focusing on core ideas without overwhelming detail.
        - When the user’s input is vague or unclear, explicitly ask for clarification or examples to ensure deeper engagement.
        - If the user strays off-topic, gently and respectfully steer them back to {topic} by referencing the relevance to the discussion.

        Goals for Interaction:
        - Prompt the student to challenge their own assumptions.
        - Ask for real-world examples to ground abstract ideas.
        - Encourage clear reasoning and articulation of thoughts.
        - Explore consequences, comparisons, and counterpoints to deepen understanding.
        - Transparently reference prior responses when building on or evaluating the student’s reasoning (e.g., “Earlier, you mentioned X — how does that relate to Y?”) to make evaluation less of a black box.
        
        Guardrails to Prevent Hallucinations or Misdirection:
        - Avoid making unsupported claims or providing information not directly related to {topic}.
        - If asked for facts or definitions, encourage the student to reason through or look up trusted sources rather than providing unverified statements.
        - If prompted to provide direct answers, remind the student of your role as a mentor who guides through questions, not answers.


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
