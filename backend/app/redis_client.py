"""键值存储抽象：Redis 可用时使用 Redis，否则降级为进程内存实现（功能一致）。

用于：登录失败计数、令牌黑名单、安全问题重置次数、订单号序列。
Docker 部署注入 redis_url 即使用真实 Redis；本地无 Redis 时自动降级，便于演示。
"""
import threading
import time

from .config import settings


class KVStore:
    def get(self, key):  # pragma: no cover
        raise NotImplementedError

    def set(self, key, value, ex=None):  # pragma: no cover
        raise NotImplementedError

    def incr(self, key):  # pragma: no cover
        raise NotImplementedError

    def expire(self, key, seconds):  # pragma: no cover
        raise NotImplementedError

    def delete(self, key):  # pragma: no cover
        raise NotImplementedError

    def ttl(self, key):  # pragma: no cover
        raise NotImplementedError

    def ping(self) -> bool:  # pragma: no cover
        raise NotImplementedError


class MemoryKV(KVStore):
    def __init__(self):
        self._data: dict[str, str] = {}
        self._exp: dict[str, float] = {}
        self._lock = threading.Lock()

    def _purge(self):
        now = time.time()
        expired = [k for k, e in self._exp.items() if e and e <= now]
        for k in expired:
            self._data.pop(k, None)
            self._exp.pop(k, None)

    def get(self, key):
        with self._lock:
            self._purge()
            e = self._exp.get(key)
            if e and e <= time.time():
                return None
            return self._data.get(key)

    def set(self, key, value, ex=None):
        with self._lock:
            self._data[key] = value
            self._exp[key] = (time.time() + ex) if ex else 0

    def incr(self, key):
        with self._lock:
            self._purge()
            v = int(self._data.get(key, 0)) + 1
            self._data[key] = str(v)
            return v

    def expire(self, key, seconds):
        with self._lock:
            if key not in self._data:
                return False
            self._exp[key] = time.time() + seconds
            return True

    def delete(self, key):
        with self._lock:
            self._data.pop(key, None)
            self._exp.pop(key, None)

    def ttl(self, key):
        with self._lock:
            self._purge()
            if key not in self._data:
                return -2
            e = self._exp.get(key)
            if not e:
                return -1
            return max(0, int(e - time.time()))

    def ping(self):
        return True


class RedisKV(KVStore):
    def __init__(self, url: str):
        import redis

        self._r = redis.Redis.from_url(url, decode_responses=True)

    def get(self, key):
        return self._r.get(key)

    def set(self, key, value, ex=None):
        self._r.set(key, value, ex=ex)

    def incr(self, key):
        return self._r.incr(key)

    def expire(self, key, seconds):
        return bool(self._r.expire(key, seconds))

    def delete(self, key):
        return self._r.delete(key)

    def ttl(self, key):
        return self._r.ttl(key)

    def ping(self):
        try:
            return bool(self._r.ping())
        except Exception:
            return False


_kv: KVStore | None = None


def get_kv() -> KVStore:
    global _kv
    if _kv is None:
        if settings.force_memory_cache or not settings.redis_url:
            _kv = MemoryKV()
        else:
            redis_kv = RedisKV(settings.redis_url)
            _kv = redis_kv if redis_kv.ping() else MemoryKV()
    return _kv
