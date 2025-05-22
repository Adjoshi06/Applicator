"""Resume parser using Ollama to extract skills and experience."""
from ollama_client import OllamaClient
from drive_client import DriveClient
from storage import Storage
from config import Config


class ResumeParser:
    """Parse resume from Google Docs and extract structured data."""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.drive = DriveClient()
        self.storage = Storage()
    
    def parse_resume(self, force_refresh: bool = False) -> dict:
        """Parse resume and extract skills/experience."""
        # Check cache first
        if not force_refresh:
            cached = self.storage.load_resume_data()
            if cached:
                return cached
        
        # Fetch resume from Google Docs
        if not Config.GOOGLE_DRIVE_RESUME_ID:
            raise ValueError("GOOGLE_DRIVE_RESUME_ID not set in .env")
        
        resume_text = self.drive.get_resume_text(Config.GOOGLE_DRIVE_RESUME_ID)
        if not resume_text:
            raise ValueError("Failed to fetch resume from Google Docs")
        
        # Parse with Llama
        prompt = f"""Extract the following information from this resume in JSON format:

{resume_text}

Return a JSON object with these fields:
- skills: array of programming languages, frameworks, tools, technologies
- experience_years: number of years of professional experience
- experience_level: "entry", "mid", "senior", or "executive"
- education: array of degrees with fields: degree, field, institution, year
- notable_projects: array of projects with fields: name, description, technologies
- areas_of_expertise: array of domain areas (e.g., "Machine Learning", "Web Development")
- current_role: string describing current or most recent position
- previous_roles: array of previous positions with fields: title, company, duration, responsibilities

Example output:
{{
  "skills": ["Python", "JavaScript", "React", "AWS"],
  "experience_years": 5,
  "experience_level": "mid",
  "education": [{{"degree": "BS", "field": "Computer Science", "institution": "University", "year": 2019}}],
  "notable_projects": [{{"name": "Project X", "description": "...", "technologies": ["Python", "Django"]}}],
  "areas_of_expertise": ["Machine Learning", "Backend Development"],
  "current_role": "Software Engineer at Company",
  "previous_roles": [{{"title": "Developer", "company": "Company", "duration": "2020-2022", "responsibilities": "..."}}]
}}

Return ONLY valid JSON, no other text:"""
        
        resume_data = self.ollama.parse_structured(prompt)
        
        # Check for errors in parsing
        if "error" in resume_data:
            raise ValueError(f"Failed to parse resume: {resume_data.get('error', 'Unknown error')}")
        
        # Ensure required fields exist with defaults
        if "skills" not in resume_data:
            resume_data["skills"] = []
        if "experience_years" not in resume_data:
            resume_data["experience_years"] = 0
        if "experience_level" not in resume_data:
            resume_data["experience_level"] = "mid"
        
        # Add raw resume text for reference
        resume_data["raw_text"] = resume_text
        
        # Cache the result
        self.storage.save_resume_data(resume_data)
        
        return resume_data

