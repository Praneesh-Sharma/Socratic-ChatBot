import streamlit as st
from langchain_groq import ChatGroq

class ConversationEvaluator:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=st.secrets["GROQ_API_KEY"],
            model_name=st.secrets["MODEL_NAME"]
            )

    def evaluate(self, conversation: str) -> str:
        prompt = f"""
            You are an expert Socratic evaluator for Generative AI education.

            Evaluate the following conversation between a Socratic mentor (EchoDeepak) and a student. For each evaluation criterion, give a score from 1 to 5. Then provide detailed, constructive feedback that includes:
            
            1. What was specifically lacking, unclear, or incorrect in the student's responses.
            2. Why this is a problem or how it hinders learning.
            3. How the student could improve or the right way to answer the question.
            
            Evaluation Criteria:
            - Clarity: Was the student's explanation easy to follow and coherent? Reference exact phrases or examples.
            - Depth: Did they explore reasoning beyond surface-level definitions? Provide examples of missed opportunities.
            - Application: Did they connect the concept to real-world use cases? Suggest better connections if missing.
            - Critical Thinking: Did they reflect on assumptions or counterpoints? Point out gaps and how to improve.
            - Progression: Did their understanding evolve? Note stagnation or repetition.
            - Relevance: Did they stay on-topic? Highlight any off-topic or filler responses.
            - Creativity: Did they offer original insights? Suggest ways to deepen creativity.
            
            Also, identify any hallucinations or unsupported claims and explain why they should be avoided.
            
            Important: Base your evaluation strictly on the conversation content. Do not add or infer information not present.
            
            Conversation:
            {conversation}
            
            Respond with your feedback in the following format:
            
            Clarity: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions]  
            Depth: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions]  
            Application: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions]  
            Critical Thinking: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions]  
            Progression: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions]  
            Relevance: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions]  
            Creativity: [score]/5 - [detailed feedback with examples, issues, and improvement suggestions] 
            """
        return self.llm.invoke(prompt).content
