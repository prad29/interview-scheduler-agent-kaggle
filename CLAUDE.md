# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An enterprise-grade agentic AI recruitment system built with Google ADK (Generative AI SDK) for automated candidate evaluation and interview scheduling. Uses Google's Gemini 2.0 Flash models for AI processing.

## Setup Commands

### Initial Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY from https://aistudio.google.com/app/apikey

# Setup Google Calendar authentication (optional, for interview scheduling)
python scripts/setup_calendar_auth.py

# Seed database with test data (optional)
python scripts/seed_data.py
```

### Running the Application

```bash
# Start FastAPI server (development mode with auto-reload)
python api/main.py
# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs

# Start Streamlit dashboard (separate terminal)
streamlit run dashboard/app.py
# Dashboard will be available at http://localhost:8501

# Run batch processing script
python scripts/run_batch_processing.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents/test_orchestrator.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run tests in verbose mode
pytest -v

# Run specific test function
pytest tests/test_agents/test_skills_matcher.py::test_skills_matching
```

### Database

The system uses SQLite by default (`recruitment.db`). To use PostgreSQL, update `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/recruitment_db
```

## Architecture

### Multi-Agent System

The system follows a hierarchical multi-agent architecture where specialized agents coordinate through the OrchestratorAgent:

1. **OrchestratorAgent** (`agents/orchestrator_agent.py`) - Master coordinator that manages the entire recruitment workflow:
   - Orchestrates parallel processing of resumes
   - Coordinates evaluation across multiple agents
   - Implements weighted scoring algorithm for candidate ranking
   - Filters qualified candidates based on configurable thresholds

2. **ResumeParserAgent** (`agents/resume_parser_agent.py`) - Extracts structured data from resumes:
   - Parses personal info, work experience, education, skills
   - Handles both PDF and DOCX formats
   - Uses prompts from `prompts/resume_parser_prompts.py`

3. **SkillsMatcherAgent** (`agents/skills_matcher_agent.py`) - Matches candidate skills with job requirements:
   - Calculates skills match score
   - Identifies matched and missing skills
   - Provides recommendation (strong_match/moderate_match/weak_match)
   - Uses prompts from `prompts/skills_matcher_prompts.py`

4. **CulturalFitAgent** (`agents/cultural_fit_agent.py`) - Analyzes cultural alignment:
   - Evaluates dimensional scores across multiple culture dimensions
   - Provides cultural fit score and rationale
   - Uses prompts from `prompts/cultural_fit_prompts.py`

5. **InterviewSchedulerAgent** (`agents/interview_scheduler_agent.py`) - Automates interview scheduling:
   - Integrates with Google Calendar API
   - Sends email invitations
   - Uses prompts from `prompts/interview_scheduler_prompts.py`

**Agent Communication Flow:**
```
Client Request → OrchestratorAgent
                      ↓
      ┌───────────────┼───────────────┐
      ↓               ↓               ↓
ResumeParserAgent  (processes N resumes in parallel)
      ↓
OrchestratorAgent (coordinates evaluation)
      ↓
      ┌───────────────┴───────────────┐
      ↓                               ↓
SkillsMatcherAgent          CulturalFitAgent
  (parallel evaluation)     (parallel evaluation)
      ↓                               ↓
      └───────────────┬───────────────┘
                      ↓
      OrchestratorAgent (ranks candidates)
                      ↓
      InterviewSchedulerAgent (schedules top candidates)
```

### BaseAgent Pattern

All agents inherit from `BaseAgent` (`agents/base_agent.py`) which provides:
- Google Generative AI configuration and API key management
- `_generate_response()` - Standard text generation
- `_generate_response_with_tools()` - Tool-augmented generation
- Logging utilities (`log_info()`, `log_error()`, `log_debug()`)
- Abstract `process()` method that all agents must implement

Each agent's `process()` method takes a dictionary of input data and returns a dictionary of results.

### Configuration

Configuration is centralized in `config.py` with a `Config` class that:
- Loads environment variables from `.env` using python-dotenv
- Provides sensible defaults for all settings
- Includes a `validate()` method that checks required configuration
- Key settings:
  - `GOOGLE_API_KEY` - Required for Google Gemini API
  - `DEFAULT_MODEL` - Defaults to "gemini-2.0-flash-exp"
  - Scoring thresholds: `SKILLS_MATCH_THRESHOLD`, `CULTURAL_FIT_THRESHOLD`
  - Scoring weights: `SKILLS_WEIGHT`, `CULTURAL_FIT_WEIGHT`, `EXPERIENCE_WEIGHT`
  - Database URL, storage paths, SMTP settings

Import as: `from config import config`

### Prompts System

System prompts for each agent are centralized in `prompts/` directory. Each agent has a corresponding prompts file that exports system instructions and prompt templates. When modifying agent behavior, update the prompts file rather than hardcoding prompts in agent code.

### API Structure

FastAPI application in `api/`:
- `main.py` - Application entry point, CORS configuration, exception handlers
- `routes/candidate_routes.py` - Resume upload, batch processing, candidate management
- `routes/job_routes.py` - Job description management
- `routes/interview_routes.py` - Interview scheduling endpoints
- `middleware/auth.py` - Authentication middleware (uses `get_current_user` dependency)

All routes use `/api` prefix (e.g., `/api/candidates`, `/api/jobs`).

### Tools

Utility tools in `tools/`:
- `pdf_parser.py` - PDF text extraction using PyPDF2 and pdfplumber
- `docx_parser.py` - DOCX text extraction using python-docx
- `data_validator.py` - Input validation and sanitization
- `calendar_integration.py` - Google Calendar API integration
- `email_service.py` - SMTP email sending

### Storage

Storage layer in `storage/`:
- `database.py` - SQLAlchemy models and database session management
- `file_storage.py` - File system operations for resume storage

### Models

Pydantic models in `models/` for data validation:
- `candidate.py` - Candidate data structures
- `job_description.py` - Job description structures
- `evaluation_result.py` - Evaluation result structures
- `interview_slot.py` - Interview scheduling structures

### Utilities

Helper functions in `utils/`:
- `logger.py` - Logging configuration with `setup_logger()` function
- `helpers.py` - Common utility functions
- `config_loader.py` - Configuration loading utilities

### Dashboard

Streamlit dashboard in `dashboard/`:
- `app.py` - Main dashboard application
- `components/` - Reusable UI components
- `pages/` - Multi-page dashboard sections

## Important Development Notes

### Working with Agents

- All agents use async/await - ensure you use `await` when calling agent methods
- The orchestrator runs agents in parallel where possible (resume parsing, evaluation)
- Agent errors are caught and logged - check `logs/` directory for debugging
- Model name is configurable via `DEFAULT_MODEL` in config

### Google Gemini API

- The system uses `google-generativeai` SDK (not the older `google-adk` package)
- API key must be set in `.env` as `GOOGLE_API_KEY`
- Default model is "gemini-2.0-flash-exp" (experimental fast model)
- Temperature is configurable per agent (default 1.0)
- Tool usage is supported via `_generate_response_with_tools()`

### Error Handling

- API uses FastAPI exception handlers for consistent error responses
- Agents log errors with context using the logging utilities
- Debug mode (DEBUG=True) includes detailed error information in API responses

### File Uploads

- Resume uploads are handled by `candidate_routes.py`
- Supported formats: PDF, DOCX (max 10MB)
- Files stored in `data/uploaded_resumes/` with timestamp prefix
- File extraction happens during batch processing, not upload

### Authentication

- Auth middleware in `api/middleware/auth.py` provides `get_current_user` dependency
- Currently returns a mock user - implement actual auth as needed
- All API routes use `Depends(get_current_user)` for protection

### Database Operations

- Default is SQLite (`recruitment.db` in root directory)
- SQLAlchemy models are in `storage/database.py`
- Many TODO comments indicate incomplete database integration
- Database queries are stubbed in several route handlers

### Scoring Algorithm

The orchestrator calculates weighted scores:
```python
overall_score = (
    skills_score * SKILLS_WEIGHT +        # Default: 0.6
    cultural_score * CULTURAL_FIT_WEIGHT +  # Default: 0.3
    experience_score * EXPERIENCE_WEIGHT    # Default: 0.1
)
```

Candidate tiers:
- strong_match: ≥85% overall score
- moderate_match: 70-84% overall score
- weak_match: <70% overall score

Qualification thresholds (configurable in config):
- Skills match: ≥70% (SKILLS_MATCH_THRESHOLD)
- Cultural fit: ≥65% (CULTURAL_FIT_THRESHOLD)

### Parallel Processing

The orchestrator uses `asyncio.gather()` for parallel processing:
- All resumes parsed in parallel in Phase 1
- Each candidate's skills and cultural fit evaluated in parallel in Phase 2
- This significantly improves performance for batch processing

## Common Gotchas

1. **API Key**: The system will fail at startup if `GOOGLE_API_KEY` is not set
2. **Virtual Environment**: Always activate venv before running any commands
3. **Async/Await**: Agent methods are async - forgetting `await` will cause errors
4. **File Paths**: Storage paths are configurable - check config if files aren't found
5. **Google Calendar**: Calendar integration is optional but requires OAuth setup via `setup_calendar_auth.py`
6. **Database**: Many endpoints have TODO comments for database integration - they currently return mock data or empty lists
