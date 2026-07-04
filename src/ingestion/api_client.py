"""
HTTP API Client

Reusable HTTP client for communicating with external
job providers.

Author: Shubham Patil
Project: Job Market Intelligence Platform
"""

"""
Reusable HTTP API Client
"""

from typing import Dict, Optional

import requests

from requests.exceptions import RequestException

from src.config.settings import settings
from src.ingestion.logger import get_logger


logger = get_logger(__name__)


class APIClient:

    def __init__(self):

        self.timeout = settings.REQUEST_TIMEOUT

    def get(
        self,
        url: str,
        headers: Dict,
        params: Optional[Dict] = None,
    ) -> Dict:

        try:

            logger.info("Sending GET request to %s", url)

            response = requests.get(
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            logger.info(
                "Request completed successfully (%s)",
                response.status_code,
            )

            return response.json()

        except RequestException as exc:

            logger.exception(
                "HTTP request failed: %s",
                exc,
            )

            raise