import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import logging
import plotly.express as px
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Base URL
API_BASE_URL = "http://localhost:8000"  # Update with your API's actual URL

# Streamlit App Configuration
st.set_page_config(page_title="Interview Panel Optimizer", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f9f9fb; padding: 20px; border-radius: 10px; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #45a049; }
    .sidebar .sidebar-content { background-color: #e8ecef; }
    .stTextInput, .stTextArea, .stSelectbox, .stMultiselect, .stNumberInput { 
        border: 1px solid #d1d5db; border-radius: 5px; padding: 8px; 
    }
    .badge-none { background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; }
    .badge-potential { background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 12px; font-size: 12px; }
    .badge-confirmed { background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; }
    .badge-dei-compliant { background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; }
    h1, h2, h3 { color: #2c3e50; }
    .stDataFrame { border: 1px solid #e2e8f0; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Helper function to make API calls
def make_api_call(endpoint, method="GET", data=None):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        st.error(f"Error: {str(e)}")
        return None

# Header
with st.container():
    st.title("Interview Panel Optimizer 🚀")
    st.markdown("""
        AI-powered interview panel optimization using **Skill Match**, **DEI Compliance**, **Conflict Checker**, and **Panel Design Optimizer** agents with RAG.
    """)

# Sidebar for navigation
st.sidebar.title("Navigation 🧭")
page = st.sidebar.radio("Go to", [
    "Home",
    "Manage Jobs",
    "Manage Interviewers",
    "Manage Candidates",
    "Panel Recommendations"
], label_visibility="collapsed")

# Home Page
if page == "Home":
    st.header("Welcome to Interview Panel Optimizer 🏠")
    with st.container():
        health = make_api_call("/health")
        if health:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("System Status", health['status'].capitalize(), delta=None, delta_color="normal")
                st.metric("Database", health['database'].capitalize())
            with col2:
                st.metric("Version", health['version'])
                st.write("**Features Active:**")
                for feature in health.get('features_active', []):
                    st.markdown(f"✅ {feature.replace('_', ' ').title()}")

# Manage Jobs
elif page == "Manage Jobs":
    st.header("Manage Jobs 💼")
    
    # Create Job
    with st.expander("Create New Job", expanded=True):
        with st.form("create_job_form"):
            st.subheader("Add Job Details")
            col1, col2 = st.columns(2)
            with col1:
                job_role = st.text_input("Job Role", placeholder="e.g., Software Engineer")
                job_description = st.text_area("Job Description", placeholder="Describe the job responsibilities...")
                required_skills = st.text_input("Required Skills (comma-separated)", placeholder="e.g., Python, Java, SQL")
            with col2:
                experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior", "lead", "principal"])
                department = st.text_input("Department", placeholder="e.g., Engineering")
                interviewer_types = st.multiselect("Interviewer Types Needed", ["technical", "behavioral", "domain_expert", "hr", "manager"])
            submit_job = st.form_submit_button("Create Job")
            
            if submit_job:
                job_data = {
                    "job_role": job_role,
                    "job_description": job_description,
                    "required_skills": [skill.strip() for skill in required_skills.split(",")],
                    "experience_level": experience_level,
                    "department": department,
                    "interviewer_types_needed": interviewer_types
                }
                result = make_api_call("/job/create", method="POST", data=job_data)
                if result:
                    st.success(f"Job created successfully! Job ID: {result['job_id']}")
    
    # List Jobs
    with st.expander("Existing Jobs"):
        st.subheader("View Jobs")
        col1, col2 = st.columns([3, 1])
        with col2:
            skip = st.number_input("Skip", min_value=0, value=0, key="job_skip")
            limit = st.number_input("Limit", min_value=1, max_value=100, value=10, key="job_limit")
            if st.button("List Jobs"):
                jobs_data = make_api_call(f"/jobs?skip={skip}&limit={limit}")
                if jobs_data and jobs_data["jobs"]:
                    df = pd.DataFrame(jobs_data["jobs"])
                    st.dataframe(
                        df[["_id", "job_role", "department", "experience_level", "status"]],
                        use_container_width=True,
                        column_config={
                            "_id": st.column_config.TextColumn("Job ID", width="medium"),
                            "job_role": st.column_config.TextColumn("Role", width="medium"),
                            "department": st.column_config.TextColumn("Department", width="small"),
                            "experience_level": st.column_config.TextColumn("Level", width="small"),
                            "status": st.column_config.TextColumn("Status", width="small")
                        }
                    )
                    dept_counts = df["department"].value_counts()
                    fig = px.bar(x=dept_counts.index, y=dept_counts.values, labels={"x": "Department", "y": "Number of Jobs"}, title="Jobs by Department")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No jobs found.")

# Manage Interviewers
elif page == "Manage Interviewers":
    st.header("Manage Interviewers 👥")
    
    # Add Interviewer
    with st.expander("Add New Interviewer", expanded=True):
        with st.form("add_interviewer_form"):
            st.subheader("Interviewer Details")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", placeholder="e.g., John Doe")
                email = st.text_input("Email", placeholder="e.g., john.doe@example.com")
                department = st.text_input("Department", placeholder="e.g., Engineering")
                skills = st.text_input("Skills (comma-separated)", placeholder="e.g., Python, Leadership")
            with col2:
                availability = st.text_area("Availability (JSON format)", placeholder="e.g., [{'from': '2025-06-16T09:00:00', 'to': '2025-06-16T17:00:00'}]")
                past_feedback_score = st.number_input("Past Feedback Score", min_value=0.0, max_value=5.0, value=0.0)
                experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior", "lead", "principal"])
                interviewer_type = st.selectbox("Interviewer Type", ["technical", "behavioral", "domain_expert", "hr", "manager"])
            years_of_experience = st.number_input("Years of Experience", min_value=0, value=0)
            gender = st.selectbox("Gender", ["male", "female", "non-binary", "prefer_not_to_say"])
            ethnicity = st.text_input("Ethnicity", placeholder="e.g., Asian, Caucasian")
            submit_interviewer = st.form_submit_button("Add Interviewer")
            
            if submit_interviewer:
                try:
                    availability_list = json.loads(availability)
                    interviewer_data = {
                        "name": name,
                        "email": email,
                        "department": department,
                        "skills": [skill.strip() for skill in skills.split(",")],
                        "availability": availability_list,
                        "past_feedback_score": past_feedback_score,
                        "experience_level": experience_level,
                        "interviewer_type": interviewer_type,
                        "years_of_experience": years_of_experience,
                        "gender": gender,
                        "ethnicity": ethnicity
                    }
                    result = make_api_call("/interviewer/add", method="POST", data=interviewer_data)
                    if result:
                        st.success(f"Interviewer added successfully! ID: {result['interviewer_id']}")
                except json.JSONDecodeError:
                    st.error("Invalid availability JSON format")
    
    # List Interviewers
    with st.expander("Existing Interviewers"):
        st.subheader("View Interviewers")
        col1, col2 = st.columns([3, 1])
        with col2:
            department_filter = st.text_input("Filter by Department (Optional)", key="interviewer_dept")
            interviewer_type_filter = st.selectbox("Filter by Interviewer Type (Optional)", [None, "technical", "behavioral", "domain_expert", "hr", "manager"], key="interviewer_type")
            skip = st.number_input("Skip", min_value=0, value=0, key="interviewer_skip")
            limit = st.number_input("Limit", min_value=1, max_value=100, value=20, key="interviewer_limit")
            if st.button("List Interviewers"):
                query = f"/interviewers?skip={skip}&limit={limit}"
                if department_filter:
                    query += f"&department={department_filter}"
                if interviewer_type_filter:
                    query += f"&interviewer_type={interviewer_type_filter}"
                interviewers_data = make_api_call(query)
                if interviewers_data and interviewers_data["interviewers"]:
                    df = pd.DataFrame(interviewers_data["interviewers"])
                    st.dataframe(
                        df[["_id", "name", "email", "department", "interviewer_type", "experience_level", "gender", "ethnicity"]],
                        use_container_width=True,
                        column_config={
                            "_id": st.column_config.TextColumn("ID", width="medium"),
                            "name": st.column_config.TextColumn("Name", width="medium"),
                            "email": st.column_config.TextColumn("Email", width="large"),
                            "department": st.column_config.TextColumn("Department", width="medium"),
                            "interviewer_type": st.column_config.TextColumn("Type", width="medium"),
                            "experience_level": st.column_config.TextColumn("Level", width="small"),
                            "gender": st.column_config.TextColumn("Gender", width="small"),
                            "ethnicity": st.column_config.TextColumn("Ethnicity", width="medium")
                        }
                    )
                    type_counts = df["interviewer_type"].value_counts()
                    fig = px.pie(names=type_counts.index, values=type_counts.values, title="Interviewer Type Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No interviewers found.")

# Manage Candidates
elif page == "Manage Candidates":
    st.header("Manage Candidates 🎓")
    
    # Register Candidate
    with st.expander("Register New Candidate", expanded=True):
        with st.form("register_candidate_form"):
            st.subheader("Candidate Details")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", placeholder="e.g., Jane Smith")
                email = st.text_input("Email", placeholder="e.g., jane.smith@example.com")
                job_role = st.text_input("Job Role", placeholder="e.g., Data Scientist")
            with col2:
                skills = st.text_input("Skills (comma-separated)", placeholder="e.g., Machine Learning, Python")
                experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior", "lead"])
            submit_candidate = st.form_submit_button("Register Candidate")
            
            if submit_candidate:
                candidate_data = {
                    "name": name,
                    "email": email,
                    "job_role": job_role,
                    "skills": [skill.strip() for skill in skills.split(",")],
                    "experience_level": experience_level
                }
                result = make_api_call("/candidate/register", method="POST", data=candidate_data)
                if result:
                    st.success(f"Candidate registered successfully! ID: {result['candidate_id']}")
    
    # List Candidates
    with st.expander("Existing Candidates"):
        st.subheader("View Candidates")
        col1, col2 = st.columns([3, 1])
        with col2:
            job_role_filter = st.text_input("Filter by Role (Optional)", key="candidate_role")
            skip = st.number_input("Skip", min_value=0, value=0, key="candidate_skip")
            limit = st.number_input("Limit", min_value=1, max_value=100, value=20, key="candidate_limit")
            if st.button("List Candidates"):
                query = f"/candidates?skip={skip}&limit={limit}"
                if job_role_filter:
                    query += f"&job_role={job_role_filter}"
                candidates_data = make_api_call(query)
                if candidates_data and candidates_data["candidates"]:
                    df = pd.DataFrame(candidates_data["candidates"])
                    st.dataframe(
                        df[["_id", "name", "email", "job_role", "experience_level"]],
                        use_container_width=True,
                        column_config={
                            "_id": st.column_config.TextColumn("ID", width="medium"),
                            "name": st.column_config.TextColumn("Name", width="medium"),
                            "email": st.column_config.TextColumn("Email", width="large"),
                            "job_role": st.column_config.TextColumn("Job Role", width="medium"),
                            "experience_level": st.column_config.TextColumn("Level", width="small")
                        }
                    )
                    level_counts = df["experience_level"].value_counts()
                    fig = px.bar(x=level_counts.index, y=level_counts.values, labels={"x": "Experience Level", "y": "Number of Candidates"}, title="Candidates by Experience Level")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No candidates found.")

# Panel Recommendations
elif page == "Panel Recommendations":
    st.header("Panel Recommendations 📊")
    
    with st.expander("Generate Panel Recommendations", expanded=True):
        st.subheader("Select Criteria")
        jobs_data = make_api_call("/jobs?skip=0&limit=100")
        candidates_data = make_api_call("/candidates?skip=0&limit=100")
        
        job_options = {None: "Select a Job"} if not jobs_data or not jobs_data["jobs"] else {j["_id"]: f"{j['job_role']} ({j['_id']})" for j in jobs_data["jobs"]}
        candidate_options = {None: "Select a Candidate"} if not candidates_data or not candidates_data["candidates"] else {c["_id"]: f"{c['name']} ({c['_id']})" for c in candidates_data["candidates"]}
        
        col1, col2 = st.columns(2)
        with col1:
            job_id = st.selectbox("Select Job for Panel Recommendation", options=list(job_options.keys()), format_func=lambda x: job_options[x])
        with col2:
            candidate_id = st.selectbox("Select Candidate for Panel Recommendation", options=list(candidate_options.keys()), format_func=lambda x: candidate_options[x])
        
        if st.button("Get Recommendations"):
            if job_id or candidate_id:
                if candidate_id:
                    result = make_api_call(f"/candidate/{candidate_id}/suggest_panel")
                else:
                    result = make_api_call(f"/job/{job_id}/recommend_panel")
                
                if result:
                    st.subheader("Recommended Panel")
                    panel_data = []
                    for member in result["recommended_panel"]:
                        badge_class = {
                            "none": "badge-none",
                            "potential": "badge-potential",
                            "confirmed": "badge-confirmed"
                        }[member["conflict_status"].lower()]
                        dei_status = member.get("dei_compliance_status", "Compliant")
                        dei_badge = "badge-dei-compliant" if dei_status == "Compliant" else "badge-confirmed"
                        st.markdown(f"""
                            - **{member['name']}** (ID: {member['interviewer_id']}, Role: {member['role_in_panel']}, Match Score: {member['match_score']:.2f})
                              - Reason: {member['recommendation_reason']}
                              - Conflict Status: <span class="{badge_class}">{member['conflict_status'].capitalize()}</span>
                              - DEI Compliance: <span class="{dei_badge}">{dei_status}</span>
                        """, unsafe_allow_html=True)
                        if member['conflict_status'] != "none":
                            st.markdown(f"  - Conflict Details: {member.get('conflict_details', 'N/A')}")
                        if dei_status != "Compliant":
                            st.markdown(f"  - DEI Issues: {member.get('dei_issues', 'N/A')}")
                        panel_data.append({
                            "Name": member["name"],
                            "Role": member["role_in_panel"],
                            "Match Score": member["match_score"],
                            "Conflict Status": member["conflict_status"],
                            "DEI Compliance": dei_status
                        })
                    st.table(pd.DataFrame(panel_data))
                    
                    st.subheader("Detailed Analysis")
                    with st.container():
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Skill Coverage**")
                            skills = result["skill_coverage"]
                            st.metric("Coverage Score", f"{skills['coverage_score']:.2f}")
                            st.write(f"Covered Skills: {', '.join(skills['covered_skills'])}")
                            st.write(f"Missing Skills: {', '.join(skills['missing_skills'])}")
                            skill_data = {
                                "Status": ["Covered", "Missing"],
                                "Count": [len(skills["covered_skills"]), len(skills["missing_skills"])]
                            }
                            fig = px.bar(skill_data, x="Status", y="Count", title="Skill Coverage Analysis")
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.write("**Quality Metrics**")
                            quality = result["quality_metrics"]
                            st.metric("Overall Quality", f"{quality['overall_quality']:.2f}")
                            st.metric("Panel Size", quality["panel_size"])
                            st.metric("Quality Rating", quality["quality_rating"].capitalize())
                            fig = go.Figure(data=[
                                go.Pie(labels=["Quality Score"], values=[quality["overall_quality"], 1-quality["overall_quality"]], 
                                       hole=0.4, textinfo="none", marker_colors=["#4CAF50", "#e0e0e0"])
                            ])
                            fig.update_layout(title="Quality Score Distribution", showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    st.write("**Conflict Summary**")
                    conflict_summary = result.get("conflict_summary", {})
                    st.metric("Overall Conflict Level", conflict_summary.get("overall_conflict_level", "None"))
                    st.write(f"Conflicts Detected: {', '.join(conflict_summary.get('conflicts_detected', []))}")
                    
                    st.write("**DEI Compliance Summary**")
                    dei_summary = result.get("dei_summary", {})
                    st.metric("DEI Compliance Score", f"{dei_summary.get('compliance_score', 0.0):.2f}")
                    st.write(f"Issues Detected: {', '.join(dei_summary.get('issues_detected', []))}")
                    
                    st.write("**Alternatives**")
                    for alt in result["alternatives"]:
                        st.markdown(f"- {alt['name']} (Score: {alt['overall_score']:.2f}, Reason: {alt['reason']})")