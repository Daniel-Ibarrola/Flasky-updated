from flask import current_app, g, jsonify, request, url_for

from flasky.app import db
from flasky.app.models import Comment, Post, Permission
from flasky.app.api import api
from flasky.app.api.errors import forbidden
from flasky.app.api.decorators import permission_required
from flasky.app.api.paginate import paginate


@api.route("/posts/")
def get_posts():
    page = request.args.get("page", 1, type=int)
    posts, prev, next_page, total = paginate(
        Post.query, page, current_app.config["FLASKY_POSTS_PER_PAGE"], "api.get_posts"
    )
    return jsonify({
        "posts": [p.to_json() for p in posts],
        "prev": prev,
        "next": next_page,
        "count": total
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
    page = request.args.get("page", 1, type=int)
    comments, prev, next_page, total = paginate(
        post.comments.order_by(Comment.timestamp.asc()),
        page, current_app.config["FLASKY_COMMENTS_PER_PAGE"], "api.get_comments"
    )
    return jsonify({
        "comments": [c.to_json() for c in comments],
        "prev": prev,
        "next": next_page,
        "count": total
    })


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
