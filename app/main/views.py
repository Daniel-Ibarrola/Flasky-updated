from flask import render_template
from . import main
from ..models import User


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route("/user/<username>")
def user(username):
    user_ = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user_)
