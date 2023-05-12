from flask import jsonify, render_template, request
from flasky.app.main import main


def handle_error(message, status_code, template):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": message})
        response.status_code = status_code
        return response
    return render_template(template)


@main.app_errorhandler(403)
def forbidden(e):
    return handle_error("forbidden", 403, "403.html")


@main.app_errorhandler(404)
def page_not_found(e):
    return handle_error("not found", 404, "404.html")


@main.app_errorhandler(500)
def internal_server_error(e):
    return handle_error("internal server error", 500, "500.html")
