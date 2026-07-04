from src.ingestion.providers.jsearch_provider import JSearchProvider
from src.ingestion.save_raw import RawDataSaver

provider = JSearchProvider()

jobs = provider.fetch_jobs("Data Engineer")

saver = RawDataSaver()

path = saver.save(jobs)

print(path)