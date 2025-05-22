"""Job scorer that compares jobs against resume and preferences."""
from ollama_client import OllamaClient
from config import Config


class JobScorer:
    """Score jobs based on resume match and user preferences."""
    
    def __init__(self, resume_data: dict):
        self.ollama = OllamaClient()
        self.resume_data = resume_data
    
    def score_job(self, job: dict) -> dict:
        """Score a job from 0-100 with reasoning."""
        # Build comparison prompt
        resume_skills = ", ".join(self.resume_data.get("skills", []))
        resume_expertise = ", ".join(self.resume_data.get("areas_of_expertise", []))
        resume_exp_years = self.resume_data.get("experience_years", 0)
        resume_level = self.resume_data.get("experience_level", "mid")
        user_prefs = ", ".join(Config.USER_PREFERENCES) if Config.USER_PREFERENCES else "None specified"
        user_location = Config.USER_LOCATION if Config.USER_LOCATION else "No preference"
        
        prompt = f"""Score this job posting from 0-100 based on how well it matches the resume and preferences.

RESUME INFORMATION:
- Skills: {resume_skills}
- Areas of Expertise: {resume_expertise}
- Experience: {resume_exp_years} years, {resume_level} level
- Current Role: {self.resume_data.get("current_role", "Unknown")}

JOB POSTING:
Title: {job.get("title", "Unknown")}
Company: {job.get("company", "Unknown")}
Location: {job.get("location", "Unknown")}
Description: {job.get("description", "")[:1000]}

USER PREFERENCES:
- Preferences: {user_prefs}
- Preferred Location: {user_location}

Score based on:
1. Skills match (40 points): How well do the job requirements match the resume skills?
2. Experience level match (20 points): Does the required experience level match?
3. Preferences match (20 points): Does it match user preferences (remote, company size, industry)?
4. Location match (10 points): Is the location desirable?
5. Overall fit (10 points): General fit based on career trajectory

Return a JSON object with:
- score: integer from 0-100
- reasoning: string explaining the score
- skill_match_score: integer 0-40
- experience_match_score: integer 0-20
- preferences_match_score: integer 0-20
- location_match_score: integer 0-10
- overall_fit_score: integer 0-10
- matched_skills: array of skills from resume that match the job
- missing_skills: array of skills mentioned in job but not in resume

Example output:
{{
  "score": 85,
  "reasoning": "Strong match: 8/10 skills match, experience level aligns, remote preference met",
  "skill_match_score": 35,
  "experience_match_score": 18,
  "preferences_match_score": 18,
  "location_match_score": 8,
  "overall_fit_score": 9,
  "matched_skills": ["Python", "AWS", "Docker"],
  "missing_skills": ["Kubernetes"]
}}

Return ONLY valid JSON, no other text:"""
        
        scoring_result = self.ollama.parse_structured(prompt)
        
        # Check for errors in parsing
        if "error" in scoring_result:
            # Return a default low score with error info
            return {
                "score": 0,
                "reasoning": f"Scoring failed: {scoring_result.get('error', 'Unknown error')}",
                "skill_match_score": 0,
                "experience_match_score": 0,
                "preferences_match_score": 0,
                "location_match_score": 0,
                "overall_fit_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "error": scoring_result.get("error", "Unknown")
            }
        
        # Ensure score is in valid range
        try:
            score = scoring_result.get("score", 0)
            score = max(0, min(100, int(score)))
            scoring_result["score"] = score
        except (ValueError, TypeError):
            scoring_result["score"] = 0
        
        # Ensure all required fields exist
        if "reasoning" not in scoring_result:
            scoring_result["reasoning"] = "Score calculated based on resume match"
        if "matched_skills" not in scoring_result:
            scoring_result["matched_skills"] = []
        if "missing_skills" not in scoring_result:
            scoring_result["missing_skills"] = []
        
        # Add scoring metadata
        scoring_result["resume_skills_count"] = len(self.resume_data.get("skills", []))
        scoring_result["job_title"] = job.get("title", "")
        scoring_result["job_company"] = job.get("company", "")
        
        return scoring_result

