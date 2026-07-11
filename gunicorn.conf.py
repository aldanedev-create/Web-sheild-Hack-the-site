
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gevent'
worker_connections = 1000
timeout = 120
graceful_timeout = 30
keepalive = 5

# Threading
threads = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'webshield-scanner'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Preload application
preload_app = False

# Environment variables
raw_env = [
    f'FLASK_APP={os.getenv("FLASK_APP", "backend/run.py")}',
    f'FLASK_ENV={os.getenv("FLASK_ENV", "production")}',
]

# Post-fork hook
def post_fork(server, worker):
    """Called after each worker process is forked."""
    server.log.info(f"Worker spawned: {worker.pid}")

# Pre-fork hook
def pre_fork(server, worker):
    """Called before a worker process is forked."""
    pass

# Post-worker init
def worker_int(worker):
    """Called when worker receives SIGINT."""
    worker.log.info(f"Worker {worker.pid} received SIGINT")

# Worker abort
def worker_abort(worker):
    """Called when worker receives SIGABRT."""
    worker.log.info(f"Worker {worker.pid} received SIGABRT")

# When workers are ready
def when_ready(server):
    """Called when the server is ready."""
    server.log.info("WebShield Scanner is ready to receive requests")