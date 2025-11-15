"""
Confluence REST API client for on-premises instances.
Handles authentication, SSL verification, and content retrieval.
"""

import requests
import urllib3
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config import settings

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ConfluenceClient:
    """Client for interacting with on-premises Confluence REST API."""
    
    def __init__(self):
        self.base_url = settings.confluence_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.confluence_api_token}",
            "Accept": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Test connection to Confluence instance."""
        try:
            url = f"{self.base_url}/rest/api/content?limit=1"
            response = requests.get(
                url, 
                headers=self.headers, 
                verify=False,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_page_by_id(self, page_id: str) -> Optional[Dict]:
        """
        Fetch a Confluence page by ID with full content.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Dictionary with page data or None if error
        """
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}"
            params = {
                "expand": "body.storage,version,space"
            }
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch page {page_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching page {page_id}: {e}")
            return None
    
    def get_pages_from_space(self, space_key: str, limit: int = 10) -> List[Dict]:
        """
        Fetch pages from a Confluence space.
        
        Args:
            space_key: Confluence space key
            limit: Maximum number of pages to fetch
            
        Returns:
            List of page dictionaries
        """
        try:
            url = f"{self.base_url}/rest/api/content"
            params = {
                "spaceKey": space_key,
                "limit": limit,
                "expand": "body.storage,version,space"
            }
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                print(f"Failed to fetch pages from space {space_key}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching pages from space {space_key}: {e}")
            return []
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract clean text from Confluence HTML storage format.
        
        Args:
            html_content: HTML content from Confluence
            
        Returns:
            Clean text content
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.splitlines()]
        text = '\n'.join(line for line in lines if line)
        
        return text
    
    def get_page_metadata(self, page_data: Dict) -> Dict:
        """
        Extract metadata from page data.
        
        Args:
            page_data: Raw page data from API
            
        Returns:
            Dictionary with metadata
        """
        return {
            "page_id": page_data.get("id"),
            "page_title": page_data.get("title"),
            "page_url": f"{self.base_url}{page_data.get('_links', {}).get('webui', '')}",
            "last_modified": page_data.get("version", {}).get("when"),
            "space_key": page_data.get("space", {}).get("key"),
            "space_name": page_data.get("space", {}).get("name")
        }
    
    def get_page_content(self, page_id: str) -> Optional[Dict]:
        """
        Get page content and metadata together.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Dictionary with content and metadata
        """
        page_data = self.get_page_by_id(page_id)
        if not page_data:
            return None
        
        html_content = page_data.get("body", {}).get("storage", {}).get("value", "")
        text_content = self.extract_text_from_html(html_content)
        metadata = self.get_page_metadata(page_data)
        
        return {
            "content": text_content,
            "metadata": metadata
        }

