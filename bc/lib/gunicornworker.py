from socketio.handler import SocketIOHandler
from socketio.server import SocketIOServer
from gunicorn.workers.ggevent import BASE_WSGI_ENV, GeventWorker

class WSGISocketIOHandler(SocketIOHandler):
    def log_request(self, *args):
        pass

    def get_environ(self):
        env = super(WSGISocketIOHandler, self).get_environ()
        env['gunicorn.sock'] = self.socket
        env['RAW_URI'] = self.path
        print "XXXXXXEnvironment:", env
        env['SERVER_PORT'] = 5000
        return env

class WSGISocketIOServer(SocketIOServer):
    base_env = BASE_WSGI_ENV
    def __init__(self, *args, **kw):
        kw["resource"] = "socket.io"
        #kw["namespace"] = "socket.io"

        # Start the Flash Policy Server?
        kw["policy_server"] = False

        super(WSGISocketIOServer, self).__init__(*args, **kw)

class SocketIOWorker(GeventWorker):
    "The Gevent StreamServer based workers."
    server_class = WSGISocketIOServer
    wsgi_handler = WSGISocketIOHandler
