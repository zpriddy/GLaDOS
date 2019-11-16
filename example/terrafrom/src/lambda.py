import json
from os import environ
from glados import Glados, GladosBot, GladosRequest, RouteType
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
    r = GladosRequest(RouteType.SendMessage, route, json=json.loads(event.get("body")))
    return glados.request(r)

RESOURCE_MAP = {
    "/SendMessage/{route+}": send_message
}

def handler(event, context):
    print(event)

    resource = event.get("resource")
    RESOURCE_MAP[resource](event)



    return {
        "headers":    {
            "content-type": "application/json"
        },
        "statusCode": 200,
        "body":       json.dumps({
            "success": True
        })
    }