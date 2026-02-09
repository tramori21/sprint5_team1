import os

API_HOST = os.getenv("API_HOST", "http://api:8000")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
