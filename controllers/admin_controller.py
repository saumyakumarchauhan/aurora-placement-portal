from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity 
from extensions import db
from models.models import User, StudentProfile, CompanyProfile, PlacementDrive, Application
from extensions import cache

admin_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

# FETCH ALL DASHBOARD DATA
@admin_bp.route("/data", methods=["GET"])
@jwt_required()
def get_dashboard_data():
    if not is_admin():
        return jsonify({"error": "Unauthorized access"}), 403

    reg_companies = CompanyProfile.query.filter_by(approval_status='Approved').all()
    registered_companies = [{"id": c.user_id, "name": c.company_name} for c in reg_companies]

    pending_companies = CompanyProfile.query.filter_by(approval_status='Pending').all()
    company_applications = [{"id": c.user_id, "name": c.company_name} for c in pending_companies]

    students = StudentProfile.query.all()
    registered_students = [{"id": s.user_id, "name": s.full_name} for s in students]

    ongoing_drives_query = db.session.query(PlacementDrive, CompanyProfile)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(PlacementDrive.status.in_(['Pending', 'Approved'])).all()

    ongoing_drives = []
    for i, (drive, company) in enumerate(ongoing_drives_query):
        ongoing_drives.append({
            "id": drive.id,
            "srNo": f"{i+1}.",
            "name": drive.job_title,
            "company": company.company_name, 
            "status": drive.status
        })

    apps_query = db.session.query(Application, StudentProfile, PlacementDrive, CompanyProfile)\
        .join(StudentProfile, Application.student_id == StudentProfile.id)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id).all()
    
    student_applications = []
    for i, (app, student, drive, company) in enumerate(apps_query):
        student_applications.append({
            "id": app.id,
            "srNo": f"{i+1}.",
            "studentName": student.full_name,
            "drive": drive.job_title,
            "company": company.company_name
        })

    return jsonify({
        "registeredCompanies": registered_companies,
        "companyApplications": company_applications,
        "registeredStudents": registered_students,
        "ongoingDrives": ongoing_drives,
        "studentApplications": student_applications
    }), 200

# APPROVE COMPANY
@admin_bp.route("/approve_company/<int:user_id>", methods=["POST"])
@jwt_required()
def approve_company(user_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    if company:
        company.approval_status = "Approved"
        db.session.commit()
        return jsonify({"message": "Company approved successfully"}), 200
        
    return jsonify({"error": "Company not found"}), 404

# BLACKLIST USER
@admin_bp.route("/blacklist/<int:user_id>", methods=["POST"])
@jwt_required()
def blacklist_user(user_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        db.session.commit()
        return jsonify({"message": "User blacklisted"}), 200
        
    return jsonify({"error": "User not found"}), 404

# UN-BLACKLIST USER
@admin_bp.route("/activate/<int:user_id>", methods=["POST"])
@jwt_required()
def activate_user(user_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        return jsonify({"message": "User activated"}), 200
        
    return jsonify({"error": "User not found"}), 404

# GET SINGLE DRIVE DETAILS
@admin_bp.route("/drive/<int:drive_id>", methods=["GET"])
@jwt_required()
def get_drive_details(drive_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403

    drive = PlacementDrive.query.get(drive_id)
    if not drive: return jsonify({"error": "Drive not found"}), 404

    company = CompanyProfile.query.get(drive.company_id)

    return jsonify({
        "id": drive.id,
        "jobTitle": drive.job_title,
        "companyName": company.company_name,
        "salary": drive.package_salary or "Not Disclosed",
        "location": drive.location or "Not Specified",
        "description": drive.job_description,
        "status": drive.status,
        "departments": drive.eligible_departments,
        "cgpa": drive.min_cgpa,
        "year": drive.eligible_year,
        "deadline": drive.application_deadline.strftime("%Y-%m-%d")
    }), 200

# CANCEL/DELETE DRIVE
@admin_bp.route("/cancel_drive/<int:drive_id>", methods=["POST"])
@jwt_required()
def cancel_drive(drive_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.status = "Cancelled"
        db.session.commit()
        return jsonify({"message": "Drive cancelled successfully"}), 200
        
    return jsonify({"error": "Drive not found"}), 404   

# MARK DRIVE AS COMPLETE (ADMIN)
@admin_bp.route("/mark_drive_complete/<int:drive_id>", methods=["POST"])
@jwt_required()
def mark_drive_complete(drive_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.status = "Closed"
        db.session.commit()
        return jsonify({"message": "Drive marked as complete"}), 200
        
    return jsonify({"error": "Drive not found"}), 404

# APPROVE PLACEMENT DRIVE
@admin_bp.route("/approve_drive/<int:drive_id>", methods=["POST"])
@jwt_required()
def approve_drive(drive_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.status = "Approved"
        db.session.commit()
        return jsonify({"message": "Drive approved successfully"}), 200
        
    return jsonify({"error": "Drive not found"}), 404  

# GET SINGLE STUDENT APPLICATION
@admin_bp.route("/student_application/<int:app_id>", methods=["GET"])
@jwt_required()
def get_student_application(app_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403

    result = db.session.query(Application, StudentProfile, PlacementDrive, CompanyProfile)\
        .join(StudentProfile, Application.student_id == StudentProfile.id)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(Application.id == app_id).first()

    if not result:
        return jsonify({"error": "Application not found"}), 404

    app, student, drive, company = result

    return jsonify({
        "appId": app.id,
        "studentName": student.full_name,
        "department": student.department or "Not Specified",
        "jobTitle": drive.job_title,
        "companyName": company.company_name,
        "status": app.status,
        "resumeUrl": getattr(app, "resume_url", "#") 
    }), 200

@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60, key_prefix='admin_dashboard_stats')
def get_stats():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({"message": "Access denied"}), 403

    total_drives = PlacementDrive.query.count()
    total_apps = Application.query.count()
    total_selected = Application.query.filter_by(status="Selected").count()
    pending_drives = PlacementDrive.query.filter_by(status="Pending").count()

    return jsonify({
        "total_drives": total_drives,
        "total_apps": total_apps,
        "total_selected": total_selected,
        "pending_drives": pending_drives
    }), 200

@admin_bp.route("/trigger_jobs/<job_type>", methods=["POST"])
@jwt_required()
def trigger_jobs(job_type):
    from tasks import daily_deadline_reminder, monthly_activity_report
    
    if job_type == "sync":
        daily_deadline_reminder.delay()
        return jsonify({"message": "Data Sync & Reminders triggered successfully!"}), 200
        
    elif job_type == "reports":
        monthly_activity_report.delay()
        return jsonify({"message": "Monthly Activity Report generation started!"}), 200

    return jsonify({"error": f"Job type '{job_type}' not recognized"}), 400


# === NEW DATA FETCH ROUTES ===

@admin_bp.route("/all_drives", methods=["GET"])
@jwt_required()
def get_all_drives():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    drives_query = db.session.query(PlacementDrive, CompanyProfile).join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id).all()
    result = []
    for drive, comp in drives_query:
        result.append({
            "id": drive.id,
            "title": drive.job_title,
            "company": comp.company_name,
            "status": drive.status,
            "deadline": drive.application_deadline.strftime("%Y-%m-%d")
        })
    return jsonify(result), 200

@admin_bp.route("/all_students", methods=["GET"])
@jwt_required()
def get_all_students():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    students_query = db.session.query(StudentProfile, User).join(User, StudentProfile.user_id == User.id).all()
    result = []
    for stu, user in students_query:
        result.append({
            "id": stu.user_id,
            "name": stu.full_name,
            "department": stu.department,
            "cgpa": stu.cgpa,
            "is_active": user.is_active
        })
    return jsonify(result), 200

@admin_bp.route("/all_companies", methods=["GET"])
@jwt_required()
def get_all_companies():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    companies_query = db.session.query(CompanyProfile, User).join(User, CompanyProfile.user_id == User.id).all()
    result = []
    for comp, user in companies_query:
        result.append({
            "id": comp.user_id,
            "name": comp.company_name,
            "contact": comp.hr_contact,
            "approval_status": comp.approval_status,
            "is_active": user.is_active
        })
    return jsonify(result), 200