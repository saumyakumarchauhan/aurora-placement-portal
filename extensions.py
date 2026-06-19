from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from celery import Celery
from flask_mail import Mail

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
mail = Mail()


celery = Celery('placement_portal', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')