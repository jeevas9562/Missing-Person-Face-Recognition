from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory
import os
import face_recognition
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database.db import db, init_db
from database.models import MissingPerson, RecognizedFace, User,Alert
import cv2
from flask import abort
from flask import jsonify  
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production

# Initialize Flask-SocketIO
socketio = SocketIO(app)


# ✅ Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/face_recognition_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize Database
init_db(app)
migrate = Migrate(app, db)  # Add Flask-Migrate

# ✅ Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Ensure folders for storing images
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
DETECTION_FOLDER = os.path.join(app.root_path, 'static/detections')
for folder in [UPLOAD_FOLDER, DETECTION_FOLDER]:
    os.makedirs(folder, exist_ok=True)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DETECTION_FOLDER'] = "static/detections"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# ✅ Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================== ROUTES ==================

@app.route('/')
def home():
    return render_template('entry.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/front_page')
def front_page():
    return render_template('front_page.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/view_missing')
@login_required
def view_missing():
    persons = MissingPerson.query.all()
    return render_template('view_missing.html', persons=persons)

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/recognized_faces')
@login_required
def recognized_faces():
    faces = RecognizedFace.query.order_by(RecognizedFace.timestamp.desc()).all()
    return render_template('recognized_faces.html', recognized_faces=faces)


@app.route('/admin')
@login_required
def admin_dashboard():
    if not getattr(current_user, 'is_admin', False):
        flash("Access Denied! Only admins can access this page.", "danger")  # Flash message
        return redirect(url_for('admin_login'))  # Redirect instead of abort(403)

    users = User.query.all()
    persons = MissingPerson.query.all()
    recognized_faces = RecognizedFace.query.order_by(RecognizedFace.timestamp.desc()).all()
    alerts = Alert.query.order_by(Alert.alert_time.desc()).all()  # ✅ Fetch alerts

    return render_template('admin_dashboard.html', users=users, persons=persons,recognized_faces=recognized_faces, alerts=alerts)  # ✅ Pass alerts to template

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        contact_info = request.form['contact_info']
        file = request.files['file']

        # ✅ Check for required fields
        if not name or not age or not contact_info:
            flash("⚠️ All fields are required!", "upload-danger")
            return redirect(url_for('upload'))

        # ✅ File type validation
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # ✅ Get face encoding of uploaded image
            try:
                new_image = face_recognition.load_image_file(file_path)
                new_encoding_list = face_recognition.face_encodings(new_image)
                if not new_encoding_list:
                    flash("⚠️ No face detected in the uploaded image. Please try a clearer image.", "upload-danger")
                    return redirect(url_for('upload'))
                new_encoding = new_encoding_list[0]
            except Exception as e:
                flash(f"❌ Face encoding failed: {str(e)}", "upload-danger")
                return redirect(url_for('upload'))

            # ✅ Check for duplicates based on face encoding
            existing_persons = MissingPerson.query.all()
            for person in existing_persons:
                try:
                    existing_path = os.path.join(app.root_path, 'static', person.image_path)
                    existing_image = face_recognition.load_image_file(existing_path)
                    existing_encodings = face_recognition.face_encodings(existing_image)
                    if existing_encodings:
                        match = face_recognition.compare_faces([existing_encodings[0]], new_encoding)[0]
                        if match:
                            flash(f"🔁 Notice: This person already exists in the system as <strong>{person.name}</strong>.", "upload-warning")
                            return redirect(url_for('upload'))
                except Exception:
                    continue  # Skip problematic images

            # ✅ Save new missing person if no duplicate
            person = MissingPerson(
                name=name,
                age=age,
                contact_info=contact_info,
                image_path=f"uploads/{filename}"
            )
            db.session.add(person)
            db.session.commit()

            flash(f"✅ Missing person <strong>{name}</strong> added successfully!", "upload-success")

            # ✅ Redirect based on user role
            if getattr(current_user, 'is_admin', False):
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))

        else:
            flash("❌ Invalid file type! Only images are allowed.", "upload-danger")

    return render_template('upload.html')


# ✅ Upload and Recognize Faces
@app.route('/upload_unknown', methods=['GET', 'POST'])
def upload_unknown():
    if request.method == 'GET':
        return render_template('upload_unknown.html')

    if 'file' not in request.files:
        return jsonify({"message": "No file part in request", "status": "failed"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"message": "Invalid file or no file selected", "status": "failed"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['DETECTION_FOLDER'], filename)
    file.save(file_path)

    relative_path = f"static/detections/{filename}"

    try:
        recognized_name = recognize_face(file_path)

        if recognized_name:
            missing_person = MissingPerson.query.filter_by(name=recognized_name).first()
            if missing_person:
                # ✅ Check if person already recognized
                already_recognized = RecognizedFace.query.filter_by(person_id=missing_person.id).first()
                if already_recognized:
                    # 🔁 Emit reappearance alert
                    alert_message = f"⚠️ ALERT: Repeat detection of {recognized_name}"
                    socketio.emit('new_alert', {'message': alert_message})

                    return jsonify({
                        "message": f"✅ {recognized_name} was already detected before.",
                        "image_path": already_recognized.image_path,
                        "status": "duplicate"
                    })

                # ✅ Save new recognition
                recognized_face = RecognizedFace(
                    person_id=missing_person.id,
                    person_name=recognized_name,
                    image_path=relative_path
                )
                db.session.add(recognized_face)
                db.session.commit()

                # 🚨 Emit new recognition alert
                alert_message = f"🚨 ALERT: {recognized_name} detected!"
                socketio.emit('new_alert', {'message': alert_message})

                return jsonify({
                    "message": f"Recognized: {recognized_name}",
                    "image_path": relative_path,
                    "status": "success"
                })
            else:
                return jsonify({"message": "Face not recognized in database.", "status": "failed"})

        return jsonify({"message": "No matching face found.", "status": "failed"})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "failed"}), 500


def recognize_face(image_path):
    known_faces = {}
    missing_persons = MissingPerson.query.all()
    for person in missing_persons:
        image = face_recognition.load_image_file(os.path.join(app.root_path, 'static', person.image_path))
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces[person.name] = encodings[0]
    
    unknown_image = face_recognition.load_image_file(image_path)
    unknown_encodings = face_recognition.face_encodings(unknown_image)
    
    if not unknown_encodings:
        return None
    
    for name, known_encoding in known_faces.items():
        matches = face_recognition.compare_faces([known_encoding], unknown_encodings[0])
        if matches[0]:
            return name
    
    return None

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid Username or Password", "danger")
            return redirect(url_for('error'))  # ✅ Redirect to login page instead of front_page.html

        login_user(user)
        flash("Login Successful!", "success")

        # ✅ Redirect based on user role
        return redirect(url_for('admin_dashboard') if getattr(user, 'is_admin', False) else url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfully!", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash, is_admin=False)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('front_page'))

    return render_template('register.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin_user = User.query.filter_by(username=username, is_admin=True).first()

        if admin_user and check_password_hash(admin_user.password_hash, password):
            login_user(admin_user)
            flash("Admin Login Successful!", "success")
            return redirect(url_for('admin_dashboard'))  # Redirect to Admin Dashboard
        else:
            flash("Invalid Admin Credentials", "danger")

    return render_template('admin_login.html')

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for('create_admin'))

        admin_user = User(username=username, password_hash=generate_password_hash(password), is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        flash("Admin created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('create_admin.html')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get(user_id)

    if not user_to_delete:
        flash("User not found.", "error")
        return redirect(url_for('admin_dashboard'))

    db.session.delete(user_to_delete)
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

from sqlalchemy.exc import IntegrityError

@app.route('/delete_missing_person/<int:person_id>', methods=['POST'])
def delete_missing_person(person_id):
    person = MissingPerson.query.get_or_404(person_id)
    
    try:
        db.session.delete(person)
        db.session.commit()
        flash("✅ Missing person deleted successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    except IntegrityError:
        db.session.rollback()
        # Render the beautiful error page instead of flashing
        return render_template('delete_error.html')


@app.route('/delete_recognized_person/<int:person_id>', methods=['POST'])
@login_required
def delete_recognized_person(person_id):
    recognized_person = RecognizedFace.query.get_or_404(person_id)
    db.session.delete(recognized_person)
    db.session.commit()
    flash("Recognized person deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app, debug=True)
