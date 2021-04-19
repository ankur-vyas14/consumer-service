from enum import Enum


class HttpMethodEnum(Enum):
    POST = 'POST'
    PUT = 'PUT'
    GET = 'GET'
    DELETE = 'DELETE'


class AsyncBrokerEnum(Enum):
    """
    Types of Asynchronous brokers
    """
    RABBITMQ = "RabbitMQ"


class RabbitMQClientEnum(Enum):
    """
    Clients for RabbitMQ operations
    """
    PIKA = "Pika"

