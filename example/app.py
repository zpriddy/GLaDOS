from flask import Flask, request
from test_plugin.test_plugin import TestPlugin

from glados import Glados, GladosBot, GladosRequest, RouteType

app = Flask(__name__)
glados = Glados()

BOT_TOKEN = "xoxb-492264639104-819624326178-x2CA7QTRPOODH5XPQujkeB94"


@app.route("/SendMessage/<route>", methods=["POST"])
def send_message_route(route):
    glados_request = GladosRequest(RouteType.SendMessage, route, **request.get_json())
    return glados.request(glados_request)


if __name__ == '__main__':
    app.secret_key = "ThisIsNotSecure"
    app.debug = True

    bot = GladosBot(BOT_TOKEN, "glados")

    glados.add_plugin(TestPlugin("test plugin", bot))

    app.run("127.0.0.1", 8083, debug=True)
