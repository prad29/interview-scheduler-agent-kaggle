"""
Prompts package for AI agent instructions
"""

from .resume_parser_prompts import (
    RESUME_PARSER_SYSTEM_PROMPT,
    RESUME_PARSER_USER_PROMPT
)
from .skills_matcher_prompts import (
    SKILLS_MATCHER_SYSTEM_PROMPT,
    SKILLS_MATCHER_USER_PROMPT
)
from .cultural_fit_prompts import (
    CULTURAL_FIT_SYSTEM_PROMPT,
    CULTURAL_FIT_USER_PROMPT
)
from .interview_scheduler_prompts import (
    INTERVIEW_SCHEDULER_SYSTEM_PROMPT,
    INTERVIEW_EMAIL_TEMPLATE
)
from .orchestrator_prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT
)

__all__ = [
    'RESUME_PARSER_SYSTEM_PROMPT',
    'RESUME_PARSER_USER_PROMPT',
    'SKILLS_MATCHER_SYSTEM_PROMPT',
    'SKILLS_MATCHER_USER_PROMPT',
    'CULTURAL_FIT_SYSTEM_PROMPT',
    'CULTURAL_FIT_USER_PROMPT',
    'INTERVIEW_SCHEDULER_SYSTEM_PROMPT',
    'INTERVIEW_EMAIL_TEMPLATE',
    'ORCHESTRATOR_SYSTEM_PROMPT'
]