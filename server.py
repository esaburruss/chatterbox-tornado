import tornado.ioloop
import tornado.web
import tornado.websocket
import redis
import json
from messageQ import MessageQueue

from tornado.options import define, options, parse_command_line


define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
client = redis.StrictRedis( host='localhost', port = 6379)
#q = MessageQueue(0, client)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write("This is your response")
        self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        self.q = MessageQueue(self.id, client, self)
        #self.q.start()
        #self.q.listenForMessage()
        clients[self.id] = {"id": self.id, "object": self}
        client.sadd('users', self.id);
        print client.scard('users');

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        m = json.loads(message)
        self.q.sendMessage(m['id'], m['message'])

    def send_message(self, message):
        self.write_message(message)

    def on_close(self):
        if self.id in clients:
            del clients[self.id]
        self.q.stop()


    def check_origin(self, origin):
        print origin
        return True

    def getOnlineUsers(self):
        return clients

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
