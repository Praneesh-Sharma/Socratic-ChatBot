import datetime
from pymongo import MongoClient
import streamlit as st

# Access MongoDB URI from Streamlit secrets (works for both local and cloud)
mongo_uri = st.secrets["mongodb"]["uri"]

# Connect to MongoDB
client = MongoClient(mongo_uri)

# Access the database and collection
db = client["chatbot_database"]  # Replace with your database name
conversations_collection = db["conversations"]  # Collection to store conversations

def save_conversation(user_id, selected_topic, selected_category, evaluation_result):
    # Prepare the conversation data
    conversation_data = {
        "turns": st.session_state.chatbot.get_conversation_turns(),  # Store the conversation turns
        "topic": selected_topic,  # Store the selected topic
        "category": selected_category,  # Store the selected category
        "evaluation": evaluation_result  # Store the evaluation result
    }

    # Prepare the document to insert into MongoDB
    conversation_doc = {
        "user_id": user_id,  # Store user ID
        "conversation_data": conversation_data,  # Store conversation data
        "timestamp": datetime.datetime.utcnow()  # Store the timestamp in UTC
    }

    # Insert the conversation into MongoDB
    conversations_collection.insert_one(conversation_doc)
