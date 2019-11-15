from pyngrok import ngrok
from example import FLASK_PORT

def start_ngrok(port=FLASK_PORT, options: dict = None):
    if not options:
        options = dict()
    ngrok.connect(port=port, proto="http", options=options)
