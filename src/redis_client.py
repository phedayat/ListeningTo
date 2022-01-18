import os
import redis
import json
import asyncio

class RedisClient:
	REDIS_URL = "redis://:pee250ae8afa93b490a534f15cc9d0176abd0aafa8982a364f8416ed9a4ccba7d@ec2-34-193-237-171.compute-1.amazonaws.com:23009"
	USER_LIST_KEY = "userList"
	USER_DATA_KEY = "userData"

	def __init__(self):
		# self.conn = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
		self.conn = redis.from_url(self.REDIS_URL, decode_responses=True)

	def checkUserExists(self, username):
		if self.conn.exists(self.USER_LIST_KEY):
			if self.conn.sismember(self.USER_LIST_KEY, username):
				return True
		return False

	def checkPassword(self, username, password):
		curr_pass = self.getUserData(username)
		return curr_pass["pass"] == password
		
	def addUser(self, username):
		self.conn.sadd(self.USER_LIST_KEY, username)
		return 1

	def addUserData(self, username, password):
		data = json.dumps({"pass": password, "connection":"", "messages":[], "lastSong":""})
		self.conn.hset(self.USER_DATA_KEY, username, data)
		return 1

	def removeUser(self, username):
		self.conn.srem(self.USER_LIST_KEY, username)
		self.conn.hdel(self.USER_DATA_KEY, username)
		return 1

	def setConnection(self, sender, connection):
		if self.checkUserExists(connection):
			sender_user_data = self.getUserData(sender)
			sender_user_data["connection"] = connection
			self.conn.hset(self.USER_DATA_KEY, sender, json.dumps(sender_user_data))

			target_user_data = self.getUserData(connection)
			target_user_data["connection"] = sender
			self.conn.hset(self.USER_DATA_KEY, connection, json.dumps(target_user_data))
			return 1
		return 0

	def setUserData(self, username, data):
		if self.checkUserExists(username):
			self.conn.hset(self.USER_DATA_KEY, username, json.dumps(data))
			return 1
		return 0

	def getConnection(self, username):
		user_data = self.getUserData(username)
		# print(f"User data: {user_data}")
		# print(f"Redis URL: {self.REDIS_URL}")
		# print(f"Keys: {self.conn.keys('*')}")
		# print(f"Hash keys: {self.conn.hkeys(self.USER_DATA_KEY)}")
		# print(f"Val: {self.conn.hget(self.USER_DATA_KEY, username)}")
		return user_data["connection"]

	def getUserData(self, username):
		data = self.conn.hget(self.USER_DATA_KEY, username)
		return json.loads(data)

	def getAllUsers(self):
		print(self.conn.smembers(self.USER_LIST_KEY))

	def getAllUserData(self):
		return self.conn.hgetall(self.USER_DATA_KEY)

	def getLastSong(self, username):
		if self.checkUserExists(username):
			if data := self.getUserData(username):
				return json.loads(data["lastSong"]) if data["lastSong"] else {}
		return 0

	def updatePassword(self, username, curr_pass, new_pass):
		if self.checkUserExists(username):
			if self.checkPassword(username, curr_pass):
				data = self.getUserData(username)
				data["pass"] = new_pass
				res = self.setUserData(username, data)
				if res == 1:
					return 1
				elif res == -1:
					return 2
				elif res == 0:
					return 3
				else:
					return 4
			return -1
		return 0

	def removeAllUsers(self):
		self.conn.delete(self.USER_DATA_KEY, self.USER_LIST_KEY)
		return 1

if __name__=="__main__":
	r = RedisClient()
	print(r.getAllUserData())