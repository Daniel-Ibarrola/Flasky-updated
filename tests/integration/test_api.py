from base64 import b64encode
import json
from app import db
from app.models import User, Role


def get_api_headers(username, password):
    return {
        "Authorization":
            "Basic " + b64encode((username + ":" + password).encode("Utf-8")).decode("utf-8"),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def test_no_auth(client_no_cookies):
    response = client_no_cookies.get("/api/v1/posts/",
                                     content_type="application/json")
    assert response.status_code == 401


def test_posts(client_no_cookies):
    # Add a user
    role = Role.query.filter_by(name="User").first()
    assert role is not None

    email = "john@example.com"
    password = "cat"
    user = User(email=email,
                password=password,
                confirmed=True
                )
    db.session.add(user)
    db.session.commit()

    # Write a post
    response = client_no_cookies.post(
        "/api/v1/posts/",
        headers=get_api_headers(email, password),
        data=json.dumps({"body": "body of the *blog* post"})
    )
    assert response.status_code == 201
    url = response.headers.get("Location")
    assert url is not None

    # Get the new post
    response = client_no_cookies.get(
        url,
        headers=get_api_headers(email, password)
    )
    assert response.status_code == 200
    json_response = json.loads(response.get_data(as_text=True))
    assert json_response["body_html"] == "<p>body of the <em>blog</em> post</p>"
