from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, List
from pymongo import MongoClient
from datetime import datetime
import os

import uuid

from app.chatbot import SocraticChatManager
from app.leetprompt import LeetPromptSocraticChatManager
from app.evaluation import ConversationEvaluator

router = APIRouter()

# Temporary in-memory session store (replace with Redis or DB later)
chat_sessions: Dict[str, dict] = {}

client = MongoClient("mongodb+srv://Praneesh:Prawns(101)!@cluster0.gsn128t.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client["chat-database"]
api_collection = db["api"]
conversation_collection = db["api"]

# Categories and topics
categories: Dict[str, List[str]] = {
    "Generative AI": [
        "Prompt Engineering",
        "Few-shot / One-shot / Chain-of-Thought",
        "LangChain / LlamaIndex",
        "Retrieval-Augmented Generation (RAG)",
        "Hallucinations in LLMs",
        "Responsible AI",
        "Agents and Automation",
        "GenAI Use Cases",
        "Ethics and Risks"
    ],
    "Professional Development": [
        "Positive Attitude at Work",
        "Professionalism in the Workplace",
        "Time Management & Meeting Deadlines",
        "Effective Team Collaboration",
        "Handling Feedback and Talking to Seniors",
        "Behavior and Communication in a Company",
        "Owning and Contributing to Projects"
    ],
    "Critical Thinking": [
        "Data Abstraction",
        "Model Testing",
        "Data Cleaning",
        "Validation",
        "Data Transformation",
        "Model Deployment",
        "Data Integration",
        "Feature Engineering"
    ]
}

# Pydantic models
class PredefinedConversationRequest(BaseModel):
    category: str
    topic: str  # required
    user_email: str # required


class CustomConversationRequest(BaseModel):
    custom_topic: str  # required
    user_email: str # required


class UserMessageRequest(BaseModel):
    user_email: str
    message: str

class EvaluateConversationRequest(BaseModel):
    session_id: str

# Endpoint: Get categories and topics
@router.get("/categories")
def get_categories():
    return categories

@router.post("/start_predefined_conversation")
def start_predefined_conversation(req: PredefinedConversationRequest):
    if req.category not in categories:
        raise HTTPException(status_code=400, detail="Invalid category")
    if req.topic not in categories[req.category]:
        raise HTTPException(status_code=400, detail="Topic does not match the selected category")

    chatbot = (
        LeetPromptSocraticChatManager(topic=req.topic, category=req.category)
        if req.category == "LeetPrompt"
        else SocraticChatManager(topic=req.topic, category=req.category)
    )
    
    session_id = str(uuid.uuid4())
    
    # Initialize the chatbot and get the introduction message
    bot_intro = chatbot.bot_start()
    initial_conversation = [{"sender": "bot", "message": bot_intro}]
    
    chat_sessions[session_id] = {
        "chatbot": chatbot,
        "category": req.category,
        "topic": req.topic,
        "user_email": req.user_email,
        "conversation": []
    }
    
    # Save to MongoDB immediately
    conversation_collection.insert_one({
        "session_id": session_id,
        "user_email": req.user_email,
        "conversation": initial_conversation
    })
    
    return {"session_id": session_id, "bot_intro": bot_intro}


@router.post("/start_custom_conversation")
def start_custom_conversation(req: CustomConversationRequest):

    chatbot = SocraticChatManager(topic=req.custom_topic)

    session_id = str(uuid.uuid4())
    bot_intro = chatbot.bot_start()
    initial_conversation = [{"sender": "bot", "message": bot_intro}]
    
    chat_sessions[session_id] = {
        "chatbot": chatbot,
        "topic": req.custom_topic,
        "user_email": req.user_email,
        "conversation": []
    }
    
    conversation_collection.insert_one({
        "session_id": session_id,
        "user_email": req.user_email,
        "conversation": initial_conversation
    })

    return {"session_id": session_id, "bot_intro": bot_intro}


# Endpoint: Send message
@router.post("/send_message/{session_id}")
def send_message(session_id: str, req: UserMessageRequest):
    session = chat_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    chatbot = session["chatbot"]
    reply = chatbot.user_reply(req.message)

    session["conversation"] = chatbot.get_conversation_turns()
    session["user_email"] = req.user_email

    try:
        api_collection.insert_one({
            "session_id": session_id,
            "user_email": req.user_email,
            "timestamp": datetime.utcnow(),
            "message": {
                "user": req.message,
                "bot": reply
            },
            "category": session.get("category"),
            "topic": session.get("topic")
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "bot_reply": reply,
        "conversation": session["conversation"]
    }


@router.post("/evaluate/{session_id}")
def evaluate_conversation(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]

    conversation = session.get("conversation", [])
    if not conversation:
        raise HTTPException(status_code=400, detail="No conversation to evaluate")

    evaluator = ConversationEvaluator()
    evaluation = evaluator.evaluate(conversation)

    return {"evaluation": evaluation}

@router.get("/conversations/{user_email}")
def get_user_conversations(user_email: str):
    try:
        results = list(conversation_collection.find(
            {"user_email": user_email},
            {"_id": 0}  # exclude MongoDB's internal ID if not needed
        ))
        return {"conversations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/conversation")
def get_conversation_by_user_and_session(user_email: str, session_id: str):
    try:
        conversation = list(api_collection.find({
            "user_email": user_email,
            "session_id": session_id
        }))
        for msg in conversation:
            msg["_id"] = str(msg["_id"])  # Convert ObjectId to string for JSON serialization

        if not conversation:
            raise HTTPException(status_code=404, detail="No conversation found for given user_email and session_id")

        return {"conversation": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")
