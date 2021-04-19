import types

from flask import got_request_exception

from app.common import api_route, log_exception
from app.manage import create_app, create_api, app_init

app = create_app()
api = create_api(app)
api.route = types.MethodType(api_route, api)
got_request_exception.connect(log_exception, app)
app_init(app)

# import RESTful API
from app.apis import *
