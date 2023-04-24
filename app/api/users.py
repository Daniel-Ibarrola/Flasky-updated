from flask import current_app, jsonify, request
from . import api
from .paginate import paginate
from ..models import User, Post


@api.route("/users/<int:id>")
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route("/users/<int:id>/posts/")
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    posts, prev, next_page, total = paginate(
        user.posts.order_by(Post.timestamp.asc()),
        page, current_app.config["FLASKY_POSTS_PER_PAGE"], "api.get_posts"
    )
    return jsonify({
        "posts": [p.to_json() for p in posts],
        "prev": prev,
        "next": next_page,
        "count": total
    })


@api.route("/users/<int:id>/timeline/")
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    posts, prev, next_page, total = paginate(
        user.followed_posts.order_by(Post.timestamp.asc()),
        page, current_app.config["FLASKY_POSTS_PER_PAGE"], "api.get_posts"
    )
    return jsonify({
        "posts": [p.to_json() for p in posts],
        "prev": prev,
        "next": next_page,
        "count": total
    })
