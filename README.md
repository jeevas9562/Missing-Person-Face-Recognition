<<<<<<< HEAD
# 🔍 Missing Person Face Recognition System

A Flask-based web application that helps detect and identify missing persons using facial recognition. It allows admins to upload missing person data, users to upload unknown face images, and uses real-time alerts for recognition updates.

---

## 🧠 Features

- 🧑‍💻 **User Authentication** (Admin & General User)
- 🧾 **Upload Missing Persons** with name, age, and contact info
- 🖼️ **Face Recognition** using `face_recognition` library
- 📡 **Real-Time Alerts** using Socket.IO for re-appearances
- 📊 **Admin Dashboard** to manage users, alerts, and logs
- 🔒 **Secure Password Hashing** via Werkzeug

---

## 🛠️ Technologies Used

| Tech             | Description                  |
|------------------|------------------------------|
| Python           | Backend language             |
| Flask            | Web framework                |
| SQLAlchemy       | ORM for database interaction |
| PostgreSQL       | Primary database             |
| face_recognition | Face encoding & matching     |
| Flask-Login      | User session management      |
| Flask-Migrate    | Database migrations          |
| Socket.IO        | Real-time communication      |
| HTML/CSS         | Frontend templating          |

---

## 📦 Project Structure
face_recognition_project/
├── app.py
├── database/
│ ├── db.py
│ └── models.py
├── templates/
│ └── *.html
├── static/
│ ├── uploads/
│ └── detections/
├── migrations/
├── requirements.txt
├── .env (not included)
├── .gitignore
└── README.md

---

## 👥 Team Members

This project was developed as part of our final year B.Tech Computer Science academic project by the following team members:

- Jeeva S
- Anjana A. K
- Meera Mohan
- Nanda Prasad

We collaboratively worked on the design, development, and deployment of this face recognition-based missing person identification system.

---
=======
# Missing-Person-Face-Recognition
A complete missing person identification system using Flask, face recognition, and PostgreSQL. Upload and recognize faces, log detections, enforce relational data checks, send real-time alerts, and manage users through a secure admin panel with a clean UI.
>>>>>>> 1a380f3c479adb6261659bcd1bf9a095715a2f3a
