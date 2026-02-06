# gunicorn.conf.py
workers = 4
worker_class = 'sync'
bind = '0.0.0.0:5000'
timeout = 120
keepalive = 5