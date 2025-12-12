from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from config import Config
from models import db, User, Destination, Itinerary, ItineraryItem, Review
from flask import abort, flash

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = os.path.join("static", "img")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.cli.command("init-db")
def init_db_command():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
    print("Initialized the database.")


@app.route("/")
def index():
    from models import Destination
    featured = Destination.query.order_by(Destination.id).limit(6).all()
    print("HOME featured count:", len(featured))
    return render_template("index.html", destinations=featured)



@app.route("/destinations")
def destinations():
    region = request.args.get("region", "")
    category = request.args.get("category", "")
    q = request.args.get("q", "")

    query = Destination.query
    if region:
        query = query.filter(Destination.region.ilike(f"%{region}%"))
    if category:
        query = query.filter(Destination.category.ilike(f"%{category}%"))
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Destination.name.ilike(like)) |
            (Destination.description.ilike(like)) |
            (Destination.region.ilike(like))
        )

    all_destinations = query.order_by(Destination.region, Destination.name).all()
    return render_template("destinations.html", destinations=all_destinations, q=q)



@app.route("/destinations/<int:dest_id>", methods=["GET", "POST"])
def destination_detail(dest_id):
    destination = Destination.query.get_or_404(dest_id)

    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Please log in to add a review", "warning")
            return redirect(url_for("login"))

        rating = int(request.form.get("rating", 5))
        comment = request.form.get("comment", "").strip()

        if rating < 1 or rating > 5:
            flash("Rating must be between 1 and 5.", "danger")
        else:
            review = Review(
                user_id=current_user.id,
                destination_id=destination.id,
                rating=rating,
                comment=comment
            )
            db.session.add(review)
            db.session.commit()
            flash("Review submitted.", "success")
            return redirect(url_for("destination_detail", dest_id=dest_id))

    reviews = Review.query.filter_by(destination_id=dest_id).order_by(Review.created_at.desc()).all()
    return render_template("destination_detail.html", destination=destination, reviews=reviews)

@app.route("/reviews/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Only the review owner or an admin can delete
    if review.user_id != current_user.id and not getattr(current_user, "is_admin", False):
        abort(403)

    dest_id = review.destination_id
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "info")
    return redirect(url_for("destination_detail", dest_id=dest_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@app.route("/itineraries", methods=["GET", "POST"])
@login_required
def itineraries():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None

        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("itineraries"))

        it = Itinerary(
            user_id=current_user.id,
            title=title,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None,
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        )
        db.session.add(it)
        db.session.commit()
        flash("Itinerary created.", "success")
        return redirect(url_for("itineraries"))

    user_itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    all_destinations = Destination.query.order_by(Destination.name).all()
    return render_template("itinerary.html", itineraries=user_itineraries, destinations=all_destinations)


@app.route("/itineraries/<int:it_id>/add_item", methods=["POST"])
@login_required
def add_itinerary_item(it_id):
    itinerary = Itinerary.query.get_or_404(it_id)
    if itinerary.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("itineraries"))

    day_number = int(request.form.get("day_number", 1))
    destination_id = int(request.form.get("destination_id"))
    notes = request.form.get("notes", "")

    item = ItineraryItem(
        itinerary_id=itinerary.id,
        day_number=day_number,
        destination_id=destination_id,
        notes=notes
    )
    db.session.add(item)
    db.session.commit()
    flash("Day added to itinerary.", "success")
    return redirect(url_for("itineraries"))


@app.route("/itineraries/<int:it_id>/delete_item/<int:item_id>", methods=["POST"])
@login_required
def delete_itinerary_item(it_id, item_id):
    itinerary = Itinerary.query.get_or_404(it_id)
    if itinerary.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("itineraries"))

    item = ItineraryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Day removed.", "info")
    return redirect(url_for("itineraries"))

@app.route("/admin/destinations")
@login_required
def admin_destinations():
    admin_required()
    # VERY SIMPLE "admin": all logged-in users see this
    all_destinations = Destination.query.order_by(Destination.id).all()
    return render_template("admin_destinations.html", destinations=all_destinations)


@app.route("/admin/destinations/<int:dest_id>/images", methods=["GET", "POST"])
@login_required
def admin_destination_images(dest_id):
    admin_required()
    destination = Destination.query.get_or_404(dest_id)

    # 🚀 HANDLE UPLOAD
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)  # save physically

                from models import DestinationImage
                img = DestinationImage(destination_id=destination.id, filename=filename)
                db.session.add(img)
                db.session.commit()

                flash("Image uploaded successfully!", "success")
                return redirect(url_for("admin_destination_images", dest_id=dest_id))
            else:
                flash("Invalid file type.", "danger")
                return redirect(url_for("admin_destination_images", dest_id=dest_id))

    return render_template("admin_destination_images.html", destination=destination)


    if request.method == "POST":
        filename = request.form.get("filename", "").strip()
        if filename:
            from models import DestinationImage
            img = DestinationImage(destination_id=destination.id, filename=filename)
            db.session.add(img)
            db.session.commit()
            flash("Image added. Make sure file exists in static/img.", "success")
        else:
            flash("Filename cannot be empty.", "danger")
        return redirect(url_for("admin_destination_images", dest_id=dest_id))

    return render_template("admin_destination_images.html", destination=destination)

@app.route("/admin/destinations/<int:dest_id>/images/<int:img_id>/delete", methods=["POST"])
@login_required
def delete_destination_image(dest_id, img_id):
    from models import DestinationImage
    img = DestinationImage.query.get_or_404(img_id)
    admin_required()

    # 🧹 Remove file from static/img folder
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], img.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    # 🗑 Remove image record from DB
    db.session.delete(img)
    db.session.commit()

    flash("Image deleted.", "info")
    return redirect(url_for("admin_destination_images", dest_id=dest_id))

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

if __name__ == "__main__":
    app.run(debug=True)
