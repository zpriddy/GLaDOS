#!/usr/bin/python3
"""
Serves a local Flask application for GLaDOS bots/plugins
"""

import argparse
import json
import logging

from .configs import read_config
from .core import Glados
from .errors import GladosRouteNotFoundError
from .request import GladosRequest, SlackVerification
from .route_type import RouteType
from .router import GladosRoute

try:
    from flask import Flask, request
except ImportError:
    raise ImportError(
        "Flask is not installed, please install Flask or install glados extra 'servelocal'"
    )

app = Flask(__name__)
glados = None


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


@app.route("/SendMessage/<bot>/<route>", methods=["POST"])
def send_message_route(bot, route):
    glados_request = GladosRequest(
        RouteType.SendMessage, route, bot_name=bot, json=request.get_json()
    )

    return glados.request(glados_request)


@app.route("/Events/<bot>", methods=["POST"])
def event_subscriptions(bot):
    body = request.json
    event_type = body.get("type", "")

    if event_type == "url_verification":
        return body.get("challenge")

    # Build GladosRequest
    r = GladosRequest(
        RouteType.Events,
        slack_verify=extract_slack_info(request),
        bot_name=bot,
        json=request.get_json(),
    )
    try:
        return glados.request(r)
    except KeyError:
        return ""


@app.route("/Slash/<bot>/<route>", methods=["POST"])
def slash_command(bot, route):
    slack_info = extract_slack_info(request)
    request_json = request.form.to_dict()
    r = GladosRequest(
        RouteType.Slash, route, slack_info, bot_name=bot, json=request_json
    )

    return glados.request(r)


@app.route("/Interaction/<bot>", methods=["POST"])
def interaction(bot):
    slack_info = extract_slack_info(request)
    request_json = request.form.to_dict()
    request_json = json.loads(request_json.get("payload"))
    r = GladosRequest(
        RouteType.Interaction, slack_verify=slack_info, bot_name=bot, json=request_json
    )
    try:
        return glados.request(r)
    except GladosRouteNotFoundError as e:
        logging.error(e)

        return "not found"


@app.route("/Menu", methods=["POST"])
def external_menu():
    slack_info = extract_slack_info(request)
    request_json = request.form.to_dict()
    request_json = json.loads(request_json.get("payload"))
    r = GladosRequest(RouteType.Menu, slack_verify=slack_info, json=request_json)

    return glados.request(r)


parser = argparse.ArgumentParser(
    description="Serve GLaDOS and plugins using a Flask server"
)
parser.add_argument(
    "configfile",
    type=str,
    help="Use the provided configfile for starting the server/GLaDOS bots",
)


def run():
    global glados

    args = parser.parse_args()
    configfile = args.configfile

    config = read_config(configfile)

    server_config = config.config.server
    glados = Glados(config.config_file)
    glados.read_config()

    app.secret_key = server_config.secret_key
    app.run(server_config.host, server_config.port, debug=server_config.debug)


if __name__ == "__main__":
    run()