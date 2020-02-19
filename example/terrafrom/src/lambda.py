import json
from os import environ
from glados import (
    Glados,
    GladosBot,
    GladosRequest,
    RouteType,
    SlackVerification,
    EventRoutes,
)
from example_plugin import ExamplePlugin

BOT_KEY = environ.get("glados_bot_key")
SIGNING_KEY = environ.get("glados_signing_key")

glados = Glados()
glados_bot = GladosBot(BOT_KEY, "glados", SIGNING_KEY)
glados.add_bot(glados_bot)
glados.add_plugin(ExamplePlugin(glados_bot))


def send_message(event):
    print("sending message")
    route = event.get("pathParameters").get("route")
    r = GladosRequest(RouteType.Webhook, route, json=json.loads(event.get("body")))
    return glados.request(r)


def events(event):
    body = json.loads(event.get("body"))
    event_type = body.get("type", "")
    if event_type == "url_verification":
        return {"challenge": body.get("challenge")}

    bot = event.get("pathParameters").get("bot")
    slack_info = SlackVerification(
        event.get("body"),
        event.get("headers").get("X-Slack-Request-Timestamp"),
        event.get("headers").get("X-Slack-Signature"),
    )
    r = GladosRequest(
        RouteType.Events, slack_verify=slack_info, bot_name=bot, json=body
    )
    return glados.request(r)


RESOURCE_MAP = {"/SendMessage/{route+}": send_message, "/Events/{bot+}": events}


def handler(event, context):
    print(event)

    resource = event.get("resource")
    response = RESOURCE_MAP[resource](event)

    return {
        "headers": {"content-type": "application/json"},
        "statusCode": 200,
        "body": json.dumps(response),
    }
