import os
from flask import Flask

app = Flask(__name__)

@app.route('/hello')
def hello():
    return 'Hello World!'

def run(*args):
    
    # Bind to PORT if defined, otherwise default to 5000.
    raise Exception(str(args))
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
if __name__ == '__main__':
    run()
    
    