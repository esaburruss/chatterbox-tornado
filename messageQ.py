import redis
from multiprocessing import Process
import threading
import time
import re

class MessageQueue(object):
    def __init__(self, id, client, tornado1):
        #threading.Thread.__init__(self)
        self.id = id
        self.client = client
        self.s = 0
        self.key = 'user:{}:messageQueue'.format(id)
        self.tornado = tornado1
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe([self.key])
        self.subscribe = Process(self.run())
        self.subscribe.start()

    def stop(self):
        self.pubsub.unsubscribe()
        self.subscribe.terminate()
        print self, "unsubscribed and finished"

    def sendMessage(self, toId, message):
        key = 'user:{}:from:{}:time:{:d}'.format(toId, self.id, int(time.time()))
        self.client.set(key, message, ex=300)
        qKey = 'user:{}:messageQueue'.format(toId)
        self.client.lpush(qKey, key)
        self.client.publish(qKey, key)

    def run(self):
        for item in self.pubsub.listen():
            print item['data']
            if item['data'] == "KILL":
                self.stop()
            else:
                self.tornado.send_message(self.getMessage())

    def getSize(self):
        self.size = self.client.llen(self.key)

    def getMessage(self):
        key1 = self.client.brpop(self.key, 0)[1];
        m = map(int, re.findall(r'\d+', key1))
        message = {'from': m[1], 'time': m[2], 'message': self.client.get(key1)}
        return message
