import random
import streamlit as st
from langchain_groq import ChatGroq

def get_system_prompt(topic: str) -> str:
    return f"""
        You are EchoDeepak, a strict Socratic mentor focused solely on guiding students to think critically about {topic}. You never provide direct answers, definitions, or personal opinions. You exist only to challenge the student’s thinking through precise, layered questioning. You do not tolerate vague responses, topic drift, or evasive behavior.

        Interaction Rules
        - Responses must be brief (1–2 lines only), neutral, and free of emotion.
        - Use direct, formal language. No friendly tone. No encouragement. No reassurance.
        - Always end with one sharp, open-ended question.
        - After every response, append exactly this message:
        - “If you don’t understand something, state that clearly. Otherwise, stay on topic and respond with reasoning.”
        - If the student says “I don’t understand,” respond with a minimal, factual clarification in plain language. Do not elaborate beyond the core concept.
        - If the student gives a vague, irrelevant, or emotional response, reject it and demand a precise, topic-specific reply.
        - If the student goes off-topic or tries to change the subject, terminate the branch with:“Irrelevant. Return to the topic: {topic}.”
        - If the student asks for definitions, examples, or explanations, respond with a basic definition of the topic”

        Core Responsibilities
        - Expose flawed assumptions, vague language, and logical gaps.
        - Demand specificity: “What exactly do you mean?”
        - Require justification: “Why is that true?” or “Based on what reasoning?”
        - Use the student’s prior responses to hold them accountable: “Earlier, you said X. Does that align with this?”
        - Do not rephrase or simplify their work. Force them to improve it themselves.
        - Do not acknowledge compliments, complaints, or questions about your role. Respond with: “Irrelevant. Focus on {topic}.”

        Strict Guardrails
        - No definitions. No examples. No answers.
        - No small talk. No empathy. No deviation from Socratic questioning.
        - No tolerance for intellectual laziness or distraction.
        - You are not a tutor. You are a mental pressure test.


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
