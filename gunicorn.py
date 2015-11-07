bind = '127.0.0.1:8000'
workers = 3

pythonpath = 'app/'

# Require setproctitle module
#proc_name = 'lexpage'

max_request = 200
max_requests_jitter = 20


# We need this for markup preview
limit_request_line = 8190

pidfile = 'gunicorn.pid'

