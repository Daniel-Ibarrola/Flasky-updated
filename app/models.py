import datetime
import hashlib
import bleach
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous.exc import BadSignature
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from . import login_manager


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE_ARTICLES = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            "User": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE_ARTICLES],
            "Moderator": [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE_ARTICLES, Permission.MODERATE],
            "Administrator": [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE_ARTICLES, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = "User"
        for role_name in roles.keys():
            role_ = Role.query.filter_by(name=role_name).first()
            if role_ is None:
                role_ = Role(name=role_name)
            role_.reset_permissions()
            for perm in roles[role_name]:
                role_.add_permission(perm)
            role_.default = (role_.name == default_role)
            db.session.add(role_)
        db.session.commit()

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None and self.email == current_app.config["FLASKY_ADMIN"]:
            self.role = Role.query.filter_by(name="Administrator").first()
        elif self.role is None:
            self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        return serializer.dumps({"confirm": self.id})

    def confirm(self, token, expiration=3600):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, max_age=expiration)
        except BadSignature:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        return serializer.dumps({"reset": self.id})

    @staticmethod
    def reset_password(token, new_password, expiration=3600):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, max_age=expiration)
        except BadSignature:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        return serializer.dumps({"change_email": self.id, "new_email": new_email})

    def change_email(self, token, expiration=3600):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, max_age=expiration)
        except BadSignature:
            return False

        if data.get("change_email") != self.id:
            return False

        new_email = data.get("new_email")
        if new_email is None:
            return False
        # Check if new email already exists
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode("utf-8")).hexdigest()

    def gravatar(self, size=100, default="identicon", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://gravatar.com/avatar"

        if self.avatar_hash is None:
            hash_ = self.gravatar_hash()
        else:
            hash_ = self.avatar_hash

        return f"{url}/{hash_}?s={size}&d={default}&r={rating}"

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)

    def unfollow(self, user):
        follower = self.followed.filter_by(followed_id=user.id).first()
        if follower:
            db.session.delete(follower)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            "a", "abbr", "acronym", "b", "blockquote", "code",
            "em", "i", "li", "ol", "pre", "strong", "ul", "h1",
            "h2", "h3", "p"
        ]
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format="html"),
                         tags=allowed_tags, strip=True),
        )


db.event.listen(Post.body, "set", Post.on_changed_body)
