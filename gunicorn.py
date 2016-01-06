bind = '127.0.0.1:8000'
workers = 3

pythonpath = 'app/'

# Require setproctitle module
#proc_name = 'lexpage'

max_request = 200
max_requests_jitter = 20

pidfile = 'gunicorn.pid'

