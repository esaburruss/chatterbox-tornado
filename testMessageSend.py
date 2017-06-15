import redis
from messageQ import MessageQueue

class A(object):
    def __init__(self):
        print 'Init'
    def send_message(self, message):
        print 'Mock Send: {}'.format(message)
client = redis.StrictRedis( host='localhost', port = 6379)

a = A()
q2 = MessageQueue(2, client, a)

q2.sendMessage(1, "Hello1!!!")

q2.stop()
