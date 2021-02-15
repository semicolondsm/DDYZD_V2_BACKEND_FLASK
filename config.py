import os
import base64
from dotenv import load_dotenv

load_dotenv(dotenv_path="./ddyzd.env")
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET')
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_SECRET_KEY = os.getenv('SECRET')
    JWT_DECODE_ALGORITHMS = 'HS256'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}/{database}'\
    .format(user='ddyzd', password='password', host='180.228.167.34:3306', database='ddyzd_db')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}/{database}'\
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