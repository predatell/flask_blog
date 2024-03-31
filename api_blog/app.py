# Import the Flask class from the flask module
from flask import Flask
import markdown
import markdown.extensions.fenced_code

from .auth import user_api as user_blueprint
from .comments import comment_api as comment_blueprint
from .models import db, BlogPost, Comment, BlogPostSchema, CommentSchema
from .config import app_config
from .views import register_api


def create_app(config_name):
    """Create app"""

    # app initiliazation
    app = Flask(__name__)

    app.config.from_object(app_config[config_name])
    db.init_app(app)

    with app.app_context():
        # create all tables
        db.create_all()

    @app.route("/", methods=['GET'])
    def index():
        readme_file = open("README.md", "r")
        md_template_string = markdown.markdown(
            readme_file.read(), extensions=["fenced_code"]
        )

        return md_template_string

    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(comment_blueprint, url_prefix='/post-comments')

    register_api(app, BlogPost, BlogPostSchema, "posts")
    register_api(app, Comment, CommentSchema, "comments")

    return app
