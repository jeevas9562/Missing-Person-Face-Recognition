from database.db import db
from database.models import User
from werkzeug.security import generate_password_hash
from app import app  # Import your Flask app

# Create an application context
with app.app_context():
    # Create an admin user
    admin_user = User(username="admin", password_hash=generate_password_hash("admin123"), is_admin=True)

    # Add to database
    db.session.add(admin_user)
    db.session.commit()

    print("Admin user created successfully!")
