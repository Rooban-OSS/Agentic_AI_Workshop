from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = MongoClient("mongodb+srv://roobanrihub:thisisthepassword@cluster0.yeygogo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["interview_panel_optimizer"]

jobs_collection = db["jobs"]
interviewers_collection = db["interviewers"]
candidates_collection = db["candidates"]
panels_collection = db["panels"]

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

