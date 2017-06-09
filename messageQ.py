import redis
import time
import re
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
        print key1
        m = map(int, re.findall(r'\d+', key1))
        #message = '{"from": {}, "time": {}, "message": {}}'.format(m[1], m[2], self.client.get(key1)[1])
        message = {'from': m[1], 'time': m[2], 'message': self.client.get(key1)}
        return message
