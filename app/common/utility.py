import datetime
import json
import logging
import os
import random
import string
from base64 import b64encode

import requests
import shortuuid
from flask import current_app, request, has_request_context
from flask_log_request_id import current_request_id
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .constants import RABBITMQ_CONSUMERS_REPORT_API, UTF_8
from .enums import HttpMethodEnum


def make_dir(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


class GrayLogContextFilter(logging.Filter):

    def filter(self, record):
        get_http_request_fields(record)
        return True


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record = get_http_request_fields(record)
        return super().format(record)


def get_ip_address(_request):
    proxy_ip_key = 'HTTP_X_FORWARDED_FOR'
    ip_address = request.environ[proxy_ip_key] if proxy_ip_key in _request.environ else _request.remote_addr
    if isinstance(ip_address, str):
        # return last access IP address
        return ip_address.split(',')[-1]


def get_request_correlation_id():
    if request.headers.get('WT_CORRELATION_ID', None) is None:
        return current_request_id()
    return request.headers.get('WT_CORRELATION_ID', '-')


def get_request_user_id():
    return request.headers.get('WT_USER_ID', '-')


def get_http_request_fields(record):
    record.correlation_id = record.path_info = record.query_string = record.method = \
        record.http_origin = record.ip_address = record.user_agent = record.file_path = record.user_id = ''
    if has_request_context():
        record.correlation_id = get_request_correlation_id()
        record.user_id = get_request_user_id()
        record.path_info = request.headers.environ.get('PATH_INFO', '')
        record.query_string = request.headers.environ.get('QUERY_STRING', '')
        record.method = request.headers.environ.get('REQUEST_METHOD', '')
        record.http_origin = request.headers.environ.get('HTTP_ORIGIN', '')
        record.ip_address = get_ip_address(request)
        record.user_agent = request.headers.environ.get('HTTP_USER_AGENT', '')
        record.file_path = record.pathname
    return record


def log_exception(sender, exception, **extra):
    """ Log an exception to our logging framework """
    sender.logger.exception('Got exception during processing: %s', exception)


def invoke_http_request(endpoint, method, headers, payload=None, timeout=61):
    _request = requests_retry_session()
    _request.headers.update({
        **headers
    })
    try:
        response = None
        if method == HttpMethodEnum.GET.value:
            response = _request.get(url=endpoint, data=payload, timeout=timeout)
        if method == HttpMethodEnum.POST.value:
            response = _request.post(url=endpoint, data=payload, timeout=timeout)
        if method == HttpMethodEnum.PUT.value:
            response = _request.put(url=endpoint, data=payload, timeout=timeout)
        if method == HttpMethodEnum.DELETE.value:
            response = _request.delete(url=endpoint, data=payload, timeout=timeout)
        return response.json(), response.status_code
    except ValueError:
        return response, response.status_code
    except requests.exceptions.RequestException:
        raise Exception("Error while invoking the request")


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def is_success_request(status_code):
    return 200 <= status_code <= 299


def api_call(endpoint, method, headers, payload):
    from app import app
    response, status_code = invoke_http_request(endpoint, method, headers, json.dumps(payload))
    app.logger.info("response {}".format(response))
    if not is_success_request(status_code):
        app.logger.info("error occurred {}".format("Unsuccessful request"))
        raise Exception("Unsuccessful request")


def get_unique_key():
    timestamp = datetime.datetime.now().strftime('%H%M%S%f')
    random_str = timestamp + ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(8))
    uuid_str = shortuuid.ShortUUID().random(length=12)
    return '{}{}'.format(uuid_str, random_str)


def get_queues_consumer_count():
    """RabbitMQ API to get queues details and it's active consumers"""
    from app import app
    with app.app_context():
        secret = '{}:{}'.format(current_app.config['RABBIT_MQ_USERNAME'], current_app.config['RABBIT_MQ_PASSWORD'])
        endpoint = RABBITMQ_CONSUMERS_REPORT_API.format(rabbitmq_host=current_app.config['RABBIT_MQ_HOST_URL'])
        token = b64encode(bytes(secret, 'utf-8')).decode("ascii")
        header = {'Authorization': 'Basic {}'.format(token)}
        response, status_code = invoke_http_request(endpoint, HttpMethodEnum.GET.value, header)
        return [{"queue_name": consumer['queue']['name'], "consumer_tag": consumer['consumer_tag']} for consumer in
                response]


def get_consumer_tag(app):
    with app.app_context():
        return current_app.config['CONSUMER_TAG']


def get_payload(payload):
    """
    "This method decodes the consumed message.

    :param payload: STRING: encoded message
    :return: JSON: decoded message
    """

    payload_str = payload.decode(UTF_8)
    payload_json = json.loads(payload_str)
    return payload_json


def get_callback_function(is_redelivered, is_process_redelivered, handle_success, handle_failure):
    if is_redelivered:
        if is_process_redelivered:
            return handle_success
        else:
            return handle_failure
    else:
        return handle_success
