PRODUCT_NAME = 'wotnot'
APP_NAME = 'consumer-service'

APP_READINESS_API = '/k8/readiness'
APP_LIVENESS_API = '/k8/liveness'
APP_TERMINATION_API = '/k8/termination'
RABBITMQ_CONSUMER_HEALTH_TEST_API = '/consumer-health-test'
RABBITMQ_CONSUMERS_REPORT_API = "{rabbitmq_host}/api/consumers/"

QUEUE = "queue"
HANDLE_FAILURE = "handle_failure"
HANDLE_SUCCESS = "handle_success"
PREFETCH_COUNT = "prefetch_count"
CONSUMERS = "consumers"
IS_BATCH_PROCESS = "is_batch_process"
WAIT_TIME = "wait_time"
BATCH_SIZE = "batch_size"
IS_PROCESS_REDELIVERED = "is_process_redelivered"
CONSUMER_TAG = "consumer_tag"

UTF_8 = "utf-8"
