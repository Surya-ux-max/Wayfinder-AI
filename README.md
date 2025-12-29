# Wayfinder-AI

> AI-powered career guidance platform using Google Gemini for resume analysis and personalized mentorship.


## Team

**Team Name:** NOVATRIX

| Name | Role |
|------|------|
| TAMILSELVAN.P | Team Lead |
| SURYAPRAKASH | Member |
| ZERA SHAHADIYA .S | Member |
| VIHASHINI.K.S | Member |


## OVERVIEW

Wayfinder-AI analyzes resumes and provides career guidance through AI-powered conversations. Upload your resume or ask career questions to get personalized insights, skill assessments, and learning roadmaps.

## Features

-  **Resume Analysis** - PDF upload with AI-powered career insights
-  **Career Q&A** - Interactive AI mentor for career questions
-  **Skill Gaps** - Identify missing skills for target roles
-  **Roadmaps** - 90-day personalized learning plans
-  **Projects** - Tailored project suggestions
-  **Resources** - Curated learning recommendations

## Tech Stack

**Frontend:** HTML5, Tailwind CSS, JavaScript  
**Backend:** Flask (Python 3.8+)  
**AI:** Google Gemini API  
**PDF:** pdfplumber

## Quick Start

```bash
# 1. Clone and install
git clone <repository-url>
cd Wayfinder-AI
pip install -r requirements.txt

# 2. Add API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Run backend
cd backend
python app.py

# 4. Run frontend (new terminal)
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000`

## Project Structure

```
Wayfinder-AI/
├── backend/
│   ├── app.py              # Flask API
│   ├── agent.py            # AI logic
│   ├── resume_parser.py    # PDF extraction
│   └── memory.py           # State management
├── frontend/
│   ├── index.html          # UI
│   ├── script.js           # Logic
│   └── style.css           # Styles
└── requirements.txt
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/analyze` | POST | Analyze resume PDF |
| `/ask` | POST | Ask career questions |

**Example Request:**
```bash
curl -X POST http://127.0.0.1:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How to become a data scientist?", "mode": "roadmap"}'
```

## Configuration

Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key
```

Get API key: [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

1. Click "Get Started" on landing page
2. **For Resume Analysis:** Upload PDF → Click "Analyze Resume"
3. **For Questions:** Select mode → Type question → Click "Ask AI"

**Modes:** `ask`, `skill_gaps`, `projects`, `roadmap`, `resources`

## Documentation

- **[DOCUMENTATION.md](https://drive.google.com/drive/folders/1oUQz4nv3RBhm0X_SbdaEPRVK6xfWPr3o?usp=drive_link)** - Complete guide (API, deployment, architecture)

## Security Notes

⚠️ Development version - Not production-ready:
- Debug mode enabled
- No CSRF protection
- No rate limiting
- No authentication

## Known Limitations

- Resume text limited to 6000 characters
- In-memory storage (no persistence)
- No user authentication
- Single-threaded server

## Contributing

1. Fork repository
2. Create branch: `git checkout -b feature/YourFeature`
3. Commit: `git commit -m 'Add YourFeature'`
4. Push: `git push origin feature/YourFeature`
5. Open Pull Request

