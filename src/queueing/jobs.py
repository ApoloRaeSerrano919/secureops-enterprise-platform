from redis import Redis
from rq import Queue

from src.ai.investigator import summarize_incident
from src.config.settings import settings


def queue() -> Queue:
    return Queue("secureops", connection=Redis.from_url(settings.redis_url))


def enqueue_investigation(incident_id: int, analyst_prompt: str, actor_user_id: int) -> str:
    job = queue().enqueue(
        summarize_incident,
        incident_id,
        analyst_prompt=analyst_prompt,
        actor_user_id=actor_user_id,
        job_timeout=settings.ai_job_timeout_seconds,
    )
    return job.id
