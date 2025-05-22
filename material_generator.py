"""Generate cover letters and resume highlights."""
from ollama_client import OllamaClient
from pathlib import Path
from config import Config
from typing import Dict


class MaterialGenerator:
    """Generate customized cover letters and resume highlights."""
    
    def __init__(self, resume_data: dict):
        self.ollama = OllamaClient()
        self.resume_data = resume_data
    
    def generate_cover_letter(self, job: dict, company_research: dict = None) -> str:
        """Generate a customized cover letter."""
        # Build prompt with job and resume information
        resume_skills = ", ".join(self.resume_data.get("skills", []))
        resume_experience = self.resume_data.get("current_role", "")
        resume_projects = self.resume_data.get("notable_projects", [])[:3]
        
        projects_text = "\n".join([
            f"- {proj.get('name', '')}: {proj.get('description', '')} (Technologies: {', '.join(proj.get('technologies', []))})"
            for proj in resume_projects
        ])
        
        company_info = ""
        if company_research:
            company_info = f"""
Company Information:
- Summary: {company_research.get('summary', '')}
- Tech Stack: {', '.join(company_research.get('tech_stack', []))}
- Values: {', '.join(company_research.get('values', []))}
- Culture: {company_research.get('culture', '')}
"""
        
        prompt = f"""Write a professional, customized cover letter for this job application.

JOB INFORMATION:
Title: {job.get("title", "")}
Company: {job.get("company", "")}
Location: {job.get("location", "")}
Description: {job.get("description", "")[:800]}

{company_info}

MY BACKGROUND:
Current Role: {resume_experience}
Key Skills: {resume_skills}
Notable Projects:
{projects_text}

INSTRUCTIONS:
1. Address the letter professionally (use "Dear Hiring Manager" if name unknown)
2. Express genuine interest in the specific role and company
3. Mention 2-3 specific skills or experiences that match the job requirements
4. Reference something specific about the company (from research if available, or general interest)
5. Highlight one relevant project or achievement
6. Keep it concise (3-4 paragraphs, ~300 words)
7. End with enthusiasm and call to action
8. Use professional but warm tone

Write the cover letter now:"""
        
        cover_letter = self.ollama.generate_text(prompt, creative=True)
        return cover_letter.strip()
    
    def generate_resume_highlights(self, job: dict) -> str:
        """Generate resume highlights tailored to the job."""
        job_description = job.get("description", "")[:1000]
        resume_skills = self.resume_data.get("skills", [])
        resume_projects = self.resume_data.get("notable_projects", [])
        resume_experience = self.resume_data.get("previous_roles", []) + [
            {"title": self.resume_data.get("current_role", ""), "company": "Current", "responsibilities": ""}
        ]
        
        prompt = f"""Generate a list of resume highlights tailored to this job posting.

JOB POSTING:
Title: {job.get("title", "")}
Company: {job.get("company", "")}
Description: {job.get("description", "")[:1000]}

MY RESUME:
Skills: {", ".join(resume_skills)}
Projects: {len(resume_projects)} notable projects
Experience: {len(resume_experience)} roles

INSTRUCTIONS:
Create 4-6 bullet points that highlight:
1. Most relevant skills that match the job
2. Relevant projects or achievements
3. Relevant experience
4. Why you're a good fit

Format as bullet points, each 1-2 sentences. Be specific and quantify achievements where possible.

Example format:
- 5+ years of experience with Python and AWS, building scalable backend systems
- Led development of [Project Name] using [Technologies], resulting in [Achievement]
- Expertise in [Skill] with [X] years of hands-on experience

Generate the highlights now:"""
        
        highlights = self.ollama.generate_text(prompt, creative=True)
        return highlights.strip()
    
    def save_cover_letter(self, job_id: str, cover_letter: str):
        """Save cover letter to file."""
        output_dir = Path("cover_letters")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / f"{job_id}_cover_letter.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cover_letter)
        
        return file_path
    
    def save_resume_highlights(self, job_id: str, highlights: str):
        """Save resume highlights to file."""
        output_dir = Path("resume_highlights")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / f"{job_id}_highlights.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(highlights)
        
        return file_path

