"""
Groq LLM Service
Wrapper for Groq API for report generation and safety analysis
"""

import os
import json
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv
from openai import OpenAI
from config import GROQ_CONFIG

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GroqService:
    """Service class for interacting with Groq API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq service
        
        Args:
            api_key: Groq API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv(GROQ_CONFIG["api_key_env"])
        if not self.api_key:
            raise ValueError(f"Groq API key not found. Set {GROQ_CONFIG['api_key_env']} environment variable.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=GROQ_CONFIG["base_url"]
        )
        self.model = GROQ_CONFIG["model_name"]
        logger.info(f"Groq service initialized with model: {self.model}")
    
    def generate_completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion using Groq
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens (overrides config)
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            logger.info(f"Generating completion with Groq ({self.model})")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert medical AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or GROQ_CONFIG["temperature"],
                max_tokens=max_tokens or GROQ_CONFIG["max_tokens"],
                top_p=GROQ_CONFIG.get("top_p", 0.95),
                **kwargs
            )
            
            result = response.choices[0].message.content
            logger.info(f"Groq completion generated ({len(result)} characters)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating Groq completion: {e}")
            raise
    
    def generate_report(self, prompt: str) -> Dict[str, Any]:
        """
        Generate medical report using Groq
        
        Args:
            prompt: Report generation prompt with all context
            
        Returns:
            Report content as dictionary
        """
        logger.info("Generating medical report with Groq")
        
        try:
            response_text = self.generate_completion(
                prompt=prompt,
                temperature=GROQ_CONFIG["temperature"]
            )
            
            # Parse JSON response
            report_data = json.loads(response_text)
            
            logger.info("Medical report generated successfully")
            return report_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response as JSON: {e}")
            # Return raw text if JSON parsing fails
            return {
                "raw_response": response_text,
                "parse_error": str(e)
            }
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def perform_safety_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Perform safety analysis using Groq
        
        Args:
            prompt: Safety analysis prompt with all data
            
        Returns:
            Safety analysis results as dictionary
        """
        logger.info("Performing safety analysis with Groq")
        
        try:
            response_text = self.generate_completion(
                prompt=prompt,
                temperature=0.1  # Lower temperature for safety analysis
            )
            
            # Parse JSON response
            safety_data = json.loads(response_text)
            
            logger.info("Safety analysis completed successfully")
            return safety_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq safety response as JSON: {e}")
            return {
                "raw_response": response_text,
                "parse_error": str(e)
            }
        except Exception as e:
            logger.error(f"Error performing safety analysis: {e}")
            raise
    
    def perform_cross_validation(
        self,
        gemini_findings: Dict[str, Any],
        gemini_validation: Dict[str, Any],
        patient_info: Dict[str, Any],
        image_type: str,
        image_classification_confidence: float
    ) -> Dict[str, Any]:
        """
        Perform independent cross-validation using Groq
        
        This method validates Gemini's findings independently and generates
        a comparison matrix showing agreements, discrepancies, and consensus.
        
        Args:
            gemini_findings: Vision analysis results from Gemini
            gemini_validation: Cross-validation results from Gemini
            patient_info: Patient information
            image_type: Detected medical image type
            image_classification_confidence: Confidence in image classification
            
        Returns:
            Cross-validation results with comparison matrix
        """
        logger.info("Performing cross-validation with Groq")
        
        try:
            # Build the cross-validation prompt
            from utils import PromptLoader
            prompt_loader = PromptLoader()
            
            prompt = prompt_loader.get_groq_cross_validation_prompt(
                gemini_findings=gemini_findings,
                gemini_validation=gemini_validation,
                patient_info=patient_info,
                image_type=image_type,
                image_classification_confidence=image_classification_confidence
            )
            
            # Perform cross-validation with lower temperature for accuracy
            response_text = self.generate_completion(
                prompt=prompt,
                temperature=0.1
            )
            
            # Parse JSON response
            # Try to extract JSON from response if wrapped in markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            validation_data = json.loads(json_text)
            
            logger.info("Groq cross-validation completed successfully")
            logger.info(f"Consensus score: {validation_data.get('groq_validation_summary', {}).get('consensus_score', 0)}")
            
            return validation_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq cross-validation response as JSON: {e}")
            return {
                "raw_response": response_text,
                "parse_error": str(e),
                "groq_validation_summary": {
                    "error": "JSON parsing failed",
                    "consensus_score": 0.0
                }
            }
        except Exception as e:
            logger.error(f"Error performing Groq cross-validation: {e}")
            raise

    
    def test_connection(self) -> bool:
        """
        Test Groq API connection
        
        Returns:
            True if connection successful
        """
        try:
            logger.info("Testing Groq API connection")
            response = self.generate_completion(
                prompt="Hello, this is a test.",
                max_tokens=10
            )
            logger.info("Groq API connection successful")
            return True
        except Exception as e:
            logger.error(f"Groq API connection failed: {e}")
            return False


# Convenience function
def get_groq_service() -> GroqService:
    """Get initialized Groq service instance"""
    return GroqService()
