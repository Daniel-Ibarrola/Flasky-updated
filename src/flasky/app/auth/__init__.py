from flask import Blueprint

auth = Blueprint("auth", __name__)

from flasky.app.auth import views
