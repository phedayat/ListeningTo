import os
import redis

class RedisClient:
	REDIS_URL = "redis://:pee250ae8afa93b490a534f15cc9d0176abd0aafa8982a364f8416ed9a4ccba7d@ec2-34-193-237-171.compute-1.amazonaws.com:23009"

	def __init__(self):
		# self.conn = redis.from_url(os.environ.get("REDIS_URL"))
		self.conn = redis.from_url(self.REDIS_URL)

	def setItem(self, key, value):
		self.conn.set(key, value)

	def getItem(self, key):
		return self.conn.get(key)

if __name__=="__main__":
	r = RedisClient()