import redis
from messageQ import MessageQueue

client = redis.StrictRedis( host='localhost', port = 6379)

q = MessageQueue(2, client)

def logMessages():
    print q.getMessage()
    print q.getSize()
    logMessages()

logMessages()
