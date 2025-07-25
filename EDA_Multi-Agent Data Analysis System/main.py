import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Data Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .step-header {
        font-size: 1.5rem;
        color: #2e7d32;
        margin: 1rem 0;
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-msg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

class GroqAgent:
    def __init__(self, name, system_message, api_key):
        self.name = name
        self.system_message = system_message
        self.api_key = api_key
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.last_response = ""
    
    def process(self, message, model="llama3-8b-8192"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            with st.spinner(f"{self.name} is processing..."):
                response = requests.post(self.endpoint, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    self.last_response = result['choices'][0]['message']['content']
                    return self.last_response, True
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    return error_msg, False
                    
        except Exception as e:
            return f"Exception occurred: {str(e)}", False

def initialize_agents(api_key):
    """Initialize all agents with the provided API key"""
    agents = {
        "data_prep": GroqAgent(
            name="Data Preparation Agent",
            system_message="You are a data preparation agent. Clean and preprocess raw data. Provide clear, actionable steps for data cleaning and identify any data quality issues.",
            api_key=api_key
        ),
        "eda": GroqAgent(
            name="EDA Agent",
            system_message="You are an EDA agent. Perform exploratory data analysis and generate insights. Focus on patterns, distributions, correlations, and key statistical findings.",
            api_key=api_key
        ),
        "critic": GroqAgent(
            name="Critic Agent",
            system_message="You are a critic agent. Review analysis outputs and provide constructive feedback. Identify potential issues, biases, and suggest improvements.",
            api_key=api_key
        ),
        "executor": GroqAgent(
            name="Executor Agent",
            system_message="You are an executor agent. Validate analysis results and provide final recommendations. Summarize key insights and actionable business recommendations.",
            api_key=api_key
        )
    }
    return agents

def create_sample_data():
    """Create sample data for demonstration"""
    return {
        "sales": [100, 150, 200, 175, 300, 250, 400, 350, 450, 380, 500, 425],
        "dates": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", 
                 "2023-07", "2023-08", "2023-09", "2023-10", "2023-11", "2023-12"],
        "categories": ["A", "B", "A", "C", "B", "A", "C", "B", "A", "C", "B", "A"],
        "regions": ["North", "South", "North", "East", "West", "South", "East", "West", 
                   "North", "South", "East", "West"]
    }

def visualize_data(data):
    """Create visualizations for the data"""
    df = pd.DataFrame(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales trend
        fig1 = px.line(df, x='dates', y='sales', title='Sales Trend Over Time')
        fig1.update_layout(xaxis_title="Date", yaxis_title="Sales")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Sales by category
        category_sales = df.groupby('categories')['sales'].sum().reset_index()
        fig2 = px.bar(category_sales, x='categories', y='sales', title='Sales by Category')
        fig2.update_layout(xaxis_title="Category", yaxis_title="Total Sales")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Sales by region
    region_sales = df.groupby('regions')['sales'].sum().reset_index()
    fig3 = px.pie(region_sales, values='sales', names='regions', title='Sales Distribution by Region')
    st.plotly_chart(fig3, use_container_width=True)

def main():
    st.markdown('<h1 class="main-header">🤖 Multi-Agent Data Analysis System</h1>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Enter your Groq API key to enable the agents"
        )
        
        # Model selection
        model = st.selectbox(
            "Select Model",
            ["llama3-8b-8192", "llama3-70b-4096", "mixtral-8x7b-32768"],
            help="Choose the Groq model for analysis"
        )
        
        st.divider()
        
        # Data input options
        st.header("📊 Data Input")
        data_option = st.radio(
            "Choose data source:",
            ["Use Sample Data", "Upload CSV", "Enter Custom Data"]
        )
        
        data = None
        
        if data_option == "Use Sample Data":
            data = create_sample_data()
            st.success("Sample data loaded!")
            
        elif data_option == "Upload CSV":
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    data = df.to_dict('list')
                    st.success(f"CSV uploaded! Shape: {df.shape}")
                    st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")
                    
        elif data_option == "Enter Custom Data":
            st.text("Enter JSON data:")
            custom_data = st.text_area(
                "Data (JSON format)",
                value='{"values": [1, 2, 3, 4, 5], "labels": ["A", "B", "C", "D", "E"]}',
                height=100
            )
            try:
                data = json.loads(custom_data)
                st.success("Custom data parsed successfully!")
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
    
    # Main content area
    if not api_key:
        st.warning("Please enter your Groq API key in the sidebar to proceed.")
        st.info("You can get a free API key from: https://console.groq.com/")
        return
    
    if data is None:
        st.warning("Please select a data source in the sidebar.")
        return
    
    # Initialize agents
    agents = initialize_agents(api_key)
    
    # Display data
    st.header("📈 Data Overview")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Data Visualization")
        visualize_data(data)
    
    with col2:
        st.subheader("Raw Data")
        st.json(data)
    
    # Workflow execution
    st.header("🔄 Multi-Agent Analysis Workflow")
    
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        # Initialize session state for results
        if 'workflow_results' not in st.session_state:
            st.session_state.workflow_results = {}
        
        # Step 1: Data Preparation
        st.markdown('<div class="step-header">🔧 Step 1: Data Preparation</div>', unsafe_allow_html=True)
        with st.container():
            prep_message = f"Analyze and prepare this data for further analysis: {json.dumps(data, indent=2)}"
            prep_result, prep_success = agents["data_prep"].process(prep_message, model)
            
            if prep_success:
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                st.markdown("**Data Preparation Agent Response:**")
                st.write(prep_result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.session_state.workflow_results['data_prep'] = prep_result
            else:
                st.error(f"Data Preparation failed: {prep_result}")
                return
        
        time.sleep(1)  # Brief pause between steps
        
        # Step 2: EDA
        st.markdown('<div class="step-header">📊 Step 2: Exploratory Data Analysis</div>', unsafe_allow_html=True)
        with st.container():
            eda_message = f"Perform comprehensive EDA on this data: {json.dumps(data, indent=2)}\n\nData preparation insights: {prep_result}"
            eda_result, eda_success = agents["eda"].process(eda_message, model)
            
            if eda_success:
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                st.markdown("**EDA Agent Response:**")
                st.write(eda_result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.session_state.workflow_results['eda'] = eda_result
            else:
                st.error(f"EDA failed: {eda_result}")
                return
        
        time.sleep(1)
        
        # Step 3: Critical Review
        st.markdown('<div class="step-header">🔍 Step 3: Critical Review</div>', unsafe_allow_html=True)
        with st.container():
            review_message = f"Critically review this EDA analysis and provide feedback:\n{eda_result}"
            critic_result, critic_success = agents["critic"].process(review_message, model)
            
            if critic_success:
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                st.markdown("**Critic Agent Response:**")
                st.write(critic_result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.session_state.workflow_results['critic'] = critic_result
            else:
                st.error(f"Critical review failed: {critic_result}")
                return
        
        time.sleep(1)
        
        # Step 4: Final Execution
        st.markdown('<div class="step-header">✅ Step 4: Final Validation & Recommendations</div>', unsafe_allow_html=True)
        with st.container():
            exec_message = f"Provide final validation and actionable recommendations based on:\nEDA Results: {eda_result}\nCritic Feedback: {critic_result}"
            exec_result, exec_success = agents["executor"].process(exec_message, model)
            
            if exec_success:
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                st.markdown("**Executor Agent Response:**")
                st.write(exec_result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.session_state.workflow_results['executor'] = exec_result
            else:
                st.error(f"Final execution failed: {exec_result}")
                return
        
        # Success message
        st.markdown('<div class="success-msg">🎉 Multi-Agent Analysis Completed Successfully!</div>', unsafe_allow_html=True)
        
        # Download results
        st.header("📥 Download Results")
        results_json = json.dumps(st.session_state.workflow_results, indent=2)
        st.download_button(
            label="Download Analysis Results (JSON)",
            data=results_json,
            file_name=f"multi_agent_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Display previous results if available
    if 'workflow_results' in st.session_state and st.session_state.workflow_results:
        st.header("📋 Previous Analysis Results")
        with st.expander("View Previous Results"):
            for step, result in st.session_state.workflow_results.items():
                st.subheader(f"{step.replace('_', ' ').title()}")
                st.write(result)
                st.divider()

if __name__ == "__main__":
    main()