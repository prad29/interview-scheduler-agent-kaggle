from .base_agent import BaseAgent
from typing import Dict, Any
import json
from prompts.resume_parser_prompts import (
    RESUME_PARSER_SYSTEM_PROMPT,
    RESUME_PARSER_USER_PROMPT
)

class ResumeParserAgent(BaseAgent):
    """Agent responsible for parsing resumes and extracting structured data"""
    
    def __init__(self):
        super().__init__("ResumeParserAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse resume and extract structured information
        
        Args:
            input_data: Dictionary containing 'resume_content' (text) or 'resume_path'
            
        Returns:
            Dictionary with parsed candidate information
        """
        self.log_info("Starting resume parsing...")
        
        try:
            resume_content = input_data.get('resume_content', '')
            
            if not resume_content:
                self.log_error("No resume content provided")
                return {
                    "status": "error",
                    "message": "No resume content provided",
                    "candidate_data": None
                }
            
            # Create the prompt
            prompt = RESUME_PARSER_USER_PROMPT.format(resume_content=resume_content)
            
            # Generate response using ADK
            response = await self._generate_response(
                prompt=prompt,
                system_instruction=RESUME_PARSER_SYSTEM_PROMPT,
                temperature=0.3  # Lower temperature for more consistent extraction
            )
            
            # Parse the JSON response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                candidate_data = json.loads(response)
                
                self.log_info("Resume parsing completed successfully")
                
                return {
                    "status": "success",
                    "candidate_data": candidate_data,
                    "confidence_scores": self._calculate_confidence_scores(candidate_data)
                }
                
            except json.JSONDecodeError as e:
                self.log_error(f"Failed to parse JSON response: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to parse response: {str(e)}",
                    "raw_response": response,
                    "candidate_data": None
                }
                
        except Exception as e:
            self.log_error(f"Error in resume parsing: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "candidate_data": None
            }
    
    def _calculate_confidence_scores(self, candidate_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for extracted fields"""
        scores = {}
        
        # Check completeness of each section
        if candidate_data.get('personal_info'):
            personal = candidate_data['personal_info']
            required_fields = ['name', 'email']
            present_fields = sum(1 for field in required_fields if personal.get(field))
            scores['personal_info'] = present_fields / len(required_fields)
        
        if candidate_data.get('work_experience'):
            scores['work_experience'] = 1.0 if len(candidate_data['work_experience']) > 0 else 0.5
        
        if candidate_data.get('education'):
            scores['education'] = 1.0 if len(candidate_data['education']) > 0 else 0.5
        
        if candidate_data.get('skills'):
            scores['skills'] = 1.0 if len(candidate_data['skills']) > 0 else 0.3
        
        return scores