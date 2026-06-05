# ⚒️ InterviewForge AI

An AI-powered Interview Preparation Agent that helps candidates ace their technical interviews. Built using **Streamlit** and the **Google Gemini API**.

## Features

- 📄 **Resume Parsing**: Automatically extracts text from PDF and DOCX resumes.
- 🤖 **AI Resume Analyzer**: Analyzes your resume for strengths, weaknesses, and missing skills.
- 🎤 **Interview Question Generator**: Generates tailored HR, Technical, Behavioral, and Project-based questions (10 per category).
- 🗺️ **Learning Roadmap**: Builds a customized 30-60-90 day learning plan based on skill gaps.
- 📊 **Candidate Readiness Score**: Evaluates readiness with interactive Plotly radar charts and progress bars.
- 💡 **Actionable Recommendations**: Offers specific suggestions for resume tweaks, certifications, and portfolio improvements.
- 🧐 **Explainable AI**: Includes "Why this recommendation was made" for full transparency.

## Architecture & Project Structure

The project follows a clean, modular architecture:
```
project/
├── app.py                      # Streamlit frontend application
├── services/
│   ├── resume_parser.py        # PDF & DOCX processing
│   ├── gemini_service.py       # LLM API integration wrapper
│   ├── analyzer.py             # Resume analysis and scoring logic
│   └── roadmap.py              # 90-day learning plan generator
├── utils/
│   └── helpers.py              # JSON parsing and string manipulation utilities
├── assets/
│   └── style.css               # Custom sleek dashboard styling
├── requirements.txt            # Python dependencies
└── .env.example                # Example environment variable file
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "AI resume analyzer"
   ```

2. **Set up a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   - Copy `.env.example` to `.env`
   - Add your Gemini API Key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Screenshots
*(Add screenshots of the Dashboard, Interview Prep, Roadmap, and Recommendations tabs here for your Loom video demo)*
- `[Screenshot 1 - Dashboard View]`
- `[Screenshot 2 - Generated Interview Questions]`

## Future Improvements
- Integrate GitHub API to directly review candidate code.
- Provide a mock interview interface where candidates can record answers and receive AI feedback on their voice/video.
- Allow downloading the customized roadmap as a PDF.
