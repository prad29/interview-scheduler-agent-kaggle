from .base_agent import BaseAgent
from typing import Dict, Any
import json
from prompts.skills_matcher_prompts import (
    SKILLS_MATCHER_SYSTEM_PROMPT,
    SKILLS_MATCHER_USER_PROMPT
)

class SkillsMatcherAgent(BaseAgent):
    """Agent responsible for matching candidate skills with job requirements"""
    
    def __init__(self):
        super().__init__("SkillsMatcherAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match candidate skills against job requirements
        
        Args:
            input_data: Dictionary containing 'candidate_data' and 'job_description'
            
        Returns:
            Dictionary with skills match score and analysis
        """
        self.log_info("Starting skills matching...")
        
        try:
            candidate_data = input_data.get('candidate_data', {})
            job_description = input_data.get('job_description', {})
            
            if not candidate_data or not job_description:
                self.log_error("Missing candidate data or job description")
                return {
                    "status": "error",
                    "message": "Missing required input data"
                }
            
            # Extract candidate skills
            candidate_skills = self._extract_candidate_skills(candidate_data)
            
            # Extract job requirements
            job_requirements = self._extract_job_requirements(job_description)
            
            # Create the prompt
            prompt = SKILLS_MATCHER_USER_PROMPT.format(
                candidate_skills=json.dumps(candidate_skills, indent=2),
                job_requirements=json.dumps(job_requirements, indent=2)
            )
            
            # Generate response using ADK
            response = await self._generate_response(
                prompt=prompt,
                system_instruction=SKILLS_MATCHER_SYSTEM_PROMPT,
                temperature=0.5
            )
            
            # Parse the JSON response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                match_result = json.loads(response)
                
                self.log_info(f"Skills matching completed. Score: {match_result.get('overall_match_percentage', 0)}%")
                
                return {
                    "status": "success",
                    "match_score": match_result.get('overall_match_percentage', 0) / 100,
                    "matched_skills": match_result.get('matched_skills', []),
                    "missing_skills": match_result.get('missing_skills', []),
                    "transferable_skills": match_result.get('transferable_skills', []),
                    "rationale": match_result.get('rationale', ''),
                    "recommendation": self._determine_recommendation(
                        match_result.get('overall_match_percentage', 0)
                    ),
                    "detailed_breakdown": match_result.get('detailed_breakdown', {})
                }
                
            except json.JSONDecodeError as e:
                self.log_error(f"Failed to parse JSON response: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to parse response: {str(e)}",
                    "raw_response": response
                }
                
        except Exception as e:
            self.log_error(f"Error in skills matching: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _extract_candidate_skills(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract skills from candidate data"""
        return {
            "technical_skills": candidate_data.get('skills', []),
            "work_experience": candidate_data.get('work_experience', []),
            "education": candidate_data.get('education', []),
            "certifications": candidate_data.get('certifications', []),
            "years_of_experience": self._calculate_years_of_experience(
                candidate_data.get('work_experience', [])
            )
        }
    
    def _extract_job_requirements(self, job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Extract requirements from job description"""
        return {
            "required_skills": job_description.get('required_skills', []),
            "preferred_skills": job_description.get('preferred_skills', []),
            "experience_level": job_description.get('experience_level', ''),
            "responsibilities": job_description.get('responsibilities', [])
        }
    
    def _calculate_years_of_experience(self, work_experience: list) -> float:
        """Calculate total years of experience"""
        # Simple calculation - can be enhanced
        return len(work_experience) * 2  # Rough estimate
    
    def _determine_recommendation(self, match_percentage: float) -> str:
        """Determine recommendation based on match percentage"""
        if match_percentage >= 85:
            return "strong_match"
        elif match_percentage >= 70:
            return "moderate_match"
        else:
            return "weak_match"