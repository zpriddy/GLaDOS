from slack.web.classes import JsonObject, extract_json
from slack.web.classes.blocks import Block


class Home(JsonObject):
    attributes = {"home"}

    def __init__(self, *, blocks=None):
        if not blocks:
            blocks = list()
        self.blocks = blocks

    def add_block(self, block: Block):
        self.blocks.append(block)

    def to_dict(self, *args) -> dict:
        json = super().to_dict()
        json["type"] = "home"
        json["blocks"] = extract_json(self.blocks)
        return json
