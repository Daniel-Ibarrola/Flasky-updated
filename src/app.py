import os
from flask_migrate import Migrate
from flasky.app import create_app, db
from flasky.app.models import Comment, User, Post, Role

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Post=Post, Comment=Comment)
