from selenium import webdriver
from flasky.app import create_app, db, fake
from flasky.app.models import User, Role


def setup_selenium_test():
    driver = webdriver.Firefox()
    driver.get("http://localhost:5000/")

    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()

    # create the application
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()

    # create the database and populate with some fake data
    db.create_all()
    Role.insert_roles()
    fake.users(10)
    fake.posts(10)

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

    return driver, app_context


def tear_down_selenium_test(driver, app_context):
    driver.quit()

    # destroy database
    db.drop_all()
    db.session.remove()

    # remove application context
    app_context.pop()
