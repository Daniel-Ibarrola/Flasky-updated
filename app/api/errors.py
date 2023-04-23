from flask import jsonify, request, render_template
from ..main import main
from ..models import ValidationError
from . import api


@main.app_error_handler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template("404.html")


@main.app_error_handler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": "internal server error"})
        response.status_code = 404
        return response
    return render_template("500.html")


def bad_request(message):
    response = jsonify({"error": "bad_request", "message": message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({"error": "unauthorized", "message": message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
