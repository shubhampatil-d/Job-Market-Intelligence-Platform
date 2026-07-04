"""
HTTP API Client

Reusable HTTP client for communicating with external
job providers.

Author: Shubham Patil
Project: Job Market Intelligence Platform
"""

from typing import Dict, Optional

import requests

from src.config.settings import settings


class APIClient:
    """
    Generic HTTP client for external APIs.
    """

    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT

    def get(
        self,
        url: str,
        headers: Dict,
        params: Optional[Dict] = None,
    ) -> Dict:
        """
        Execute an HTTP GET request.

        Parameters
        ----------
        url : str
            Endpoint URL.

        headers : Dict
            HTTP headers.

        params : Dict
            Query parameters.

        Returns
        -------
        Dict
            JSON response from API.
        """

        response = requests.get(
            url=url,
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()