import tornado.ioloop
import tornado.web
import tornado.websocket
import redis

from tornado.options import define, options, parse_command_line


define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
client = redis.StrictRedis( host='localhost', port = 6379)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write("This is your response")
        self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}
        client.sadd('users', self.id);
        print client.scard('users');

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print "Client %s received a message : %s" % (self.id, message)
        self.write_message(u"PONG: " + self.id)

    def on_close(self):
        if self.id in clients:
            del clients[self.id]
    def check_origin(self, origin):
        print origin
        return True

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()