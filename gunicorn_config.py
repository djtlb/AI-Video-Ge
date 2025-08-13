"""
Gunicorn configuration file for production deployment.
"""

import os

# Server socket
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8081")  # Using 8081 as default port
backlog = 2048

# Worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", 2))  # Reduced number of workers
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 100  # Reduced connections per worker
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "300"))  # Default 5 minutes timeout
keepalive = 2

# Process naming
proc_name = 'ai-avatar-video'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get("LOG_LEVEL", "info")

# Process management
preload_app = True
reload = os.environ.get("GUNICORN_RELOAD", "False").lower() == "true"
reload_engine = 'auto'

# Server hooks
def on_starting(server):
    """
    Server startup operations
    """
    print(f"Starting AI Avatar Video Server on {bind}")
    print(f"GPU Preference: AMD = {os.environ.get('PREFER_AMD_GPU', 'true')}")
    print(f"Worker Count: {workers}")

def on_reload(server):
    """
    Server reload operations
    """
    print("Reloading AI Avatar Video Server")

def post_fork(server, worker):
    """
    Post fork operations
    """
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server, worker):
    """
    Pre fork operations
    """
    pass

def pre_exec(server):
    """
    Pre exec operations
    """
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """
    Server ready operations
    """
    server.log.info("Server is ready. Spawning workers")
    print(f"🚀 Server ready at http://{bind.split(':')[0]}:{bind.split(':')[1]}")

def worker_int(worker):
    """
    Worker interrupt operations
    """
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """
    Worker abort operations
    """
    worker.log.info("Worker received SIGABRT signal")

def worker_exit(server, worker):
    """
    Worker exit operations
    """
    server.log.info(f"Worker exited (pid: {worker.pid})")
