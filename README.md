# 🤖 Socratic Chatbot for Generative AI

This is a Streamlit-based interactive chatbot that guides users through key concepts in Generative AI using the Socratic method. Instead of providing direct answers, the bot asks thought-provoking questions to deepen your understanding and critical thinking.



## 🚀 Features

- 🧠 **Topic-based Socratic Dialogue**  
  Explore advanced GenAI topics like RAG, hallucinations, agents, and more.

- 💬 **Conversation History**  
  View a clear record of both your responses and chatbot's prompts.

- 🧪 **Automatic Evaluation**  
  Once the conversation ends, receive a summary evaluating your reasoning and insights.



## 📚 Topics Covered

- Prompt Engineering  
- Few-shot / One-shot / Chain-of-Thought  
- LangChain / LlamaIndex  
- Retrieval-Augmented Generation (RAG)  
- Hallucinations in LLMs  
- Responsible AI  
- Agents and Automation  
- GenAI Use Cases  
- Ethics and Risks



## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Praneesh-Sharma/Socratic-ChatBot.git
   cd Socratic-ChatBot
   ```

2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run main.py
   ```


## 📁 Project Structure
```bash
SOCRATIC-CHATBOT/
├── app/
│   ├── __pycache__/
│   ├── chatbot.py
│   └── evaluation.py
│
├── .streamlit/
│   ├── secrets.toml
│
├── venv/
│   └── ... (virtual environment files)
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```


## 🔐 Secrets Configuration

To use the app, create a `.streamlit/secrets.toml` file in the project root with the following content:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
MODEL_NAME = "mixtral-8x7b-32768"
```
