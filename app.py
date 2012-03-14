import os
from flask import Flask
import sys
from flask_peewee.auth import Auth
from flask_peewee.db import Database
import settings
from flaskext.mail import Mail

##----environment
root_join = lambda *a: os.path.join(ROOT, *a)

ROOT    = os.path.dirname(os.path.abspath(__file__))
ROOTMOM = os.path.abspath(root_join(ROOT, ".."))

paths = [
    ROOTMOM,
    root_join('apps'),
    root_join('lib'),
]

print paths
# Reverse the paths so they end up in the same order they're listed
paths.reverse()

for path in paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
    else:
        print "Does not exist:" + path






app = Flask(__name__)
app.config.from_object(settings)
db = Database(app)
auth = Auth(app, db)
mail = Mail(app)

@app.route('/hello')
def hello():
    return 'Hello World!'

from tictactoe import tictactoe
app.register_blueprint(tictactoe, url_prefix='/ttt')

def run(*args):
    
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
if __name__ == '__main__':
    run()
    
