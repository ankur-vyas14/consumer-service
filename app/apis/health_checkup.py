from app import app
from app.common import (APP_READINESS_API, APP_LIVENESS_API, APP_TERMINATION_API, RABBITMQ_CONSUMER_HEALTH_TEST_API)
from flask import current_app
from app.manage import restart_dead_consumers


__all__ = ['queue_service_health', 'service_status']


@app.route(APP_READINESS_API)
@app.route(APP_LIVENESS_API)
@app.route(APP_TERMINATION_API)
def service_status():
    return '', 204


@app.route(RABBITMQ_CONSUMER_HEALTH_TEST_API)
def queue_service_health():
    print(current_app.config['CONSUMER_TAG'])
    restart_dead_consumers()
    return '', 204
