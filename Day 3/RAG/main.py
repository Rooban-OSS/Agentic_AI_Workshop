import os
import fitz
import tempfile
import streamlit as st
import google.generativeai as genai
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
import glob
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import re
import shutil

# === Config ===
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "AIzaSyCsgO_aaQyeGygSq76sH3M456R2E9ruUAQ")

# Documents folder path - modify this to your documents folder path
DOCUMENTS_FOLDER = "documents"  # Change this to your folder path

# === Helper Functions ===
class ImprovedEmbeddings:
    """Improved embedding function using TF-IDF for better semantic similarity"""
    
    def __init__(self):
        self.vectorizer = None
        self.is_fitted = False
        
    def embed_documents(self, texts):
        """Embed a list of documents"""
        # Clean and preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Initialize and fit TF-IDF vectorizer if not already fitted
        if not self.is_fitted:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,  # Limit features for efficiency
                stop_words='english',
                ngram_range=(1, 2),  # Include unigrams and bigrams
                min_df=1,  # Minimum document frequency
                max_df=0.95  # Maximum document frequency
            )
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            self.is_fitted = True
        else:
            tfidf_matrix = self.vectorizer.transform(processed_texts)
        
        # Convert to dense arrays and normalize
        embeddings = []
        for i in range(tfidf_matrix.shape[0]):
            vector = tfidf_matrix[i].toarray().flatten()
            # Add some randomness to avoid identical vectors
            vector = vector + np.random.normal(0, 0.001, vector.shape)
            embeddings.append(vector.tolist())
        
        return embeddings
    
    def embed_query(self, text):
        """Embed a single query"""
        if not self.is_fitted:
            # If vectorizer is not fitted, return a random vector
            return np.random.random(1000).tolist()
        
        processed_text = self._preprocess_text(text)
        tfidf_vector = self.vectorizer.transform([processed_text])
        vector = tfidf_vector.toarray().flatten()
        return vector.tolist()
    
    def _preprocess_text(self, text):
        """Clean and preprocess text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Convert to lowercase
        text = text.lower()
        return text

def get_pdf_files_from_folder(folder_path):
    """Get all PDF files from the specified folder"""
    if not os.path.exists(folder_path):
        return []
    
    pdf_pattern = os.path.join(folder_path, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    return pdf_files

def extract_text_from_pdf_path(file_path):
    """Extract text from PDF file path with minimal logging"""
    try:
        doc = fitz.open(file_path)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            try:
                page_text = page.get_text()
                if page_text.strip():  # Only add non-empty pages
                    text_parts.append(page_text)
            except Exception:
                continue
        
        doc.close()
        full_text = "\n\n".join(text_parts)
        return full_text
        
    except Exception:
        return ""

def extract_text_from_uploaded_file(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Extract text
        text = extract_text_from_pdf_path(tmp_file_path)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return text
    except Exception:
        return ""

def chunk_text(text, filename=""):
    """Split text into chunks without metadata"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # Increased chunk size for better context
        chunk_overlap=100,  # More overlap for continuity
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Better separators
    )
    
    chunks = splitter.split_text(text)
    
    # Return clean chunks without metadata
    improved_chunks = []
    for chunk in chunks:
        if len(chunk.strip()) > 50:  # Only keep meaningful chunks
            improved_chunks.append(chunk.strip())
    
    return improved_chunks

def store_chunks_in_chroma(chunks, persist_dir):
    """Store text chunks in Chroma vector database silently"""
    embeddings = ImprovedEmbeddings()
    
    # Filter out empty chunks
    valid_chunks = [chunk for chunk in chunks if len(chunk.strip()) > 30]
    
    if not valid_chunks:
        raise ValueError("No valid chunks to store")
    
    vectordb = Chroma.from_texts(
        texts=valid_chunks, 
        embedding=embeddings, 
        persist_directory=persist_dir
    )
    
    return vectordb

def search_similar_chunks(query, vectordb, k=8):
    """Search for similar chunks and return clean context"""
    try:
        # Get more results and filter them
        results = vectordb.similarity_search(query, k=k*2)
        
        # Remove duplicate or very similar chunks
        unique_results = []
        seen_content = set()
        
        for doc in results:
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
            if content_hash not in seen_content:
                unique_results.append(doc)
                seen_content.add(content_hash)
            
            if len(unique_results) >= k:
                break
        
        # Combine the results with simple separation
        context_parts = []
        for doc in unique_results:
            context_parts.append(doc.page_content)
        
        combined_context = "\n\n".join(context_parts)
        return combined_context
        
    except Exception:
        return ""

def ask_gemini(context, question):
    """Ask Gemini AI with improved prompt engineering"""
    try:
        # Enhanced prompt for better responses
        prompt = f"""You are a helpful assistant that answers questions based on provided context. 

IMPORTANT INSTRUCTIONS:
1. Answer based ONLY on the provided context
2. Provide a comprehensive, detailed answer that fully addresses the question
3. Include relevant examples, explanations, and details from the context
4. Structure your answer with proper paragraphs for readability
5. If the context contains multiple relevant points, address them all
6. If the context doesn't contain enough information, clearly state what information is missing
7. Be thorough and informative – aim for brief but clear responses. Do not use HTML or Markdown tags (like <sub>, <sup>, <strong>, etc.) in your response. Instead, represent superscripts and subscripts in plain text (e.g., W_Q^i)
8. Do NOT include any chunk references, numbers, or metadata in your response
9. Answer in a conversational tone as if you're chatting with the user – make it friendly, clear, and engaging. Avoid sounding like a textbook or purely technical paper.
10. Make sure your answer is substantial and informative (aim for at least 3–4 sentences minimum)
11. Avoid bullet points unless specifically requested. Use short paragraphs instead.
12. When explaining technical concepts, use analogies or intuitive explanations where possible to help the user understand better.

CONTEXT:
{context}

QUESTION: {question}

Please provide a detailed and comprehensive answer:"""

        # Try different model names in order of preference
        model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                # Check if response is meaningful
                if response.text and len(response.text.strip()) > 10:
                    return response.text.strip()
                else:
                    return "I received an empty response. Please try rephrasing your question."
                    
            except Exception as model_error:
                if "not found" in str(model_error).lower() and model_name != model_names[-1]:
                    continue  # Try next model
                else:
                    raise model_error
                    
    except Exception as e:
        return f"Error generating response: {str(e)}. Please check your API key and try again."

def load_documents_from_folder():
    """Load and process all PDF documents from the documents folder silently"""
    pdf_files = get_pdf_files_from_folder(DOCUMENTS_FOLDER)
    
    if not pdf_files:
        return None, []
    
    all_chunks = []
    processed_files = []
    
    for pdf_file in pdf_files:
        try:
            filename = os.path.basename(pdf_file)
            text = extract_text_from_pdf_path(pdf_file)
            
            if text.strip():  # Only process if text was extracted
                chunks = chunk_text(text, filename)
                
                if chunks:  # Only add if chunks were created
                    all_chunks.extend(chunks)
                    processed_files.append(filename)
                    
        except Exception:
            continue
    
    return all_chunks, processed_files

def process_uploaded_files(uploaded_files):
    """Process uploaded PDF files"""
    all_chunks = []
    processed_files = []
    
    for uploaded_file in uploaded_files:
        try:
            filename = uploaded_file.name
            text = extract_text_from_uploaded_file(uploaded_file)
            
            if text.strip():  # Only process if text was extracted
                chunks = chunk_text(text, filename)
                
                if chunks:  # Only add if chunks were created
                    all_chunks.extend(chunks)
                    processed_files.append(filename)
                    
        except Exception:
            continue
    
    return all_chunks, processed_files

def clear_documents_folder():
    """Clear all files from the documents folder"""
    if os.path.exists(DOCUMENTS_FOLDER):
        shutil.rmtree(DOCUMENTS_FOLDER)
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'vectordb' not in st.session_state:
        st.session_state.vectordb = None
    if 'indexed' not in st.session_state:
        st.session_state.indexed = False
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = None
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False
    # New session state for controlling auto-initialization
    if 'use_folder_docs' not in st.session_state:
        st.session_state.use_folder_docs = True

def auto_initialize_documents():
    """Auto-initialize documents if they exist in folder and are enabled"""
    # Only auto-initialize if use_folder_docs is True
    if not st.session_state.use_folder_docs:
        return
        
    pdf_files = get_pdf_files_from_folder(DOCUMENTS_FOLDER)
    if pdf_files and not st.session_state.indexed:
        with st.spinner("Initializing documents..."):
            try:
                # Load documents from folder
                all_chunks, processed_files = load_documents_from_folder()
                
                if all_chunks:
                    # Create a temporary directory that persists during the session
                    if st.session_state.temp_dir is None:
                        st.session_state.temp_dir = tempfile.mkdtemp()
                    
                    st.session_state.vectordb = store_chunks_in_chroma(
                        all_chunks, 
                        st.session_state.temp_dir
                    )
                    st.session_state.indexed = True
                    st.session_state.processed_files = processed_files
                    st.session_state.show_upload = False
                    
            except Exception:
                st.session_state.indexed = False
                st.session_state.show_upload = True

def display_chat_history():
    """Display chat history in a conversational format"""
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        # User message
        with st.chat_message("user"):
            st.write(question)
        
        # Assistant message
        with st.chat_message("assistant"):
            st.write(answer)

def add_to_chat_history(question, answer):
    """Add question and answer to chat history"""
    st.session_state.chat_history.append((question, answer))

# === Streamlit UI ===
st.set_page_config(page_title="PDF Chat Assistant", layout="wide")

# Initialize session state
initialize_session_state()

# Auto-initialize documents
auto_initialize_documents()

# Header
st.title("💬 PDF Chat Assistant")
st.markdown("Upload PDF documents and have a conversation about their content!")

# Main layout
col1, col2 = st.columns([3, 1])

with col1:
    # File upload section
    if not st.session_state.indexed or st.session_state.show_upload:
        st.markdown("### 📁 Upload Your Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload one or more PDF files to chat about their content"
        )
        
        if uploaded_files:
            if st.button("🔍 Process Documents", type="primary"):
                with st.spinner("Processing your documents..."):
                    try:
                        # Process uploaded files
                        all_chunks, processed_files = process_uploaded_files(uploaded_files)
                        
                        if all_chunks:
                            # Create a temporary directory that persists during the session
                            if st.session_state.temp_dir is None:
                                st.session_state.temp_dir = tempfile.mkdtemp()
                            
                            st.session_state.vectordb = store_chunks_in_chroma(
                                all_chunks, 
                                st.session_state.temp_dir
                            )
                            st.session_state.indexed = True
                            st.session_state.processed_files = processed_files
                            st.session_state.show_upload = False
                            st.session_state.chat_history = []  # Clear chat history
                            st.success(f"Successfully processed {len(processed_files)} document(s)!")
                            st.rerun()
                        else:
                            st.error("No text could be extracted from the uploaded files.")
                            
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")
    
    # Chat interface
    if st.session_state.indexed and st.session_state.vectordb:
        st.markdown("### 💬 Chat with Your Documents")
        
        # Display current documents
        if st.session_state.processed_files:
            st.info(f"Chatting about: {', '.join(st.session_state.processed_files)}")
        
        # Create a container for the chat area with fixed height
        chat_container = st.container(height=500)  # Fixed height container
        
        with chat_container:
            # Suggested questions (only show if no chat history)
            if not st.session_state.chat_history:
                st.markdown("**Suggested questions:**")
                example_questions = [
                    "What is the main topic of these documents?",
                    "Can you summarize the key points?",
                    "What are the main findings or conclusions?",
                    "Tell me about the methodology used",
                    "What are the limitations mentioned?"
                ]
                
                cols = st.columns(2)
                for i, question in enumerate(example_questions):
                    with cols[i % 2]:
                        if st.button(f"💬 {question}", key=f"example_{i}"):
                            st.session_state.current_question = question
                            st.rerun()
                st.markdown("---")
            
            # Display chat history
            if st.session_state.chat_history:
                display_chat_history()

            st.markdown("""
                <style>
                div[data-testid="stChatInput"] {
                    border: 3px solid #1E90FF !important; /* Bright blue border */
                    border-radius: 10px !important; /* Softer rounded corners */
                    background-color: #E6F3FF !important; /* Light blue background */
                    padding: 8px !important; /* More padding for a cleaner look */
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important; /* Subtle shadow */
                }
                div[data-testid="stChatInput"] textarea {
                    background-color: #FFFFFF !important; /* White textarea background */
                    color: #1A1A1A !important; /* Dark text for contrast */
                    font-size: 16px !important; /* Slightly larger text */
                    border: none !important; /* No inner border */
                    outline: none !important; /* No outline on focus */
                }
                div[data-testid="stChatInput"]:hover {
                    border-color: #0077CC !important; /* Darker blue on hover */
                    box-shadow: 0 4px 8px rgba(0, 119, 204, 0.2) !important; /* Enhanced shadow on hover */
                }
                div[data-testid="stChatInput"] textarea::placeholder {
                    color: #666666 !important; /* Gray placeholder text */
                    opacity: 1 !important; /* Ensure placeholder is fully visible */
                }
                </style>
            """, unsafe_allow_html=True)
        
        # Chat input - NOW FIXED OUTSIDE THE SCROLLABLE CONTAINER
        question = st.chat_input("Ask me anything about your documents...")
        
        # Process the question if one was submitted
        if question or hasattr(st.session_state, 'current_question'):
            if hasattr(st.session_state, 'current_question'):
                question = st.session_state.current_question
                del st.session_state.current_question
            
            # Add question and answer to history
            with st.spinner("Thinking..."):
                try:
                    # Search for relevant chunks
                    context = search_similar_chunks(question, st.session_state.vectordb, k=6)
                    
                    if not context.strip():
                        answer = "I couldn't find relevant information in your documents to answer that question. Could you try rephrasing or asking about something more specific?"
                    else:
                        # Generate answer using Gemini
                        answer = ask_gemini(context, question)
                    
                    # Add to chat history
                    add_to_chat_history(question, answer)
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    add_to_chat_history(question, error_msg)
            
            # Rerun to show the updated chat
            st.rerun()

with col2:
    st.markdown("### 🔧 Controls")
    
    if st.session_state.indexed:
        st.success("Documents ready!")
        
        if st.session_state.processed_files:
            st.markdown("**📄 Loaded files:**")
            for file in st.session_state.processed_files:
                st.markdown(f"• {file}")
        
        # MODIFIED RESET BUTTON - No longer deletes files
        if st.button("🔄 Reset & Upload New", type="secondary"):
            # Clear session state but DON'T delete files
            st.session_state.vectordb = None
            st.session_state.indexed = False
            st.session_state.temp_dir = None
            st.session_state.processed_files = []
            st.session_state.chat_history = []
            st.session_state.show_upload = True
            st.session_state.use_folder_docs = False  # Disable auto-initialization
            # NOTE: Removed clear_documents_folder() call to preserve files
            st.rerun()
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    else:
        st.info("📁 Upload documents to start chatting")
        
        # Add option to re-enable folder documents if they exist
        pdf_files = get_pdf_files_from_folder(DOCUMENTS_FOLDER)
        if pdf_files and not st.session_state.use_folder_docs:
            st.markdown("---")
            st.info(f"📂 Found {len(pdf_files)} PDF(s) in documents folder")
            if st.button("📁 Use Folder Documents"):
                st.session_state.use_folder_docs = True
                st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ How to use:")
    st.markdown("""
    1. **Upload PDFs**: Select one or more PDF files
    2. **Process**: Click to index your documents  
    3. **Chat**: Ask questions about your documents
    4. **Reset**: Upload new documents anytime
    """)
    
    st.markdown("### 🔧 Features:")
    st.markdown("• **Conversational UI**: Chat-like interface")
    st.markdown("• **Multiple files**: Upload several PDFs at once")
    st.markdown("• **Smart search**: Finds relevant content")
    st.markdown("• **Chat history**: Maintains conversation context")
    st.markdown("• **Easy reset**: Switch documents easily")
