# -*- coding:utf-8 -*-
import os

bind = "0.0.0.0:80"
workers = os.environ.get("GUNICORN_WORKERS", 1)
backlog = 2048
worker_class = "gevent"
keepalive = 5
proc_name = "gunicorn.api.proc"
pidfile = "/tmp/gunicorn.pid"
loglevel = "warning"
