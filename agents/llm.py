import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()

# ChatGroq is LangChain's chat-model wrapper for Groq; Groq is used here for fast,
# low-latency LLM reasoning in routing and conversational response generation.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)
