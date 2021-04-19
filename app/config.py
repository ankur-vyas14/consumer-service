import os
from distutils.util import strtobool

from app.common import get_unique_key

__all__ = ['configure_app']


def configure_app(app):
    app.config['ENVIRONMENT'] = os.environ.get("ENVIRONMENT")
    app.config['DEBUG'] = strtobool(os.environ.get("DEBUG"))
    app.config['TESTING'] = strtobool(os.environ.get("TESTING"))
    app.config['PORT'] = int(os.environ.get("SERVICE_PORT", 7777))

    # Logger
    app.config['GL_SERVER'] = os.environ.get("GL_SERVER")
    app.config['GL_PORT'] = int(os.environ.get("GL_PORT"))
    app.config['ENABLE_GRAYLOG'] = int(os.environ.get('ENABLE_GRAYLOG'))

    # RabbitMQ
    app.config['RABBIT_MQ_USERNAME'] = os.environ.get('RABBIT_MQ_USERNAME')
    app.config['RABBIT_MQ_HOST_URL'] = os.environ.get('RABBIT_MQ_HOST_URL')
    app.config['RABBIT_MQ_PASSWORD'] = os.environ.get('RABBIT_MQ_PASSWORD')

    app.config['CONSUMER_TAG'] = get_unique_key()
