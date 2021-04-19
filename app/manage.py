import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, request
from flask_log_request_id import RequestID
from flask_restful import Api
from pygelf import GelfUdpHandler

from app.bot_engine.consumer import Consumer
from .common import (get_consumer_tag, make_dir, GrayLogContextFilter, RequestFormatter, errors, APP_NAME, PRODUCT_NAME,
                     get_queues_consumer_count)
from .config import configure_app
from .service import QueueEnum

__all__ = ['create_app', 'create_api', 'app_init']


def create_app():
    """Initialize Flask Application"""
    app = Flask(__name__)
    configure_app(app)
    configure_logging(app)
    RequestID(app)
    configure_hook(app)
    return app


def create_api(app):
    """ Initialize Flask RESTful"""
    api = Api(app, prefix="/api", errors=errors)
    return api


def configure_logging_log_file(app):
    """Track Logging in Log file"""
    log_folder_location = os.path.abspath(os.path.join(__file__, '..', '..', 'data', 'logs'))

    make_dir(log_folder_location)

    app.logger.setLevel(logging.INFO)
    log_file = '{0}/log'.format(log_folder_location)
    handler = TimedRotatingFileHandler(log_file, when='midnight',
                                       interval=1, encoding='utf8', backupCount=1825)
    handler.setLevel(logging.INFO)

    formatter = RequestFormatter(
        '[%(asctime)s] [%(levelname)s] [%(correlation_id)s] '
        '[%(method)s] [%(path_info)s] [%(query_string)s] '
        '[%(pathname)s] %(funcName)s: %(lineno)d : %(message)s] '
        '[%(ip_address)s] [%(http_origin)s] [%(user_agent)s] ')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)


def configure_graylog(app):
    """Set up Graylog"""

    additional_fields = {
        "app": APP_NAME,
        "facility": PRODUCT_NAME,
        "environment": app.config['ENVIRONMENT']}

    app.logger.setLevel(logging.INFO)
    gelf_upd_handler = GelfUdpHandler(host=app.config["GL_SERVER"],
                                      port=app.config["GL_PORT"],
                                      include_extra_fields=True,
                                      compress=False,
                                      chunk_size=1300,
                                      **additional_fields)

    gelf_upd_handler.debug = True
    gelf_upd_handler.setLevel(logging.INFO)
    app.logger.addFilter(GrayLogContextFilter())
    app.logger.addHandler(gelf_upd_handler)


def configure_logging(app):
    """Set up the global logging settings."""

    if app.config["ENABLE_GRAYLOG"]:
        configure_graylog(app)
    else:
        configure_logging_log_file(app)


def configure_hook(app):
    def is_ignore_log():
        return not (request.path.endswith(
            ('.png', '.jpg', '.jpeg', '.css', '.js', '.woff', '.ico', '.css.map''.js.map', '.svg')) or
                    request.path in ('/k8/readiness', '/k8/liveness'))

    @app.before_request
    def before_request():
        if is_ignore_log():
            app.logger.info('Request-Start')

    @app.teardown_request
    def teardown_request(exc):
        if is_ignore_log():
            app.logger.info('Request-End')


def restart_dead_consumers():
    from app import app
    active_consumers = get_queues_consumer_count()
    consumer_tag = get_consumer_tag(app)
    consumer = Consumer(QueueEnum, consumer_tag, app)
    consumer.recover_consumer(active_consumers)
    # print(consumers)
    # for data in QueueEnum:
    #     queue_name = data.value['queue_name']
    #     active_consumer = queues.get(queue_name, 0)
    #     if data.name in consumer_map.keys() and active_consumer < define_consumer:
    #         # It finds dead consumers of the queue and starts the dead consumers
    #         dead_workers = define_consumer - active_consumer
    #         _load_consumer(data.name, queue_name, dead_workers)


def app_init(app):
    consumer_tag = get_consumer_tag(app)
    consumer = Consumer(QueueEnum, consumer_tag, app)
    consumer.consume()
