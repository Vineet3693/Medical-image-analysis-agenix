# MIA Logging System Documentation

## Overview

The MIA system uses **loguru** for advanced logging with automatic rotation, compression, and multiple output targets.

## Log Files

All logs are stored in `outputs/logs/`:

### 1. Main Application Log
- **File**: `mia_YYYYMMDD.log`
- **Level**: DEBUG and above
- **Rotation**: 100 MB
- **Retention**: 30 days
- **Compression**: ZIP
- **Content**: All application activity

### 2. Error Log
- **File**: `mia_errors_YYYYMMDD.log`
- **Level**: ERROR and above only
- **Rotation**: 50 MB
- **Retention**: 90 days (longer for errors)
- **Compression**: ZIP
- **Content**: Errors with full tracebacks and variable values

### 3. Workflow Log
- **File**: `workflow_YYYYMMDD.log`
- **Level**: INFO and above
- **Rotation**: 50 MB
- **Retention**: 60 days
- **Content**: Workflow execution tracking with Report IDs

### 4. Console Output
- **Target**: stderr
- **Level**: INFO and above
- **Format**: Colored, human-readable
- **Content**: Real-time execution status

## Usage

### Basic Logging

```python
from utils.logger import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

### Workflow Logging

```python
from utils.logger import log_workflow_step

log_workflow_step(
    report_id="MIA-20260103-123456",
    step="vision_analysis",
    message="Starting Gemini vision analysis"
)

# With different levels
log_workflow_step(report_id, step, "Warning message", level="WARNING")
log_workflow_step(report_id, step, "Error occurred", level="ERROR")
```

### API Call Logging

```python
from utils.logger import log_api_call

log_api_call(
    service="Gemini",
    endpoint="generate_content",
    status="Success",
    duration_ms=1234.56
)
```

### Patient Processing Logging

```python
from utils.logger import log_patient_processing

log_patient_processing(
    patient_name="Robert Johnson",
    patient_id="MIA-P001",
    study_type="Brain MRI"
)
```

### Error Logging with Context

```python
from utils.logger import log_error_with_context

try:
    # Some operation
    pass
except Exception as e:
    log_error_with_context(e, {
        "report_id": "MIA-20260103-123456",
        "patient_id": "MIA-P001",
        "step": "vision_analysis"
    })
```

## Log Format

### Console Format
```
HH:mm:ss | LEVEL    | module:function - message
```

Example:
```
15:30:45 | INFO     | nodes:vision_node - Starting Gemini vision analysis
```

### File Format
```
YYYY-MM-DD HH:mm:ss.SSS | LEVEL    | module:function:line - message
```

Example:
```
2026-01-03 15:30:45.123 | INFO     | nodes:vision_node:125 - Starting Gemini vision analysis
```

### Workflow Format
```
YYYY-MM-DD HH:mm:ss | REPORT_ID | STEP | message
```

Example:
```
2026-01-03 15:30:45 | MIA-20260103-153045 | vision_analysis | Starting Gemini vision analysis
```

## Features

### Automatic Rotation
- Logs automatically rotate when they reach size limit
- Old logs are compressed to save space
- Configurable retention period

### Thread-Safe
- All logging is enqueued for thread safety
- Safe for concurrent operations

### Rich Error Information
- Full tracebacks for errors
- Variable values at error point (diagnose mode)
- Backtrace for error context

### Filtering
- Workflow logs only contain workflow-related entries
- Error logs only contain errors
- Console shows INFO and above

## Log Levels

1. **DEBUG**: Detailed diagnostic information
2. **INFO**: General informational messages
3. **WARNING**: Warning messages for potential issues
4. **ERROR**: Error messages for failures
5. **CRITICAL**: Critical errors requiring immediate attention

## Best Practices

### 1. Use Appropriate Levels
```python
logger.debug("Detailed variable state")  # Development only
logger.info("Normal operation")          # Production events
logger.warning("Potential issue")        # Warnings
logger.error("Operation failed")         # Errors
```

### 2. Include Context
```python
# Good
logger.info(f"Processing patient {patient_id} with study {study_type}")

# Better
log_workflow_step(report_id, "processing", f"Patient: {patient_id}, Study: {study_type}")
```

### 3. Log Workflow Steps
```python
# At the start of each node
log_workflow_step(report_id, step_name, "Starting step")

# At the end of each node
log_workflow_step(report_id, step_name, "Step completed successfully")

# On errors
log_workflow_step(report_id, step_name, f"Step failed: {error}", "ERROR")
```

### 4. Track API Calls
```python
import time

start = time.time()
try:
    response = api_call()
    duration = (time.time() - start) * 1000
    log_api_call("Gemini", "analyze_image", "Success", duration)
except Exception as e:
    duration = (time.time() - start) * 1000
    log_api_call("Gemini", "analyze_image", "Failure", duration)
    raise
```

## Viewing Logs

### Real-Time Monitoring
```bash
# Watch main log
tail -f outputs/logs/mia_20260103.log

# Watch errors only
tail -f outputs/logs/mia_errors_20260103.log

# Watch workflow
tail -f outputs/logs/workflow_20260103.log
```

### Search Logs
```bash
# Find all errors for a specific report
grep "MIA-20260103-153045" outputs/logs/workflow_20260103.log

# Find all API failures
grep "Failure" outputs/logs/mia_20260103.log
```

## Configuration

Logger configuration is in `utils/logger.py`. You can customize:

- Log file locations
- Rotation sizes
- Retention periods
- Log formats
- Log levels

## Troubleshooting

### Logs Not Appearing
- Check `outputs/logs/` directory exists
- Verify log level is appropriate
- Check file permissions

### Too Many Log Files
- Adjust retention period in `utils/logger.py`
- Manually clean old compressed logs

### Performance Issues
- Logs are enqueued (async) by default
- Should not impact performance
- Check disk space if rotation fails

## Example Workflow Logging

```python
def process_mri_workflow(patient_id, report_id, image_path):
    # Start
    log_patient_processing("John Doe", patient_id, "Brain MRI")
    log_workflow_step(report_id, "start", "Workflow initiated")
    
    # Vision analysis
    log_workflow_step(report_id, "vision", "Calling Gemini API")
    try:
        result = gemini_analyze(image_path)
        log_api_call("Gemini", "analyze", "Success", 1234)
        log_workflow_step(report_id, "vision", "Analysis complete")
    except Exception as e:
        log_error_with_context(e, {"report_id": report_id, "step": "vision"})
        log_workflow_step(report_id, "vision", "Analysis failed", "ERROR")
        raise
    
    # Complete
    log_workflow_step(report_id, "complete", "Workflow finished successfully")
```

This provides complete traceability of every workflow execution!
