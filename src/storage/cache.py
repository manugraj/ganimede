import abc
import pickle

import redis
from redis import Redis

from src.config import SystemConfig


class Cache(abc.ABC):
    __cache__: Redis

    @staticmethod
    def start():
        Cache.__cache__ = redis.Redis(host=SystemConfig.get_vital("REDIS_HOST"),
                                      port=SystemConfig.get("REDIS_PORT", "6379"),
                                      db=SystemConfig.get("REDIS_DB", "0"),
                                      password=None, socket_timeout=None)

    def put(self, key, value) -> bool:
        return Cache.__cache__.set(self.internal_key(key), pickle.dumps(value)) if value else None

    def get(self, key, default=None):
        value = Cache.__cache__.get(self.internal_key(key))
        return pickle.loads(value) if value else default

    def rm(self, key):
        return Cache.__cache__.delete(self.internal_key(key))

    def rm_all(self, partial: str = None):
        search_key = f'{self.data_prefix()}*{partial}*' if partial else f'{self.data_prefix()}*'
        count = 0
        for key in Cache.__cache__.scan_iter(search_key):
            Cache.__cache__.delete(key)
            count += 1
        return count

    def exists(self, key) -> bool:
        return Cache.__cache__.exists(self.internal_key(key))

    def keys(self):
        return Cache.__cache__.keys(self.data_prefix() + "*")

    @abc.abstractmethod
    def data_prefix(self) -> str:
        pass

    def internal_key(self, key: str):
        return self.data_prefix() + str(key)
