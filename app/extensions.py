from flask_mongoengine import MongoEngine
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from .config import celery_url
from .utils import limiter_key
from flask_socketio import SocketIO

db = MongoEngine()
mail = Mail()
bcrypt = Bcrypt()
socket_io = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading",
    message_queue=f"{celery_url}/1",
    max_http_buffer_size=100 * 1024 * 1024,
)

limiter = Limiter(
    key_func=limiter_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=f"{celery_url}/1",
)
