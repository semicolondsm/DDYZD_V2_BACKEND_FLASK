from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import configs
from flask_socketio import SocketIO
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('./logs/access.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

websocket = SocketIO(cors_allowed_origins='*')
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs[config])

    db.init_app(app)
    jwt.init_app(app)
    
    from app.api_v1_0 import api_v1_0
    app.register_blueprint(api_v1_0) 

    websocket.init_app(app)
    return app