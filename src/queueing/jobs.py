from redis import Redis
from rq import Queue

from src.ai.investigator import summarize_incident
from src.config.settings import settings


def queue() -> Queue:
    return Queue("secureops", connection=Redis.from_url(settings.redis_url))


