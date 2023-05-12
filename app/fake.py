from random import randint
# from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import create_app, db
from .models import User, Post, Role


def clear_db(app):
    """ Clears all data from the database """
    with app.app_context():
        db.drop_all()
        db.session.remove()


def add_users(count=100):
    fake = Faker()
    ii = 0
    while ii < count:
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            password="password",
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date()
        )
        db.session.add(user)
        try:
            db.session.commit()
            ii += 1
        except:
            db.session.rollback()


def add_posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for ii in range(count):
        user = User.query.offset(randint(0, user_count - 1)).first()
        post = Post(body=fake.text(), timestamp=fake.past_date(), author=user)
        db.session.add(post)
    db.session.commit()


def add_admin():
    # add administrator user
    admin_role = Role.query.filter_by(permissions=0xff).first()
    admin = User(
        email="john@example.com",
        username="john",
        password="cat",
        role=admin_role,
        confirmed=True
    )
    db.session.add(admin)
    db.session.commit()


def add_followers():
    pass


def add_comments():
    pass


def main():
    """ Inserts fake data into the database.

        If the database already exists all data will be deleted.

        DO NOT use in production.

    """
    app = create_app("development")
    clear_db(app)

    with app.app_context():
        db.create_all()
        Role.insert_roles()

        add_users(100)
        add_posts(100)

        add_admin()


if __name__ == "__main__":
    main()
