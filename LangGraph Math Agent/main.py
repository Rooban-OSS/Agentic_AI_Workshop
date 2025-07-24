import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import re
from typing import Union

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stTitle {
        color: #1a3c87;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
    }
    .stMarkdown {
        color: #333;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stTextInput > div > div > input {
        border: 2px solid #1a3c87;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        font-family: 'Arial', sans-serif;
    }
    .stButton > button {
        background-color: #1a3c87;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-family: 'Arial', sans-serif;
        border: none;
        width: 100%;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #2a5db0;
    }
    .response-box {
        background-color: #ffffff;
        border: 2px solid #1a3c87;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        color: #333;
    }
    .stAlert {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Arial', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit configuration
with st.container():
    st.title("Math Query Solver")
    st.markdown("Enter a mathematical query, such as '5 plus 3', 'What is the Pythagorean theorem?', or 'Solve x^2 + 2x - 3 = 0'. Non-mathematical queries are not supported.")

# Input section with columns for better layout
col1, col2 = st.columns([3, 1])
with col1:
    api_key = st.text_input("Groq API Key", type="password", placeholder="Enter your Groq API key here")
with col2:
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)  # Spacer for alignment
    if st.button("Clear Inputs"):
        st.session_state.api_key = ""
        st.session_state.user_input = ""

if not api_key:
    st.error("Please enter your Groq API key to continue.")
    st.stop()

os.environ["GROQ_API_KEY"] = api_key

# Define a reducer function for messages
def append_messages(current: List[Union[HumanMessage, AIMessage]], new: List[Union[HumanMessage, AIMessage]]) -> List[Union[HumanMessage, AIMessage]]:
    return current + new

# Define the state
class GraphState(TypedDict):
    question: str
    messages: Annotated[List[Union[HumanMessage, AIMessage]], append_messages]
    response: str

# Custom mathematical functions
def plus(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> str:
    if b == 0:
        return "Error: Division by zero is not allowed"
    return str(a / b)

# Define tools
tools = {
    "plus": plus,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide
}

# Define prompt for LLM to handle math queries
math_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a mathematical assistant. Respond only to mathematical queries, including definitions, theorems, explanations, equations, and problem solving. You may explain concepts if asked to, such as 'Explain the Pythagorean theorem'. Do not answer non-mathematical questions. If the query is not mathematical, respond with: "Sorry, I only handle mathematical queries." Avoid programming examples or code."""),
    ("human", "{question}")
])

# Initialize LLM with prompt
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
math_chain = math_prompt | llm

# Node to handle chatbot (math-only) responses
def chatbot(state: GraphState) -> GraphState:
    question = state["question"]
    messages = state["messages"]
    
    # Check if the question is a simple arithmetic query
    math_pattern = r'(\d*\.?\d+)\s*(plus|minus|times|divided by)\s*(\d*\.?\d+)'
    match = re.search(math_pattern, question.lower())
    
    if match:
        num1, operation, num2 = match.groups()
        try:
            num1, num2 = float(num1), float(num2)
        except ValueError:
            state["response"] = "Invalid numerical input"
            state["messages"] = append_messages(state["messages"], [AIMessage(content="Invalid numerical input")])
            return state
        
        operation_map = {
            "plus": "plus",
            "minus": "subtract",
            "times": "multiply",
            "divided by": "divide"
        }
        
        tool_name = operation_map.get(operation)
        if tool_name:
            result = tools[tool_name](num1, num2)
            state["response"] = str(result)
            state["messages"] = append_messages(state["messages"], [AIMessage(content=str(result))])
        else:
            state["response"] = "Invalid mathematical operation"
            state["messages"] = append_messages(state["messages"], [AIMessage(content="Invalid mathematical operation")])
    else:
        # Forward to LLM for other mathematical queries
        response = math_chain.invoke({"question": question})
        state["response"] = response.content
        state["messages"] = append_messages(state["messages"], [AIMessage(content=response.content)])
    
    return state

# Create LangGraph
workflow = StateGraph(GraphState)
workflow.add_node("chatbot", chatbot)
workflow.set_entry_point("chatbot")
workflow.add_edge("chatbot", END)

# Compile the graph
app = workflow.compile()

# Query input and submission
with st.container():
    user_input = st.text_input("Mathematical Query", placeholder="Enter your math query here (e.g., '5 plus 3' or 'Solve x^2 + 2x - 3 = 0')")
    if st.button("Submit Query"):
        if user_input:
            # Initialize state
            initial_state = {
                "question": user_input,
                "messages": [HumanMessage(content=user_input)],
                "response": ""
            }
            
            # Run the graph
            final_state = app.invoke(initial_state)
            
            # Display response in a styled box
            st.markdown("<div class='response-box'>Response:<br>{}</div>".format(final_state["response"]), unsafe_allow_html=True)
        else:
            st.error("Please enter a mathematical query.")