from pprint import pprint 
from src.ingestion.fetch_jobs import JobIngestionPipeline

pipeline =JobIngestionPipeline()
result =pipeline.run("Data Engineer")
pprint(result)