# 🤖 Intelligent Recruitment & Talent Matching System

An enterprise-grade AI-powered recruitment system built with **Google Gemini 2.0 Flash** for automated candidate evaluation, skills matching, cultural fit analysis, and interview scheduling.

## 🌟 Features

### Multi-Agent AI System
- **Resume Parser Agent**: Extracts structured data from PDF/DOCX resumes
- **Skills Matcher Agent**: Intelligent matching of candidate skills with job requirements
- **Cultural Fit Agent**: Analyzes candidate alignment with company culture
- **Interview Scheduler Agent**: Automates interview scheduling with Google Calendar integration
- **Orchestrator Agent**: Coordinates all agents for end-to-end workflow

### Smart Candidate Evaluation
- **AI-Powered Scoring**: Weighted scoring algorithm (Skills 60%, Cultural Fit 30%, Experience 10%)
- **Automatic Ranking**: Candidates ranked by overall score
- **Tier Classification**: Strong Match (≥85%), Moderate Match (70-84%), Weak Match (<70%)
- **Detailed Insights**: Skills analysis, cultural fit rationale, and recommendations

### Automation Features
- **Batch Resume Processing**: Process multiple resumes simultaneously
- **Parallel Evaluation**: Multiple agents run in parallel for speed
- **Auto Interview Scheduling**: Automatically schedule interviews for top candidates
- **Email Notifications**: Send interview invitations to candidates and interviewers
- **Calendar Integration**: Seamless Google Calendar integration

### Interactive Dashboard
- **Streamlit UI**: Modern, intuitive web interface
- **Real-time Processing**: Live progress updates during evaluation
- **Candidate Management**: View, filter, and search candidates
- **Interview Management**: Track and manage scheduled interviews
- **Job Management**: Create and manage job descriptions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google API Key (for Gemini AI)
- Google Calendar API credentials (optional, for interview scheduling)
- Gmail account with App Password (optional, for email notifications)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intelligent-recruitment-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or: venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   # Required
   GOOGLE_API_KEY=your_google_api_key_here

   # Optional - For interview scheduling
   GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

5. **Get Google API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create an API key
   - Add to `.env` file

### Running the Application

**Option 1: Streamlit Dashboard (Recommended)**
```bash
streamlit run dashboard/app.py
```
Access at: http://localhost:8501

**Option 2: FastAPI Backend**
```bash
python api/main.py
```
Access at: http://localhost:8000
API Docs: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Create a Job Description

1. Go to **Jobs** page → **Create New Job** tab
2. Fill in job details:
   - Basic information (title, location, experience level)
   - Required and preferred skills
   - Responsibilities
   - Company culture values
   - Compensation range
3. Click **Save Job Description**

### 2. Upload and Process Resumes

1. Go to **Candidates** page → **Upload Resumes** tab
2. Select the job from dropdown
3. Upload resume files (PDF or DOCX, max 10MB each)
4. (Optional) Check "Automatically schedule interviews" and enter interviewer email
5. Click **🚀 Process Resumes**
6. Wait 30-60 seconds for AI evaluation
7. View results in **All Candidates** tab

### 3. View Candidate Rankings

1. Go to **Candidates** page → **All Candidates** tab
2. View ranked candidates with scores:
   - Overall Score
   - Skills Match Score
   - Cultural Fit Score
   - Tier (Strong/Moderate/Weak Match)
3. Click on a candidate to see detailed evaluation
4. Use filters to narrow down candidates

### 4. Manage Interviews

1. Go to **Interviews** page
2. View all scheduled interviews
3. Filter by status, date, or candidate
4. Schedule new interviews manually if needed

## 🏗️ Architecture

### Multi-Agent Workflow

```
Client Request → OrchestratorAgent
                      ↓
      ┌───────────────┼───────────────┐
      ↓               ↓               ↓
ResumeParserAgent  (parallel processing)
      ↓
OrchestratorAgent (coordinates evaluation)
      ↓
      ┌───────────────┴───────────────┐
      ↓                               ↓
SkillsMatcherAgent          CulturalFitAgent
  (parallel)                   (parallel)
      ↓                               ↓
      └───────────────┬───────────────┘
                      ↓
      OrchestratorAgent (ranks & filters)
                      ↓
      InterviewSchedulerAgent (top candidates)
```

### Technology Stack

**Backend:**
- Python 3.8+
- Google Generative AI SDK (Gemini 2.0 Flash)
- FastAPI (REST API)
- SQLAlchemy (ORM)
- SQLite/PostgreSQL (Database)

**Frontend:**
- Streamlit (Interactive Dashboard)
- Plotly (Data Visualization)

**AI & Processing:**
- Google Gemini 2.0 Flash (AI Model)
- PyPDF2 & pdfplumber (PDF Extraction)
- python-docx (DOCX Extraction)

**Integrations:**
- Google Calendar API (Interview Scheduling)
- SMTP (Email Notifications)

## 📁 Project Structure

```
intelligent-recruitment-system/
├── agents/                      # AI Agent implementations
│   ├── base_agent.py           # Base agent class
│   ├── orchestrator_agent.py   # Master coordinator
│   ├── resume_parser_agent.py  # Resume parsing
│   ├── skills_matcher_agent.py # Skills matching
│   ├── cultural_fit_agent.py   # Cultural fit analysis
│   └── interview_scheduler_agent.py # Interview scheduling
├── api/                         # FastAPI backend
│   ├── main.py                 # API entry point
│   ├── routes/                 # API endpoints
│   └── middleware/             # Authentication & middleware
├── dashboard/                   # Streamlit frontend
│   ├── app.py                  # Dashboard entry point
│   ├── pages/                  # Dashboard pages
│   ├── components/             # Reusable UI components
│   └── services/               # Data fetching services
├── tools/                       # Utility tools
│   ├── pdf_parser.py           # PDF text extraction
│   ├── docx_parser.py          # DOCX text extraction
│   ├── calendar_integration.py # Google Calendar
│   └── email_service.py        # Email sending
├── storage/                     # Data persistence
│   ├── database.py             # SQLAlchemy models
│   └── file_storage.py         # File operations
├── models/                      # Pydantic models
├── prompts/                     # AI prompts
├── config.py                    # Configuration
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

## ⚙️ Configuration

### Scoring Weights

Adjust in `config.py`:
```python
SKILLS_WEIGHT = 0.6        # 60% weight
CULTURAL_FIT_WEIGHT = 0.3  # 30% weight
EXPERIENCE_WEIGHT = 0.1    # 10% weight
```

### Qualification Thresholds

```python
SKILLS_MATCH_THRESHOLD = 70     # Minimum 70% skills match
CULTURAL_FIT_THRESHOLD = 65     # Minimum 65% cultural fit
```

### AI Model

```python
DEFAULT_MODEL = "gemini-2.0-flash-exp"  # Fast, cost-effective
# Alternative: "gemini-1.5-pro" for more complex analysis
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_agents/test_orchestrator.py
```

### Manual Testing Scripts
```bash
# Test resume processing
python test_resume_upload.py

# Test interview scheduling
python test_interview_scheduling.py

# Process resume manually
python manually_process_resume.py
```

## 🔧 Troubleshooting

### Common Issues

**1. "GOOGLE_API_KEY not found"**
- Solution: Add API key to `.env` file

**2. "Failed to extract text from PDF"**
- Cause: Image-based PDF without searchable text
- Solution: Use text-based PDFs or enable OCR

**3. "No candidates to display"**
- Cause: Database is empty or processing failed
- Solution: Check error messages during upload

**4. Interview scheduling not working**
- Cause: Google Calendar API not configured
- Solution: Set up OAuth credentials or disable auto-scheduling

### Enable Debug Logging

In `.env`:
```env
DEBUG=True
```

Check logs:
```bash
tail -f logs/api.log
tail -f logs/recruitment_system_*.log
```

## 📊 Performance

- **Resume Processing**: 30-60 seconds per resume
- **Parallel Processing**: Up to 5 resumes simultaneously
- **Skills Matching**: ~10-15 seconds
- **Cultural Fit Analysis**: ~10-15 seconds
- **Total Time**: ~45-90 seconds per candidate

## 🔐 Security

- API key stored in environment variables (never in code)
- Database credentials secured
- SMTP password using app-specific passwords
- OAuth for Google Calendar API
- Input validation on all user inputs
- SQL injection protection via SQLAlchemy ORM

## 🚧 Roadmap

- [ ] Support for LinkedIn profile import
- [ ] Video interview scheduling with Zoom/Meet integration
- [ ] Advanced analytics and reporting
- [ ] Candidate communication templates
- [ ] Multi-language support
- [ ] Resume scoring history and trends
- [ ] Collaborative hiring (multiple reviewers)
- [ ] ATS integration (Greenhouse, Lever, etc.)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powering the intelligent evaluation
- **Streamlit** for the interactive dashboard framework
- **FastAPI** for the high-performance API backend

## 📞 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Review [STREAMLIT_UPLOAD_FIXED.md](STREAMLIT_UPLOAD_FIXED.md) for troubleshooting

---

**Built with ❤️ using Google Gemini 2.0 Flash and Python**
