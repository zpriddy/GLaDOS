from os import getenv
import sys
import logging
from time import sleep

from flask import (
    Flask,
    request,
    g,
    appcontext_tearing_down,
    signals_available,
    appcontext_pushed,
    current_app,
)

from flask.views import MethodView

from glados import (
    Glados,
    GladosBot,
    GladosRequest,
    RouteType,
    SlackVerification,
    GladosRouteNotFoundError,
    GladosConfig,
)
from test_plugin.test_plugin import TestPlugin
from example import FLASK_HOST, FLASK_PORT
import json

import signal


def receiveSignal(signalNumber, frame):
    print("Received:", signalNumber)
    return


signal.signal(signal.SIGHUP, receiveSignal)
signal.signal(signal.SIGINT, receiveSignal)
signal.signal(signal.SIGQUIT, receiveSignal)
signal.signal(signal.SIGILL, receiveSignal)
signal.signal(signal.SIGTRAP, receiveSignal)
signal.signal(signal.SIGABRT, receiveSignal)
signal.signal(signal.SIGBUS, receiveSignal)
signal.signal(signal.SIGFPE, receiveSignal)
# signal.signal(signal.SIGKILL, receiveSignal)
signal.signal(signal.SIGUSR1, receiveSignal)
signal.signal(signal.SIGSEGV, receiveSignal)
signal.signal(signal.SIGUSR2, receiveSignal)
signal.signal(signal.SIGPIPE, receiveSignal)
signal.signal(signal.SIGALRM, receiveSignal)
signal.signal(signal.SIGTERM, receiveSignal)

# app = Flask(__name__)

glados = None  # Glados()

GLADOS_BOT_KEY = getenv("GLADOS_GLADOS_BOT_KEY")


def extract_slack_info(r: request):
    try:
        data = r.get_data(as_text=True)
        timestamp = r.headers.get("X-Slack-Request-Timestamp")
        signature = r.headers.get("X-Slack-Signature")
        return SlackVerification(data, timestamp, signature)
    except Exception as e:
        # If it makes it here, the request probably isn't from Slack.
        logging.error(e)
        return None


class SendMessage(MethodView):
    def post(self, route):
        glados_request = GladosRequest(
            RouteType.SendMessage, route, json=request.get_json()
        )
        return glados.request(glados_request)


# @current_app.route("/Events/<bot>", methods=["POST"])
# def event_subscriptions(bot):
#     body = request.json
#     event_type = body.get("type", "")
#     if event_type == "url_verification":
#         return body.get("challenge")
#
#     # Build GladosRequest
#     r = GladosRequest(
#         RouteType.Events,
#         slack_verify=extract_slack_info(request),
#         bot_name=bot,
#         json=request.get_json(),
#     )
#     try:
#         return glados.request(r)
#     except KeyError:
#         return ""


# @current_app.route("/Slash/<route>", methods=["POST"])
# def slash_command(route):
#     slack_info = extract_slack_info(request)
#     request_json = request.form.to_dict()
#     r = GladosRequest(RouteType.Slash, route, slack_info, json=request_json)
#     return glados.request(r)
#
#
# @current_app.route("/Interaction/<bot>", methods=["POST"])
# def interaction(bot):
#     slack_info = extract_slack_info(request)
#     request_json = request.form.to_dict()
#     request_json = json.loads(request_json.get("payload"))
#     r = GladosRequest(
#         RouteType.Interaction, slack_verify=slack_info, bot_name=bot, json=request_json
#     )
#     try:
#         return glados.request(r)
#     except GladosRouteNotFoundError as e:
#         logging.error(e)
#         return "not found"

#
# @current_app.route("/Menu", methods=["POST"])
# def external_menu():
#     slack_info = extract_slack_info(request)
#     request_json = request.form.to_dict()
#     request_json = json.loads(request_json.get("payload"))
#     r = GladosRequest(RouteType.Menu, slack_verify=slack_info, json=request_json)
#     return glados.request(r)


class HomePage(MethodView):
    def get(self):
        return "GLaDOS Server: Running"


def register_views(flask_app: Flask):
    with flask_app.app_context():
        flask_app.add_url_rule(
            rule="/", view_func=HomePage.as_view("home"), methods=["GET"],
        )

    with flask_app.app_context():
        flask_app.add_url_rule(
            "/SendMessage/<string:route>",
            view_func=SendMessage.as_view("send_message"),
            methods=["POST"],
        )


def read_config(config_file: str = "glados.yaml"):
    logging.debug(f"importing config from: {config_file}")
    config = GladosConfig(config_file)
    config.read_config()
    return config


def setup_ngrok(app):
    from .ngrok_handler import start_ngrok

    ngrok = start_ngrok(
        port=app.glados_config.config.server.port,
        options=app.glados_config.config.ngrok.options.to_dict(),
    )
    return ngrok


def teardown_ngrok(app, *args, **kwargs):
    # logging.critical(f"Shutting down ngrok: {app.ngrok}")
    from .ngrok_handler import end_ngrok

    end_ngrok()


def create_app(config_file):
    app = Flask(__name__)

    app.glados_config = read_config(config_file)
    if app.glados_config.config.ngrok.enabled:
        logging.debug("launching ngrok")
        # app.ngrok = setup_ngrok(app)
        register_views(app)
        setup_ngrok(app)
        appcontext_pushed.connect(setup_ngrok, app)
        appcontext_tearing_down.connect(teardown_ngrok, app)

    return app


def run(config_file: str = "glados.yaml"):
    try:
        app = create_app(config_file)

        logging.info("Starting Standalone GLaDOS Server")

        app.secret_key = app.glados_config.config.server.secret_key
        app.debug = app.glados_config.config.server.debug

        app.run(
            host=app.glados_config.config.server.host,
            port=app.glados_config.config.server.port,
        )

    finally:
        # with app.app_context():
        #     app.ngrok.disconnect()
        print("SHUTTING DOWN")
