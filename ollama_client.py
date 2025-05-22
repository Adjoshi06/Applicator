"""Ollama client for LLM operations."""
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from config import Config
from typing import Dict
import json
import re


class OllamaClient:
    """Wrapper for Ollama LLM operations."""
    
    def __init__(self):
        self.llm = Ollama(
            model=Config.OLLAMA_MODEL,
            base_url=Config.OLLAMA_BASE_URL,
            temperature=0
        )
        self.llm_creative = Ollama(
            model=Config.OLLAMA_MODEL,
            base_url=Config.OLLAMA_BASE_URL,
            temperature=0.7
        )
    
    def parse_structured(self, prompt: str, max_retries: int = 3) -> Dict:
        """Parse structured output from LLM with retry logic."""
        response = ""
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(prompt)
                # Ensure response is a string
                if not isinstance(response, str):
                    response = str(response)
                
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    if isinstance(parsed, dict):
                        return parsed
                
                # If no JSON found, try parsing the whole response
                parsed = json.loads(response.strip())
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, Exception) as e:
                if attempt == max_retries - 1:
                    # Last attempt - return a structured error
                    return {"error": str(e), "raw_response": response[:500]}
                continue
        return {"error": "Failed to parse after retries", "raw_response": response[:500]}
    
    def generate_text(self, prompt: str, creative: bool = False) -> str:
        """Generate text using LLM."""
        llm = self.llm_creative if creative else self.llm
        response = llm.invoke(prompt)
        # Ensure response is a string
        if not isinstance(response, str):
            response = str(response)
        return response
    
    def invoke(self, prompt: str, temperature: float = 0) -> str:
        """Invoke LLM with custom temperature."""
        if temperature > 0:
            llm = Ollama(
                model=Config.OLLAMA_MODEL,
                base_url=Config.OLLAMA_BASE_URL,
                temperature=temperature
            )
            return llm.invoke(prompt)
        return self.llm.invoke(prompt)

