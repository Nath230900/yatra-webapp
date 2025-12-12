from app import app, db
from models import User

with app.app_context():
    u = User.query.filter_by(email="nathmahesh207@gmail.com").first()
    print("User:", u)
    if u:
        u.is_admin = True
        db.session.commit()
        print("Updated is_admin:", u.is_admin)
    else:
        print("No user with that email")
