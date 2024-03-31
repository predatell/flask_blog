import os

from .app import create_app

config_name = os.getenv('BLOG_ENV_NAME')
create_app(config_name)
