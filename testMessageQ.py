import redis
from messageQ import MessageQueue

client = redis.StrictRedis( host='localhost', port = 6379)

q2 = MessageQueue(1, client)
q2.sendMessage(2, 'Hi!')

#q1 = MessageQueue(1, client)
#q1.getSize()
#print q1.size
#print q1.getMessage()
