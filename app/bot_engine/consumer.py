from MessageBrokerLib import MessageBroker

from .consumer_handler import (SingleMessageHandler, BatchMessageHandler)
from app.common.enums import (AsyncBrokerEnum, RabbitMQClientEnum)


class Consumer:

    def __init__(self, queue_enum, consumer_tag, app, broker=AsyncBrokerEnum.RABBITMQ.value,
                 client=RabbitMQClientEnum.PIKA.value):
        self.queue_enum = queue_enum
        self.consumer_tag = consumer_tag
        self.app = app
        self.broker = broker,
        self.client = client
        self.broker = MessageBroker.broker(self.broker, self.client)

    def _load_consumer(self, queue):
        if queue.value['is_batch_process']:
            BatchMessageHandler(self.consumer_tag, self.app, self.broker, queue.value['prefetch_count'],
                                queue.value['queue'], queue.value['handle_success'], queue.value['handle_failure'],
                                queue.value['batch_size'], queue.value['wait_time'],
                                queue.value['is_process_redelivered'])
        else:
            SingleMessageHandler(self.consumer_tag, self.app, self.broker, queue.value['prefetch_count'],
                                 queue.value['queue'], queue.value['handle_success'], queue.value['handle_failure'],
                                 queue.value['is_process_redelivered'])

    def load_consumers(self, queue_enum, consumers):
        for _ in range(consumers):
            self._load_consumer(queue_enum)

    def consume(self):
        for queue_enum in self.queue_enum:
            self.load_consumers(queue_enum, queue_enum.value['consumers'])

    def recover_consumer(self, active_consumers):
        for queue in self.queue_enum:
            define_consumer = queue.value['consumers']
            queue_name = queue.value['queue']
            active_consumer = len(list((filter(
                lambda q: q['queue_name'] == queue_name and q['consumer_tag'] == self.consumer_tag, active_consumers))))
            print(define_consumer, active_consumer)
            load_consumer = define_consumer + active_consumer
            self._recover_consumer(queue, load_consumer)

    def _recover_consumer(self, queue_enum, consumers):
        self.load_consumers(queue_enum, consumers)

