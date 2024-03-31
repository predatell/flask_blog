from flask import Blueprint, jsonify, request

from .models import db, Comment, CommentSchema
from .utils import pagination

comment_api = Blueprint('comment_api', __name__)
comment_schema = CommentSchema()


@comment_api.route('/<int:post_id>', methods=['GET'])
def get_post_comments(post_id):
    """Get all comments for specific post"""
    comment_schema = CommentSchema()
    response = pagination(request, db.select(Comment).filter_by(post_id=post_id), comment_schema)
    return jsonify(response), 200
