# MIA Project Structure

This document shows the complete VS Code project hierarchy for the MIA (Medical Image Analysis) system.

## Directory Tree

```
e:\MIA\
├── .vscode/                          # VS Code settings
│   ├── settings.json
│   ├── launch.json
│   └── extensions.json
├── .miavenv/                         # Virtual environment (auto-generated)
├── prompts/                          # LLM prompts
│   ├── gemini_vision_analysis_prompt.md
│   ├── gemini_cross_validation_prompt.md
│   ├── groq_report_generation_prompt.md
│   └── groq_safety_analysis_prompt.md
├── models/                           # Data models
│   ├── __init__.py
│   └── patient_data_schema.py
├── utils/                            # Utility functions
│   ├── __init__.py
│   ├── prompt_loader.py
│   ├── pdf_generator.py
│   └── validators.py
├── nodes.py                         # Single file containing all LangGraph nodes
├── services/                         # LLM services
│   ├── __init__.py
│   ├── gemini_service.py
│   └── groq_service.py
├── assets/                           # Static assets
│   ├── logo.png (user-provided)
│   └── README.md
├── outputs/                          # Generated outputs
│   ├── reports/
│   ├── images/
│   ├── logs/
│   └── temp/
├── data/                             # Sample data
│   ├── sample_patient.json
│   └── sample_mri/
├── tests/                            # Unit tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_pdf_generator.py
│   ├── test_prompt_loader.py
│   └── test_workflow.py
├── docs/                             # Documentation
│   ├── API.md
│   ├── PROMPTS.md
│   └── WORKFLOW.md
├── .env                              # Environment variables (not in git)
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore file
├── config.py                         # Configuration
├── requirements.txt                  # Python dependencies
├── mia_langgraph.py                  # Main LangGraph workflow
├── example_usage.py                  # Usage examples
├── README.md                         # Project documentation
└── setup.py                          # Package setup
```

## File Descriptions

### Root Level
- **mia_langgraph.py**: Main LangGraph workflow orchestration
- **config.py**: Central configuration for LLMs, PDF, paths
- **example_usage.py**: Example usage and testing
- **requirements.txt**: Python package dependencies
- **setup.py**: Package installation configuration
- **.env**: Environment variables (API keys)
- **.gitignore**: Git ignore patterns

### Prompts Directory
- **gemini_vision_analysis_prompt.md**: Gemini vision analysis prompt
- **gemini_cross_validation_prompt.md**: Gemini validation prompt
- **groq_report_generation_prompt.md**: Groq report generation prompt
- **groq_safety_analysis_prompt.md**: Groq safety analysis prompt

### Models Directory
- **patient_data_schema.py**: Pydantic models for all data structures

### Utils Directory
- **prompt_loader.py**: Load and format prompts
- **pdf_generator.py**: Generate PDF reports
- **validators.py**: Input validation functions

### Nodes File
- **nodes.py**: Single file containing all LangGraph nodes:
  - user_input_node
  - validation_node
  - vision_node
  - cross_validation_node
  - report_node
  - safety_node
  - pdf_node

### Services Directory
- **gemini_service.py**: Gemini API wrapper
- **groq_service.py**: Groq API wrapper

### Tests Directory
- Unit tests for all components

### Outputs Directory
- **reports/**: Generated PDF reports
- **images/**: Processed images
- **logs/**: System logs
- **temp/**: Temporary files

## VS Code Configuration

The `.vscode/` directory contains:
- **settings.json**: Python interpreter, formatting, linting
- **launch.json**: Debug configurations
- **extensions.json**: Recommended extensions
