# import os
# from dotenv import load_dotenv
#
# # load .env environment variables
# load_dotenv()
#
# DATABASE_URL = os.environ['DATABASE_URL']
# DATABASE_URL_TEST = os.environ['DATABASE_URL_TEST']


import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_TEST')
