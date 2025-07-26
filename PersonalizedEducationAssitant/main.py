import streamlit as st
import requests
import json
from typing import List, Dict, Any
import time
from dataclasses import dataclass
from enum import Enum

# Configuration
class Config:
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    SERPER_API_URL = "https://google.serper.dev/search"

class ExpertiseLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class LearningTask:
    task_id: int
    title: str
    description: str
    expertise_level: ExpertiseLevel
    topic: str
    completed: bool = False

class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate_response(self, prompt: str, model: str = "llama3-8b-8192") -> str:
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1,
            "stream": False
        }
        
        try:
            response = requests.post(Config.GROQ_API_URL, 
                                   headers=self.headers, 
                                   json=payload,
                                   timeout=30)
            
            if response.status_code != 200:
                st.error(f"Groq API Error {response.status_code}: {response.text}")
                return f"API Error: {response.status_code} - {response.text}"
            
            response_data = response.json()
            
            if "choices" not in response_data or not response_data["choices"]:
                st.error("Invalid response format from Groq API")
                return "Error: Invalid API response format"
                
            return response_data["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return "Error: Request timed out"
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")
            return f"Network Error: {str(e)}"
        except json.JSONDecodeError as e:
            st.error(f"JSON decode error: {str(e)}")
            return f"JSON Error: {str(e)}"
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return f"Error: {str(e)}"

class SerperClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

    def search_learning_materials(self, query: str, num_results: int = 5) -> List[Dict]:
        payload = {
            "q": f"{query} tutorial learning resources",
            "num": num_results
        }
        
        try:
            response = requests.post(Config.SERPER_API_URL, 
                                   headers=self.headers, 
                                   json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("organic", [])
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return []

class PersonalizedEducationAssistant:
    def __init__(self, groq_client: GroqClient, serper_client: SerperClient):
        self.groq = groq_client
        self.serper = serper_client
        self.learning_tasks = []

    def process_sequential_tasks(self, topics: List[str], expertise_level: ExpertiseLevel) -> List[LearningTask]:
        """Process learning topics in sequential manner"""
        tasks = []
        
        for i, topic in enumerate(topics):
            prompt = f"""
            Create a learning task for {expertise_level.value} level learner on the topic: {topic}
            
            Provide:
            1. A clear task title
            2. Detailed description of what to learn
            3. Learning objectives
            4. Estimated time to complete
            
            Keep it concise and actionable.
            """
            
            response = self.groq.generate_response(prompt)
            
            # Skip if there was an error
            if "Error" in response:
                continue
            
            task = LearningTask(
                task_id=i+1,
                title=f"Learn {topic}",
                description=response,
                expertise_level=expertise_level,
                topic=topic
            )
            tasks.append(task)
        
        return tasks

    def curate_content(self, topic: str, expertise_level: ExpertiseLevel) -> Dict:
        """Curate learning materials based on user topics and expertise"""
        # Search for current materials
        search_results = self.serper.search_learning_materials(
            f"{topic} {expertise_level.value} tutorial"
        )
        
        # Generate personalized recommendations
        prompt = f"""
        Based on the topic "{topic}" for {expertise_level.value} level learners, provide:
        
        1. Core concepts to understand
        2. Learning progression path
        3. Recommended study approach
        4. Key skills to develop
        5. Common challenges and how to overcome them
        
        Make it specific and actionable.
        """
        
        ai_recommendations = self.groq.generate_response(prompt)
        
        return {
            "ai_recommendations": ai_recommendations,
            "web_resources": search_results[:3],  # Top 3 results
            "topic": topic,
            "level": expertise_level.value
        }

    def generate_quiz(self, topic: str, expertise_level: ExpertiseLevel, num_questions: int = 5) -> Dict:
        """Generate personalized quizzes"""
        prompt = f"""
        Create a {num_questions}-question quiz on "{topic}" for {expertise_level.value} level learners.
        
        Format each question as:
        Q: [Question]
        A) [Option A]
        B) [Option B] 
        C) [Option C]
        D) [Option D]
        Correct Answer: [Letter]
        Explanation: [Brief explanation]
        
        Make questions progressive in difficulty and relevant to practical application.
        """
        
        quiz_content = self.groq.generate_response(prompt)
        
        return {
            "topic": topic,
            "level": expertise_level.value,
            "questions": quiz_content,
            "total_questions": num_questions
        }

    def suggest_projects(self, topic: str, expertise_level: ExpertiseLevel, user_interests: List[str] = None) -> Dict:
        """Custom tool: Project suggestion based on expertise level"""
        interests_context = f"User interests: {', '.join(user_interests)}" if user_interests else ""
        
        if expertise_level == ExpertiseLevel.BEGINNER:
            project_type = "simple, hands-on projects that build foundational skills"
        elif expertise_level == ExpertiseLevel.INTERMEDIATE:
            project_type = "moderately complex projects that integrate multiple concepts"
        else:  # Advanced
            project_type = "challenging projects that push boundaries and involve innovation"
        
        prompt = f"""
        Suggest 3 practical project ideas for "{topic}" at {expertise_level.value} level.
        Focus on {project_type}.
        {interests_context}
        
        For each project provide:
        1. Project title
        2. Brief description
        3. Key technologies/concepts involved
        4. Estimated timeline
        5. Learning outcomes
        6. Step-by-step approach outline
        
        Make projects engaging and aligned with current industry trends.
        """
        
        project_suggestions = self.groq.generate_response(prompt)
        
        return {
            "topic": topic,
            "level": expertise_level.value,
            "suggestions": project_suggestions,
            "interests": user_interests or []
        }

def main():
    st.set_page_config(
        page_title="Personalized Education Assistant", 
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Personalized Education Assistant")
    st.markdown("*Powered by Groq AI and Real-time Web Search*")
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key inputs with validation
        groq_api_key = st.text_input("Groq API Key", type="password", 
                                   help="Get your free API key from https://console.groq.com/")
        serper_api_key = st.text_input("Serper API Key", type="password",
                                     help="Get your API key from https://serper.dev/")
        
        # Model selection
        model_options = [
            "llama3-8b-8192",
            "llama3-70b-8192", 
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        selected_model = st.selectbox("Groq Model:", model_options, index=0)
        
        # API key validation
        if not groq_api_key or not serper_api_key:
            st.warning("⚠️ Please enter both API keys to continue")
            st.info("💡 **Getting API Keys:**")
            st.markdown("- **Groq**: https://console.groq.com/ (Free tier available)")
            st.markdown("- **Serper**: https://serper.dev/ (Free 2500 searches)")
            return
        
        # Test API connection
        if groq_api_key and serper_api_key:
            if st.button("🔧 Test API Connection"):
                test_groq = GroqClient(groq_api_key)
                test_response = test_groq.generate_response("Say 'API connection successful!'", selected_model)
                
                if "Error" not in test_response and "API connection successful" in test_response:
                    st.success("✅ Groq API connected successfully!")
                else:
                    st.error(f"❌ Groq API connection failed: {test_response}")
                    st.info("💡 **Troubleshooting:**")
                    st.markdown("- Check if your API key is correct")
                    st.markdown("- Ensure you have API credits remaining")
                    st.markdown("- Try a different model")
                    return
        
        st.success("✅ APIs configured")
    
    # Initialize clients
    groq_client = GroqClient(groq_api_key)
    serper_client = SerperClient(serper_api_key)
    assistant = PersonalizedEducationAssistant(groq_client, serper_client)
    
    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Learning Path", "🔍 Content Curation", "📝 Quiz Generator", "🚀 Project Ideas"])
    
    with tab1:
        st.header("Sequential Learning Path")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            topics_input = st.text_area(
                "Enter learning topics (one per line):",
                placeholder="Python basics\nWeb development\nMachine learning\nData analysis",
                height=100
            )
        
        with col2:
            expertise = st.selectbox(
                "Expertise Level:",
                options=[level.value for level in ExpertiseLevel],
                index=0
            )
        
        if st.button("Generate Learning Path", type="primary"):
            if topics_input:
                topics = [topic.strip() for topic in topics_input.split('\n') if topic.strip()]
                expertise_level = ExpertiseLevel(expertise)
                
                with st.spinner("Creating personalized learning path..."):
                    tasks = assistant.process_sequential_tasks(topics, expertise_level)
                
                # Filter out any failed tasks
                successful_tasks = [task for task in tasks if not task.description.startswith("Error")]
                
                if successful_tasks:
                    st.success(f"Generated {len(successful_tasks)} learning tasks!")
                    
                    for i, task in enumerate(successful_tasks, 1):
                        with st.expander(f"Task {i}: {task.title}", expanded=i==1):
                            st.write(task.description)
                            if st.button(f"Mark as Complete", key=f"complete_{i}"):
                                st.success("Task completed! 🎉")
                else:
                    st.error("Failed to generate learning tasks. Please check your API keys and try again.")
    
    with tab2:
        st.header("Content Curation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("Topic:", placeholder="e.g., Machine Learning")
        
        with col2:
            expertise = st.selectbox(
                "Level:",
                options=[level.value for level in ExpertiseLevel],
                key="content_expertise"
            )
        
        if st.button("Curate Content", type="primary"):
            if topic:
                expertise_level = ExpertiseLevel(expertise)
                
                with st.spinner("Curating personalized content..."):
                    content = assistant.curate_content(topic, expertise_level)
                
                st.subheader("🤖 AI Recommendations")
                st.write(content["ai_recommendations"])
                
                st.subheader("🌐 Current Web Resources")
                for resource in content["web_resources"]:
                    with st.container():
                        st.markdown(f"**[{resource.get('title', 'Resource')}]({resource.get('link', '#')})**")
                        st.write(resource.get('snippet', 'No description available'))
                        st.divider()
    
    with tab3:
        st.header("Quiz Generator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quiz_topic = st.text_input("Quiz Topic:", placeholder="e.g., Python Functions")
        
        with col2:
            quiz_expertise = st.selectbox(
                "Difficulty:",
                options=[level.value for level in ExpertiseLevel],
                key="quiz_expertise"
            )
        
        with col3:
            num_questions = st.slider("Number of Questions:", 3, 10, 5)
        
        if st.button("Generate Quiz", type="primary"):
            if quiz_topic:
                expertise_level = ExpertiseLevel(quiz_expertise)
                
                with st.spinner("Generating personalized quiz..."):
                    quiz = assistant.generate_quiz(quiz_topic, expertise_level, num_questions)
                
                st.subheader(f"📝 Quiz: {quiz['topic']} ({quiz['level'].title()} Level)")
                
                with st.container():
                    st.text_area(
                        "Quiz Questions:",
                        value=quiz["questions"],
                        height=400,
                        disabled=True
                    )
    
    with tab4:
        st.header("Project Ideas Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_topic = st.text_input("Topic:", placeholder="e.g., Web Development")
            project_expertise = st.selectbox(
                "Your Level:",
                options=[level.value for level in ExpertiseLevel],
                key="project_expertise"
            )
        
        with col2:
            interests = st.text_area(
                "Your Interests (optional):",
                placeholder="e.g., Gaming, Finance, Health",
                height=100
            )
        
        if st.button("Get Project Ideas", type="primary"):
            if project_topic:
                expertise_level = ExpertiseLevel(project_expertise)
                user_interests = [interest.strip() for interest in interests.split(',') if interest.strip()] if interests else None
                
                with st.spinner("Generating personalized project ideas..."):
                    projects = assistant.suggest_projects(project_topic, expertise_level, user_interests)
                
                st.subheader(f"🚀 Project Ideas for {projects['topic']} ({projects['level'].title()} Level)")
                
                with st.container():
                    st.write(projects["suggestions"])
    
    # Footer
    st.markdown("---")
    st.markdown("**Built with ❤️ using Streamlit, Groq API, and Serper API**")

if __name__ == "__main__":
    main()