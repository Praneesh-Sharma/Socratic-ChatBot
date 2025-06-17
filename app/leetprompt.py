import streamlit as st
from langchain_groq import ChatGroq

# LeetPrompt Question Bank
leetprompt_questions = {
    "Zero-Shot Basic Conversation": {
        "title": "Zero-Shot Basic Conversation",
        "problem": """**Problem Description**
Write a zero-shot prompt to initiate a basic conversation with an AI chatbot.

**Evaluation Criteria**
The prompt should be clear, specific, and directly address the task without examples. It should focus on initiating a simple conversation.

**Examples**
**Good Example**
Start a conversation with an AI chatbot by greeting it and asking how it is doing.

**Bad Example**
Talk to the chatbot.""",
        "socratic_query": """
Evaluate this prompt using the Socratic method. Your goal is not to directly fix it, but to guide the user to improve their prompt.

Steps:
1. Briefly reflect on the clarity and specificity of the user input.
2. Ask the user a follow-up question to push them to think more critically or clearly.
3. Keep responses under 3 lines.
4. Always end with a question.
"""
    },
    "One-Shot Simple Query": {
        "title": "One-Shot Simple Query",
        "problem": """**Problem Description**
Write a one-shot prompt to ask an AI chatbot a simple question. Include one example in your prompt.

**Evaluation Criteria**
The prompt should include one clear example, demonstrate one-shot learning, and focus on asking a simple question.

**Examples**
**Good Example**
Explain photosynthesis in simple terms like you're talking to a 10-year-old. For example: "Imagine plants are like solar panels..." 

**Bad Example**
Explain photosynthesis.""",
        "socratic_query": """
You're a Socratic evaluator. Guide the user in refining their one-shot prompt. Focus on the clarity and usefulness of the example given. Never fix the prompt—just ask probing questions.
"""
    },
    "Few-Shot Greeting Variations": {
        "title": "Few-Shot Greeting Variations",
        "problem": """**Problem Description**
Create a few-shot prompt that demonstrates how an AI can respond to different greetings in a friendly and human-like way.

**Evaluation Criteria**
The prompt should include 2–3 examples showing varied greetings and friendly replies. Each pair should illustrate tone and phrasing.

**Examples**
**Good Example**
User: Hey there!  
AI: Hi! Nice to hear from you.

User: What's up?  
AI: Not much, just happy to chat with you!""",
        "socratic_query": """
Review the user’s prompt and ask a question that gets them to consider if their few-shot examples are varied and helpful. Encourage introspection.
"""
    },
    "Zero-Shot Open Ended Question": {
        "title": "Zero-Shot Open Ended Question",
        "problem": """**Problem Description**
Write a zero-shot prompt that asks the AI an open-ended question about the future of work and AI.

**Evaluation Criteria**
The prompt should not include examples but must be clearly open-ended and exploratory in nature.

**Examples**
**Good Example**
What changes do you anticipate in how people work as AI becomes more common?

**Bad Example**
Explain AI.""",
        "socratic_query": """
Challenge the user to think about what makes a question 'open-ended.' Ask Socratic-style questions to help them reframe their prompt if needed.
"""
    },
    "One-Shot Fact-Based Query": {
        "title": "One-Shot Fact-Based Query",
        "problem": """**Problem Description**
Write a one-shot prompt to ask an AI chatbot a fact-based question. Include one example in your prompt.

**Evaluation Criteria**
The prompt should include one clear example, demonstrate one-shot learning, and focus on asking a fact-based question.

**Examples**
**Good Example**
Ask the AI chatbot a fact-based question. Example: 'What is the capital of France?'

**Bad Example**
Ask a fact.""",
        "socratic_query": """
Guide the user to think about the factual clarity and formatting of their prompt. Ask if the format is clear enough to steer the AI response.
"""
    }
}

class LeetPromptSocraticChatManager:
    def __init__(self, category: str, topic: str):
        self.category = category
        self.topic = topic
        self.history = []
        self.llm = ChatGroq(
            api_key=st.secrets["GROQ_API_KEY"],
            model_name=st.secrets["MODEL_NAME"]
        )
        self.question_data = leetprompt_questions.get(topic)
        if not self.question_data:
            raise ValueError(f"Topic '{topic}' not found in LeetPrompt questions.")
        self.system_prompt = f"""
        You are EchoDeepak, a Socratic mentor helping users improve their prompt engineering skills.
        Never directly fix or rewrite the user’s input. Your role is to guide them by asking brief, layered Socratic questions.

        Use two techniques:
        - Clarify: Ask questions that reveal ambiguities, assumptions, or vagueness in the prompt.
        - Reflect: Ask questions that prompt users to connect the prompt to their own experiences, goals, or prior understanding.

        Keep responses concise and friendly. Avoid jargon.
        Always end your response with one single guiding question that invites deeper thinking or personal reflection.

        If the user input is unclear, ask them to clarify or provide examples.
        If the user asks for direct fixes, gently remind them that your role is to guide through questioning, not to give answers.

        If you dont understand something, feel free to ask for an explanation.
        """

    def bot_start(self) -> str:
        intro = f"You're working on the LeetPrompt: **{self.question_data['title']}**\n\n{self.question_data['problem']}"
        self.history.append({"user": "", "bot": intro})
        return intro

    def _format_chat(self, user_input: str):
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        messages.append({"role": "user", "content": f"{self.question_data['socratic_query']}\n\nUser Input:\n{user_input}"})
        return messages

    def user_reply(self, user_input: str) -> str:
        messages = self._format_chat(user_input)
        response = self.llm.invoke(messages).content.strip()
        self.history.append({"user": user_input, "bot": response})
        return response

    def get_conversation_turns(self):
        return self.history

    def get_full_conversation(self) -> str:
        return "\n\n".join(
            [f"Turn {i+1}:\nYou: {turn['user']}\nEchoDeepak: {turn['bot']}" for i, turn in enumerate(self.history)]
        )
