# API for Blog with comments

## Installation
  - Export the required environment variables
    - `$ export BLOG_ENV_NAME=prod`
    - `$ export POSTGRES_PASSWORD=postgres`
    - `$ export POSTGRES_USER=postgres`
    - `$ export POSTGRES_DB=postgres`
    - `$ export JWT_SECRET_KEY=sdjfbhj63fd`

  - Build and start the app with:
    - `docker-compose build`
    - `docker-compose up flask_app`

## Description of API
  - POST /users/ - Create a new user (required token and fields: username, email, password)
  - GET /users/ - Get all registered users (required token)
  - GET /users/<user_id> - Get a user(required token)
  - GET /users/me - Get info about my account (required token)
  - POST /posts/ - Create a new blog post (required token and fields: title, content)
  - GET /posts/ - Get all blog post
  - GET /posts/<id> - Get a single blog post
  - PATCH /posts/<id> - Update a blog post (required token)
  - DELETE /posts/<id> - Delete a blog post (required token)
  - POST /comments/ - Create a new blog post (required token and fields: post_id, content)
  - GET /comments/ - Get all comments
  - GET /comments/<id> - Get a single comment
  - PATCH /comments/<id> - Update a comment (required token)
  - DELETE /comments/<id> - Delete a comment (required token)
  - GET /post-comments/<id> - Get a list of comments for one blog post
