import streamlit as st
import os
import json
import plotly.graph_objects as go
from dotenv import load_dotenv

from services.resume_parser import ResumeParser
from services.gemini_service import GeminiClient
from services.analyzer import ResumeAnalyzer
from services.roadmap import LearningRoadmap

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="InterviewForge AI",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

# Initialize Services
@st.cache_resource
def get_services():
    try:
        client = GeminiClient()
        analyzer = ResumeAnalyzer(client)
        roadmap = LearningRoadmap(client)
        return analyzer, roadmap
    except Exception as e:
        st.error(f"Failed to initialize AI services: {e}")
        return None, None

analyzer, roadmap = get_services()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚒️ InterviewForge AI")
    st.markdown("Your Personal AI Career Coach.")
    st.divider()
    
    st.header("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=['pdf', 'docx'])
    
    st.header("2. Target Role")
    target_role = st.text_input("e.g., Data Scientist, Frontend Dev")
    
    st.header("3. Experience Level")
    experience_level = st.selectbox(
        "Select your level",
        ["Student", "Fresher", "Intern", "Junior Developer", "Mid-Level", "Senior"]
    )
    
    st.divider()
    analyze_btn = st.button("🚀 Generate AI Analysis", use_container_width=True)
    
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit & Gemini")

# --- MAIN LOGIC ---
if analyze_btn:
    if not uploaded_file:
        st.error("Please upload a resume first.")
    elif not target_role:
        st.error("Please enter a target role.")
    elif not analyzer:
        st.error("AI Services are not available. Check your API Key.")
    else:
        try:
            with st.spinner("Extracting text from document..."):
                resume_text = ResumeParser.extract_text(uploaded_file, uploaded_file.name)
            
            # Use progress bar for overall progress
            progress_bar = st.progress(0, text="Starting AI Analysis...")
            
            with st.spinner("Analyzing Resume & Finding Gaps..."):
                analysis_data = analyzer.analyze_resume(resume_text, target_role, experience_level)
                progress_bar.progress(25, text="Generating Readiness Score...")
                
                score_data = analyzer.generate_readiness_score(resume_text, target_role, experience_level)
                progress_bar.progress(50, text="Creating Interview Questions...")
                
                missing_skills = analysis_data.get("missing_skills", [])
                questions_data = analyzer.generate_interview_questions(resume_text, target_role, experience_level)
                progress_bar.progress(75, text="Building Learning Roadmap...")
                
                roadmap_data = roadmap.generate_roadmap(missing_skills, target_role, experience_level)
                progress_bar.progress(100, text="Analysis Complete!")
                
            # Store in session state to persist across tab switches
            st.session_state['analysis'] = analysis_data
            st.session_state['scores'] = score_data
            st.session_state['questions'] = questions_data
            st.session_state['roadmap'] = roadmap_data
            
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# --- DASHBOARD RENDER ---
if 'analysis' in st.session_state:
    st.title(f"Targeting: {target_role} ({experience_level})")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard & Analysis", 
        "🎤 Interview Prep", 
        "🗺️ Learning Roadmap", 
        "💡 Recommendations"
    ])
    
    # --- TAB 1: DASHBOARD ---
    with tab1:
        scores = st.session_state['scores'].get('scores', {})
        st.header("Candidate Readiness Score")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            # Overall Score Metric
            overall = scores.get('overall', 0)
            st.metric("Overall Readiness", f"{overall}/100")
            
            # Simple progress bar alternative for radar if Plotly radar is complex
            st.markdown(f"**Technical Skills**: {scores.get('technical_skills', 0)}")
            st.progress(scores.get('technical_skills', 0) / 100)
            
            st.markdown(f"**Project Quality**: {scores.get('project_quality', 0)}")
            st.progress(scores.get('project_quality', 0) / 100)
            
            st.markdown(f"**Resume Quality**: {scores.get('resume_quality', 0)}")
            st.progress(scores.get('resume_quality', 0) / 100)
            
            st.markdown(f"**Industry Readiness**: {scores.get('industry_readiness', 0)}")
            st.progress(scores.get('industry_readiness', 0) / 100)
            
        with col2:
            # Plotly Radar Chart
            categories = ['Technical Skills', 'Project Quality', 'Resume Quality', 'Industry Readiness']
            values = [
                scores.get('technical_skills', 0),
                scores.get('project_quality', 0),
                scores.get('resume_quality', 0),
                scores.get('industry_readiness', 0)
            ]
            # Close the loop
            categories = categories + [categories[0]]
            values = values + [values[0]]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                line_color='#6366f1',
                fillcolor='rgba(99, 102, 241, 0.4)'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("🤔 Why this score?"):
            st.write(st.session_state['scores'].get('reasoning', 'No reasoning provided.'))
            
        st.divider()
        st.header("Resume Analysis")
        st.write(st.session_state['analysis'].get('summary', ''))
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💪 Key Strengths")
            for item in st.session_state['analysis'].get('strengths', []):
                st.markdown(f"- ✅ {item}")
        with c2:
            st.subheader("⚠️ Areas for Improvement")
            for item in st.session_state['analysis'].get('weaknesses', []):
                st.markdown(f"- ❌ {item}")
                
        st.subheader("🎯 Missing Skills for Role")
        tags = "".join([f"<span style='background:#334155; padding:4px 8px; border-radius:4px; margin-right:8px;'>{s}</span>" for s in st.session_state['analysis'].get('missing_skills', [])])
        st.markdown(tags, unsafe_allow_html=True)
        
        st.info(f"**Recruiter Feedback**: {st.session_state['analysis'].get('recruiter_feedback', '')}")
        with st.expander("🤔 Why this analysis?"):
            st.write(st.session_state['analysis'].get('reasoning', ''))

    # --- TAB 2: INTERVIEW PREP ---
    with tab2:
        st.header("Tailored Interview Questions")
        q_data = st.session_state['questions']
        
        with st.expander("🤔 Why these questions?", expanded=True):
            st.write(q_data.get('reasoning', ''))
            
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            st.subheader("🤝 HR & Culture Fit")
            for i, q in enumerate(q_data.get('hr_questions', []), 1):
                st.markdown(f"**{i}.** {q}")
                
            st.subheader("🧠 Behavioral")
            for i, q in enumerate(q_data.get('behavioral_questions', []), 1):
                st.markdown(f"**{i}.** {q}")
        with q_col2:
            st.subheader("💻 Technical")
            for i, q in enumerate(q_data.get('technical_questions', []), 1):
                st.markdown(f"**{i}.** {q}")
                
            st.subheader("📂 Project-Based")
            for i, q in enumerate(q_data.get('project_based_questions', []), 1):
                st.markdown(f"**{i}.** {q}")

    # --- TAB 3: LEARNING ROADMAP ---
    with tab3:
        st.header("Your 90-Day Upskill Roadmap")
        r_data = st.session_state['roadmap']
        
        with st.expander("🤔 Why this roadmap?"):
            st.write(r_data.get('reasoning', ''))
            
        phases = [('day_30', 'Days 1-30', '🌱'), ('day_60', 'Days 31-60', '🚀'), ('day_90', 'Days 61-90', '⭐')]
        
        for key, title, icon in phases:
            phase_data = r_data.get(key, {})
            st.subheader(f"{icon} {title}: {phase_data.get('focus', 'Focus')}")
            for task in phase_data.get('tasks', []):
                st.markdown(f"- {task}")
            st.markdown("---")

    # --- TAB 4: RECOMMENDATIONS ---
    with tab4:
        st.header("Actionable Recommendations")
        s_data = st.session_state['scores'].get('suggestions', {})
        
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.subheader("📝 Resume Improvements")
            for item in s_data.get('resume_improvements', []):
                st.markdown(f"- {item}")
                
            st.subheader("🏆 Suggested Certifications")
            for item in s_data.get('certifications', []):
                st.markdown(f"- {item}")
        with r_col2:
            st.subheader("💻 Project Ideas to Build")
            for item in s_data.get('project_suggestions', []):
                st.markdown(f"- {item}")
                
            st.subheader("🌐 Portfolio Enhancements")
            for item in s_data.get('portfolio', []):
                st.markdown(f"- {item}")
else:
    # Landing state
    st.info("👈 Please upload your resume and select your target role in the sidebar to begin.")
    
    st.markdown("""
    ### Welcome to InterviewForge AI
    This tool helps you prepare for interviews by providing:
    - **Resume Analysis**: Identify strengths, weaknesses, and skill gaps.
    - **Readiness Score**: Get a quantifiable measure of your preparation.
    - **Interview Questions**: Practice with tailored HR, Technical, and Behavioral questions.
    - **Learning Roadmap**: Follow a customized 90-day plan to bridge your skill gaps.
    """)
