import json
import logging

import os
from base64 import b64decode


def get_var(var_name: str):
    """Get an ENV VAR"""
    return os.environ[var_name]


def decode_kms(ciphertext_blob: str) -> str:
    """Decode a secret using the IAM role of the lambda function.

    :param ciphertext_blob: str
        ciphertext_blob to decode
    :return:
    str
        decoded text
    """
    import boto3

    return (
        boto3.client("kms")
        .decrypt(CiphertextBlob=b64decode(ciphertext_blob))["Plaintext"]
        .decode("utf-8")
    )


def get_enc_var(var_name: str):
    """Get an encrypted ENV VAR"""
    ciphertext_blob = get_var(var_name)
    return decode_kms(ciphertext_blob)


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
