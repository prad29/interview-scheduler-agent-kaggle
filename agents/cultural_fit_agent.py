from .base_agent import BaseAgent
from typing import Dict, Any
import json
from prompts.cultural_fit_prompts import (
    CULTURAL_FIT_SYSTEM_PROMPT,
    CULTURAL_FIT_USER_PROMPT
)

class CulturalFitAgent(BaseAgent):
    """Agent responsible for analyzing cultural fit"""
    
    def __init__(self):
        super().__init__("CulturalFitAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze candidate's cultural fit
        
        Args:
            input_data: Dictionary containing 'candidate_data' and 'company_culture'
            
        Returns:
            Dictionary with cultural fit score and analysis
        """
        self.log_info("Starting cultural fit analysis...")
        
        try:
            candidate_data = input_data.get('candidate_data', {})
            company_culture = input_data.get('company_culture', {})
            job_description = input_data.get('job_description', {})
            
            if not candidate_data:
                self.log_error("Missing candidate data")
                return {
                    "status": "error",
                    "message": "Missing candidate data"
                }
            
            # Extract candidate background
            candidate_background = self._extract_candidate_background(candidate_data)
            
            # Extract or create company culture profile
            if not company_culture:
                company_culture = self._extract_culture_from_jd(job_description)
            
            # Create the prompt
            prompt = CULTURAL_FIT_USER_PROMPT.format(
                candidate_background=json.dumps(candidate_background, indent=2),
                company_culture=json.dumps(company_culture, indent=2)
            )
            
            # Generate response using ADK
            response = await self._generate_response(
                prompt=prompt,
                system_instruction=CULTURAL_FIT_SYSTEM_PROMPT,
                temperature=0.6
            )
            
            # Parse the JSON response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                fit_result = json.loads(response)
                
                self.log_info(f"Cultural fit analysis completed. Score: {fit_result.get('overall_cultural_fit_score', 0)}")
                
                return {
                    "status": "success",
                    "cultural_fit_score": fit_result.get('overall_cultural_fit_score', 0) / 100,
                    "dimensional_scores": fit_result.get('dimensional_scores', {}),
                    "rationale": fit_result.get('rationale', ''),
                    "evidence": fit_result.get('evidence', []),
                    "potential_concerns": fit_result.get('potential_concerns', []),
                    "interview_discussion_points": fit_result.get('interview_discussion_points', [])
                }
                
            except json.JSONDecodeError as e:
                self.log_error(f"Failed to parse JSON response: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to parse response: {str(e)}",
                    "raw_response": response
                }
                
        except Exception as e:
            self.log_error(f"Error in cultural fit analysis: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _extract_candidate_background(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant background for cultural assessment"""
        return {
            "work_history": candidate_data.get('work_experience', []),
            "education": candidate_data.get('education', []),
            "skills": candidate_data.get('skills', []),
            "certifications": candidate_data.get('certifications', []),
            "projects": candidate_data.get('projects', []),
            "achievements": candidate_data.get('achievements', [])
        }
    
    def _extract_culture_from_jd(self, job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Extract or infer cultural attributes from job description"""
        return {
            "cultural_attributes": job_description.get('cultural_attributes', {}),
            "team_description": job_description.get('team_description', ''),
            "responsibilities": job_description.get('responsibilities', []),
            "work_environment": job_description.get('work_environment', ''),
            "values": job_description.get('company_values', [])
        }