"""
JSearch Provider

Fetches job postings from the JSearch API.
"""

from typing import Dict, List

from src.config.settings import settings
from src.ingestion.api_client import APIClient
from src.ingestion.providers.base_provider import BaseJobProvider


class JSearchProvider(BaseJobProvider):

    BASE_URL = "https://jsearch.p.rapidapi.com/search-v2"

    def __init__(self):

        self.client = APIClient()

    def fetch_jobs(
        self,
        keyword: str,
        location: str = settings.DEFAULT_LOCATION,
        page: int = 1,
    ) -> List[Dict]:

        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
        }

        params = {
            "query": f"{keyword} jobs in {location}",
            "page": page,
            "num_pages": 1,
            "date_posted": "all",
        }

        response = self.client.get(
            url=self.BASE_URL,
            headers=headers,
            params=params,
        )

        return response.get("data", [])