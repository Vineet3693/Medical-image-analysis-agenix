"""
Logging configuration for MIA system
Uses loguru for enhanced logging with rotation, formatting, and levels
"""

import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = Path("outputs/logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Remove default logger
logger.remove()

# Console output - INFO and above with colors
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# File output - DEBUG and above with rotation
log_file = LOGS_DIR / f"mia_{datetime.now().strftime('%Y%m%d')}.log"
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="100 MB",  # Rotate when file reaches 100 MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated logs
    enqueue=True  # Thread-safe
)

# Error file - ERROR and above only
error_log_file = LOGS_DIR / f"mia_errors_{datetime.now().strftime('%Y%m%d')}.log"
logger.add(
    error_log_file,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    level="ERROR",
    rotation="50 MB",
    retention="90 days",  # Keep error logs longer
    compression="zip",
    backtrace=True,  # Include full traceback
    diagnose=True,  # Include variable values
    enqueue=True
)

# Workflow execution log - separate file for workflow tracking
workflow_log_file = LOGS_DIR / f"workflow_{datetime.now().strftime('%Y%m%d')}.log"
logger.add(
    workflow_log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {extra[report_id]} | {extra[step]} | {message}",
    level="INFO",
    rotation="50 MB",
    retention="60 days",
    filter=lambda record: "report_id" in record["extra"],
    enqueue=True
)


def get_logger(name: str = None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_workflow_step(report_id: str, step: str, message: str, level: str = "INFO"):
    """
    Log a workflow step with context
    
    Args:
        report_id: Report ID for tracking
        step: Current workflow step
        message: Log message
        level: Log level (INFO, WARNING, ERROR)
    """
    workflow_logger = logger.bind(report_id=report_id, step=step)
    
    if level == "INFO":
        workflow_logger.info(message)
    elif level == "WARNING":
        workflow_logger.warning(message)
    elif level == "ERROR":
        workflow_logger.error(message)
    elif level == "DEBUG":
        workflow_logger.debug(message)


def log_api_call(service: str, endpoint: str, status: str, duration_ms: float = None):
    """
    Log API calls with timing
    
    Args:
        service: Service name (Gemini, Groq)
        endpoint: API endpoint called
        status: Success/Failure
        duration_ms: Call duration in milliseconds
    """
    msg = f"API Call: {service} - {endpoint} - {status}"
    if duration_ms:
        msg += f" ({duration_ms:.2f}ms)"
    
    if status == "Success":
        logger.info(msg)
    else:
        logger.error(msg)


def log_patient_processing(patient_name: str, patient_id: str, study_type: str):
    """
    Log patient processing start
    
    Args:
        patient_name: Patient name
        patient_id: Patient ID
        study_type: Type of study
    """
    logger.info(f"Processing patient: {patient_name} ({patient_id}) - {study_type}")


def log_error_with_context(error: Exception, context: dict = None):
    """
    Log error with additional context
    
    Args:
        error: Exception object
        context: Additional context dictionary
    """
    if context:
        logger.error(f"Error occurred: {str(error)} | Context: {context}")
    else:
        logger.error(f"Error occurred: {str(error)}")
    
    logger.exception(error)


# Export logger instance
__all__ = [
    'logger',
    'get_logger',
    'log_workflow_step',
    'log_api_call',
    'log_patient_processing',
    'log_error_with_context'
]
