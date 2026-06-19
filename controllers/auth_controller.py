from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime

from extensions import db
from models.models import (
    User,
    StudentProfile,
    CompanyProfile,
    ActivityLog
)

auth_bp = Blueprint("auth", __name__)

# SIGNUP ROUTE (Handles both GET and POST)
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not email or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    if role not in ["student", "company"]:
        return jsonify({"error": "Invalid role"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        is_active=True,
        deactivated_reason=""
    )

    db.session.add(new_user)
    db.session.flush() 

    if role == "student":
        student_profile = StudentProfile(
            user_id=new_user.id,
            full_name=data.get("full_name"),
            department=data.get("department"),
            cgpa=data.get("cgpa"),
            year_of_study=data.get("year_of_study")
        )
        db.session.add(student_profile)

    elif role == "company":
        company_profile = CompanyProfile(
            user_id=new_user.id,
            company_name=data.get("company_name"),
            hr_contact=data.get("hr_contact"),
            website=data.get("website"),
            description=data.get("description"),
            approval_status="Pending"
        )
        db.session.add(company_profile)

    log = ActivityLog(user_id=new_user.id, action=f"{role} account created")
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Account created successfully"}), 201


# LOGIN ROUTE (Handles both GET and POST)
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account deactivated", "reason": user.deactivated_reason}), 403   

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id), # Cast to string here!
        additional_claims={"role": user.role, "email": user.email}
    )
    log = ActivityLog(user_id=user.id, action="User logged in")
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": user.role
    }), 200


# LOGOUT (CLIENT SIDE JWT REMOVAL)
@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route("/student_dashboard", methods=["GET"])
def student_dashboard():
    return render_template("student_dash.html")

# DASHBOARD ROUTES
@auth_bp.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    return render_template("admin_dashboard.html")

@auth_bp.route("/company_dashboard", methods=["GET"])
def company_dashboard():
    return render_template("company_dashboard.html")

@auth_bp.route("/company_create_drive", methods=["GET"])
def company_create_drive():
    return render_template("company_create_drive.html")

@auth_bp.route("/admin_view_drive_details", methods=["GET"])
def admin_view_drive_details():
    return render_template("admin_view_drive_details.html") 

@auth_bp.route("/student_view_company_details", methods=["GET"])
def student_view_company_details():
    return render_template("student_view_company_details.html")

@auth_bp.route("/student_view_drive_details", methods=["GET"])
def student_view_drive_details():
    return render_template("student_view_drive_details.html")

@auth_bp.route("/student_app_history", methods=["GET"])
def student_app_history():
    return render_template("student_app_history.html")

@auth_bp.route("/company_view_drive_details", methods=["GET"])
def company_view_drive_details():
    return render_template("company_view_drive_details.html")

@auth_bp.route("/company_view_student_details", methods=["GET"])
def company_view_student_details():
    return render_template("company_view_student_details.html")

@auth_bp.route("/admin_view_student_application", methods=["GET"])
def admin_view_student_application():
    return render_template("admin_view_student_application.html")

@auth_bp.route('/student_profile', methods=["GET"])
def render_student_profile():
    return render_template('student_profile.html')

# === NEW ADMIN ROUTES ===

@auth_bp.route("/admin_all_drives", methods=["GET"])
def admin_all_drives():
    return render_template("admin_all_drives.html")

@auth_bp.route("/admin_students", methods=["GET"])
def admin_students():
    return render_template("admin_students.html")

@auth_bp.route("/admin_companies", methods=["GET"])
def admin_companies():
    return render_template("admin_companies.html")