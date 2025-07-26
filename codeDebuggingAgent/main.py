import streamlit as st
import os
from groq import Groq
import re
import ast
import traceback
from typing import Dict, List, Tuple
import time

# Set page config
st.set_page_config(
    page_title="Automated Code Debugging Assistant",
    page_icon="🐛",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #2E86AB;
    }
    .task-output {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .error-code {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
    }
    .corrected-code {
        background-color: #e8f5e8;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
    }
    .agent-thinking {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🐛 Automated Code Debugging Assistant</h1>', unsafe_allow_html=True)

# Initialize Groq client
@st.cache_resource
def init_groq_client(api_key):
    return Groq(api_key=api_key)

class Agent:
    """Base Agent class for the multi-agent system"""
    def __init__(self, name: str, role: str, goal: str, backstory: str, groq_client: Groq):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.groq_client = groq_client
        self.model = "mixtral-8x7b-32768"
    
    def execute_task(self, task: str, context: str = "") -> str:
        """Execute a task using the Groq LLM"""
        system_prompt = f"""
        You are a {self.role}.
        Goal: {self.goal}
        Background: {self.backstory}
        
        Context from previous agents: {context}
        
        Please provide a detailed and professional response to the following task.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error executing task: {str(e)}"

class CodeAnalyzer(Agent):
    """Specialized agent for analyzing code errors"""
    def __init__(self, groq_client: Groq):
        super().__init__(
            name="Code Analyzer",
            role="Senior Python Code Analyzer",
            goal="Identify syntax and logical errors in Python code with high precision",
            backstory="""You are an expert Python code analyzer with 10+ years of experience. 
            You excel at identifying various types of errors including syntax errors, logical errors, 
            runtime errors, and potential issues. You provide detailed analysis of what's wrong.""",
            groq_client=groq_client
        )
    
    def analyze_code(self, code: str) -> Dict:
        """Analyze code for various types of errors"""
        analysis_task = f"""
        Analyze the following Python code and identify all errors:
        
        ```python
        {code}
        ```
        
        Provide a detailed analysis including:
        1. **Syntax Errors**: Any syntax issues (missing colons, brackets, incorrect operators)
        2. **Logical Errors**: Logic flow issues, wrong conditions, incorrect algorithms  
        3. **Runtime Errors**: Potential runtime issues (division by zero, key errors, etc.)
        4. **Best Practice Issues**: Code improvements and Python best practices
        5. **Line-by-Line Analysis**: Specific issues with line numbers
        
        Format your response clearly with sections for each type of error.
        Be specific about what's wrong and why it's problematic.
        """
        
        result = self.execute_task(analysis_task)
        
        # Also perform basic Python syntax check
        syntax_errors = self._check_syntax(code)
        
        return {
            "detailed_analysis": result,
            "syntax_errors": syntax_errors,
            "agent": self.name
        }
    
    def _check_syntax(self, code: str) -> List[str]:
        """Perform basic Python syntax checking"""
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax Error on line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse Error: {str(e)}")
        
        return errors

class CodeCorrector(Agent):
    """Specialized agent for correcting code errors"""
    def __init__(self, groq_client: Groq):
        super().__init__(
            name="Code Corrector",
            role="Senior Python Developer and Code Corrector",
            goal="Fix identified errors and provide clean, working Python code",
            backstory="""You are a senior Python developer specializing in code correction and optimization. 
            You take error analysis and transform buggy code into clean, efficient, and error-free Python code. 
            You ensure the corrected code maintains the original intent while fixing all issues.""",
            groq_client=groq_client
        )
    
    def correct_code(self, original_code: str, analysis: str) -> Dict:
        """Correct code based on the analysis"""
        correction_task = f"""
        Based on the following error analysis, fix the Python code:
        
        **Original Code:**
        ```python
        {original_code}
        ```
        
        **Error Analysis:**
        {analysis}
        
        Please provide:
        1. **Corrected Code**: The complete fixed Python code wrapped in ```python``` tags
        2. **Changes Made**: Detailed explanation of each fix applied
        3. **Verification**: Confirm the code should now run without errors
        4. **Improvements**: Any additional improvements made beyond fixing errors
        
        Ensure the corrected code maintains the original purpose and functionality.
        """
        
        result = self.execute_task(correction_task)
        
        # Extract corrected code from the response
        corrected_code = self._extract_code_block(result)
        
        return {
            "correction_details": result,
            "corrected_code": corrected_code,
            "agent": self.name
        }
    
    def _extract_code_block(self, text: str) -> str:
        """Extract Python code block from response"""
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Fallback: look for any code block
        pattern = r'```\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        return "No code block found in correction"

class ProjectManager(Agent):
    """Manager agent to oversee the debugging process"""
    def __init__(self, groq_client: Groq):
        super().__init__(
            name="Project Manager",
            role="Technical Project Manager",
            goal="Oversee the debugging process and ensure quality output",
            backstory="""You are an experienced technical project manager who coordinates between analysts and developers. 
            You ensure the debugging process runs smoothly, validate that all errors are addressed, 
            and provide clear communication about the debugging results.""",
            groq_client=groq_client
        )
    
    def manage_process(self, original_code: str, analysis_result: Dict, correction_result: Dict) -> Dict:
        """Manage and summarize the debugging process"""
        management_task = f"""
        Review the code debugging process and provide an executive summary:
        
        **Original Code Issues:**
        {analysis_result['detailed_analysis']}
        
        **Correction Applied:**
        {correction_result['correction_details']}
        
        **Corrected Code:**
        ```python
        {correction_result['corrected_code']}
        ```
        
        Provide a comprehensive summary including:
        1. **Process Overview**: Summary of the debugging workflow
        2. **Issues Identified**: Key problems found in the original code
        3. **Solutions Applied**: Main corrections and improvements made
        4. **Quality Assurance**: Confirmation that issues have been resolved
        5. **Recommendations**: Any additional suggestions for the developer
        
        Keep the summary clear and actionable for the user.
        """
        
        result = self.execute_task(management_task)
        
        return {
            "management_summary": result,
            "process_status": "completed",
            "agent": self.name
        }

class MultiAgentDebuggingSystem:
    """Main system that orchestrates the multi-agent debugging process"""
    def __init__(self, groq_client: Groq):
        self.groq_client = groq_client
        self.code_analyzer = CodeAnalyzer(groq_client)
        self.code_corrector = CodeCorrector(groq_client)
        self.project_manager = ProjectManager(groq_client)
    
    def debug_code(self, code: str) -> Dict:
        """Run the complete debugging process"""
        results = {
            "original_code": code,
            "analysis": None,
            "correction": None,
            "management": None,
            "process_log": []
        }
        
        try:
            # Step 1: Code Analysis
            st.write("🔍 **Code Analyzer is working...**")
            with st.spinner("Analyzing code for errors..."):
                analysis_result = self.code_analyzer.analyze_code(code)
                results["analysis"] = analysis_result
                results["process_log"].append("✅ Code analysis completed")
            
            # Step 2: Code Correction
            st.write("🛠️ **Code Corrector is working...**")
            with st.spinner("Fixing identified errors..."):
                correction_result = self.code_corrector.correct_code(
                    code, 
                    analysis_result["detailed_analysis"]
                )
                results["correction"] = correction_result
                results["process_log"].append("✅ Code correction completed")
            
            # Step 3: Project Management Review
            st.write("👔 **Project Manager is reviewing...**")
            with st.spinner("Finalizing debugging report..."):
                management_result = self.project_manager.manage_process(
                    code, 
                    analysis_result, 
                    correction_result
                )
                results["management"] = management_result
                results["process_log"].append("✅ Management review completed")
            
            results["status"] = "success"
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            results["process_log"].append(f"❌ Error: {str(e)}")
        
        return results

# Sidebar for API key input
with st.sidebar:
    st.header("🔧 Configuration")
    
    # API Key input
    groq_api_key = st.text_input(
        "Enter your Groq API Key:",
        type="password",
        help="Get your API key from https://console.groq.com/"
    )
    
    if groq_api_key:
        st.success("✅ API Key set successfully!")
    
    st.markdown("---")
    st.header("🤖 Agent Information")
    
    # Agent descriptions
    agents_info = {
        "🔍 Code Analyzer": {
            "role": "Senior Python Code Analyzer",
            "description": "Identifies syntax, logical, and runtime errors with detailed analysis"
        },
        "🛠️ Code Corrector": {
            "role": "Senior Python Developer",
            "description": "Fixes identified errors and provides clean, working code"
        },
        "👔 Project Manager": {
            "role": "Technical Project Manager", 
            "description": "Oversees the process and provides quality assurance"
        }
    }
    
    for agent, info in agents_info.items():
        with st.expander(f"{agent}", expanded=False):
            st.write(f"**Role:** {info['role']}")
            st.write(f"**Function:** {info['description']}")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🐛 Input Code (with errors)")
    
    # Example codes
    example_codes = {
        "Select an example...": "",
        "Fibonacci with errors": '''def fibonacci_iterative(n):
    if n = 0:
        return []
    elif n == 1:
        return [0]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_fib = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_fib)
    
    return fib_sequence

print(fibonacci_iterative(10))''',
        
        "List processing errors": '''def process_list(numbers):
    result = []
    for i in range(len(numbers)):
        if numbers[i] % 2 = 0:
            result.append(numbers[i] * 2)
        else:
            result.append(numbers[i] / 0)
    
    return result

numbers = [1, 2, 3, 4, 5]
print(process_list(numbers))''',
        
        "Dictionary errors": '''def get_user_info():
    users = {
        "john": {"age": 25, "city": "New York"},
        "jane": {"age": 30, "city": "Boston"}
    }
    
    user_name = input("Enter username: ")
    user_info = users[user_name]  # No error handling
    
    print(f"User {user_name} is {user_info['age']} years old and lives in {user_info['city']}")
    
    return user_info

get_user_info()''',
        
        "Variable scope issues": '''def calculate_total():
    items = [10, 20, 30, 40, 50]
    
    for item in items:
        total += item  # total not initialized
    
    return total

def display_result():
    result = calculate_total()
    print(f"Total: {total}")  # wrong variable name
    
display_result()'''
    }
    
    selected_example = st.selectbox("Choose an example:", list(example_codes.keys()))
    
    input_code = st.text_area(
        "Enter your Python code:",
        value=example_codes[selected_example],
        height=300,
        placeholder="Paste your Python code here..."
    )

with col2:
    st.header("🎯 Debugging Process")
    
    if st.button("🔍 Start Debugging", type="primary", use_container_width=True):
        if not input_code.strip():
            st.error("Please enter some Python code to debug!")
        elif not groq_api_key:
            st.error("Please enter your Groq API key in the sidebar!")
        else:
            try:
                # Initialize the multi-agent system
                groq_client = init_groq_client(groq_api_key)
                debugging_system = MultiAgentDebuggingSystem(groq_client)
                
                # Create progress tracking
                progress_placeholder = st.empty()
                
                # Run the debugging process
                with st.container():
                    st.markdown("### 🚀 Multi-Agent Debugging in Progress")
                    
                    # Execute debugging
                    results = debugging_system.debug_code(input_code)
                    
                    if results["status"] == "success":
                        st.success("✅ Debugging completed successfully!")
                        
                        # Display results in tabs
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "📊 Analysis", "🛠️ Correction", "👔 Management", "📝 Summary"
                        ])
                        
                        with tab1:
                            st.markdown("### 🔍 Code Analysis Results")
                            analysis = results["analysis"]
                            
                            if analysis["syntax_errors"]:
                                st.error("**Syntax Errors Found:**")
                                for error in analysis["syntax_errors"]:
                                    st.write(f"• {error}")
                            
                            st.markdown("**Detailed Analysis:**")
                            st.markdown(analysis["detailed_analysis"])
                        
                        with tab2:
                            st.markdown("### 🛠️ Code Correction Results")
                            correction = results["correction"]
                            
                            st.markdown("**Correction Details:**")
                            st.markdown(correction["correction_details"])
                            
                            if correction["corrected_code"] != "No code block found in correction":
                                st.markdown("**✅ Corrected Code:**")
                                st.code(correction["corrected_code"], language="python")
                        
                        with tab3:
                            st.markdown("### 👔 Management Summary")
                            management = results["management"]
                            st.markdown(management["management_summary"])
                        
                        with tab4:
                            st.markdown("### 📝 Complete Summary")
                            
                            # Side-by-side comparison
                            col_orig, col_fixed = st.columns(2)
                            
                            with col_orig:
                                st.markdown("**🐛 Original Code:**")
                                st.code(input_code, language="python")
                            
                            with col_fixed:
                                st.markdown("**✅ Corrected Code:**")
                                corrected_code = results["correction"]["corrected_code"]
                                if corrected_code != "No code block found in correction":
                                    st.code(corrected_code, language="python")
                                    
                                    # Download button
                                    st.download_button(
                                        label="📥 Download Corrected Code",
                                        data=corrected_code,
                                        file_name="corrected_code.py",
                                        mime="text/plain"
                                    )
                                else:
                                    st.warning("Could not extract corrected code from response")
                            
                            # Process log
                            st.markdown("**🔄 Process Log:**")
                            for log_entry in results["process_log"]:
                                st.write(log_entry)
                    
                    else:
                        st.error(f"❌ Debugging failed: {results.get('error', 'Unknown error')}")
                        
            except Exception as e:
                st.error(f"An error occurred during debugging: {str(e)}")
                st.error("Please check your API key and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🤖 Powered by Multi-Agent System & Groq API</p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)

# Instructions in expander
with st.expander("📝 How to Use This Tool"):
    st.markdown("""
    ### Getting Started:
    1. **Get a Groq API Key**: Visit [console.groq.com](https://console.groq.com/) to get your free API key
    2. **Enter your API key** in the sidebar
    3. **Paste your Python code** in the input area (or select an example)
    4. **Click "Start Debugging"** to begin the analysis
    
    ### What This Tool Does:
    - **🔍 Code Analyzer**: Identifies all types of errors in your code
    - **🛠️ Code Corrector**: Fixes the errors and provides clean code
    - **👔 Project Manager**: Oversees the process and provides a summary
    
    ### Types of Errors Detected:
    - **Syntax errors**: Missing colons, incorrect indentation, wrong operators
    - **Logical errors**: Wrong conditions, incorrect logic flow
    - **Runtime errors**: Division by zero, key errors, index errors
    - **Best practices**: Code improvements and Python conventions
    
    ### Features:
    - Multi-agent collaborative debugging
    - Detailed error analysis with explanations
    - Clean, corrected code output
    - Download option for corrected code
    - Example codes to test with
    - Real-time progress tracking
    
    ### Multi-Agent Process:
    1. **Analysis Phase**: Code Analyzer identifies all errors
    2. **Correction Phase**: Code Corrector fixes the issues  
    3. **Review Phase**: Project Manager validates and summarizes
    4. **Results**: Get detailed reports and corrected code
    """)