from pprint import pprint

from src.ingestion.providers.jsearch_provider import JSearchProvider

provider = JSearchProvider()

jobs = provider.fetch_jobs("Data Engineer")

print(type(jobs))

if jobs:
    pprint(jobs)