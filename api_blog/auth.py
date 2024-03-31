from flask import request, Blueprint, jsonify, g
from marshmallow.exceptions import ValidationError

from .models import db, User, UserSchema
from .utils import generate_token, error_response, auth_required, pagination


user_api = Blueprint('user_api', __name__)
user_schema = UserSchema()


@user_api.route('/', methods=['POST'])
def create():
    """Create User Function"""
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return error_response(e.messages)

    # check if user already exist in the db
    user = db.session.execute(db.select(User).filter_by(email=data.get('email'))).one_or_none()
    if user:
        message = 'User with this email already exist, please use another email.'
        return error_response(message)
    user = db.session.execute(db.select(User).filter_by(username=data.get('username'))).one_or_none()
    if user:
        message = 'User with this username already exist, please use another username.'
        return error_response(message)

    user = User(**data)
    user.save()
    token = generate_token(user.id)
    return jsonify({'jwt_token': token}), 201


@user_api.route('/login', methods=['POST'])
def login():
    """User Login Function"""
    password = request.json.get('password')
    email = request.json.get('email')
    username = request.json.get('username')
    if not password or (not email and not username):
        return error_response('You need provide username or email and password to sign in.')
    user = None
    if email:
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if not user:
            return error_response('User with this email is not found.')
    elif username:
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        if not user:
            return error_response('User with this username is not found.')
    if not user or not user.check_hash(password):
        return error_response('Invalid credentials')
    try:
        token = generate_token(user.id)
    except Exception:
        return error_response('Error in generating user token')

    return jsonify({'jwt_token': token}), 200


@user_api.route('/', methods=['GET'])
@auth_required
def get_all_users():
    """Get all users"""
    response = pagination(request, db.select(User), user_schema)
    return jsonify(response), 200


@user_api.route('/<int:user_id>', methods=['GET'])
@auth_required
def get_user(user_id):
    """Get one single user"""
    user = db.session.get(User, user_id)
    if not user:
        return error_response('User not found', code=404)

    data = user_schema.dump(user)
    return jsonify(data), 200


@user_api.route('/me', methods=['GET'])
@auth_required
def get_me():
    """Get my user"""
    user = db.session.get(User, g.user.get('id'))
    data = user_schema.dump(user)
    return jsonify(data), 200
