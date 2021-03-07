from dotenv import load_dotenv
import base64
import os

load_dotenv(dotenv_path="./ddyzd.env")
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET')
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_SECRET_KEY = os.getenv('SECRET')
    ROOM_SECRET_KEY = os.getenv('ROOM_SECRET') 
    JWT_DECODE_ALGORITHMS = 'HS256'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4'\
    .format(user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),  host=os.getenv('DB_URL')+':3306', database=os.getenv('DB_NAME'))

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4'\
    .format(user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), host=os.getenv('DB_URL')+':3306', database=os.getenv('DB_NAME'))

class TestConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+BASEDIR+'/test.sqlite' 

configs = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig 
}
