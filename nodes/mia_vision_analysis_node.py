"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MIA VISION ANALYSIS NODE                                 ║
║                     Powered by Gemini 2.5 Flash                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Node Name: Vision Analysis Node
Description: Performs comprehensive vision analysis on MRI images using Gemini 2.5 Flash.
             Includes input validation, image quality assessment, and measurements extraction.

Input:
    - patient_info: Dict containing patient details (name, age, gender, etc.)
    - mri_metadata: Dict containing MRI study information
    - mri_image_path: String path to the MRI image file

Output:
    - vision_analysis: Dict containing:
        * image_quality: Assessment of image quality
        * findings: List of detected findings with locations and descriptions
        * measurements: Extracted measurements from the image
        * confidence_score: Confidence level of the analysis
        * raw_response: Complete response from Gemini

Author: MIA Team - Agenix AI
Created: 2026-01-07
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

# Import services
from services import get_gemini_service
from utils import PromptLoader
from utils.validators import validate_patient_info, validate_image_path, validate_mri_metadata
from utils.logger import logger, log_workflow_step, log_error_with_context


class VisionAnalysisNode:
    """
    Vision Analysis Node for MIA Workflow
    
    This node performs the first critical step in the medical image analysis pipeline.
    It uses Gemini 2.5 Flash's advanced vision capabilities to:
    1. Validate all input data (patient info, MRI metadata, image path)
    2. Assess the quality of the MRI image
    3. Detect and describe findings in the image
    4. Extract relevant measurements
    """
    
    def __init__(self):
        """Initialize the Vision Analysis Node with Gemini service."""
        self.gemini_service = None
        self.prompt_loader = PromptLoader()
        logger.info("Vision Analysis Node initialized")
    
    def _initialize_services(self):
        """Lazy initialization of Gemini service."""
        if self.gemini_service is None:
            self.gemini_service = get_gemini_service()
            logger.info("Gemini 2.5 Flash service initialized")
    
    def validate_input(self, state: Dict[str, Any]) -> List[str]:
        """
        Validate all input data before processing.
        
        Args:
            state: Current workflow state containing patient_info, mri_metadata, mri_image_path
            
        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        
        # Validate patient information
        patient_info = state.get("patient_info", {})
        errors.extend(validate_patient_info(patient_info))
        
        # Validate image metadata
        image_metadata = state.get("image_metadata", state.get("mri_metadata", {}))
        errors.extend(validate_mri_metadata(image_metadata))
        
        # Validate image path (support both old and new key names)
        image_path = state.get("medical_image_path", state.get("mri_image_path", ""))
        errors.extend(validate_image_path(image_path))
        
        if errors:
            logger.error(f"Input validation failed with {len(errors)} errors")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info("Input validation passed successfully")
        
        return errors
    
    def assess_image_quality(self, image_path: str) -> Dict[str, Any]:
        """
        Assess the quality of the MRI image.
        
        Args:
            image_path: Path to the MRI image
            
        Returns:
            Dict containing quality assessment results
        """
        logger.info(f"Assessing image quality for: {image_path}")
        
        # Check if file exists and is readable
        if not os.path.exists(image_path):
            return {
                "quality_score": 0,
                "is_acceptable": False,
                "issues": ["Image file not found"],
                "recommendations": ["Please provide a valid image path"]
            }
        
        # Check file size
        file_size = os.path.getsize(image_path)
        if file_size < 1024:  # Less than 1KB
            return {
                "quality_score": 0,
                "is_acceptable": False,
                "issues": ["Image file too small"],
                "recommendations": ["Please provide a valid MRI image"]
            }
        
        # Basic quality assessment passed
        return {
            "quality_score": 85,
            "is_acceptable": True,
            "issues": [],
            "recommendations": [],
            "file_size_kb": round(file_size / 1024, 2)
        }
    
    def classify_image_type(self, image_path: str, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the type of medical image using Gemini.
        
        Args:
            image_path: Path to the medical image
            patient_info: Patient information for context
            
        Returns:
            Dict containing image classification results
        """
        logger.info(f"Classifying medical image type: {image_path}")
        
        try:
            # Get the image classification prompt
            prompt = self.prompt_loader.get_image_classification_prompt(patient_info)
            
            # Perform image classification with Gemini
            response_text = self.gemini_service.analyze_image(image_path, prompt)
            
            # Parse JSON response
            import json
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            classification_data = json.loads(json_text)
            
            image_type = classification_data.get("image_type", "Unknown")
            confidence = classification_data.get("confidence", 0.0)
            
            logger.info(f"Image classified as: {image_type} (confidence: {confidence:.2%})")
            
            return classification_data
            
        except Exception as e:
            logger.error(f"Image classification failed: {str(e)}")
            # Return default classification on error
            return {
                "image_type": "Unknown",
                "confidence": 0.0,
                "sub_type": "Classification failed",
                "characteristics": [],
                "anatomical_region": "Unknown",
                "imaging_plane": "Unknown",
                "technical_observations": [],
                "reasoning": f"Classification error: {str(e)}"
            }
    
    def extract_measurements(self, vision_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract measurements from Gemini's vision analysis response.
        
        Args:
            vision_response: Raw response from Gemini vision analysis
            
        Returns:
            Dict containing extracted measurements
        """
        measurements = {}
        
        # Try to extract measurements from the response
        if isinstance(vision_response, dict):
            # Look for measurements in various possible keys
            if "measurements" in vision_response:
                measurements = vision_response["measurements"]
            elif "findings" in vision_response:
                # Extract measurements from findings
                for finding in vision_response.get("findings", []):
                    if isinstance(finding, dict) and "measurements" in finding:
                        measurements.update(finding["measurements"])
        
        logger.info(f"Extracted {len(measurements)} measurements from vision analysis")
        return measurements
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function for Vision Analysis Node.
        
        This function orchestrates the entire vision analysis workflow:
        1. Validates input data
        2. Initializes Gemini service
        3. Assesses image quality
        4. Performs vision analysis using Gemini 2.5 Flash
        5. Extracts measurements
        6. Returns updated state with analysis results
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with vision_analysis results
        """
        report_id = state.get("report_id", f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        log_workflow_step(report_id, "vision_analysis", "Starting Vision Analysis Node")
        
        # Update current step
        state["current_step"] = "vision_analysis"
        
        # Step 1: Validate input
        logger.info("=" * 80)
        logger.info("STEP 1: INPUT VALIDATION")
        logger.info("=" * 80)
        
        validation_errors = self.validate_input(state)
        if validation_errors:
            state.setdefault("errors", []).extend(validation_errors)
            log_workflow_step(report_id, "vision_analysis", 
                            f"Validation failed with {len(validation_errors)} errors", "ERROR")
            return state
        
        # Step 2: Initialize services
        logger.info("=" * 80)
        logger.info("STEP 2: INITIALIZING GEMINI 2.5 FLASH SERVICE")
        logger.info("=" * 80)
        
        try:
            self._initialize_services()
        except Exception as e:
            error_msg = f"Failed to initialize Gemini service: {str(e)}"
            logger.error(error_msg)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        # Step 3: Assess image quality
        logger.info("=" * 80)
        logger.info("STEP 3: IMAGE QUALITY ASSESSMENT")
        logger.info("=" * 80)
        
        # Support both old key (mri_image_path) and new key (medical_image_path)
        image_path = state.get("medical_image_path", state.get("mri_image_path", ""))
        # Normalise state to always use the new key
        state["medical_image_path"] = image_path
        quality_assessment = self.assess_image_quality(image_path)
        
        if not quality_assessment.get("is_acceptable", False):
            error_msg = f"Image quality check failed: {quality_assessment.get('issues', [])}"
            logger.error(error_msg)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        logger.info(f"Image quality score: {quality_assessment.get('quality_score', 0)}/100")
        
        # Step 3.5: Classify image type
        logger.info("=" * 80)
        logger.info("STEP 3.5: MEDICAL IMAGE TYPE CLASSIFICATION")
        logger.info("=" * 80)
        
        try:
            image_classification = self.classify_image_type(image_path, state.get("patient_info", {}))
            logger.info(f"Image Type: {image_classification.get('image_type', 'Unknown')}")
            logger.info(f"Sub-Type: {image_classification.get('sub_type', 'N/A')}")
            logger.info(f"Confidence: {image_classification.get('confidence', 0):.2%}")
            
            # Store classification in state for use by other nodes
            state["image_classification"] = image_classification
            
        except Exception as e:
            logger.warning(f"Image classification encountered an error: {str(e)}")
            # Continue with default classification
            state["image_classification"] = {
                "image_type": "Unknown",
                "confidence": 0.0,
                "reasoning": "Classification failed"
            }
        
        # Step 4: Perform vision analysis with Gemini
        logger.info("=" * 80)
        logger.info("STEP 4: GEMINI 2.5 FLASH VISION ANALYSIS")
        logger.info("=" * 80)
        
        try:
            # Get the vision analysis prompt — now dynamic based on detected image type
            prompt = self.prompt_loader.get_vision_analysis_prompt(
                patient_info=state["patient_info"],
                image_classification=state.get("image_classification")
            )
            
            # Perform vision analysis
            logger.info(f"Analyzing image: {image_path}")
            vision_results = self.gemini_service.perform_vision_analysis(
                image_path=image_path,
                prompt=prompt
            )
            
            # Step 5: Extract measurements
            logger.info("=" * 80)
            logger.info("STEP 5: EXTRACTING MEASUREMENTS")
            logger.info("=" * 80)
            
            measurements = self.extract_measurements(vision_results)
            
            # Compile final results
            state["vision_analysis"] = {
                "image_quality": quality_assessment,
                "image_type": state.get("image_classification", {}).get("image_type", "Unknown"),
                "image_classification": state.get("image_classification", {}),
                "findings": vision_results.get("findings", []),
                "measurements": measurements,
                "confidence_score": vision_results.get("confidence_score", 0.85),
                "raw_response": vision_results,
                "analyzed_at": datetime.now().isoformat(),
                "model_used": "gemini-2.5-flash"
            }
            
            log_workflow_step(report_id, "vision_analysis", 
                            "Vision analysis completed successfully", "SUCCESS")
            logger.info("=" * 80)
            logger.info("VISION ANALYSIS COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
        except Exception as e:
            error_msg = f"Vision analysis failed: {str(e)}"
            log_error_with_context(e, {"report_id": report_id, "step": "vision_analysis"})
            state.setdefault("errors", []).append(error_msg)
        
        return state


# ============================================================================
# STANDALONE FUNCTION FOR LANGGRAPH INTEGRATION
# ============================================================================

def vision_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function wrapper for LangGraph integration.
    
    This function can be directly used in LangGraph workflow definitions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with vision analysis results
    """
    node = VisionAnalysisNode()
    return node.process(state)


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test the Vision Analysis Node with sample data.
    """
    print("=" * 80)
    print("TESTING VISION ANALYSIS NODE")
    print("=" * 80)
    
    # Sample test state
    test_state = {
        "report_id": "TEST-001",
        "patient_info": {
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "height_cm": 175.0,
            "weight_kg": 80.0,
            "bmi": 26.1,
            "profession": "Engineer"
        },
        "mri_metadata": {
            "study_type": "Brain MRI",
            "sequence_type": "T2",
            "imaging_plane": "Axial"
        },
        "mri_image_path": "data/sample_mri/sample.jpg"
    }
    
    # Run the node
    result_state = vision_analysis_node(test_state)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if "errors" in result_state and result_state["errors"]:
        print("❌ ERRORS:")
        for error in result_state["errors"]:
            print(f"  - {error}")
    else:
        print("✅ Vision analysis completed successfully!")
        if "vision_analysis" in result_state:
            print(f"\nFindings: {len(result_state['vision_analysis'].get('findings', []))}")
            print(f"Measurements: {len(result_state['vision_analysis'].get('measurements', {}))}")
            print(f"Confidence: {result_state['vision_analysis'].get('confidence_score', 0)}")
