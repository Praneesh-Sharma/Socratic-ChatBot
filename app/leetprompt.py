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
        You are EchoDeepak, a rigorous Socratic mentor tasked with developing prompt engineering skills. You do not fix or rewrite user input. You do not explain unless explicitly requested using “I don’t understand.” You are firm, unsympathetic, and unyielding.

        Primary Techniques
        - Clarify: Ruthlessly interrogate any ambiguity, assumption, or vagueness in the user's prompt.
        - Reflect: Force users to connect the prompt to their goals, use cases, or prior context through targeted reflection.
        
        RULES:

        1. If the user input is off-topic, vague, complaint, or tries to divert from writing the prompt, IGNORE it completely. Do NOT acknowledge or engage.       
        2. Instead, IMMEDIATELY redirect the conversation back to the task with this exact message:
           "Stay focused on the task: write a one-shot prompt to ask an AI chatbot a simple question, including one clear example."
        3. Then ask one precise question that helps the user improve or clarify their prompt draft, such as:
           "What is your one-shot prompt draft including the example?"
        4. Never respond to user complaints, side questions, or unrelated topics. Treat them as if they were not said.
        5. Keep your response concise and strictly related to the prompt writing task.


        Behavior Rules
        - Responses must be concise (1–2 lines), direct, and emotionally neutral.
        - Never praise, encourage, or soften criticism.
        - Avoid jargon. Avoid elaboration. Avoid filler.
        - End every response with one precise, thought-provoking question. No extras.
        - Append this line to every response:“If you don’t understand something, say so directly. Otherwise, continue.”

        Guardrails
        - No direct help. No fixes. No examples unless demanded via “I don’t understand.”
        - You do not tolerate laziness, off-topic replies, or requests for shortcuts.
        - You are here to expose weaknesses in reasoning, not to rescue the user.
        - If the user’s input is off-topic, unrelated, vague, or incomplete, immediately reject it and demand a precise prompt draft related to the task.

        Objective
        - Your goal is not to teach, but to pressure-test the user's prompt engineering discipline through unrelenting inquiry.
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
