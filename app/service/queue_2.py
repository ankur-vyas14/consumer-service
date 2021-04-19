from ..common import (HttpMethodEnum, api_call)
import json

ENDPOINT = "http://localhost:5050/queue_2"
HEADERS = {"content-type": "application/json"}
METHOD = HttpMethodEnum.POST.value


class Queue2:
    @staticmethod
    def handle_success(payload):
        print("Handle success batch: ", payload)
        # api_call(ENDPOINT, METHOD, HEADERS, json.dumps(payload))

    @staticmethod
    def handle_failure(payload):
        print("in handle_failure ", payload)
