from config.settings import GROQ_API_KEY, MODEL_NAME
from langchain_groq import ChatGroq

class ConversationEvaluator:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=MODEL_NAME
        )

    def evaluate(self, topic: str, full_conversation: str) -> str:
        system_prompt = f"""
You are an expert Socratic mentor tasked with evaluating a student's conversational performance on the topic: {topic}.

Your job is to reflect on their responses and provide:
- A brief summary of their understanding (clarity, misconceptions)
- Strengths in their reasoning or critical thinking
- Suggestions for deeper reflection or learning

Use a kind, constructive tone. Keep the response under 150 words.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_conversation}
        ]

        response = self.llm.invoke(messages).content
        return response
