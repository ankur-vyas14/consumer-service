import json
import os

import pika

QUEUE_NAME = 'test_queue'
ROUTING_KEY = 'test_routing_key'
RMQ_EXCHANGE = "test_exchange"


def create_queues():
    exchange = RMQ_EXCHANGE
    with RabbitMqConnection() as conn:
        channel = conn.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=exchange, routing_key=ROUTING_KEY, queue=QUEUE_NAME)


def queue_init():
    create_queues()


def queue_connect():
    parameters = pika.URLParameters(RABBIT_MQ_URL_PARAMETER)
    connection = pika.BlockingConnection(parameters)
    return connection


def queue_close(connection):
    if connection is not None:
        connection.close()


class RabbitMqConnection(object):
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = queue_connect()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        queue_close(self.conn)


if __name__ == '__main__':
    rabbit_mq_user = input("RABBIT_MQ_USERNAME: ") or os.environ.get("RABBIT_MQ_USERNAME")
    rabbit_mq_password = input("RABBIT_MQ_PASSWORD: ") or os.environ.get("RABBIT_MQ_PASSWORD")
    rabbit_mq_host = input("RABBIT_MQ_HOST: ") or os.environ.get("RABBIT_MQ_HOST")

    RABBIT_MQ_URL_PARAMETER = 'amqp://{}:{}@{}:5672/%2F?heartbeat_interval:0'.format(
        rabbit_mq_user, rabbit_mq_password, rabbit_mq_host)
    print("*** Process Start ***")
    queue_init()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbit_mq_host))
    channel = connection.channel()
    print(' [*] Waiting for messages. To exit press CTRL+C')


    def callback(ch, method, properties, body):
        params = body.decode('utf-8')
        message = json.loads(params)
        print("Received Message: ", message)
        try:
            print("Processing Message")
        except Exception as e:
            msg = 'Error Message: {data}'.format(data=e)
            print(msg)
        finally:
            print("Processed Message")
            ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_message_callback=callback, queue=QUEUE_NAME)

    channel.start_consuming()
