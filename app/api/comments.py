from flask import current_app, jsonify, request
from . import api
from .paginate import paginate
from ..models import Comment


@api.route("/comments/")
def get_comments():
    page = request.args.get("page", 1, type=int)
    comments, prev, next_page, total = paginate(
        Comment.query, page, current_app.config["FLASKY_COMMENTS_PER_PAGE"], "api.get_comments"
    )
    return jsonify({
        "comments": [c.to_json() for c in comments],
        "prev": prev,
        "next": next_page,
        "count": total
    })


@api.route("/comments/<int:id>")
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
