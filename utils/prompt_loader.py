"""
Prompt Loader Utility for MIA System
Loads and formats prompt templates with variable substitution
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
from config import PROMPTS

logger = logging.getLogger(__name__)


class PromptLoader:
    """Utility class to load and format prompts"""
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize PromptLoader
        
        Args:
            prompts_dir: Directory containing prompt files (default from config)
        """
        self.prompts_dir = prompts_dir or Path(__file__).parent.parent / "prompts"
        self._prompt_cache = {}
    
    def load_prompt(self, prompt_key: str, use_cache: bool = True) -> str:
        """
        Load a prompt from file
        
        Args:
            prompt_key: Key from PROMPTS config (e.g., 'gemini_vision_analysis')
            use_cache: Whether to use cached prompts
            
        Returns:
            Prompt content as string
        """
        if use_cache and prompt_key in self._prompt_cache:
            logger.debug(f"Loading prompt '{prompt_key}' from cache")
            return self._prompt_cache[prompt_key]
        
        if prompt_key not in PROMPTS:
            raise ValueError(f"Unknown prompt key: {prompt_key}")
        
        prompt_path = PROMPTS[prompt_key]
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        logger.info(f"Loading prompt from: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        if use_cache:
            self._prompt_cache[prompt_key] = prompt_content
        
        return prompt_content
    
    def format_prompt(self, prompt_key: str, variables: Dict[str, Any]) -> str:
        """
        Load and format a prompt with variables
        
        Args:
            prompt_key: Key from PROMPTS config
            variables: Dictionary of variables to substitute
            
        Returns:
            Formatted prompt string
        """
        prompt_template = self.load_prompt(prompt_key)
        
        try:
            formatted_prompt = prompt_template.format(**variables)
            logger.debug(f"Formatted prompt '{prompt_key}' with {len(variables)} variables")
            return formatted_prompt
        except KeyError as e:
            logger.error(f"Missing variable in prompt template: {e}")
            raise ValueError(f"Missing required variable: {e}")
    
    # Per-modality guidance injected into the dynamic vision prompt
    _MODALITY_INSTRUCTIONS = {
        "MRI": (
            "### MRI-Specific Analysis Guidelines\n"
            "- Identify MRI sequence: T1, T2, FLAIR, DWI, SWI, GRE, etc.\n"
            "- Evaluate signal intensities: hyperintense (bright), hypointense (dark), isointense\n"
            "- Assess gray-white matter differentiation\n"
            "- Look for enhancement patterns (if contrast study)\n"
            "- Evaluate diffusion restriction or ADC values if DWI sequence\n"
            "- Check for midline shift, herniation, ventricular size\n"
            "- Note any edema, mass effect, or leptomeningeal involvement"
        ),
        "X-Ray": (
            "### X-Ray-Specific Analysis Guidelines\n"
            "- Evaluate bone density, cortical integrity, and trabecular pattern\n"
            "- Identify any fractures: location, type (transverse, oblique, comminuted, etc.), displacement\n"
            "- Assess joint spaces for narrowing, effusion, or subluxation\n"
            "- For chest X-ray: evaluate cardiothoracic ratio, lung fields, hilum, costophrenic angles\n"
            "- Note soft tissue calcifications or foreign bodies\n"
            "- Identify any lytic or sclerotic lesions\n"
            "- Assess alignment and symmetry of bony structures"
        ),
        "CT": (
            "### CT-Specific Analysis Guidelines\n"
            "- Report Hounsfield Unit (HU) ranges for observed densities\n"
            "- Identify window/level settings that best display the region of interest\n"
            "- Evaluate bone window for cortical and medullary detail\n"
            "- Assess soft tissue window for organ morphology and density\n"
            "- Look for hemorrhage (hyperdense), edema (hypodense), calcifications (hyperdense)\n"
            "- For CT angiography: evaluate vascular anatomy and any occlusions\n"
            "- Assess for air, fluid levels, and free fluid"
        ),
        "Ultrasound": (
            "### Ultrasound-Specific Analysis Guidelines\n"
            "- Classify echogenicity: anechoic, hypoechoic, isoechoic, hyperechoic\n"
            "- Assess posterior acoustic enhancement or shadowing\n"
            "- Evaluate organ size, shape, and margins\n"
            "- Identify any fluid collections, cysts, or solid masses\n"
            "- Note vascularity if Doppler is present\n"
            "- Assess for free fluid in peritoneal/pleural spaces\n"
            "- For obstetric: note gestational age markers, fetal anatomy"
        ),
        "PET": (
            "### PET-Specific Analysis Guidelines\n"
            "- Identify areas of abnormal metabolic activity (hot spots)\n"
            "- Report SUV (Standardized Uptake Value) estimates where visible\n"
            "- Compare metabolic activity to background tissues\n"
            "- Identify physiologic uptake areas (brain, heart, kidneys, bladder)\n"
            "- Note any suspicious foci for malignancy staging\n"
            "- If PET-CT fusion: correlate metabolic with structural findings"
        ),
        "Mammography": (
            "### Mammography-Specific Analysis Guidelines\n"
            "- Assess breast density (A: almost entirely fatty to D: extremely dense)\n"
            "- Identify masses: shape, margins, density\n"
            "- Look for calcifications: morphology (amorphous, pleomorphic, linear branching)\n"
            "- Note architectural distortion or asymmetries\n"
            "- Evaluate skin thickening or nipple changes\n"
            "- Provide BI-RADS category assessment (0-6)"
        ),
        "Fluoroscopy": (
            "### Fluoroscopy-Specific Analysis Guidelines\n"
            "- Evaluate contrast opacification pattern (if contrast study)\n"
            "- Look for filling defects, mucosal irregularity, or strictures\n"
            "- Assess motility patterns (if GI study)\n"
            "- Note any perforation, leak, or extravasation\n"
            "- Evaluate vascular anatomy (if angiography)"
        ),
        "Nuclear Medicine": (
            "### Nuclear Medicine-Specific Analysis Guidelines\n"
            "- Identify distribution pattern of radiotracer\n"
            "- Note areas of increased or decreased uptake\n"
            "- Compare uptake to contralateral structures where applicable\n"
            "- Correlate with clinical indication (bone scan, thyroid, cardiac, etc.)\n"
            "- Report photopenic defects or cold spots"
        ),
    }

    def get_vision_analysis_prompt(
        self,
        patient_info: Optional[Dict[str, Any]] = None,
        image_classification: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get Gemini vision analysis prompt, dynamically adapted to the detected image type.

        Args:
            patient_info: Optional patient information for context
            image_classification: Classification result from classify_image_type() containing
                                   image_type, sub_type, anatomical_region, imaging_plane, confidence

        Returns:
            Vision analysis prompt tailored to the detected medical imaging modality
        """
        prompt = self.load_prompt("gemini_vision_analysis", use_cache=False)

        # --- Inject modality fields ---
        classification = image_classification or {}
        image_type = classification.get("image_type", "Medical Image")
        image_subtype = classification.get("sub_type", "Unknown sub-type")
        anatomical_region = classification.get("anatomical_region", "Unknown region")
        imaging_plane = classification.get("imaging_plane", "Unknown")
        confidence = classification.get("confidence", 0.0)

        # Get modality-specific instructions
        modality_instructions = self._MODALITY_INSTRUCTIONS.get(
            image_type,
            (
                "### General Medical Imaging Analysis Guidelines\n"
                "- Apply standard radiological interpretation principles\n"
                "- Identify all visible anatomical structures\n"
                "- Note any abnormalities in density, signal, or structure\n"
                "- Compare with expected normal anatomy for this body region"
            )
        )

        prompt = prompt.replace("{image_type}", image_type)
        prompt = prompt.replace("{image_subtype}", image_subtype)
        prompt = prompt.replace("{anatomical_region}", anatomical_region)
        prompt = prompt.replace("{imaging_plane}", imaging_plane)
        prompt = prompt.replace("{classification_confidence}", f"{confidence:.0%}")
        prompt = prompt.replace("{modality_specific_instructions}", modality_instructions)

        # --- Inject patient context ---
        patient_context = ""
        if patient_info:
            patient_context = (
                "## Patient Context\n"
                f"- Age: {patient_info.get('age', 'Unknown')} years\n"
                f"- Gender: {patient_info.get('gender', 'Unknown')}\n"
                f"- BMI: {patient_info.get('bmi', 'Unknown')}\n"
                f"- Profession: {patient_info.get('profession', 'Unknown')}\n"
            )
        prompt = prompt.replace("{patient_context}", patient_context)

        return prompt
    
    def get_cross_validation_prompt(self, 
                                    vision_results: Dict[str, Any],
                                    patient_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Get Gemini cross-validation prompt with vision results
        
        Args:
            vision_results: Results from vision analysis
            patient_info: Optional patient information
            
        Returns:
            Cross-validation prompt with embedded results
        """
        prompt = self.load_prompt("gemini_cross_validation")
        
        # Add vision results context
        import json
        results_json = json.dumps(vision_results, indent=2)
        context = f"\n\n## Vision Analysis Results to Validate\n```json\n{results_json}\n```\n"
        
        if patient_info:
            context += f"\n## Patient Demographics\n"
            context += f"- Age: {patient_info.get('age', 'Unknown')} years\n"
            context += f"- Gender: {patient_info.get('gender', 'Unknown')}\n"
            context += f"- BMI: {patient_info.get('bmi', 'Unknown')}\n"
            context += f"- Profession: {patient_info.get('profession', 'Unknown')}\n"
        
        prompt += context
        return prompt
    
    def get_report_generation_prompt(self,
                                    vision_results: Dict[str, Any],
                                    validation_results: Dict[str, Any],
                                    patient_info: Dict[str, Any],
                                    image_metadata: Dict[str, Any],
                                    image_classification: Optional[Dict[str, Any]] = None) -> str:
        """
        Get Grok report generation prompt with all analysis data.

        Args:
            vision_results: Vision analysis results
            validation_results: Cross-validation results
            patient_info: Patient information
            image_metadata: Medical image study metadata (modality-agnostic)
            image_classification: Image type classification result (image_type, sub_type, etc.)

        Returns:
            Report generation prompt with all context
        """
        prompt = self.load_prompt("groq_report_generation")

        import json

        context = "\n\n## Input Data for Report Generation\n\n"

        # --- Image type context (Bug #2 fix) ---
        if image_classification:
            context += "### Medical Image Classification\n```json\n"
            context += json.dumps(image_classification, indent=2, default=str)
            context += "\n```\n\n"
            context += (
                f"**IMPORTANT**: This report is for a "
                f"**{image_classification.get('image_type', 'Medical')} image** "
                f"(sub-type: {image_classification.get('sub_type', 'N/A')}, "
                f"region: {image_classification.get('anatomical_region', 'N/A')}). "
                f"Generate your report using the clinical language and standards "
                f"appropriate for this imaging modality.\n\n"
            )

        context += "### Patient Information\n```json\n"
        context += json.dumps(patient_info, indent=2, default=str)
        context += "\n```\n\n"

        context += "### Image Study Metadata\n```json\n"
        context += json.dumps(image_metadata, indent=2, default=str)
        context += "\n```\n\n"

        context += "### Vision Analysis Results\n```json\n"
        context += json.dumps(vision_results, indent=2, default=str)
        context += "\n```\n\n"

        context += "### Cross-Validation Results\n```json\n"
        context += json.dumps(validation_results, indent=2, default=str)
        context += "\n```\n\n"

        prompt += context
        return prompt
    
    def get_safety_analysis_prompt(self,
                                   vision_results: Dict[str, Any],
                                   validation_results: Dict[str, Any],
                                   report_content: Dict[str, Any],
                                   patient_info: Dict[str, Any],
                                   image_classification: Optional[Dict[str, Any]] = None) -> str:
        """
        Get Grok safety analysis prompt with all data.

        Args:
            vision_results: Vision analysis results
            validation_results: Cross-validation results
            report_content: Generated report content
            patient_info: Patient information
            image_classification: Image type classification result

        Returns:
            Safety analysis prompt with all context
        """
        prompt = self.load_prompt("groq_safety_analysis")

        import json

        context = "\n\n## Data for Safety Analysis\n\n"

        # --- Image type context (Bug #2 fix) ---
        if image_classification:
            context += "### Imaging Modality Context\n```json\n"
            context += json.dumps(image_classification, indent=2, default=str)
            context += "\n```\n\n"

        context += "### Patient Demographics\n```json\n"
        context += json.dumps(patient_info, indent=2, default=str)
        context += "\n```\n\n"

        context += "### Vision Analysis Results\n```json\n"
        context += json.dumps(vision_results, indent=2, default=str)
        context += "\n```\n\n"

        context += "### Cross-Validation Results\n```json\n"
        context += json.dumps(validation_results, indent=2, default=str)
        context += "\n```\n\n"

        context += "### Generated Report Content\n```json\n"
        context += json.dumps(report_content, indent=2, default=str)
        context += "\n```\n\n"

        prompt += context
        return prompt
    
    def get_image_classification_prompt(self, 
                                       patient_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Get Gemini image classification prompt
        
        Args:
            patient_info: Optional patient information for context
            
        Returns:
            Image classification prompt
        """
        prompt = self.load_prompt("gemini_image_classification")
        
        # Add patient context if available
        patient_context = ""
        if patient_info:
            patient_context = f"Age: {patient_info.get('age', 'Unknown')} years, "
            patient_context += f"Gender: {patient_info.get('gender', 'Unknown')}, "
            patient_context += f"BMI: {patient_info.get('bmi', 'Unknown')}"
        else:
            patient_context = "No patient information provided"
        
        # Replace placeholders
        prompt = prompt.replace("{patient_context}", patient_context)
        prompt = prompt.replace("{additional_notes}", "")
        
        return prompt
    
    def get_groq_cross_validation_prompt(self,
                                        gemini_findings: Dict[str, Any],
                                        gemini_validation: Dict[str, Any],
                                        patient_info: Dict[str, Any],
                                        image_type: str,
                                        image_classification_confidence: float) -> str:
        """
        Get Groq cross-validation prompt with all context
        
        Args:
            gemini_findings: Vision analysis results from Gemini
            gemini_validation: Cross-validation results from Gemini
            patient_info: Patient information
            image_type: Detected medical image type
            image_classification_confidence: Confidence in image classification
            
        Returns:
            Groq cross-validation prompt with all data
        """
        prompt = self.load_prompt("groq_cross_validation")
        
        import json
        
        # Replace placeholders with actual data
        prompt = prompt.replace("{image_type}", image_type)
        prompt = prompt.replace("{image_classification_confidence}", 
                              f"{image_classification_confidence:.2f}")
        prompt = prompt.replace("{patient_info}", 
                              json.dumps(patient_info, indent=2, default=str))
        prompt = prompt.replace("{gemini_findings}", 
                              json.dumps(gemini_findings, indent=2, default=str))
        prompt = prompt.replace("{gemini_validation}", 
                              json.dumps(gemini_validation, indent=2, default=str))
        
        return prompt

    
    def clear_cache(self):
        """Clear the prompt cache"""
        self._prompt_cache = {}
        logger.info("Prompt cache cleared")
    
    def reload_prompt(self, prompt_key: str) -> str:
        """
        Reload a prompt from file, bypassing cache
        
        Args:
            prompt_key: Key from PROMPTS config
            
        Returns:
            Reloaded prompt content
        """
        if prompt_key in self._prompt_cache:
            del self._prompt_cache[prompt_key]
        return self.load_prompt(prompt_key, use_cache=False)


# Convenience function for quick access
def load_prompt(prompt_key: str) -> str:
    """
    Quick function to load a prompt
    
    Args:
        prompt_key: Key from PROMPTS config
        
    Returns:
        Prompt content
    """
    loader = PromptLoader()
    return loader.load_prompt(prompt_key)
