"""
Base Provider Interface

Every job provider must implement this interface.
This allows the pipeline to work with multiple
data sources without changing downstream code.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseJobProvider(ABC):
    """
    Abstract base class for all job providers.
    """

    @abstractmethod
    def fetch_jobs(
        self,
        keyword: str,
        location: str = "India",
        page: int = 1
    ) -> List[Dict]:
        """
        Fetch jobs from the provider.

        Parameters
        ----------
        keyword : str
            Job title or search keyword.

        location : str
            Search location.

        page : int
            Pagination number.

        Returns
        -------
        List[Dict]
            Raw job data.
        """

        pass