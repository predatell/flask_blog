import os
import jwt
import datetime
from flask import request, g, jsonify
from functools import wraps
from .models import db, User


JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


def error_response(message, code=400):
    return jsonify({'error': message}), code


def generate_token(user_id):
    """Generate Token"""
    now = datetime.datetime.utcnow()
    data = {
        'sub': user_id,
        'iat': now,
        'exp': now + datetime.timedelta(days=1),
    }
    return jwt.encode(data, JWT_SECRET_KEY, 'HS256')


def decode_token(token):
    """Decode token method"""
    response = {}
    try:
        data = jwt.decode(token, JWT_SECRET_KEY, 'HS256')
        response = {'user_id': data['sub']}
    except jwt.ExpiredSignatureError:
        response = {'error': 'Token expired, please login again'}
    except jwt.InvalidTokenError:
        response = {'error': 'Invalid token, please try again with a new token'}
    return response


def auth_required(func):
    """
    Auth decorator
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'api-token' not in request.headers:
            message = 'Authentication token is not available, please login'
            return error_response(message)
        token = request.headers.get('api-token')
        data = decode_token(token)
        error_message = data.get('error', None)
        if error_message:
            return error_response(error_message)

        user = db.session.get(User, data['user_id'])
        if not user:
            message = 'User does not exist, invalid token'
            return error_response(message)
        g.user = {'id': user.id}
        return func(*args, **kwargs)
    return wrapper


def pagination(req, db_select, schema):
    try:
        page = int(req.args.get("page"))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = int(req.args.get("per_page"))
    except (ValueError, TypeError):
        per_page = 20

    results = db.paginate(db_select, page=page, per_page=per_page)
    response = {
        'data': schema.dump(results, many=True)
    }
    if results.has_next:
        response['next'] = "%s?page=%s&per_page=%s" % (request.base_url, results.page + 1, results.per_page)
    if results.has_prev:
        response['prev'] = "%s?page=%s&per_page=%s" % (request.base_url, results.page - 1, results.per_page)
    return response
