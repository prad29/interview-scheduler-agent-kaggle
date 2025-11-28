"""
Utils package for helper functions and utilities

This package contains utility modules for:
- Logging configuration and setup
- Configuration loading and management
- Helper functions for common tasks
- General purpose utilities
"""

from .logger import (
    setup_logger,
    get_logger,
    log_execution_time,
    log_function_call
)
from .config_loader import (
    load_config,
    get_config_value,
    validate_config
)
from .helpers import (
    generate_id,
    format_date,
    parse_date,
    calculate_age,
    format_currency,
    truncate_text,
    clean_text,
    extract_keywords,
    calculate_similarity,
    chunk_list,
    retry_on_failure,
    measure_time
)

__all__ = [
    # Logger utilities
    'setup_logger',
    'get_logger',
    'log_execution_time',
    'log_function_call',
    
    # Config utilities
    'load_config',
    'get_config_value',
    'validate_config',
    
    # Helper functions
    'generate_id',
    'format_date',
    'parse_date',
    'calculate_age',
    'format_currency',
    'truncate_text',
    'clean_text',
    'extract_keywords',
    'calculate_similarity',
    'chunk_list',
    'retry_on_failure',
    'measure_time'
]

__version__ = '1.0.0'