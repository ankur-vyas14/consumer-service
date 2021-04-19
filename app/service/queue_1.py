import json

from ..common import (HttpMethodEnum, api_call)

ENDPOINT = "http://localhost:5050/queue_1"
HEADERS = {"content-type": "application/json"}
METHOD = HttpMethodEnum.POST.value


class Queue1:
    @staticmethod
    def handle_success(payload):
        print("Handle success called: ", payload)
        # api_call(ENDPOINT, METHOD, HEADERS, json.dumps(payload))

    @staticmethod
    def handle_failure(payload, error=''):
        print("in handle_failure ", payload, error)
