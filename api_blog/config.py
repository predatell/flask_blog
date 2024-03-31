import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Dev(object):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


class Prod(object):
    """Production configurations"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


class Test(object):
    """Configuration for unit test"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    JWT_SECRET_KEY = "dsjysvufy6fht"


app_config = {
    'dev': Dev,
    'prod': Prod,
    'test': Test,
}
