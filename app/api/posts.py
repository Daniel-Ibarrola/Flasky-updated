from flask import g, jsonify, request, url_for
from . import api
from .. import db
from .errors import forbidden
from .decorators import permission_required
from ..models import Comment, Post, Permission


@api.route("/posts/")
def get_posts():
    posts = Post.query.all()
    return jsonify({
        "posts": [p.to_json() for p in posts]
    })


@api.route("/posts/<int:id>")
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route("/posts/", methods=["POST"])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return (
        jsonify(post.to_json()), 201,
        {"Location": url_for("api.get_post", id=post.id)}
    )


@api.route("/posts/<int:id>", methods=["PUT"])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden("Insufficent permissions")
    post.body = request.json.get("body", "")
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route("/posts/<int:id>/comments/")
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    comments = post.comments.all()
    return {
        "comments": [c.to_json() for c in comments]
    }


@api.route("/posts/<int:id>/comments/", methods=["POST"])
@permission_required(Permission.COMMENT)
def new_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author_id = g.current_user.id
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return (
        jsonify(comment.to_json()),
        201,
        {"Location": url_for("api.get_comment", id=comment.id)}
    )
