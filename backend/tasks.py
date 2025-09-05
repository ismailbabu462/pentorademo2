"""
Background Tasks for PentoraSec

This module contains Celery tasks for AI-powered vulnerability enrichment.
Tasks include web scraping, AI analysis, and database updates.
"""

from celery import current_task
from celery_app import celery_app
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Optional
import time
from sqlalchemy.orm import Session
from database import get_db, Vulnerability as DBVulnerability
from config import JWT_SECRET_KEY, JWT_ALGORITHM
import os
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Search API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Ollama configuration for AI analysis
OLLAMA_URL = "http://ollama:11434"
MODEL_NAME = "llama3.1"

def get_google_search_results(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Search Google using Custom Search API and return results.
    
    Args:
        query: Search query string
        num_results: Number of results to return
        
    Returns:
        List of dictionaries containing title, link, and snippet
    """
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        logger.warning("Google API credentials not configured, using mock results")
        return [
            {
                "title": f"Mock result for: {query}",
                "link": "https://example.com/mock-result",
                "snippet": f"This is a mock search result for the query: {query}"
            }
        ]
    
    try:
        # Build Google Custom Search service
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        
        # Execute search
        result = service.cse().list(
            q=query,
            cx=SEARCH_ENGINE_ID,
            num=num_results
        ).execute()
        
        # Extract results
        search_results = []
        for item in result.get("items", []):
            search_results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        
        logger.info(f"Found {len(search_results)} Google search results for query: {query}")
        return search_results
        
    except Exception as e:
        logger.error(f"Google search failed: {str(e)}")
        return []

def scrape_webpage_content(url: str, timeout: int = 10) -> str:
    """
    Scrape content from a webpage using BeautifulSoup.
    
    Args:
        url: URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Cleaned text content from the webpage
    """
    try:
        # Set headers to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to prevent overwhelming the AI
        if len(text) > 5000:
            text = text[:5000] + "..."
        
        logger.info(f"Successfully scraped {len(text)} characters from {url}")
        return text
        
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")
        return ""

def analyze_with_ai(vulnerability_title: str, context_text: str) -> str:
    """
    Analyze vulnerability context using AI (Ollama/Llama).
    
    Args:
        vulnerability_title: Name of the vulnerability
        context_text: Combined text from web scraping
        
    Returns:
        AI-generated analysis in Markdown format
    """
    try:
        # Create analysis prompt
        prompt = f"""You are a cybersecurity expert analyzing vulnerability information. Based on the following research data, provide a comprehensive analysis of the '{vulnerability_title}' vulnerability.

Please provide:
1. **Exploitation Steps**: Step-by-step guide on how to exploit this vulnerability
2. **Technical Details**: Key technical information about the vulnerability
3. **Code Examples**: If available, provide relevant code snippets or commands
4. **Mitigation**: How to prevent or fix this vulnerability
5. **References**: Important links or resources mentioned

Format your response in Markdown with clear headings and bullet points.

RESEARCH DATA:
{context_text}

Analysis:"""

        # Prepare request for Ollama
        ollama_request = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        # Send request to Ollama
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=ollama_request,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get("response", "").strip()
            logger.info(f"AI analysis completed for {vulnerability_title}")
            return analysis
        else:
            logger.error(f"Ollama request failed with status {response.status_code}")
            return f"# AI Analysis Failed\n\nUnable to analyze the vulnerability '{vulnerability_title}' at this time. Please try again later."
            
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        return f"# AI Analysis Error\n\nAn error occurred while analyzing the vulnerability '{vulnerability_title}': {str(e)}"

@celery_app.task(bind=True, name="tasks.enrich_vulnerability")
def enrich_vulnerability(self, vulnerability_id: str) -> Dict[str, str]:
    """
    Main task for enriching vulnerability with AI analysis.
    
    Args:
        vulnerability_id: ID of the vulnerability to enrich
        
    Returns:
        Dictionary with task result information
    """
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"status": "Starting vulnerability analysis...", "progress": 10}
        )
        
        # Get database session
        from database import DatabaseContext
        with DatabaseContext() as db:
            # Fetch vulnerability from database
            vulnerability = db.query(DBVulnerability).filter(
                DBVulnerability.id == vulnerability_id
            ).first()
            
            if not vulnerability:
                logger.error(f"Vulnerability {vulnerability_id} not found")
                return {"error": "Vulnerability not found"}
            
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Searching for vulnerability information...", "progress": 25}
            )
            
            # Create search query
            search_query = f'"{vulnerability.title}" exploit tutorial code vulnerability'
            logger.info(f"Searching for: {search_query}")
            
            # Get Google search results
            search_results = get_google_search_results(search_query, num_results=5)
            
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Scraping web content...", "progress": 50}
            )
            
            # Scrape content from search results
            context_text = ""
            for i, result in enumerate(search_results):
                if result.get("link"):
                    logger.info(f"Scraping result {i+1}: {result['link']}")
                    content = scrape_webpage_content(result["link"])
                    if content:
                        context_text += f"\n\n--- Source {i+1}: {result['title']} ---\n"
                        context_text += f"URL: {result['link']}\n"
                        context_text += f"Content: {content}\n"
            
            # If no content was scraped, use search snippets
            if not context_text.strip():
                logger.warning("No content scraped, using search snippets")
                for i, result in enumerate(search_results):
                    context_text += f"\n\n--- Source {i+1}: {result['title']} ---\n"
                    context_text += f"URL: {result['link']}\n"
                    context_text += f"Snippet: {result.get('snippet', '')}\n"
            
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Analyzing with AI...", "progress": 75}
            )
            
            # Analyze with AI
            ai_analysis = analyze_with_ai(vulnerability.title, context_text)
            
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Saving analysis to database...", "progress": 90}
            )
            
            # Save AI analysis to database
            vulnerability.ai_analysis = ai_analysis
            # DatabaseContext will handle commit automatically
        
        logger.info(f"Successfully enriched vulnerability {vulnerability_id}")
        
        # Update final status
        self.update_state(
            state="SUCCESS",
            meta={"status": "Analysis completed successfully", "progress": 100}
        )
        
        return {
            "status": "success",
            "vulnerability_id": vulnerability_id,
            "analysis_length": len(ai_analysis),
            "sources_analyzed": len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Vulnerability enrichment failed: {str(e)}")
        
        # Update error status
        self.update_state(
            state="FAILURE",
            meta={"status": f"Analysis failed: {str(e)}", "progress": 0}
        )
        
        return {"error": str(e)}
    
    finally:
        pass  # DatabaseContext handles cleanup automatically

@celery_app.task
def test_task() -> str:
    """
    Simple test task to verify Celery is working.
    """
    return "Celery is working correctly!"