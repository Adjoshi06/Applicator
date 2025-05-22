"""Storage layer for jobs and vectors."""
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from config import Config


class Storage:
    """Handles JSON storage and ChromaDB vector storage."""
    
    def __init__(self):
        Config.ensure_directories()
        self.client = chromadb.PersistentClient(
            path=str(Config.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(name="jobs")
    
    def save_job(self, job: Dict) -> str:
        """Save a job to JSON and ChromaDB."""
        job_id = self._generate_job_id(job)
        job["id"] = job_id
        
        # Save to JSON
        job_file = Config.DATA_DIR / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job, f, indent=2)
        
        # Save to ChromaDB (embedding job description)
        self.collection.upsert(
            ids=[job_id],
            documents=[job.get("description", "")],
            metadatas=[{
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "score": job.get("score", 0),
                "source": job.get("source", "")
            }]
        )
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Retrieve a job by ID."""
        job_file = Config.DATA_DIR / f"{job_id}.json"
        if job_file.exists():
            with open(job_file, "r") as f:
                return json.load(f)
        return None
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all stored jobs."""
        jobs = []
        for job_file in Config.DATA_DIR.glob("*.json"):
            with open(job_file, "r") as f:
                jobs.append(json.load(f))
        return jobs
    
    def get_high_scoring_jobs(self, min_score: int) -> List[Dict]:
        """Get jobs with score >= min_score."""
        all_jobs = self.get_all_jobs()
        return [job for job in all_jobs if job.get("score", 0) >= min_score]
    
    def save_resume_data(self, resume_data: Dict):
        """Save parsed resume data to cache."""
        with open(Config.RESUME_CACHE_FILE, "w") as f:
            json.dump(resume_data, f, indent=2)
    
    def load_resume_data(self) -> Optional[Dict]:
        """Load cached resume data."""
        if Config.RESUME_CACHE_FILE.exists():
            with open(Config.RESUME_CACHE_FILE, "r") as f:
                return json.load(f)
        return None
    
    def _generate_job_id(self, job: Dict) -> str:
        """Generate a unique ID for a job based on title, company, and URL."""
        unique_string = f"{job.get('title', '')}{job.get('company', '')}{job.get('url', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

