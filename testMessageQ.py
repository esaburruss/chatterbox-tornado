import redis
from messageQ import MessageQueue

client = redis.StrictRedis( host='localhost', port = 6379)

q1 = MessageQueue(1, client)
q1.start()

#q1 = MessageQueue(1, client)
#q1.getSize()
#print q1.size
#print q1.getMessage()
