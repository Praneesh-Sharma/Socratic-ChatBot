from config.settings import GROQ_API_KEY, MODEL_NAME
from langchain_groq import ChatGroq

class ConversationEvaluator:
    def __init__(self):
        self.llm = ChatGroq(api_key=GROQ_API_KEY, model_name=MODEL_NAME)

    def evaluate(self, conversation: str) -> str:
        prompt = f"""
            You are an expert Socratic evaluator for Generative AI education.

            Evaluate the following conversation between a Socratic mentor (EchoDeepak) and a student. Use the criteria below to assess the quality of the student’s responses. For each, give a score from 1 to 5 and a short, constructive comment.

            Evaluation Criteria:
            - **Clarity**: Was the student's explanation easy to follow and coherent?
            - **Depth**: Did they go beyond surface-level definitions to explore reasoning, implications, or challenges?
            - **Application**: Did they connect the concept to a real-world use case or startup scenario?
            - **Critical Thinking**: Did they reflect on assumptions, limitations, or offer counterpoints?
            - **Progression**: Did their understanding deepen as the conversation evolved?
            - **Relevance**: Did they remain on-topic and avoid fluff?
            - **Creativity**: Did they provide a fresh, original, or unique view?

            Conversation:
            {conversation}

            Respond with your feedback in the following format:

            Clarity: [score]/5 - [comment]  
            Depth: [score]/5 - [comment]  
            Application: [score]/5 - [comment]  
            Critical Thinking: [score]/5 - [comment]  
            Progression: [score]/5 - [comment]  
            Relevance: [score]/5 - [comment]  
            Creativity: [score]/5 - [comment]
            """
        return self.llm.invoke(prompt).content
