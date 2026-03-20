"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  MIA REPORT & SAFETY ANALYSIS NODE                           ║
║                        Powered by Grok                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Node Name: Report & Safety Analysis Node
Description: Generates professional medical reports and performs critical safety analysis
             using Grok LLM. Combines report generation and safety checks in one node.

Input:
    - vision_analysis: Dict containing vision analysis results
    - cross_validation: Dict containing validation results
    - patient_info: Dict containing patient details
    - mri_metadata: Dict containing MRI study information

Output:
    - report_content: Dict containing:
        * professional_report: Formatted medical report
        * clinical_correlation: Clinical analysis and correlation
        * recommendations: Medical recommendations
        * raw_response: Complete response from Grok
    - safety_analysis: Dict containing:
        * critical_findings: List of critical findings requiring immediate attention
        * safety_score: Overall safety score (0-100)
        * urgency_level: ROUTINE/URGENT/CRITICAL
        * safety_recommendations: Safety-specific recommendations

Author: MIA Team - Agenix AI
Created: 2026-01-07
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

# Import services
from services import get_groq_service
from utils import PromptLoader
from utils.logger import logger, log_workflow_step, log_error_with_context


class ReportSafetyNode:
    """
    Report & Safety Analysis Node for MIA Workflow
    
    This node performs two critical functions:
    1. REPORT GENERATION: Creates professional medical reports using Grok
       - Synthesizes findings from vision and validation
       - Provides clinical correlation
       - Generates actionable recommendations
    
    2. SAFETY ANALYSIS: Performs critical safety checks using Grok
       - Identifies critical findings
       - Assesses urgency levels
       - Provides safety-specific recommendations
    """
    
    def __init__(self):
        """Initialize the Report & Safety Node with Grok service."""
        self.groq_service = None
        self.prompt_loader = PromptLoader()
        logger.info("Report & Safety Analysis Node initialized")
    
    def _initialize_services(self):
        """Lazy initialization of Grok service."""
        if self.groq_service is None:
            self.groq_service = get_groq_service()
            logger.info("Grok service initialized")
    
    def synthesize_findings(self, vision_analysis: Dict[str, Any], 
                           cross_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize findings from vision analysis and cross-validation.
        
        Args:
            vision_analysis: Results from vision analysis node
            cross_validation: Results from cross-validation node
            
        Returns:
            Dict containing synthesized findings
        """
        synthesized = {
            "total_findings": 0,
            "verified_findings": 0,
            "critical_findings": 0,
            "findings_summary": []
        }
        
        # Get verified findings from cross-validation
        verified_findings = cross_validation.get("verified_findings", [])
        synthesized["total_findings"] = len(verified_findings)
        
        for finding in verified_findings:
            if finding.get("verification_status") == "VERIFIED":
                synthesized["verified_findings"] += 1
            
            # Check for critical findings
            severity = finding.get("severity", "").upper()
            if severity in ["CRITICAL", "SEVERE", "HIGH"]:
                synthesized["critical_findings"] += 1
            
            # Create summary
            synthesized["findings_summary"].append({
                "location": finding.get("location", "Unknown"),
                "description": finding.get("description", "No description"),
                "severity": finding.get("severity", "UNKNOWN"),
                "verified": finding.get("verification_status") == "VERIFIED"
            })
        
        logger.info(f"Synthesized {synthesized['verified_findings']}/{synthesized['total_findings']} "
                   f"verified findings ({synthesized['critical_findings']} critical)")
        
        return synthesized
    
    def generate_clinical_correlation(self, patient_info: Dict[str, Any], 
                                     findings: Dict[str, Any]) -> str:
        """
        Generate clinical correlation based on patient info and findings.
        
        Args:
            patient_info: Patient information
            findings: Synthesized findings
            
        Returns:
            Clinical correlation text
        """
        age = patient_info.get("age", "unknown")
        gender = patient_info.get("gender", "unknown")
        
        correlation = f"Patient is a {age}-year-old {gender}. "
        
        if findings["critical_findings"] > 0:
            correlation += f"Analysis revealed {findings['critical_findings']} critical finding(s) "
            correlation += "requiring immediate clinical attention. "
        elif findings["verified_findings"] > 0:
            correlation += f"Analysis identified {findings['verified_findings']} verified finding(s). "
        else:
            correlation += "No significant abnormalities detected. "
        
        correlation += "Detailed findings are documented in the report below."
        
        return correlation
    
    def assess_urgency_level(self, critical_findings: int, safety_score: float) -> str:
        """
        Assess the urgency level based on findings and safety score.
        
        Args:
            critical_findings: Number of critical findings
            safety_score: Safety score (0-100)
            
        Returns:
            Urgency level: ROUTINE, URGENT, or CRITICAL
        """
        if critical_findings > 0 or safety_score < 50:
            return "CRITICAL"
        elif safety_score < 75:
            return "URGENT"
        else:
            return "ROUTINE"
    
    def identify_critical_findings(self, findings_summary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify critical findings that require immediate attention.
        
        Args:
            findings_summary: List of all findings
            
        Returns:
            List of critical findings
        """
        critical = []
        
        for finding in findings_summary:
            severity = finding.get("severity", "").upper()
            if severity in ["CRITICAL", "SEVERE", "HIGH"]:
                critical.append({
                    "location": finding.get("location"),
                    "description": finding.get("description"),
                    "severity": severity,
                    "action_required": "Immediate clinical review recommended"
                })
        
        if critical:
            logger.warning(f"Identified {len(critical)} critical findings requiring immediate attention")
        
        return critical
    
    def calculate_safety_score(self, findings: Dict[str, Any], 
                              validation_status: str) -> float:
        """
        Calculate overall safety score based on findings and validation.
        
        Args:
            findings: Synthesized findings
            validation_status: Validation status from cross-validation
            
        Returns:
            Safety score (0-100)
        """
        base_score = 100.0
        
        # Deduct points for critical findings
        base_score -= findings["critical_findings"] * 30
        
        # Deduct points for unverified findings
        unverified = findings["total_findings"] - findings["verified_findings"]
        base_score -= unverified * 10
        
        # Deduct points for validation issues
        if validation_status == "FAILED":
            base_score -= 25
        elif validation_status == "WARNING":
            base_score -= 10
        
        # Ensure score is between 0 and 100
        safety_score = max(0.0, min(100.0, base_score))
        
        logger.info(f"Calculated safety score: {safety_score}/100")
        
        return safety_score
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function for Report & Safety Analysis Node.
        
        This function orchestrates both report generation and safety analysis:
        1. Checks for required input data
        2. Initializes Grok service
        3. Synthesizes findings from previous nodes
        4. Generates professional medical report using Grok
        5. Performs safety analysis using Grok
        6. Calculates safety scores and urgency levels
        7. Returns updated state with report and safety results
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with report_content and safety_analysis results
        """
        report_id = state.get("report_id", f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        log_workflow_step(report_id, "report_safety", "Starting Report & Safety Analysis Node")
        
        # Update current step
        state["current_step"] = "report_safety"
        
        # Check for previous errors
        if state.get("errors"):
            logger.warning("Previous errors detected, skipping report and safety analysis")
            return state
        
        # Step 1: Check for required data
        logger.info("=" * 80)
        logger.info("STEP 1: CHECKING REQUIRED DATA")
        logger.info("=" * 80)
        
        vision_analysis = state.get("vision_analysis", {})
        cross_validation = state.get("cross_validation", {})
        
        if not vision_analysis:
            error_msg = "No vision analysis results found. Cannot generate report."
            logger.error(error_msg)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        if not cross_validation:
            logger.warning("No cross-validation results found. Proceeding with vision analysis only.")
        
        logger.info("Required data available, proceeding with report generation")
        
        # Step 2: Initialize services
        logger.info("=" * 80)
        logger.info("STEP 2: INITIALIZING GROK SERVICE")
        logger.info("=" * 80)
        
        try:
            self._initialize_services()
        except Exception as e:
            error_msg = f"Failed to initialize Grok service: {str(e)}"
            logger.error(error_msg)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        # Step 3: Synthesize findings
        logger.info("=" * 80)
        logger.info("STEP 3: SYNTHESIZING FINDINGS")
        logger.info("=" * 80)
        
        synthesized_findings = self.synthesize_findings(vision_analysis, cross_validation)
        
        # Step 4: Generate clinical correlation
        logger.info("=" * 80)
        logger.info("STEP 4: GENERATING CLINICAL CORRELATION")
        logger.info("=" * 80)
        
        clinical_correlation = self.generate_clinical_correlation(
            state.get("patient_info", {}),
            synthesized_findings
        )
        logger.info(f"Clinical correlation: {clinical_correlation}")
        
        # Step 5: Generate professional report with Grok
        logger.info("=" * 80)
        logger.info("STEP 5: GENERATING PROFESSIONAL REPORT (GROK)")
        logger.info("=" * 80)
        
        try:
            # Get image classification from state (Bug #2 fix)
            image_classification = state.get("image_classification")
            if image_classification:
                logger.info(f"Report will use image type context: {image_classification.get('image_type', 'Unknown')}")

            # Get the report generation prompt
            # Use modality-agnostic key with fallback to old key (Bug #3 fix)
            image_metadata = state.get("image_metadata", state.get("mri_metadata", {}))
            prompt = self.prompt_loader.get_report_generation_prompt(
                vision_results=vision_analysis,
                validation_results=cross_validation,
                patient_info=state.get("patient_info", {}),
                image_metadata=image_metadata,
                image_classification=image_classification
            )
            
            logger.info("Generating report with Grok...")
            
            # Generate report using Grok
            report_data = self.groq_service.generate_report(prompt)
            
            logger.info("Professional report generated successfully")
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            log_error_with_context(e, {"report_id": report_id, "step": "report_generation"})
            state.setdefault("errors", []).append(f"Report generation error: {str(e)}")
            return state
        
        # Step 6: Perform safety analysis with Grok
        logger.info("=" * 80)
        logger.info("STEP 6: PERFORMING SAFETY ANALYSIS (GROK)")
        logger.info("=" * 80)
        
        try:
            # Get the safety analysis prompt (Bug #2 fix — pass image_classification)
            safety_prompt = self.prompt_loader.get_safety_analysis_prompt(
                vision_results=vision_analysis,
                validation_results=cross_validation,
                report_content=report_data,
                patient_info=state.get("patient_info", {}),
                image_classification=state.get("image_classification")
            )
            
            logger.info("Performing safety analysis with Grok...")
            
            # Perform safety analysis using Grok
            safety_results = self.groq_service.perform_safety_analysis(safety_prompt)
            
            logger.info("Safety analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Safety analysis failed: {str(e)}")
            log_error_with_context(e, {"report_id": report_id, "step": "safety_analysis"})
            # Continue with local safety analysis
            safety_results = {}
        
        # Step 7: Identify critical findings
        logger.info("=" * 80)
        logger.info("STEP 7: IDENTIFYING CRITICAL FINDINGS")
        logger.info("=" * 80)
        
        critical_findings = self.identify_critical_findings(synthesized_findings["findings_summary"])
        
        # Step 8: Calculate safety score
        logger.info("=" * 80)
        logger.info("STEP 8: CALCULATING SAFETY SCORE")
        logger.info("=" * 80)
        
        validation_status = cross_validation.get("validation_status", "UNKNOWN")
        safety_score = self.calculate_safety_score(synthesized_findings, validation_status)
        
        # Step 9: Assess urgency level
        logger.info("=" * 80)
        logger.info("STEP 9: ASSESSING URGENCY LEVEL")
        logger.info("=" * 80)
        
        urgency_level = self.assess_urgency_level(len(critical_findings), safety_score)
        logger.info(f"Urgency level: {urgency_level}")
        
        # Step 10: Generate safety recommendations
        logger.info("=" * 80)
        logger.info("STEP 10: GENERATING SAFETY RECOMMENDATIONS")
        logger.info("=" * 80)
        
        safety_recommendations = []
        
        if urgency_level == "CRITICAL":
            safety_recommendations.append("⚠️ CRITICAL: Immediate clinical review required")
            safety_recommendations.append("Contact attending physician immediately")
        elif urgency_level == "URGENT":
            safety_recommendations.append("⚠️ URGENT: Clinical review recommended within 24 hours")
        else:
            safety_recommendations.append("✓ ROUTINE: Standard follow-up recommended")
        
        if critical_findings:
            safety_recommendations.append(f"Address {len(critical_findings)} critical finding(s)")
        
        for rec in safety_recommendations:
            logger.info(f"  {rec}")
        
        # Compile final results
        state["report_content"] = {
            "professional_report": report_data.get("raw_response", "Report generated"),
            "clinical_correlation": clinical_correlation,
            "recommendations": report_data.get("recommendations", [
                "Consult with healthcare provider for detailed interpretation",
                "Follow recommended treatment plan",
                "Schedule follow-up imaging as advised"
            ]),
            "synthesized_findings": synthesized_findings,
            "raw_response": report_data,
            "generated_at": datetime.now().isoformat(),
            "model_used": "grok"
        }
        
        state["safety_analysis"] = {
            "critical_findings": critical_findings,
            "safety_score": safety_score,
            "urgency_level": urgency_level,
            "safety_recommendations": safety_recommendations,
            "groq_safety_analysis": safety_results,
            "analyzed_at": datetime.now().isoformat(),
            "model_used": "grok"
        }
        
        log_workflow_step(report_id, "report_safety", 
                        f"Report and safety analysis completed (Urgency: {urgency_level})", 
                        "SUCCESS")
        
        logger.info("=" * 80)
        logger.info("REPORT & SAFETY ANALYSIS COMPLETED")
        logger.info("=" * 80)
        
        return state


# ============================================================================
# STANDALONE FUNCTIONS FOR LANGGRAPH INTEGRATION
# ============================================================================

def report_safety_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function wrapper for LangGraph integration (combined).
    
    This function can be directly used in LangGraph workflow definitions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with report and safety analysis results
    """
    node = ReportSafetyNode()
    return node.process(state)


def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function for report generation only (backward compatibility).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with report_content results
    """
    return report_safety_node(state)


def safety_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function for safety analysis only (backward compatibility).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with safety_analysis results
    """
    return report_safety_node(state)


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test the Report & Safety Analysis Node with sample data.
    """
    print("=" * 80)
    print("TESTING REPORT & SAFETY ANALYSIS NODE")
    print("=" * 80)
    
    # Sample test state with vision and validation results
    test_state = {
        "report_id": "TEST-001",
        "patient_info": {
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "profession": "Engineer"
        },
        "mri_metadata": {
            "study_type": "Brain MRI",
            "sequence_type": "T2",
            "imaging_plane": "Axial"
        },
        "vision_analysis": {
            "findings": [
                {
                    "finding_id": 1,
                    "location": "Frontal lobe",
                    "description": "Normal brain tissue",
                    "severity": "NORMAL"
                }
            ],
            "measurements": {
                "brain_width_mm": 145.5
            }
        },
        "cross_validation": {
            "validation_status": "PASSED",
            "verified_findings": [
                {
                    "finding_id": 1,
                    "location": "Frontal lobe",
                    "description": "Normal brain tissue",
                    "severity": "NORMAL",
                    "verification_status": "VERIFIED"
                }
            ]
        }
    }
    
    # Run the node
    result_state = report_safety_node(test_state)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if "errors" in result_state and result_state["errors"]:
        print("❌ ERRORS:")
        for error in result_state["errors"]:
            print(f"  - {error}")
    else:
        print("✅ Report and safety analysis completed!")
        
        if "report_content" in result_state:
            print(f"\n📄 REPORT GENERATED")
            print(f"Clinical Correlation: {result_state['report_content'].get('clinical_correlation', 'N/A')}")
        
        if "safety_analysis" in result_state:
            sa = result_state["safety_analysis"]
            print(f"\n🛡️ SAFETY ANALYSIS")
            print(f"Safety Score: {sa.get('safety_score', 0)}/100")
            print(f"Urgency Level: {sa.get('urgency_level', 'UNKNOWN')}")
            print(f"Critical Findings: {len(sa.get('critical_findings', []))}")
            print(f"\nSafety Recommendations:")
            for rec in sa.get('safety_recommendations', []):
                print(f"  • {rec}")
