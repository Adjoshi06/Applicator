"""Company researcher using web search."""
from duckduckgo_search import DDGS
from ollama_client import OllamaClient
import requests
from bs4 import BeautifulSoup
from typing import List, Dict


class CompanyResearcher:
    """Research companies using web search and LLM summarization."""
    
    def __init__(self):
        self.ollama = OllamaClient()
    
    def research_company(self, company_name: str, max_urls: int = 5) -> dict:
        """Research a company and generate insights."""
        # Search for company information
        search_results = self._search_company(company_name, max_results=max_urls)
        
        # Fetch and parse URLs
        url_contents = []
        for result in search_results[:max_urls]:
            try:
                content = self._fetch_url_content(result["href"])
                if content:
                    url_contents.append({
                        "url": result["href"],
                        "title": result.get("title", ""),
                        "content": content[:2000]  # Limit content length
                    })
            except Exception as e:
                print(f"Error fetching {result['href']}: {e}")
                continue
        
        if not url_contents:
            return {
                "company": company_name,
                "summary": "No information found",
                "tech_stack": [],
                "values": [],
                "recent_news": [],
                "culture": "Unknown"
            }
        
        # Summarize with LLM
        content_text = "\n\n---\n\n".join([
            f"URL: {item['url']}\nTitle: {item['title']}\nContent: {item['content']}"
            for item in url_contents
        ])
        
        prompt = f"""Research this company and extract key information in JSON format:

Company: {company_name}

Sources:
{content_text[:5000]}

Return a JSON object with:
- company: company name
- summary: brief company overview (2-3 sentences)
- tech_stack: array of technologies they use (if tech company)
- values: array of company values/culture points
- recent_news: array of recent news items (max 3)
- culture: description of company culture (2-3 sentences)
- size: company size if mentioned (e.g., "500-1000 employees")
- industry: primary industry
- funding_stage: funding stage if startup (e.g., "Series B", "Public")

Example output:
{{
  "company": "Tech Corp",
  "summary": "Tech Corp is a leading SaaS company...",
  "tech_stack": ["Python", "React", "AWS", "Kubernetes"],
  "values": ["Innovation", "Work-life balance", "Diversity"],
  "recent_news": ["Raised Series B funding", "Launched new product"],
  "culture": "Fast-paced startup culture with emphasis on collaboration",
  "size": "200-500 employees",
  "industry": "SaaS",
  "funding_stage": "Series B"
}}

Return ONLY valid JSON, no other text:"""
        
        research_result = self.ollama.parse_structured(prompt)
        
        # Check for errors in parsing
        if "error" in research_result:
            # Return minimal result with error info
            return {
                "company": company_name,
                "summary": f"Research failed: {research_result.get('error', 'Unknown error')}",
                "tech_stack": [],
                "values": [],
                "recent_news": [],
                "culture": "Unknown",
                "size": "Unknown",
                "industry": "Unknown",
                "funding_stage": "Unknown",
                "sources": [item["url"] for item in url_contents] if url_contents else [],
                "error": research_result.get("error", "Unknown")
            }
        
        # Ensure all fields exist
        if "company" not in research_result:
            research_result["company"] = company_name
        if "tech_stack" not in research_result:
            research_result["tech_stack"] = []
        if "values" not in research_result:
            research_result["values"] = []
        if "recent_news" not in research_result:
            research_result["recent_news"] = []
        
        research_result["sources"] = [item["url"] for item in url_contents]
        
        return research_result
    
    def _search_company(self, company_name: str, max_results: int = 5) -> List[Dict]:
        """Search for company information."""
        try:
            with DDGS() as ddgs:
                query = f"{company_name} company culture technology stack"
                results = list(ddgs.text(query, max_results=max_results))
                return results
        except Exception as e:
            print(f"Error searching for company: {e}")
            return []
    
    def _fetch_url_content(self, url: str) -> str:
        """Fetch and extract text content from URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return ""

