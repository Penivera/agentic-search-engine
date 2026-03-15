import httpx
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

STANDARD_PATHS = [
    "/.well-known/llms.txt",
    "/llms.txt",
    "/.agents/skills/agentic-search-engine/SKILL.md",  # The customized agentic skill path
    "/.well-known/ai-plugin.json"
]

class CrawlerService:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def check_standard_endpoints(self, base_url: str) -> Optional[str]:
        """
        Check common paths for an AI agent skill file.
        Returns the content of the file if found, otherwise None.
        """
        for path in STANDARD_PATHS:
            url = urljoin(base_url, path)
            try:
                response = await self.client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"Found standard endpoint at {url}")
                    return response.text
            except httpx.RequestError as e:
                logger.debug(f"Failed to check standard path {url}: {e}")
                
        return None

    async def extract_meta_tags(self, base_url: str) -> Dict[str, Optional[str]]:
        """
        Fetches the homepage and extracts the title and meta description.
        Returns a dictionary representing a fallback description.
        """
        try:
            response = await self.client.get(base_url, follow_redirects=True)
            if response.status_code != 200:
                return {}
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            title_tag = soup.find("title")
            title = title_tag.string if title_tag else ""

            description_tag = soup.find("meta", attrs={"name": "description"})
            description = description_tag.get("content", "") if description_tag else ""
            if isinstance(description, list):
                description = " ".join(description)
            
            # Additional check for agentic verification token in meta tag
            verification_tag = soup.find("meta", attrs={"name": "agentic-site-verification"})
            verification_token = verification_tag.get("content", None) if verification_tag else None
            if isinstance(verification_token, list):
                verification_token = verification_token[0]

            return {
                "title": title.strip() if title else "",
                "description": description.strip() if description else "",
                "verification_token": verification_token.strip() if isinstance(verification_token, str) else None
            }
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch homepage meta for {base_url}: {e}")
            return {}

    async def crawl_platform(self, url: str) -> Dict[str, Optional[str]]:
        """
        Crawls the given URL. Prioritizes finding a standard agent skill file.
        If none is found, extracts HTML meta data to generate a fallback description.
        """
        # 1. Look for standard endpoints first
        skill_content = await self.check_standard_endpoints(url)
        
        # 2. Grab meta tags to serve as a meaningful description fallback
        meta_data = await self.extract_meta_tags(url)
        
        return {
            "skill_content": skill_content,
            "title": meta_data.get("title"),
            "description": meta_data.get("description"),
            "verification_token": meta_data.get("verification_token")
        }
        
    async def close(self):
        await self.client.aclose()
