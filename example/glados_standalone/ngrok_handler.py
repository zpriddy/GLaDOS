from pyngrok import ngrok
import logging
from time import sleep


def start_ngrok(port, options: dict = None):
    logging.debug("starting ngrok")
    ngrok.kill()
    sleep(4)
    if not options:
        options = dict()
    ngrok.connect(port=port, proto="http", options=options)
    sleep(4)
    return


def end_ngrok(ngrok_url=None):
    logging.info("disconnecting ngrok")
    if ngrok_url:
        ngrok.disconnect(ngrok_url)

    ngrok.kill()
    sleep(5)
