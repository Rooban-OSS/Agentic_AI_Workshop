# logistics_optimization_crew.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
import time
from dataclasses import dataclass
from groq import Groq
import os

# Set page config
st.set_page_config(
    page_title="Logistics Optimization Crew AI",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .agent-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .task-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    .status-running {
        background-color: #ffc107;
    }
    .status-completed {
        background-color: #28a745;
    }
    .status-pending {
        background-color: #6c757d;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class Agent:
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    
@dataclass
class Task:
    description: str
    agent: str
    expected_output: str
    status: str = "pending"
    result: str = ""

class LogisticsCrewAI:
    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.agents = self._initialize_agents()
        self.tasks = self._initialize_tasks()
        
    def _initialize_agents(self) -> Dict[str, Agent]:
        return {
            "logistics_analyst": Agent(
                name="Senior Logistics Analyst",
                role="Logistics Data Analyst",
                goal="Analyze logistics operations data to identify inefficiencies, bottlenecks, and optimization opportunities in route planning and inventory management",
                backstory="""You are a senior logistics analyst with 15+ years of experience in supply chain optimization. 
                You specialize in analyzing complex logistics data, identifying patterns in delivery routes, inventory turnover, 
                and operational efficiency. Your expertise includes statistical analysis, demand forecasting, and identifying 
                cost-saving opportunities in transportation and warehousing operations.""",
                tools=["data_analysis", "statistical_modeling", "route_analysis", "inventory_analysis"]
            ),
            "optimization_strategist": Agent(
                name="Optimization Strategist",
                role="Strategic Optimization Consultant",
                goal="Develop comprehensive optimization strategies based on logistics analysis to improve delivery efficiency and inventory management",
                backstory="""You are a strategic optimization consultant with expertise in operations research and supply chain management. 
                You excel at translating data insights into actionable optimization strategies. Your background includes implementing 
                successful logistics transformations, route optimization algorithms, and inventory management systems across various industries.""",
                tools=["strategy_development", "optimization_algorithms", "implementation_planning", "roi_analysis"]
            )
        }
    
    def _initialize_tasks(self) -> List[Task]:
        return [
            Task(
                description="""Research and analyze the current state of logistics operations focusing on:
                1. Route efficiency analysis - identify suboptimal routes and delivery patterns
                2. Inventory turnover trends - analyze stock levels, demand patterns, and holding costs
                3. Operational bottlenecks - pinpoint areas causing delays or inefficiencies
                4. Cost analysis - break down transportation, warehousing, and operational costs
                5. Performance metrics - calculate KPIs like on-time delivery, order accuracy, inventory turnover
                Provide detailed insights with supporting data and visualizations.""",
                agent="logistics_analyst",
                expected_output="Comprehensive logistics analysis report with key findings, metrics, and identified optimization opportunities"
            ),
            Task(
                description="""Based on the logistics analysis, develop a comprehensive optimization strategy that includes:
                1. Route optimization recommendations - specific improvements for delivery efficiency
                2. Inventory management strategy - optimal stock levels, reorder points, and supplier management
                3. Technology integration suggestions - systems and tools to improve operations
                4. Implementation roadmap - phased approach with timelines and resource requirements
                5. Expected ROI and cost-benefit analysis
                6. Risk assessment and mitigation strategies
                Parametrize all recommendations to enable systematic optimization.""",
                agent="optimization_strategist",
                expected_output="Detailed optimization strategy document with actionable recommendations, implementation plan, and expected outcomes"
            )
        ]
    
    def _call_groq_api(self, prompt: str, system_message: str) -> str:
        """Make API call to Groq"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=4000
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error calling Groq API: {str(e)}"
    
    def execute_task(self, task: Task, context: str = "") -> str:
        """Execute a task using the appropriate agent"""
        agent = self.agents[task.agent]
        
        system_message = f"""You are {agent.name}, a {agent.role}.
        
        Your Goal: {agent.goal}
        
        Your Background: {agent.backstory}
        
        Available Tools: {', '.join(agent.tools)}
        
        Context from previous tasks: {context}
        """
        
        prompt = f"""
        Please complete the following task:
        
        {task.description}
        
        Expected Output: {task.expected_output}
        
        Please provide a comprehensive, professional response that demonstrates your expertise and delivers actionable insights.
        Include specific recommendations, data points, and strategic considerations where applicable.
        """
        
        return self._call_groq_api(prompt, system_message)
    
    def run_crew(self) -> Dict[str, Any]:
        """Execute all tasks in sequence"""
        results = {}
        context = ""
        
        for i, task in enumerate(self.tasks):
            st.write(f"### 🔄 Executing Task {i+1}: {task.agent.replace('_', ' ').title()}")
            
            # Update task status
            task.status = "running"
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress
            for percent in range(0, 101, 20):
                progress_bar.progress(percent)
                status_text.text(f"Processing... {percent}%")
                time.sleep(0.1)
            
            # Execute task
            result = self.execute_task(task, context)
            task.result = result
            task.status = "completed"
            
            # Store result and update context
            results[task.agent] = result
            context += f"\n\nResults from {task.agent}:\n{result}"
            
            # Display result
            st.success(f"✅ Task completed by {task.agent.replace('_', ' ').title()}")
            with st.expander(f"View {task.agent.replace('_', ' ').title()} Results"):
                st.write(result)
        
        return results

def validate_delivery_data(delivery_data: pd.DataFrame) -> bool:
    """Validate delivery data columns"""
    required_columns = ['date', 'route_id', 'delivery_time_hours', 'distance_km', 
                       'fuel_cost_inr', 'packages_delivered', 'on_time_delivery']
    return all(col in delivery_data.columns for col in required_columns)

def validate_inventory_data(inventory_data: pd.DataFrame) -> bool:
    """Validate inventory data columns"""
    required_columns = ['product_id', 'current_stock', 'reorder_point', 
                       'holding_cost_per_unit_inr', 'demand_last_30_days', 'supplier_lead_time_days']
    return all(col in inventory_data.columns for col in required_columns)

def display_logistics_dashboard(delivery_data: pd.DataFrame, inventory_data: pd.DataFrame):
    """Display logistics dashboard with key metrics"""
    st.markdown("## 📊 Current Logistics Performance Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_delivery_time = delivery_data['delivery_time_hours'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Avg Delivery Time</h3>
            <h2>{avg_delivery_time:.1f} hours</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        on_time_rate = delivery_data['on_time_delivery'].mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅ On-Time Rate</h3>
            <h2>{on_time_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_fuel_cost = delivery_data['fuel_cost_inr'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>⛽ Avg Fuel Cost</h3>
            <h2>₹{avg_fuel_cost:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_packages = delivery_data['packages_delivered'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦 Total Packages</h3>
            <h2>{total_packages:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Route efficiency chart
        route_efficiency = delivery_data.groupby('route_id').agg({
            'delivery_time_hours': 'mean',
            'fuel_cost_inr': 'mean',
            'on_time_delivery': 'mean'
        }).reset_index()
        
        fig = px.bar(route_efficiency, x='route_id', y='delivery_time_hours',
                    title='Average Delivery Time by Route',
                    color='delivery_time_hours',
                    color_continuous_scale='RdYlBu_r')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Inventory levels chart
        low_stock = inventory_data[inventory_data['current_stock'] < inventory_data['reorder_point']]
        fig = px.histogram(inventory_data, x='current_stock', nbins=20,
                          title='Inventory Distribution',
                          color_discrete_sequence=['#2E86AB'])
        fig.add_vline(x=inventory_data['reorder_point'].mean(), 
                     line_dash="dash", line_color="red",
                     annotation_text="Avg Reorder Point")
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.markdown('<h1 class="main-header">🚚 Logistics Optimization Crew AI System</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        groq_api_key = st.text_input("Groq API Key", type="password", 
                                    help="Enter your Groq API key to enable AI agents")
        
        if not groq_api_key:
            st.warning("Please enter your Groq API key to proceed")
            st.info("Get your free API key at: https://console.groq.com/keys")
            return
        
        st.success("✅ API Key configured")
        
        # Agent information
        st.header("🤖 Active Agents")
        st.info("**Logistics Analyst**: Analyzes current operations and identifies optimization opportunities")
        st.info("**Optimization Strategist**: Develops comprehensive improvement strategies")
        
        # File upload for delivery and inventory data
        st.header("📂 Upload Logistics Data")
        st.info("Use the templates generated by `generate_data_templates.py` to ensure compatibility.")
        delivery_file = st.file_uploader("Upload Delivery Data (CSV)", type=['csv'])
        inventory_file = st.file_uploader("Upload Inventory Data (CSV)", type=['csv'])
        
        if delivery_file and inventory_file:
            try:
                delivery_data = pd.read_csv(delivery_file)
                inventory_data = pd.read_csv(inventory_file)
                
                # Validate uploaded data
                if not validate_delivery_data(delivery_data):
                    st.error("Delivery data must contain columns: date, route_id, delivery_time_hours, distance_km, fuel_cost_inr, packages_delivered, on_time_delivery")
                    return
                if not validate_inventory_data(inventory_data):
                    st.error("Inventory data must contain columns: product_id, current_stock, reorder_point, holding_cost_per_unit_inr, demand_last_30_days, supplier_lead_time_days")
                    return
                
                st.success("✅ Data uploaded and validated successfully")
            except Exception as e:
                st.error(f"Error reading uploaded files: {str(e)}")
                return
        else:
            st.warning("Please upload both delivery and inventory data files to proceed")
            return
    
    # Initialize Crew AI system
    try:
        crew_ai = LogisticsCrewAI(groq_api_key)
        
        # Display current logistics dashboard
        display_logistics_dashboard(delivery_data, inventory_data)
        
        # Main execution section
        st.markdown("## 🚀 Execute Optimization Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("The Crew AI system will analyze your logistics operations and develop optimization strategies.")
            st.write("**Process:**")
            st.write("1. 📊 **Logistics Analyst** will analyze current performance and identify issues")
            st.write("2. 🎯 **Optimization Strategist** will create actionable improvement strategies")
        
        with col2:
            execute_button = st.button("▶️ Start Analysis", type="primary", use_container_width=True)
        
        if execute_button:
            st.markdown("---")
            st.markdown("## 🔄 Crew AI Execution")
            
            # Execute the crew
            with st.container():
                start_time = time.time()
                results = crew_ai.run_crew()
                execution_time = time.time() - start_time
                
                st.success(f"🎉 Analysis completed in {execution_time:.1f} seconds!")
                
                # Display final results
                st.markdown("## 📋 Final Optimization Report")
                
                tab1, tab2, tab3 = st.tabs(["📊 Analysis Results", "🎯 Optimization Strategy", "📈 Implementation Plan"])
                
                with tab1:
                    st.markdown("### Logistics Analysis Results")
                    if "logistics_analyst" in results:
                        st.write(results["logistics_analyst"])
                
                with tab2:
                    st.markdown("### Optimization Strategy")
                    if "optimization_strategist" in results:
                        st.write(results["optimization_strategist"])
                
                with tab3:
                    st.markdown("### Next Steps & Implementation")
                    st.write("""
                    **Recommended Implementation Approach:**
                    
                    1. **Phase 1 (Week 1-2)**: Implement quick wins identified in the analysis
                    2. **Phase 2 (Week 3-6)**: Deploy route optimization solutions
                    3. **Phase 3 (Week 7-12)**: Implement inventory management improvements
                    4. **Phase 4 (Month 4+)**: Advanced analytics and continuous optimization
                    
                    **Key Success Metrics to Track:**
                    - Delivery time reduction percentage
                    - Fuel cost savings (in ₹)
                    - On-time delivery improvement
                    - Inventory holding cost reduction
                    - Customer satisfaction scores
                    """)
                
                # Export results
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Generate PDF Report", use_container_width=True):
                        st.info("PDF generation feature would be implemented here")
                
                with col2:
                    report_data = {
                        "execution_time": execution_time,
                        "timestamp": datetime.now().isoformat(),
                        "results": results
                    }
                    st.download_button(
                        "💾 Download JSON Report",
                        data=json.dumps(report_data, indent=2),
                        file_name=f"logistics_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
        
        # Additional features section
        st.markdown("---")
        st.markdown("## 🔧 Additional Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Upload Custom Data", use_container_width=True):
                st.info("Use the sidebar to upload your logistics data")
        
        with col2:
            if st.button("🔄 Schedule Analysis", use_container_width=True):
                st.info("Scheduling feature would enable automatic periodic analysis")
        
        with col3:
            if st.button("📈 Advanced Analytics", use_container_width=True):
                st.info("Advanced analytics would provide deeper insights and predictive modeling")
    
    except Exception as e:
        st.error(f"Error initializing Crew AI system: {str(e)}")
        st.info("Please check your API key and try again")

if __name__ == "__main__":
    main()