import json
import os
from base64 import b64decode

from glados import logging
from typing import Union


def check_for_env_vars(value: Union[str, dict]):
    """Check an input value to see if it is an env_var or enc_env_var and get the value.

    Parameters
    ----------
    value
        input to check.

    Returns
    -------
    Any:
        Returns the value of the var from either the passed in value, or the env var value.

    Raises
    ------
    KeyError if the env var is not set for what youre tying to get.
    """
    if type(value) is dict and "env_var" in value:
        var_name = value["env_var"]
        try:
            return get_var(var_name)
        except KeyError:
            raise KeyError(f"missing env var: {value['env_var']}")
    if type(value) is dict and "enc_env_var" in value:
        var_name = value["enc_env_var"]
        try:
            return get_enc_var(var_name)
        except KeyError:
            raise KeyError(f"missing enc env var: {value['enc_env_var']}")
    return value


def get_var(var_name: str):
    """Get an ENV VAR"""
    return os.environ[var_name]


def decode_kms(ciphertext_blob: str) -> str:
    """Decode a secret using the IAM role of the lambda function.

    Parameters
    ----------
    ciphertext_blob
        ciphertext_blob to decode

    Returns
    -------
    :obj: `str`
        Decoded KMS data
    """
    import boto3

    return (
        boto3.client("kms")
        .decrypt(CiphertextBlob=b64decode(ciphertext_blob))["Plaintext"]
        .decode("utf-8")
    )


def get_enc_var(var_name: str) -> str:
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
            value = check_for_env_vars(value)
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

    def to_dict(self) -> dict:
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
        value = self.__dict__[key]
        return value

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default
