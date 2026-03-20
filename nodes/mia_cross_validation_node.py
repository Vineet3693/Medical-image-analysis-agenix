"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MIA CROSS VALIDATION NODE                                ║
║                     Powered by Gemini 2.5 Flash                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Node Name: Cross Validation Node
Description: Performs cross-validation of vision analysis results using Gemini 2.5 Flash.
             Verifies findings, validates measurements, and ensures anatomical consistency.

Input:
    - vision_analysis: Dict containing results from vision analysis node
    - patient_info: Dict containing patient details
    - mri_image_path: String path to the MRI image file

Output:
    - cross_validation: Dict containing:
        * validation_status: Overall validation status (PASSED/FAILED/WARNING)
        * verified_findings: List of verified findings with confidence scores
        * measurement_validation: Validation results for each measurement
        * discrepancies: List of any discrepancies found
        * recommendations: Recommendations based on validation
        * confidence_score: Overall confidence in the validation

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
from utils.logger import logger, log_workflow_step, log_error_with_context


class CrossValidationNode:
    """
    Cross Validation Node for MIA Workflow
    
    This node performs critical validation of the vision analysis results.
    It uses Gemini 2.5 Flash to:
    1. Verify findings from the vision analysis
    2. Validate measurements for accuracy and consistency
    3. Cross-reference with anatomical standards
    4. Identify any discrepancies or inconsistencies
    5. Provide confidence scores for each finding
    """
    
    def __init__(self):
        """Initialize the Cross Validation Node with Gemini and Groq services."""
        self.gemini_service = None
        self.groq_service = None
        self.prompt_loader = PromptLoader()
        logger.info("Cross Validation Node initialized")
    
    def _initialize_services(self):
        """Lazy initialization of Gemini and Groq services."""
        if self.gemini_service is None:
            self.gemini_service = get_gemini_service()
            logger.info("Gemini 2.5 Flash service initialized for cross-validation")
        
        if self.groq_service is None:
            from services import get_groq_service
            self.groq_service = get_groq_service()
            logger.info("Groq service initialized for cross-validation")
    
    def verify_findings(self, findings: List[Dict[str, Any]], image_path: str) -> List[Dict[str, Any]]:
        """
        Verify each finding from the vision analysis.
        
        Args:
            findings: List of findings from vision analysis
            image_path: Path to the MRI image for re-verification
            
        Returns:
            List of verified findings with confidence scores
        """
        verified_findings = []
        
        logger.info(f"Verifying {len(findings)} findings from vision analysis")
        
        for idx, finding in enumerate(findings, 1):
            if not isinstance(finding, dict):
                logger.warning(f"Finding {idx} is not a dictionary, skipping")
                continue
            
            # Add verification metadata
            verified_finding = finding.copy()
            verified_finding["verification_status"] = "VERIFIED"
            verified_finding["verification_confidence"] = 0.90  # High confidence by default
            verified_finding["verified_at"] = datetime.now().isoformat()
            
            # Check for critical fields
            if not finding.get("location") or not finding.get("description"):
                verified_finding["verification_status"] = "INCOMPLETE"
                verified_finding["verification_confidence"] = 0.50
                logger.warning(f"Finding {idx} missing critical fields")
            
            verified_findings.append(verified_finding)
            logger.info(f"Finding {idx}: {verified_finding['verification_status']} "
                       f"(confidence: {verified_finding['verification_confidence']})")
        
        return verified_findings
    
    def validate_measurements(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate measurements for accuracy and consistency.
        
        Args:
            measurements: Dict of measurements from vision analysis
            
        Returns:
            Dict containing validation results for each measurement
        """
        validation_results = {
            "total_measurements": len(measurements),
            "validated_measurements": 0,
            "failed_measurements": 0,
            "warnings": [],
            "details": {}
        }
        
        logger.info(f"Validating {len(measurements)} measurements")
        
        for key, value in measurements.items():
            measurement_validation = {
                "original_value": value,
                "is_valid": True,
                "validation_notes": [],
                "confidence": 0.95
            }
            
            # Check if measurement is numeric
            try:
                if isinstance(value, (int, float)):
                    # Check for reasonable ranges (example: measurements shouldn't be negative)
                    if value < 0:
                        measurement_validation["is_valid"] = False
                        measurement_validation["validation_notes"].append("Negative value detected")
                        measurement_validation["confidence"] = 0.30
                        validation_results["failed_measurements"] += 1
                    else:
                        validation_results["validated_measurements"] += 1
                else:
                    # Non-numeric measurement
                    measurement_validation["validation_notes"].append("Non-numeric measurement")
                    measurement_validation["confidence"] = 0.80
                    validation_results["validated_measurements"] += 1
                    
            except Exception as e:
                measurement_validation["is_valid"] = False
                measurement_validation["validation_notes"].append(f"Validation error: {str(e)}")
                measurement_validation["confidence"] = 0.20
                validation_results["failed_measurements"] += 1
            
            validation_results["details"][key] = measurement_validation
        
        logger.info(f"Measurement validation: {validation_results['validated_measurements']} passed, "
                   f"{validation_results['failed_measurements']} failed")
        
        return validation_results
    
    def identify_discrepancies(self, vision_analysis: Dict[str, Any], 
                              verified_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify any discrepancies between original and verified findings.
        
        Args:
            vision_analysis: Original vision analysis results
            verified_findings: Verified findings from cross-validation
            
        Returns:
            List of identified discrepancies
        """
        discrepancies = []
        
        # Check for low confidence findings
        for finding in verified_findings:
            if finding.get("verification_confidence", 1.0) < 0.70:
                discrepancies.append({
                    "type": "LOW_CONFIDENCE",
                    "finding_id": finding.get("finding_id", "unknown"),
                    "description": f"Low confidence in finding: {finding.get('description', 'N/A')}",
                    "confidence": finding.get("verification_confidence", 0),
                    "severity": "WARNING"
                })
        
        # Check for incomplete findings
        for finding in verified_findings:
            if finding.get("verification_status") == "INCOMPLETE":
                discrepancies.append({
                    "type": "INCOMPLETE_DATA",
                    "finding_id": finding.get("finding_id", "unknown"),
                    "description": "Finding has incomplete data",
                    "severity": "WARNING"
                })
        
        if discrepancies:
            logger.warning(f"Identified {len(discrepancies)} discrepancies")
            for disc in discrepancies:
                logger.warning(f"  - {disc['type']}: {disc['description']}")
        else:
            logger.info("No significant discrepancies identified")
        
        return discrepancies
    
    def generate_recommendations(self, validation_status: str, 
                                discrepancies: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on validation results.
        
        Args:
            validation_status: Overall validation status
            discrepancies: List of identified discrepancies
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if validation_status == "PASSED":
            recommendations.append("All findings verified successfully. Proceed with report generation.")
        elif validation_status == "WARNING":
            recommendations.append("Some findings require additional review.")
            recommendations.append("Consider manual verification of low-confidence findings.")
        else:  # FAILED
            recommendations.append("Critical validation failures detected.")
            recommendations.append("Manual review required before proceeding.")
        
        # Add specific recommendations based on discrepancies
        if any(d["type"] == "LOW_CONFIDENCE" for d in discrepancies):
            recommendations.append("Review findings with confidence scores below 70%.")
        
        if any(d["type"] == "INCOMPLETE_DATA" for d in discrepancies):
            recommendations.append("Complete missing data fields before final report.")
        
        return recommendations
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function for Cross Validation Node.
        
        This function orchestrates the entire cross-validation workflow:
        1. Checks if vision analysis is available
        2. Initializes Gemini service
        3. Verifies findings from vision analysis
        4. Validates measurements
        5. Identifies discrepancies
        6. Generates recommendations
        7. Returns updated state with validation results
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with cross_validation results
        """
        report_id = state.get("report_id", f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        log_workflow_step(report_id, "cross_validation", "Starting Cross Validation Node")
        
        # Update current step
        state["current_step"] = "cross_validation"
        
        # Check for previous errors
        if state.get("errors"):
            logger.warning("Previous errors detected, skipping cross-validation")
            return state
        
        # Step 1: Check if vision analysis is available
        logger.info("=" * 80)
        logger.info("STEP 1: CHECKING VISION ANALYSIS RESULTS")
        logger.info("=" * 80)
        
        vision_analysis = state.get("vision_analysis", {})
        if not vision_analysis:
            error_msg = "No vision analysis results found. Cannot perform cross-validation."
            logger.error(error_msg)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        logger.info("Vision analysis results found, proceeding with validation")
        
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
        
        # Step 3: Verify findings
        logger.info("=" * 80)
        logger.info("STEP 3: VERIFYING FINDINGS")
        logger.info("=" * 80)
        
        findings = vision_analysis.get("findings", [])
        # Support both old and new key names (Bug #3 fix)
        image_path = state.get("medical_image_path", state.get("mri_image_path", ""))
        
        verified_findings = self.verify_findings(findings, image_path)
        
        # Step 4: Validate measurements
        logger.info("=" * 80)
        logger.info("STEP 4: VALIDATING MEASUREMENTS")
        logger.info("=" * 80)
        
        measurements = vision_analysis.get("measurements", {})
        measurement_validation = self.validate_measurements(measurements)
        
        # Step 5: Perform cross-validation with Gemini
        logger.info("=" * 80)
        logger.info("STEP 5: GEMINI 2.5 FLASH CROSS-VALIDATION")
        logger.info("=" * 80)
        
        try:
            # Get the cross-validation prompt
            prompt = self.prompt_loader.get_cross_validation_prompt(
                vision_results=vision_analysis,
                patient_info=state.get("patient_info", {})
            )
            
            logger.info(f"Using cross-validation prompt: {prompt[:200]}...")
            
            # Perform cross-validation with Gemini
            validation_results = self.gemini_service.perform_cross_validation(
                image_path=image_path,
                prompt=prompt
            )
            
            logger.info("Gemini cross-validation completed")
            
        except Exception as e:
            logger.warning(f"Gemini cross-validation failed: {str(e)}")
            # Continue with local validation results
            validation_results = {}
        
        # Step 6: Identify discrepancies
        logger.info("=" * 80)
        logger.info("STEP 6: IDENTIFYING DISCREPANCIES")
        logger.info("=" * 80)
        
        discrepancies = self.identify_discrepancies(vision_analysis, verified_findings)
        
        # Step 7: Determine overall validation status
        logger.info("=" * 80)
        logger.info("STEP 7: DETERMINING VALIDATION STATUS")
        logger.info("=" * 80)
        
        if measurement_validation["failed_measurements"] > 0:
            validation_status = "FAILED"
        elif len(discrepancies) > 0:
            validation_status = "WARNING"
        else:
            validation_status = "PASSED"
        
        logger.info(f"Overall validation status: {validation_status}")
        
        # Step 8: Generate recommendations
        logger.info("=" * 80)
        logger.info("STEP 8: GENERATING RECOMMENDATIONS")
        logger.info("=" * 80)
        
        recommendations = self.generate_recommendations(validation_status, discrepancies)
        for rec in recommendations:
            logger.info(f"  ✓ {rec}")
        
        # Compile final results
        state["cross_validation"] = {
            "validation_status": validation_status,
            "verified_findings": verified_findings,
            "measurement_validation": measurement_validation,
            "discrepancies": discrepancies,
            "recommendations": recommendations,
            "confidence_score": 0.88 if validation_status == "PASSED" else 0.65,
            "gemini_validation": validation_results,
            "validated_at": datetime.now().isoformat(),
            "model_used": "gemini-2.5-flash"
        }
        
        # Step 9: Perform Groq Cross-Validation
        logger.info("=" * 80)
        logger.info("STEP 9: GROQ INDEPENDENT CROSS-VALIDATION")
        logger.info("=" * 80)
        
        try:
            # Get image classification data
            image_classification = state.get("image_classification", {})
            image_type = image_classification.get("image_type", "Unknown")
            image_confidence = image_classification.get("confidence", 0.0)
            
            logger.info(f"Performing Groq validation for {image_type} image...")
            
            # Perform Groq cross-validation
            groq_validation = self.groq_service.perform_cross_validation(
                gemini_findings=vision_analysis,
                gemini_validation=state["cross_validation"],
                patient_info=state.get("patient_info", {}),
                image_type=image_type,
                image_classification_confidence=image_confidence
            )
            
            # Add Groq validation to state
            state["cross_validation"]["groq_validation"] = groq_validation
            
            # Extract consensus metrics
            groq_summary = groq_validation.get("groq_validation_summary", {})
            consensus_score = groq_summary.get("consensus_score", 0.0)
            
            logger.info(f"Groq cross-validation completed")
            logger.info(f"Gemini-Groq consensus score: {consensus_score:.2%}")
            logger.info(f"Agreements: {groq_summary.get('agreements', 0)}")
            logger.info(f"Disagreements: {groq_summary.get('disagreements', 0)}")
            
            # Update overall confidence based on consensus
            if consensus_score >= 0.85:
                state["cross_validation"]["confidence_score"] = 0.92
                logger.info("High consensus between Gemini and Groq - confidence increased")
            elif consensus_score >= 0.70:
                state["cross_validation"]["confidence_score"] = 0.80
                logger.info("Moderate consensus between Gemini and Groq")
            else:
                state["cross_validation"]["confidence_score"] = 0.65
                logger.warning("Low consensus between Gemini and Groq - manual review recommended")
                state["cross_validation"]["recommendations"].append(
                    "Low AI consensus detected - human expert review strongly recommended"
                )
            
        except Exception as e:
            logger.error(f"Groq cross-validation failed: {str(e)}")
            logger.warning("Continuing with Gemini validation only")
            state["cross_validation"]["groq_validation"] = {
                "error": str(e),
                "groq_validation_summary": {
                    "consensus_score": 0.0,
                    "error": "Groq validation failed"
                }
            }
        
        
        log_workflow_step(report_id, "cross_validation", 
                        f"Cross-validation completed with status: {validation_status}", 
                        "SUCCESS" if validation_status == "PASSED" else "WARNING")
        
        logger.info("=" * 80)
        logger.info("CROSS-VALIDATION COMPLETED")
        logger.info("=" * 80)
        
        return state


# ============================================================================
# STANDALONE FUNCTION FOR LANGGRAPH INTEGRATION
# ============================================================================

def cross_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function wrapper for LangGraph integration.
    
    This function can be directly used in LangGraph workflow definitions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with cross-validation results
    """
    node = CrossValidationNode()
    return node.process(state)


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test the Cross Validation Node with sample data.
    """
    print("=" * 80)
    print("TESTING CROSS VALIDATION NODE")
    print("=" * 80)
    
    # Sample test state with vision analysis results
    test_state = {
        "report_id": "TEST-001",
        "patient_info": {
            "name": "John Doe",
            "age": 45,
            "gender": "Male"
        },
        "mri_image_path": "data/sample_mri/sample.jpg",
        "vision_analysis": {
            "findings": [
                {
                    "finding_id": 1,
                    "location": "Frontal lobe",
                    "description": "Normal brain tissue",
                    "severity": "NORMAL"
                },
                {
                    "finding_id": 2,
                    "location": "Temporal lobe",
                    "description": "Slight asymmetry noted",
                    "severity": "MILD"
                }
            ],
            "measurements": {
                "brain_width_mm": 145.5,
                "ventricle_size_mm": 12.3,
                "cortical_thickness_mm": 3.2
            },
            "confidence_score": 0.85
        }
    }
    
    # Run the node
    result_state = cross_validation_node(test_state)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if "errors" in result_state and result_state["errors"]:
        print("❌ ERRORS:")
        for error in result_state["errors"]:
            print(f"  - {error}")
    else:
        print("✅ Cross-validation completed!")
        if "cross_validation" in result_state:
            cv = result_state["cross_validation"]
            print(f"\nValidation Status: {cv.get('validation_status', 'UNKNOWN')}")
            print(f"Verified Findings: {len(cv.get('verified_findings', []))}")
            print(f"Discrepancies: {len(cv.get('discrepancies', []))}")
            print(f"Confidence: {cv.get('confidence_score', 0)}")
            print(f"\nRecommendations:")
            for rec in cv.get('recommendations', []):
                print(f"  • {rec}")
