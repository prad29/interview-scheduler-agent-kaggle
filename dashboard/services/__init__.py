"""
Services package for data fetching
"""

from .data_service import (
    get_jobs,
    get_candidates,
    get_interviews,
    get_metrics,
    get_recent_activities
)

__all__ = [
    'get_jobs',
    'get_candidates',
    'get_interviews',
    'get_metrics',
    'get_recent_activities'
]
