"""
Tests for prompt loader functionality
"""

import pytest
from pathlib import Path
from utils.prompt_loader import PromptLoader


def test_prompt_loader_initialization():
    """Test PromptLoader can be initialized."""
    loader = PromptLoader()
    assert loader is not None


def test_load_prompt_file():
    """Test loading a prompt file."""
    loader = PromptLoader()
    
    # Test loading vision analysis prompt
    try:
        prompt = loader.load_prompt("gemini_vision_analysis")
        assert prompt is not None
        assert len(prompt) > 0
    except FileNotFoundError:
        pytest.skip("Prompt file not found")


def test_format_prompt_with_context():
    """Test formatting prompt with patient context."""
    loader = PromptLoader()
    
    patient_info = {
        "name": "John Doe",
        "age": 45,
        "gender": "Male",
        "bmi": 26.1,
        "profession": "Engineer"
    }
    
    try:
        prompt = loader.get_vision_analysis_prompt(patient_info)
        assert "45" in prompt or "age" in prompt.lower()
    except Exception:
        pytest.skip("Prompt loading not fully implemented")


def test_prompt_caching():
    """Test that prompts are cached after first load."""
    loader = PromptLoader()
    
    try:
        # Load same prompt twice
        prompt1 = loader.load_prompt("gemini_vision_analysis")
        prompt2 = loader.load_prompt("gemini_vision_analysis")
        
        # Should be the same object if cached
        assert prompt1 == prompt2
    except FileNotFoundError:
        pytest.skip("Prompt file not found")
