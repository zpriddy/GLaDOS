from flask import Flask, request
from test_plugin.test_plugin import TestPlugin

from glados import Glados, GladosBot, GladosRequest, RouteType

from os import getenv

app = Flask(__name__)
glados = Glados()


GLADOS_BOT_KEY=getenv("GLADOS_GLADOS_BOT_KEY")

@app.route("/SendMessage/<route>", methods=["POST"])
def send_message_route(route):
    glados_request = GladosRequest(RouteType.SendMessage, route, **request.get_json())
    return glados.request(glados_request)


if __name__ == '__main__':
    app.secret_key = "ThisIsNotSecure"
    app.debug = True

    bot = GladosBot(GLADOS_BOT_KEY, "glados")

    glados.add_plugin(TestPlugin("test plugin", bot))

    app.run("127.0.0.1", 8083, debug=True)
