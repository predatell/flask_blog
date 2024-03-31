import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from flask_bcrypt import Bcrypt
from marshmallow import fields, Schema


class Base(DeclarativeBase):
    pass


bcrypt = Bcrypt()
db = SQLAlchemy(model_class=Base)

Base.query = db.session.query_property()


class BaseMixin(object):
    created_at = Column(DateTime)

    def __init__(self, **kwargs):
        self.created_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            if key == 'password':
                self.password = self.generate_hash(data.get('password'))
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class BlogPost(BaseMixin, Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # comments = relationship('Comment', backref='blog_posts', lazy=True)

    def __init__(self, title=None, content=None, author_id=None):
        self.title = title
        self.content = content
        self.author_id = author_id
        super(BlogPost, self).__init__()

    def __repr__(self):
        return f'<Post {self.title!r}>'


class BlogPostSchema(Schema):
    """Blogpost Schema"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    author_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)


class Comment(BaseMixin, Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('blog_posts.id'), nullable=False)

    def __init__(self, content=None, post_id=None, author_id=None):
        self.content = content
        self.post_id = post_id
        self.author_id = author_id
        super(Comment, self).__init__()

    def __repr__(self):
        return f'<Comment {self.id!r}>'


class CommentSchema(Schema):
    """Comment Schema"""
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    author_id = fields.Int(required=True)
    post_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)


class User(BaseMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(128), nullable=True)
    # blog_posts = relationship('BlogpostModel', backref='users', lazy=True)
    # comments = relationship('Comment', backref='users', lazy=True)

    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password_hash = self.generate_hash(password)
        super(User, self).__init__()

    def __repr__(self):
        return f'<User {self.username!r}>'

    def generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10)

    def check_hash(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class UserSchema(Schema):
    """User Schema"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)
    # blog_posts = fields.Nested(BlogPostSchema, many=True)
