import json
import logging


def read_config(config_file: str):
    from glados import GladosConfig

    logging.debug(f"Reading GLaDOS config from {config_file}")
    config = GladosConfig(config_file)
    config.read_config()
    return config


class PyJSON:
    def __init__(self, d):
        if type(d) is str:
            d = json.loads(d)

        self.from_dict(d)

    def from_dict(self, d):
        self.__dict__ = {}
        for key, value in d.items():
            if type(value) is dict:
                value = PyJSON(value)
            if type(value) is list:
                value_list = list()
                for v in value:
                    if type(v) in [list, dict]:
                        value_list.append(PyJSON(v))
                    else:
                        value_list.append(v)
                value = value_list
            self.__dict__[key] = value

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if type(value) is PyJSON:
                value = value.to_dict()
            d[key] = value
        return d

    def __repr__(self):
        return str(self.to_dict())

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default
