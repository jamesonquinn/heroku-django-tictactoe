import os, sys, bc.environment
import multiprocessing
#from settings import GUNICORN_pidfile as pidfile

sys.path.insert(0, os.path.abspath(os.path.join(
	os.path.dirname(os.path.abspath(__file__)), "..")))

try:
    import environment
except Exception, e:
    print "Can't load local environment settings file 'environment.py'"
    raise

workers = 5
worker_class = "gunicornworker.SocketIOWorker"

os.environ['SOCKETIO_WORKER'] = 'True'
bind = '127.0.0.1:5000'

def def_post_fork(server, worker):
    from psyco_gevent import make_psycopg_green
    make_psycopg_green()
    worker.log.info("Made Psycopg Green")

post_fork = def_post_fork
