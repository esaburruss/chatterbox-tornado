from __future__ import print_function
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
from tornado.options import define, options, parse_command_line

import redis

import tornadoredis
import time
import json
import re

c = tornadoredis.Client()
c.connect()

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
client = redis.StrictRedis( host='localhost', port = 6379)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("test.html", title="PubSub + WebSocket Demo")

class NewMessageHandler(tornado.web.RequestHandler):
    def check_origin(self, origin):
        return True

    def set_default_headers(self):
        print('setting headers!!!')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("content-type", "application/json")
        self.set_header("Access-Control-Allow-Headers", "content-type, *")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self):
        #print('Working')
        body = tornado.escape.json_decode(self.request.body)
        #print(body)
        message = body['message']
        from_id = body['from_id']
        to_id = body['to_id']
        key = 'user:{}:from:{}:time:{:d}'.format(to_id, from_id, int(time.time()))
        client.set(key, message, ex=300)
        q_key = 'user:{}:messageQueue'.format(to_id)
        #print(q_key)
        #print(key)
        #client.lpush(qKey, key)
        client.publish(q_key, key)

    def get(self):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()



class MessageHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.listen()

    def check_origin(self, origin):
        return True

    def user_log(self, msg):
        print(msg)

    @tornado.gen.engine
    def listen(self):
        self.id = self.get_argument('id')
        self.username = self.get_argument('username')

        self.key = 'user:{}:messageQueue'.format(self.id)
        #print(self.key)
        self.client = tornadoredis.Client()
        self.client.connect()
        self.usr = '{}:{}'.format(self.id, self.username)
        client.publish('userlog', '{}:1'.format(self.usr))

        yield tornado.gen.Task(self.client.subscribe, self.key)
        self.client.listen(self.on_message)
        yield tornado.gen.Task(self.client.subscribe, 'userlog')
        #self.client.listen()

        #self.client.listen(self.user_log)
        self.write_message(self.getOnlineUsers())

        client.sadd('users', self.usr)
        clients[self.id] = {"id": self.id, "object": self}


    def on_message(self, msg):
        print(msg)
        if msg.kind == 'message':
            if msg.pattern == self.key:
                m = map(int, re.findall(r'\d+', msg.body))
                message = '{{"code": "message", "from": {}, "time": {}, "message": "{}"}}'.format(m[1], m[2], client.get(msg.body))
                print(message)
                self.write_message(message)
            elif msg.channel == 'userlog':
                m = msg.body.encode('ascii', 'ignore').split(':')
                print(m[2])
                if int(m[2]) == 1:
                    message = '{{"code": "signIn", "userId": {}, "username": "{}"}}'.format(m[0], m[1])
                    print(message)
                    self.write_message(message)
                else:
                    message = '{{"code": "signOut", "userId": {}, "username": "{}"}}'.format(m[0], m[1])
                    print(message)
                    self.write_message(message)
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe(self.key)
            self.client.disconnect()
        if self.id in clients:
            del clients[self.id]
        client.publish('userlog', '{}:0'.format(self.usr))
        client.srem('users', self.usr)

    def getOnlineUsers(self):
        users = client.smembers('users')
        json = '{"code": "online-users", "users":['
        i=0
        for x in users:
            m = x.encode('ascii', 'ignore').split(':')
            if int(m[0]) != self.id:
                if i!=0:
                    json += ','
                json += '{{"id": {}, "username": "{}"}}'.format(m[0], m[1])
                i+=1
        json += ']}'
        return json

application = tornado.web.Application([
    #(r'/', MainHandler),
    (r'/msg', NewMessageHandler),
    (r'/websocket', MessageHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    client.delete('users')
    print('Demo is runing at 0.0.0.0:8888\nQuit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()
