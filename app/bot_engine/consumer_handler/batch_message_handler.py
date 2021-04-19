import functools
import time
from threading import Thread, Lock, Timer

from app.common.utility import (get_payload)


class BatchMessageHandler(Thread):
    def __init__(self, consumer_tag, app, broker, prefetch_count, queue, handle_success, handle_failure, batch_size,
                 wait_time, is_process_redelivered):
        self.consumer_tag = consumer_tag
        self.handle_success = handle_success
        self.handle_failure = handle_failure
        self.broker = broker
        self.app = app
        self.prefetch_count = prefetch_count
        self.queue = queue
        self.event = None
        self.BATCH_SIZE = batch_size
        self.WAIT_TIME = wait_time / 1000
        self.is_process_redelivered = is_process_redelivered
        self.messages = []
        self.wait_time_duration = 0
        self.async_lock = Lock()
        Thread.__init__(self)
        Thread.daemon = True
        self.connection = self.broker.connection()
        self.start()

    def message_operation(self, cmd, message=None):
        return self._message_operations(cmd, message)

    def _message_operations(self, cmd, message):
        if cmd == "LEN":
            return len(self.messages)
        elif cmd == "APPEND":
            self.messages.append(message)
        elif cmd == "CLEAR":
            self.messages = []

    def cancel_timer(self):
        if self.event and self.event.is_alive():
            self.event.cancel()

    def get_wait_time(self):
        wait_time = self.WAIT_TIME
        if self.wait_time_duration:
            wait_time = wait_time - (time.time() - self.wait_time_duration)
        else:
            self.wait_time_duration = time.time()
        if wait_time < 0:
            wait_time = 0
        return wait_time

    def start_timer(self, wait_time):
        self.event = Timer(wait_time, self.async_process_message)
        self.event.start()

    def async_process_message(self):
        with self.async_lock:
            self.process_messages()

    def process_messages(self):
        messages = self.messages
        is_process_messages = False
        channel = None
        delivery_tag = None
        try:
            if len(messages) > 0:
                is_process_messages = True
                channel = messages[len(messages) - 1]['channel']
                delivery_tag = messages[len(messages) - 1]['delivery_tag']
                self.process()
        except Exception as e:
            self.app.logger.info("error occurred {}".format(e))
            self.handle_failure(self.get_messages([message['payload'] for message in messages]))
        finally:
            if is_process_messages:
                self.multiple_acknowledgement(channel, delivery_tag)

    def reset_wait_time_and_messages(self):
        messages = self.messages
        self.message_operation("CLEAR")
        self.wait_time_duration = 0
        return messages

    @staticmethod
    def get_messages(messages):
        return {"messages": messages}

    def process(self):
        self.cancel_timer()
        messages = self.reset_wait_time_and_messages()
        messages = [message['payload'] for message in messages]
        self.handle_success(self.get_messages(messages))

    def success_callback(self, payload):
        with self.async_lock:
            self.cancel_timer()
            self.message_operation("APPEND", payload)
            length = self.message_operation("LEN")
            if length == self.BATCH_SIZE:
                self.process_messages()
            elif length > 0:
                wait_time = self.get_wait_time()
                if wait_time == 0:
                    self.process_messages()
                else:
                    self.start_timer(wait_time)

    def _multiple_acknowledgement(self, channel, delivery_tag):
        self.broker.acknowledge(channel, delivery_tag=delivery_tag, multiple=True)

    def multiple_acknowledgement(self, channel, delivery_tag):
        self.conn.add_callback_threadsafe(functools.partial(self._multiple_acknowledgement, channel, delivery_tag))

    def on_message_callback(self, channel, method, properties, body):
        payload_json = get_payload(body)
        payload = {
            'payload': payload_json,
            'channel': channel,
            'delivery_tag': method.delivery_tag
        }
        if method.redelivered:
            if self.is_process_redelivered:
                self.success_callback(payload)
            else:
                try:
                    self.app.logger.info("Ignored redelivered message")
                    self.handle_failure(payload_json)
                except Exception:
                    pass
                finally:
                    channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            self.success_callback(payload)

    def run(self):
        with self.connection as conn:
            self.conn = conn
            self.broker.consume(conn.channel(), self.prefetch_count, self.queue, self.on_message_callback,
                                self.consumer_tag)
