"""
Gemini LLM Service
Wrapper for Google Gemini API for vision analysis and cross-validation
"""

import os
import json
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from config import GEMINI_CONFIG

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiService:
    """Service class for interacting with Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini service
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv(GEMINI_CONFIG["api_key_env"])
        if not self.api_key:
            raise ValueError(f"Gemini API key not found. Set {GEMINI_CONFIG['api_key_env']} environment variable.")
        
        genai.configure(api_key=self.api_key)
        
        # Configure model
        self.model = genai.GenerativeModel(
            model_name=GEMINI_CONFIG["model_name"],
            generation_config={
                "temperature": GEMINI_CONFIG["temperature"],
                "top_p": GEMINI_CONFIG["top_p"],
                "top_k": GEMINI_CONFIG["top_k"],
                "max_output_tokens": GEMINI_CONFIG["max_output_tokens"],
            },
            safety_settings=GEMINI_CONFIG["safety_settings"]
        )
        
        logger.info(f"Gemini service initialized with model: {GEMINI_CONFIG['model_name']}")
    
    def analyze_image(
        self,
        image_path: str,
        prompt: str
    ) -> str:
        """
        Analyze image with Gemini vision
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            
        Returns:
            Analysis result as text
        """
        try:
            logger.info(f"Analyzing image with Gemini: {image_path}")
            
            # Load image
            image = Image.open(image_path)
            
            # Generate content
            response = self.model.generate_content([prompt, image])
            
            result = response.text
            logger.info(f"Gemini vision analysis complete ({len(result)} characters)")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {e}")
            raise
    
    def generate_completion(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Generate text completion using Gemini
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            logger.info("Generating completion with Gemini")
            
            response = self.model.generate_content(prompt)
            result = response.text
            
            logger.info(f"Gemini completion generated ({len(result)} characters)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating Gemini completion: {e}")
            raise
    
    def perform_vision_analysis(
        self,
        image_path: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Perform vision analysis on MRI image
        
        Args:
            image_path: Path to MRI image
            prompt: Vision analysis prompt
            
        Returns:
            Vision analysis results as dictionary
        """
        logger.info("Performing vision analysis with Gemini")
        
        try:
            response_text = self.analyze_image(image_path, prompt)
            
            # Parse JSON response - json already imported at top of file
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            vision_data = json.loads(json_text)
            
            logger.info("Vision analysis completed successfully")
            return vision_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return {
                "raw_response": response_text,
                "parse_error": str(e)
            }
        except Exception as e:
            logger.error(f"Error performing vision analysis: {e}")
            raise
    
    def perform_cross_validation(
        self,
        image_path: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Perform cross-validation on analysis results
        
        Args:
            image_path: Path to MRI image
            prompt: Cross-validation prompt with results
            
        Returns:
            Cross-validation results as dictionary
        """
        logger.info("Performing cross-validation with Gemini")
        
        try:
            response_text = self.analyze_image(image_path, prompt)
            
            # Parse JSON response - json already imported at top of file
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            validation_data = json.loads(json_text)
            
            logger.info("Cross-validation completed successfully")
            return validation_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini validation response as JSON: {e}")
            return {
                "raw_response": response_text,
                "parse_error": str(e)
            }
        except Exception as e:
            logger.error(f"Error performing cross-validation: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test Gemini API connection
        
        Returns:
            True if connection successful
        """
        try:
            logger.info("Testing Gemini API connection")
            response = self.generate_completion("Hello, this is a test.")
            logger.info("Gemini API connection successful")
            return True
        except Exception as e:
            logger.error(f"Gemini API connection failed: {e}")
            return False


# Convenience function
def get_gemini_service() -> GeminiService:
    """Get initialized Gemini service instance"""
    return GeminiService()
