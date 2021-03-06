from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery

app = Flask(__name__, template_folder='./frontend/templates', static_folder='./frontend/static')
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from appli import routes, models

db.create_all()
db.session.commit()