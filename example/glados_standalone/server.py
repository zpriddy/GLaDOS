from os import getenv
import logging

from flask import Flask, request

from glados import (
    Glados,
    GladosBot,
    GladosRequest,
    RouteType,
    SlackVerification,
    GladosRouteNotFoundError,
)
from test_plugin.test_plugin import TestPlugin
from example import FLASK_HOST, FLASK_PORT
import json

glados_config = "glados_standalone/glados.yaml"

app = Flask(__name__)
glados = Glados(glados_config)


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


@app.route("/SendMessage/<route>", methods=["POST"])
def send_message_route(route):
    glados_request = GladosRequest(
        RouteType.SendMessage, route, json=request.get_json()
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


@app.route("/Slash/<route>", methods=["POST"])
def slash_command(route):
    slack_info = extract_slack_info(request)
    request_json = request.form.to_dict()
    r = GladosRequest(RouteType.Slash, route, slack_info, json=request_json)
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


def start():
    glados.read_config()
    print(glados.router.routes)


def run():
    start()
    app.run("127.0.0.1", FLASK_PORT, debug=False, load_dotenv=False)


if __name__ == "__main__":
    run()
