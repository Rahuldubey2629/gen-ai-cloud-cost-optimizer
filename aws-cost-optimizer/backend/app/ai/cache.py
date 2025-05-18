import redis
from functools import wraps
import pickle
import asyncio

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def cache(self, ttl=3600):
        def decorator(f):
            @wraps(f)
            async def wrapper(*args, **kwargs):
                key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
                if cached := self.redis.get(key):
                    return pickle.loads(cached)
                result = await f(*args, **kwargs)
                self.redis.setex(key, ttl, pickle.dumps(result))
                return result
            return wrapper
        return decorator

cache = CacheManager()