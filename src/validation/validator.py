"""
Job Validator

Validates raw job records before processing.
"""

from typing import Dict, List


class JobValidator:

    REQUIRED_FIELDS = [

        "job_title",

        "employer_name",

        "job_city",

    ]

    def validate(
        self,
        jobs: List[Dict],
    ) -> List[Dict]:

        valid_jobs = []

        for job in jobs:

            valid = True

            for field in self.REQUIRED_FIELDS:

                if not job.get(field):

                    valid = False

                    break

            if valid:

                valid_jobs.append(job)

        return valid_jobs