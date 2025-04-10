from config.settings import GROQ_API_KEY, MODEL_NAME
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

Goals:
- Challenge assumptions
- Ask for real-world examples
- Encourage clarity and reasoning
- Explore consequences, comparisons, counterpoints
"""

class SocraticChatManager:
    def __init__(self, topic: str, max_turns: int = 6):
        self.topic = topic
        self.max_turns = max_turns
        self.history = []  # List of dicts: {"user": ..., "bot": ...}
        self.turn = 0
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=MODEL_NAME
        )
        self.system_prompt = get_system_prompt(topic)

    def _format_chat(self):
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        return messages

    def bot_start(self) -> str:
        if self.turn == 0:
            self.turn += 1
            return f"Let's begin our exploration of {self.topic}. What comes to your mind when you hear this topic?"
        return ""

    def user_reply(self, user_input: str) -> str:
        if self.turn >= self.max_turns:
            return "This concludes our discussion. You can now review or evaluate your responses."

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
