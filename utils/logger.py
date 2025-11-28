"""
Logging utilities

Provides logging configuration and utilities for the recruitment system.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import functools
import time


# Color codes for console output
class LogColors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    COLORS = {
        'DEBUG': LogColors.CYAN,
        'INFO': LogColors.GREEN,
        'WARNING': LogColors.YELLOW,
        'ERROR': LogColors.RED,
        'CRITICAL': LogColors.RED + LogColors.BOLD
    }
    
    def format(self, record):
        # Add color to level name
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{LogColors.RESET}"
        
        return super().format(record)


def setup_logger(
    name: str = 'recruitment_system',
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        log_file: Path to log file (creates in logs/ directory if not specified)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output to console
        file_output: Whether to output to file
        format_string: Custom format string for log messages
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Use colored formatter for console
        console_formatter = ColoredFormatter(
            fmt=format_string,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if file_output:
        # Create logs directory if it doesn't exist
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Use provided log file or generate default name
        if log_file is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file = logs_dir / f'{name}_{timestamp}.log'
        else:
            log_file = logs_dir / log_file
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        # Use regular formatter for file (no colors)
        file_formatter = logging.Formatter(
            fmt=format_string,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        setup_logger(name)
    
    return logger


def log_execution_time(func):
    """
    Decorator to log function execution time
    
    Usage:
        @log_execution_time
        def my_function():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        start_time = time.time()
        logger.debug(f"Starting execution of {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Completed {func.__name__} in {execution_time:.2f} seconds"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Failed {func.__name__} after {execution_time:.2f} seconds: {str(e)}"
            )
            raise
    
    return wrapper


def log_function_call(func):
    """
    Decorator to log function calls with arguments
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Format arguments
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        logger.debug(f"Calling {func.__name__}({signature})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result!r}")
            return result
            
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {str(e)}")
            raise
    
    return wrapper


class LoggerContext:
    """Context manager for temporary logging configuration"""
    
    def __init__(self, logger: logging.Logger, level: int):
        """
        Initialize logger context
        
        Args:
            logger: Logger to modify
            level: Temporary logging level
        """
        self.logger = logger
        self.new_level = level
        self.original_level = None
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


def temporary_log_level(logger: logging.Logger, level: int):
    """
    Temporarily change logger level
    
    Usage:
        with temporary_log_level(logger, logging.DEBUG):
            # Detailed logging here
            pass
    
    Args:
        logger: Logger instance
        level: Temporary logging level
        
    Returns:
        Context manager
    """
    return LoggerContext(logger, level)


def setup_file_rotation(
    logger_name: str,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5
):
    """
    Setup rotating file handler for logger
    
    Args:
        logger_name: Name of logger
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    """
    from logging.handlers import RotatingFileHandler
    
    logger = get_logger(logger_name)
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f'{logger_name}.log'
    
    # Create rotating handler
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    logger.info(f"Rotating file handler configured: {log_file}")


def log_system_info():
    """Log system information for debugging"""
    import platform
    import sys
    
    logger = get_logger('system')
    
    logger.info("=" * 70)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 70)
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Machine: {platform.machine()}")
    logger.info("=" * 70)


# Create default logger
default_logger = setup_logger('recruitment_system')