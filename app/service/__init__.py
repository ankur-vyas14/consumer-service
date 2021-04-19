from enum import Enum

from .queue_1 import Queue1
from .queue_2 import Queue2
from ..common import (CONSUMERS, QUEUE, HANDLE_FAILURE, HANDLE_SUCCESS, WAIT_TIME, BATCH_SIZE, IS_PROCESS_REDELIVERED,
                      IS_BATCH_PROCESS, PREFETCH_COUNT)


class QueueEnum(Enum):
    QUEUE_1 = {
        QUEUE: 'queue_1',
        HANDLE_SUCCESS: Queue1.handle_success,
        HANDLE_FAILURE: Queue1.handle_failure,
        PREFETCH_COUNT: 1,
        CONSUMERS: 2,
        IS_BATCH_PROCESS: False,
        WAIT_TIME: 0,
        BATCH_SIZE: 0,
        IS_PROCESS_REDELIVERED: True
    }
    QUEUE_2 = {
        QUEUE: 'queue_2',
        HANDLE_SUCCESS: Queue2.handle_success,
        HANDLE_FAILURE: Queue2.handle_failure,
        PREFETCH_COUNT: 5,
        CONSUMERS: 1,
        IS_BATCH_PROCESS: True,
        WAIT_TIME: 5000,
        BATCH_SIZE: 5,
        IS_PROCESS_REDELIVERED: False
    }
