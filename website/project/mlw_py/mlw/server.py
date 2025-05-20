from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import logging
import os

app = Flask(__name__)
app.config.from_object('config.config.Config')
app.config['SQLALCHEMY_DATABASE_URI'] = f"{app.config['DB_TYPE']}{app.config['DB_USER']}:{app.config['DB_PASSWORD']}@{app.config['DB_HOST']}/{app.config['DB_DATABASE']}"

db = SQLAlchemy(app)

log_dir = app.config['LOG_DIR']
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d")
log_filename = os.path.join(os.getcwd(), app.config['LOG_DIR'], f'log-{formatted_time}.log')
handler = TimedRotatingFileHandler(
    log_filename, when="midnight", interval=1, backupCount=7
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
