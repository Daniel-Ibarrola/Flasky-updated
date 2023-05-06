from app.models import User
import re


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Stranger" in response.get_data(as_text=True)


def test_register_and_login(client):
    # Register a new account
    response = client.post("/auth/register", data={
        "email": "john@example.com",
        "username": "john",
        "password": "cat",
        "password2": "cat",
    })
    assert response.status_code == 302

    # Log in with the new account
    response = client.post("/auth/login", data={
        "email": "john@example.com",
        "password": "cat",
    }, follow_redirects=True)
    response_data =response.get_data(as_text=True)
    assert response.status_code == 200
    assert re.search("Hello,\s+john!", response_data)
    assert "You have not confirmed your account yet" in response_data

    # Send a confirmation token
    user = User.query.filter_by(email="john@example.com").first()
    token = user.generate_confirmation_token()
    response = client.get(f"/auth/confirm/{token}", follow_redirects=True)
    user.confirm(token)
    assert response.status_code == 200
    assert "You have confirmed your account" in response.get_data(as_text=True)

    # Log out
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "You have been logged out" in response.get_data(as_text=True)
