"""
Production deployment configuration for OpenVoice API Server
"""
import os
import logging
from gunicorn.app.base import BaseApplication
from main import app

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openvoice_api.log'),
        logging.StreamHandler()
    ]
)

class StandaloneApplication(BaseApplication):
    """Gunicorn application for production deployment"""
    
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def create_production_config():
    """Create production configuration"""
    return {
        'bind': f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}",
        'workers': int(os.getenv('WORKERS', '4')),
        'worker_class': 'uvicorn.workers.UvicornWorker',
        'worker_connections': int(os.getenv('WORKER_CONNECTIONS', '1000')),
        'max_requests': int(os.getenv('MAX_REQUESTS', '1000')),
        'max_requests_jitter': int(os.getenv('MAX_REQUESTS_JITTER', '100')),
        'timeout': int(os.getenv('TIMEOUT', '120')),
        'keepalive': int(os.getenv('KEEPALIVE', '5')),
        'preload_app': True,
        'accesslog': '-',
        'errorlog': '-',
        'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
        'log_level': os.getenv('LOG_LEVEL', 'info').lower(),
    }

if __name__ == '__main__':
    options = create_production_config()
    StandaloneApplication(app, options).run()
