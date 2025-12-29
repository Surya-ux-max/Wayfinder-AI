import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

genai.configure(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# Model selection (KEEP YOUR WORKING TRICK)
# --------------------------------------------------
def get_working_model():
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)
    raise RuntimeError("No compatible Gemini model found")


model = get_working_model()


# --------------------------------------------------
# Safe text extraction (DO NOT TOUCH)
# --------------------------------------------------
def extract_text(response):
    try:
        if response.candidates:
            parts = response.candidates[0].content.parts
            return "".join(part.text for part in parts if hasattr(part, "text"))
        return "AI could not generate a response."
    except Exception:
        return "AI response parsing failed."


# --------------------------------------------------
# Resume Analysis (UNCHANGED CORE IDEA)
# --------------------------------------------------
def analyze_career_profile(resume_text: str, job_description: str = ""):
    resume_text = resume_text[:6000]

    prompt = f"""
You are an Agentic AI Career Guidance Assistant.

Use clear headings and bullet points.
Avoid long paragraphs.

Provide:
## Career Summary
## Suitable Roles
## Skill Gaps
## 90-Day Roadmap
## Project Ideas
## Practical Advice

Resume:
{resume_text}

Optional Job Description:
{job_description}
"""

    response = model.generate_content(prompt, request_options={"timeout": 60})
    return extract_text(response)


# --------------------------------------------------
# FEATURE-BASED QUESTION HANDLER
# --------------------------------------------------
def handle_feature_question(mode: str, question: str):
    base_rules = """
Formatting Rules:
- Use headings (##)
- Use bullet points
- Short, clear points
- No long paragraphs
"""

    prompts = {
        "ask": f"""
You are an AI Career Mentor.
{base_rules}

User Question:
{question}
""",

        "skill_gaps": f"""
You are a Career Skill Gap Analyst.
{base_rules}

Task:
- Identify missing or weak skills
- Assume the user is asking generally unless a role is mentioned

User Question:
{question}
""",

        "projects": f"""
You are a Project Mentor.
{base_rules}

Task:
- Suggest project ideas
- Categorize by difficulty (Beginner / Intermediate / Advanced)

User Question:
{question}
""",

        "roadmap": f"""
You are a Career Roadmap Planner.
{base_rules}

Task:
- Create a clear step-by-step roadmap
- Use timelines where possible

User Question:
{question}
""",

        "resources": f"""
You are a Learning Advisor.
{base_rules}

Task:
- Suggest learning resources (topics, platforms, formats)
- Avoid links unless necessary

User Question:
{question}
"""
    }

    prompt = prompts.get(mode, prompts["ask"])

    response = model.generate_content(prompt, request_options={"timeout": 60})
    return extract_text(response)
