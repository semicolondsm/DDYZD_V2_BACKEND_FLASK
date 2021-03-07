from config import configs
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask
import logging

LOG_FORMAT = logging.Formatter("[%(asctime)-15s] (%(filename)s:%(lineno)d) %(levelname)s - %(message)s")
logging.basicConfig(level=logging.INFO)
logHandler = logging.FileHandler('./logs/access.log')
logHandler.setFormatter(LOG_FORMAT)
logHandler.setLevel(logging.INFO)

errHandler = logging.FileHandler('./logs/error.log')
errHandler.setFormatter(LOG_FORMAT)
errHandler.setLevel(logging.ERROR)


db = SQLAlchemy()
jwt = JWTManager()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs[config])
    app.logger.addHandler(logHandler)
    app.logger.addHandler(errHandler)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    
    from app.api_v1_0 import api_v1_0
    app.register_blueprint(api_v1_0) 

    return app
