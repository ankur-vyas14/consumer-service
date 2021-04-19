from threading import Thread

from app.common.utility import (get_payload, get_callback_function)


class SingleMessageHandler(Thread):
    def __init__(self, consumer_tag, app, broker, prefetch_count, queue, handle_success, handle_failure,
                 is_process_redelivered):
        self.consumer_tag = consumer_tag
        self.handle_success = handle_success
        self.handle_failure = handle_failure
        self.is_process_redelivered = is_process_redelivered
        self.broker = broker
        self.app = app
        self.prefetch_count = prefetch_count
        self.queue = queue
        Thread.__init__(self)
        Thread.daemon = True
        self.connection = self.broker.connection()
        self.start()

    def on_message_callback(self, channel, method, properties, body):
        payload_json = get_payload(body)
        try:
            get_callback_function(method.redelivered, self.is_process_redelivered, self.handle_success,
                                  self.handle_failure)(payload_json)
        except Exception as e:
            try:
                self.app.logger.info("error occurred {}".format(e))
                self.handle_failure(payload_json, e)
            except Exception:
                pass
        finally:
            self.broker.acknowledge(channel, delivery_tag=method.delivery_tag)

    def run(self):
        with self.connection as conn:
            self.broker.consume(conn.channel(), self.prefetch_count, self.queue, self.on_message_callback,
                                self.consumer_tag)
