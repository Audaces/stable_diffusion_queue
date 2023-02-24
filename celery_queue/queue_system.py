import redis

class QueueManager():
    def __init__(self, host, port) -> None:
        self.conn = redis.Redis(host=host, port=port)

    def results_set(self, key, value):
        self.conn.hset("results_from_tasks", key, value)
        self.conn.expire(key, time=120)

    def results_get(self, key):
        return self.conn.hget("results_from_tasks", key)

    def results_pop(self, key):
        value = self.conn.hget("results_from_tasks", key)
        self.conn.hdel("results_from_tasks", key)
        return value

    def queue_append(self, value):
        self.conn.lpush("timed_list", value)

    def queue_remove(self, value):
        self.conn.lrem("timed_list", 0, value)

    def queue_index(self, value):
        return self.conn.lpos("timed_list", value)

    def queue_size(self):
        return self.conn.llen("timed_list")