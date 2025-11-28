"""
Helper Functions

General purpose utility functions for common tasks.
"""

import re
import uuid
import hashlib
from datetime import datetime, date
from typing import Any, List, Optional, Callable, TypeVar
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def generate_id(prefix: str = '', length: int = 8) -> str:
    """
    Generate a unique identifier
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of random part (default: 8)
        
    Returns:
        Unique identifier string
    """
    random_part = str(uuid.uuid4()).replace('-', '')[:length]
    
    if prefix:
        return f"{prefix}_{random_part}"
    else:
        return random_part


def generate_hash(text: str, algorithm: str = 'sha256') -> str:
    """
    Generate hash of text
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm ('md5', 'sha256', 'sha512')
        
    Returns:
        Hash string
    """
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def format_date(
    dt: datetime,
    format_str: str = '%Y-%m-%d %H:%M:%S'
) -> str:
    """
    Format datetime object to string
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    if dt is None:
        return ''
    
    return dt.strftime(format_str)


def parse_date(
    date_str: str,
    format_str: str = '%Y-%m-%d'
) -> Optional[datetime]:
    """
    Parse date string to datetime object
    
    Args:
        date_str: Date string
        format_str: Expected format
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse date: {date_str}")
        return None


def calculate_age(birth_date: date) -> int:
    """
    Calculate age from birth date
    
    Args:
        birth_date: Date of birth
        
    Returns:
        Age in years
    """
    today = date.today()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


def format_currency(
    amount: float,
    currency: str = 'USD',
    locale: str = 'en_US'
) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Monetary amount
        currency: Currency code (USD, EUR, etc.)
        locale: Locale for formatting
        
    Returns:
        Formatted currency string
    """
    # Simple implementation without babel
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    elif currency == 'GBP':
        return f"£{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = '...'
) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ''
    
    # Remove extra whitespace
    cleaned = ' '.join(text.split())
    
    # Remove control characters
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')
    
    return cleaned.strip()


def extract_keywords(
    text: str,
    min_length: int = 3,
    max_keywords: int = 20
) -> List[str]:
    """
    Extract keywords from text
    
    Simple implementation that extracts unique words.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum word length
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    # Convert to lowercase and split
    words = text.lower().split()
    
    # Remove punctuation and filter by length
    keywords = []
    for word in words:
        # Remove punctuation
        word = re.sub(r'[^\w\s]', '', word)
        
        # Check length and if not already in list
        if len(word) >= min_length and word not in keywords:
            keywords.append(word)
        
        if len(keywords) >= max_keywords:
            break
    
    return keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple algorithm
    
    Uses Jaccard similarity on word sets.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split list into chunks of specified size
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    chunks = []
    
    for i in range(0, len(lst), chunk_size):
        chunks.append(lst[i:i + chunk_size])
    
    return chunks


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on failure
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch
        
    Usage:
        @retry_on_failure(max_attempts=3, delay=1.0)
        def unstable_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {str(e)}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    
    return decorator


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time
    
    Usage:
        @measure_time
        def slow_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper


def flatten_dict(
    d: dict,
    parent_key: str = '',
    sep: str = '.'
) -> dict:
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def unflatten_dict(d: dict, sep: str = '.') -> dict:
    """
    Unflatten dictionary with dot-notation keys
    
    Args:
        d: Flattened dictionary
        sep: Separator used in keys
        
    Returns:
        Nested dictionary
    """
    result = {}
    
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    try:
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def percentage(part: float, total: float, decimals: int = 2) -> float:
    """
    Calculate percentage
    
    Args:
        part: Part value
        total: Total value
        decimals: Number of decimal places
        
    Returns:
        Percentage value
    """
    if total == 0:
        return 0.0
    
    result = (part / total) * 100
    return round(result, decimals)


def normalize_string(s: str) -> str:
    """
    Normalize string for comparison
    
    Args:
        s: String to normalize
        
    Returns:
        Normalized string (lowercase, no extra spaces)
    """
    return ' '.join(s.lower().split())


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if string is a valid UUID
    
    Args:
        uuid_string: String to check
        
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, AttributeError):
        return False