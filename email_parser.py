"""Email parser using Ollama to extract job data."""
from ollama_client import OllamaClient
import re


class EmailParser:
    """Parse job alert emails and extract structured job data."""
    
    def __init__(self):
        self.ollama = OllamaClient()
    
    def parse_email(self, email_subject: str, email_body: str, email_from: str) -> dict:
        """Parse email and extract job information."""
        prompt = f"""Extract job information from this email in JSON format:

Subject: {email_subject}
From: {email_from}
Body: {email_body[:2000]}

Return a JSON object with these fields:
- title: job title (string)
- company: company name (string)
- location: job location (string, "Remote" if remote)
- description: job description (string, max 500 chars)
- url: application URL if present (string, empty if not found)
- source: email source (e.g., "LinkedIn", "Indeed", "Glassdoor")
- salary: salary range if mentioned (string, empty if not found)
- employment_type: "full-time", "part-time", "contract", or "unknown"

Example output:
{{
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "description": "We are looking for a software engineer...",
  "url": "https://company.com/jobs/123",
  "source": "LinkedIn",
  "salary": "$100k-150k",
  "employment_type": "full-time"
}}

Return ONLY valid JSON, no other text:"""
        
        job_data = self.ollama.parse_structured(prompt)
        
        # Clean up and validate
        if "title" not in job_data or not job_data["title"]:
            # Try to extract title from subject as fallback
            job_data["title"] = self._extract_title_from_subject(email_subject)
        
        if "company" not in job_data:
            job_data["company"] = "Unknown"
        
        if "location" not in job_data:
            job_data["location"] = "Unknown"
        
        if "url" not in job_data:
            # Try to extract URL from email body
            job_data["url"] = self._extract_url(email_body)
        
        if "source" not in job_data:
            job_data["source"] = self._extract_source(email_from)
        
        job_data["description"] = job_data.get("description", email_body[:500])
        
        return job_data
    
    def _extract_title_from_subject(self, subject: str) -> str:
        """Extract job title from email subject."""
        # Remove common prefixes
        subject = re.sub(r'^RE:\s*', '', subject, flags=re.IGNORECASE)
        subject = re.sub(r'^FWD?:\s*', '', subject, flags=re.IGNORECASE)
        # Take first part before common separators
        title = re.split(r'[|\-–—]', subject)[0].strip()
        return title[:100]  # Limit length
    
    def _extract_url(self, body: str) -> str:
        """Extract URL from email body."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, body)
        # Prefer URLs that look like job postings
        for url in urls:
            if any(keyword in url.lower() for keyword in ['job', 'career', 'apply', 'position', 'opening']):
                return url
        return urls[0] if urls else ""
    
    def _extract_source(self, email_from: str) -> str:
        """Extract job source from email address."""
        email_lower = email_from.lower()
        if 'linkedin' in email_lower:
            return "LinkedIn"
        elif 'indeed' in email_lower:
            return "Indeed"
        elif 'glassdoor' in email_lower:
            return "Glassdoor"
        elif 'ziprecruiter' in email_lower:
            return "ZipRecruiter"
        elif 'monster' in email_lower:
            return "Monster"
        else:
            return "Unknown"

