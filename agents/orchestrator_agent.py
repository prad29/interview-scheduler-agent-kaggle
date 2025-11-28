from .base_agent import BaseAgent
from .resume_parser_agent import ResumeParserAgent
from .skills_matcher_agent import SkillsMatcherAgent
from .cultural_fit_agent import CulturalFitAgent
from .interview_scheduler_agent import InterviewSchedulerAgent
from typing import Dict, Any, List
import asyncio
from config import config

class OrchestratorAgent(BaseAgent):
    """Master coordinator agent managing the workflow"""
    
    def __init__(self):
        super().__init__("OrchestratorAgent")
        self.resume_parser = ResumeParserAgent()
        self.skills_matcher = SkillsMatcherAgent()
        self.cultural_fit = CulturalFitAgent()
        self.interview_scheduler = InterviewSchedulerAgent()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the entire recruitment workflow
        
        Args:
            input_data: Dictionary containing 'resumes', 'job_description', and optional config
            
        Returns:
            Dictionary with ranked candidates and processing results
        """
        self.log_info("Starting orchestration workflow...")
        
        try:
            resumes = input_data.get('resumes', [])
            job_description = input_data.get('job_description', {})
            company_culture = input_data.get('company_culture', {})
            interviewer_email = input_data.get('interviewer_email', '')
            
            if not resumes:
                self.log_error("No resumes provided")
                return {
                    "status": "error",
                    "message": "No resumes provided",
                    "ranked_candidates": []
                }
            
            if not job_description:
                self.log_error("No job description provided")
                return {
                    "status": "error",
                    "message": "No job description provided",
                    "ranked_candidates": []
                }
            
            # Phase 1: Parse all resumes in parallel
            self.log_info(f"Phase 1: Parsing {len(resumes)} resumes...")
            parsed_candidates = await self._parse_resumes_parallel(resumes)
            
            # Filter out failed parses
            valid_candidates = [c for c in parsed_candidates if c['status'] == 'success']
            self.log_info(f"Successfully parsed {len(valid_candidates)} resumes")
            
            # Phase 2: Skills matching and cultural fit analysis in parallel
            self.log_info("Phase 2: Evaluating candidates...")
            evaluated_candidates = await self._evaluate_candidates_parallel(
                valid_candidates,
                job_description,
                company_culture
            )
            
            # Phase 3: Rank candidates
            self.log_info("Phase 3: Ranking candidates...")
            ranked_candidates = self._rank_candidates(evaluated_candidates)
            
            # Phase 4: Schedule interviews for top candidates
            self.log_info("Phase 4: Scheduling interviews...")
            qualified_candidates = self._filter_qualified_candidates(ranked_candidates)
            
            scheduling_result = {"scheduled_slots": []}
            if qualified_candidates and interviewer_email:
                scheduling_result = await self.interview_scheduler.process({
                    "candidates": qualified_candidates,
                    "interviewer_email": interviewer_email
                })
            
            self.log_info("Orchestration workflow completed successfully")
            
            return {
                "status": "success",
                "ranked_candidates": ranked_candidates,
                "processing_summary": {
                    "total_resumes": len(resumes),
                    "successfully_parsed": len(valid_candidates),
                    "qualified_candidates": len(qualified_candidates),
                    "interviews_scheduled": len(scheduling_result.get('scheduled_slots', []))
                },
                "scheduled_interviews": scheduling_result.get('scheduled_slots', [])
            }
            
        except Exception as e:
            self.log_error(f"Error in orchestration: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "ranked_candidates": []
            }
    
    async def _parse_resumes_parallel(self, resumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse multiple resumes in parallel"""
        tasks = []
        
        for idx, resume in enumerate(resumes):
            task = self._parse_single_resume(resume, idx)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        parsed_candidates = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                self.log_error(f"Resume {idx} parsing failed: {str(result)}")
                parsed_candidates.append({
                    "status": "error",
                    "resume_index": idx,
                    "error": str(result)
                })
            else:
                parsed_candidates.append({
                    **result,
                    "resume_index": idx,
                    "id": f"candidate_{idx}"
                })
        
        return parsed_candidates
    
    async def _parse_single_resume(self, resume: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Parse a single resume"""
        self.log_debug(f"Parsing resume {index}...")
        return await self.resume_parser.process(resume)
    
    async def _evaluate_candidates_parallel(self,
                                           candidates: List[Dict[str, Any]],
                                           job_description: Dict[str, Any],
                                           company_culture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate candidates in parallel (skills + cultural fit)"""
        tasks = []
        
        for candidate in candidates:
            task = self._evaluate_single_candidate(
                candidate,
                job_description,
                company_culture
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        evaluated_candidates = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                self.log_error(f"Candidate {idx} evaluation failed: {str(result)}")
            else:
                evaluated_candidates.append(result)
        
        return evaluated_candidates
    
    async def _evaluate_single_candidate(self,
                                        candidate: Dict[str, Any],
                                        job_description: Dict[str, Any],
                                        company_culture: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single candidate (skills and cultural fit in parallel)"""
        candidate_data = candidate.get('candidate_data', {})
        
        # Run skills matching and cultural fit analysis in parallel
        skills_task = self.skills_matcher.process({
            "candidate_data": candidate_data,
            "job_description": job_description
        })
        
        cultural_task = self.cultural_fit.process({
            "candidate_data": candidate_data,
            "company_culture": company_culture,
            "job_description": job_description
        })
        
        skills_result, cultural_result = await asyncio.gather(skills_task, cultural_task)
        
        # Combine results
        return {
            "id": candidate.get('id'),
            "resume_index": candidate.get('resume_index'),
            "candidate_data": candidate_data,
            "skills_evaluation": skills_result,
            "cultural_evaluation": cultural_result
        }
    
    def _rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank candidates based on weighted scores"""
        ranked = []
        
        for candidate in candidates:
            skills_eval = candidate.get('skills_evaluation', {})
            cultural_eval = candidate.get('cultural_evaluation', {})
            candidate_data = candidate.get('candidate_data', {})
            
            # Get scores
            skills_score = skills_eval.get('match_score', 0)
            cultural_score = cultural_eval.get('cultural_fit_score', 0)
            
            # Calculate years of experience score (normalized)
            years_exp = self._get_years_of_experience(candidate_data)
            exp_score = min(years_exp / 10, 1.0)  # Normalize to 0-1
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * config.SKILLS_WEIGHT +
                cultural_score * config.CULTURAL_FIT_WEIGHT +
                exp_score * config.EXPERIENCE_WEIGHT
            )
            
            # Determine tier
            tier = self._determine_tier(overall_score)
            
            ranked.append({
                "id": candidate.get('id'),
                "candidate_data": candidate_data,
                "name": candidate_data.get('personal_info', {}).get('name', 'Unknown'),
                "email": candidate_data.get('personal_info', {}).get('email', ''),
                "phone": candidate_data.get('personal_info', {}).get('phone', ''),
                "overall_score": round(overall_score * 100, 2),
                "skills_match_score": round(skills_score * 100, 2),
                "cultural_fit_score": round(cultural_score * 100, 2),
                "experience_score": round(exp_score * 100, 2),
                "tier": tier,
                "matched_skills": skills_eval.get('matched_skills', []),
                "missing_skills": skills_eval.get('missing_skills', []),
                "skills_rationale": skills_eval.get('rationale', ''),
                "cultural_rationale": cultural_eval.get('rationale', ''),
                "dimensional_scores": cultural_eval.get('dimensional_scores', {}),
                "recommendation": skills_eval.get('recommendation', 'weak_match')
            })
        
        # Sort by overall score descending
        ranked.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return ranked
    
    def _get_years_of_experience(self, candidate_data: Dict[str, Any]) -> float:
        """Calculate years of experience from work history"""
        work_experience = candidate_data.get('work_experience', [])
        # Simple calculation - can be enhanced
        return len(work_experience) * 2  # Rough estimate
    
    def _determine_tier(self, overall_score: float) -> str:
        """Determine candidate tier based on overall score"""
        percentage = overall_score * 100
        
        if percentage >= 85:
            return "strong_match"
        elif percentage >= 70:
            return "moderate_match"
        else:
            return "weak_match"
    
    def _filter_qualified_candidates(self, ranked_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter candidates who meet minimum thresholds"""
        qualified = []
        
        for candidate in ranked_candidates:
            skills_score = candidate.get('skills_match_score', 0)
            cultural_score = candidate.get('cultural_fit_score', 0)
            
            # Check if meets minimum thresholds
            if (skills_score >= config.SKILLS_MATCH_THRESHOLD and 
                cultural_score >= config.CULTURAL_FIT_THRESHOLD):
                qualified.append(candidate)
        
        # Return top 20% or candidates with "strong_match" tier
        strong_matches = [c for c in qualified if c['tier'] == 'strong_match']
        
        if strong_matches:
            return strong_matches
        
        # If no strong matches, return top 20% of qualified
        top_20_percent = max(1, len(qualified) // 5)
        return qualified[:top_20_percent]