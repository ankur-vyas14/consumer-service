import os

import newrelic.agent

if os.environ.get("IS_NEW_RELIC_ENABLED", False) and os.path.exists(os.path.abspath(os.path.join(__file__, '..', 'app', 'newrelic.ini'))):
    newrelic.agent.initialize(os.path.abspath(os.path.join(__file__, '..', 'app', 'newrelic.ini')))

import cherrypy

from app import app

if __name__ == '__main__':
    try:
        # Mount the application
        cherrypy.tree.graft(app, "/")

        # Set the configuration of the web server
        cherrypy.config.update({
            'log.screen': True,
            'server.socket_port': app.config['PORT'],
            'server.socket_host': '::',
            'server.thread_pool': 30,
            'server.shutdown_timeout': 1
        })
        cherrypy.engine.start()
        cherrypy.engine.block()
    except KeyboardInterrupt:
        cherrypy.engine.stop()
