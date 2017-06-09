import redis
import time
class MessageQueue(object):
    def __init__(self, id, client):
        self.id = id
        self.client = client
        self.s = 0
        self.key = 'user:{}:messageQueue'.format(id)

    def sendMessage(self, toId, message):
        print message
        key = 'user:{}:from:{}:time:{:d}'.format(toId, self.id, int(time.time()))
        self.client.set(key, message)
        qKey = 'user:{}:messageQueue'.format(toId)
        self.client.lpush(qKey, key)
        print key
        print qKey

    def getSize(self):
        self.size = self.client.llen(self.key)

    def getMessage(self):
        key1 = self.client.brpop(self.key, 0)[1];
        #print key1[1]
        return self.client.get(key1)
