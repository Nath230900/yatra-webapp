# tests/test_integration.py

from app import db
from models import Destination, User, Review
from werkzeug.security import generate_password_hash


def test_register_login_create_review_flow(app, client):
    """
    FULL INTEGRATION FLOW:
    1. Create a destination in the test DB
    2. Register a user via /register
    3. Log in via /login
    4. Post a review on /destinations/<id>
    5. Verify the review exists in the DB
    """

    # 1. Create a destination directly in the test database
with app.app_context():
    dest = Destination(
        name="Test Destination",
        region="Test Region",
        category="Test Category",
        description="Some description",
        latitude=27.0,
        longitude=85.0,
        image_url="test.jpg",   # 👈 use a dummy filename, NOT None
    )
    db.session.add(dest)
    db.session.commit()
    dest_id = dest.id


    # 2. Register a new user via the normal register route
    # NOTE: your form fields are: name, email, password
    resp = client.post(
        "/register",
        data={
            "name": "Integration User",
            "email": "integration@example.com",
            "password": "secret123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # 3. Log in with that user
    resp = client.post(
        "/login",
        data={"email": "integration@example.com", "password": "secret123"},
        follow_redirects=True,
    )
    # If login fails, later POST to /destinations/<id> will also fail,
    # but we still expect a 200 here.
    assert resp.status_code == 200

    # 4. Post a review on that destination (route is @login_required)
    resp = client.post(
        f"/destinations/{dest_id}",
        data={"rating": "5", "comment": "Amazing integration test review!"},
        follow_redirects=True,
    )
    # If user was not logged in, this would redirect to /login or give 4xx
    assert resp.status_code == 200

    # 5. Verify the review exists in the database
    with app.app_context():
        review = Review.query.filter_by(
            comment="Amazing integration test review!"
        ).first()

        assert review is not None, "Review was not saved to DB"
        assert review.destination_id == dest_id
        assert review.rating == 5


def test_admin_access_protection(app, client):
    """
    Integration test for admin-only pages:
    - non-logged user gets redirected or denied
    - normal user gets 403
    - admin user gets 200
    """

    # A. Non-logged-in user: should NOT be able to access admin page
    resp = client.get("/admin/destinations", follow_redirects=False)
    # Depending on your setup, this may be a redirect (302) or 401/403
    assert resp.status_code in (302, 401, 403)

    # B. Create normal and admin users directly in the DB
    with app.app_context():
        normal_user = User(
            name="Normal User",
            email="normal@example.com",
            password_hash=generate_password_hash("pass123"),
            is_admin=False,
        )
        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
        )
        db.session.add_all([normal_user, admin_user])
        db.session.commit()

    # C. Log in as normal user → should get 403 on admin page
    resp = client.post(
        "/login",
        data={"email": "normal@example.com", "password": "pass123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    resp = client.get("/admin/destinations")
    assert resp.status_code == 403

    # D. Log out normal user
    client.get("/logout", follow_redirects=True)

    # E. Log in as admin user → should get 200 on admin page
    resp = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    resp = client.get("/admin/destinations", follow_redirects=False)
    assert resp.status_code == 200
    # Optional: check that the page looks like the admin page
    html = resp.get_data(as_text=True)
    assert "Admin: Destinations" in html
