from MessageBrokerLib import MessageBroker, RabbitMQPikaConsume


def handler_success(payload):
    print("handler_success ", payload)


def handler_failure(payload, error=''):
    print("handler_failure ", payload, " error: ", error)


def handler_redelivered(payload):
    print("handler_redelivered ", payload)


def on_message_callback(channel, method, properties, body):
    RabbitMQPikaConsume.callback(channel, method, body, handler_success, handler_failure, handler_redelivered,
                                 IS_ACKNOWLEDGE)


if __name__ == '__main__':
    UTF_8 = "utf-8"

    PREFETCH_COUNT = 1
    QUEUE = "queue_1"
    AUTO_ACKNOWLEDGEMENT = False
    IS_ACKNOWLEDGE = True

    broker = MessageBroker.broker()
    connection = broker.connection()
    with connection as conn:
        channel = conn.channel()
        print("--------Consumer started----------")
        broker.consume(channel, PREFETCH_COUNT, QUEUE, on_message_callback, AUTO_ACKNOWLEDGEMENT)
    print("--------Consumer ended----------")
