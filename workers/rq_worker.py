from redis import Redis
from rq import Worker
from src.config.settings import settings

if __name__ == "__main__":
    Worker(["secureops"], connection=Redis.from_url(settings.redis_url)).work()
