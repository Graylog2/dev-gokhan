# -*- coding: utf-8 -*-
import json


class JsonConverter:

    def __init__(self) -> None:
        pass

    def loads(self, input):
        try:
            output = json.loads(input)
            return output
        except Exception as e:
            raise Exception(e)

    def decode(self, input):
        try:
            output = json.JSONDecoder().decode(input)
            return output
        except Exception as e:
            raise Exception(e)

    def encode(self, input):
        try:
            output = json.JSONEncoder().encode(input)
            return output
        except Exception as e:
            raise Exception(e)
