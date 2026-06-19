from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db, cache
from models.models import StudentProfile, PlacementDrive, CompanyProfile, Application, User
import os
from werkzeug.utils import secure_filename

student_bp = Blueprint("student_api", __name__, url_prefix="/api/student")

def is_student():
    claims = get_jwt()
    return claims.get("role") == "student"


# FETCH DASHBOARD DATA

@student_bp.route("/data", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60, key_prefix='student_dashboard_data') # Caches for 60 seconds
def get_dashboard_data():
    if not is_student():
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = StudentProfile.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    # 1. Fetch Active Companies (Companies that have "Approved" drives)
    approved_drives = db.session.query(PlacementDrive, CompanyProfile)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(PlacementDrive.status == "Approved").all()

    # We use a dictionary to group them so a company only shows up ONCE
    active_companies_dict = {}
    for drive, company in approved_drives:
        if company.id not in active_companies_dict:
            active_companies_dict[company.id] = {
                "id": company.id,
                "name": company.company_name,
                "driveCount": 0
            }
        active_companies_dict[company.id]["driveCount"] += 1

    active_companies_data = list(active_companies_dict.values())

    # 2. Fetch My Applications (Keep your existing apps_query code here...)
    apps_query = db.session.query(Application, PlacementDrive, CompanyProfile)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(Application.student_id == student.id).all()

    my_applications_data = []
    for app, drive, company in apps_query:
        my_applications_data.append({
            "id": app.id,
            "driveName": drive.job_title,
            "company": company.company_name,
            "date": app.applied_on.strftime("%d/%m/%Y"),
            "status": app.status
        })

    # Return activeCompanies instead of activeDrives
    return jsonify({
        "studentName": student.full_name,
        "activeCompanies": active_companies_data, 
        "myApplications": my_applications_data
    }), 200


# APPLY FOR A DRIVE

@student_bp.route("/apply/<int:drive_id>", methods=["POST"])
@jwt_required()
def apply_for_drive(drive_id):
    if not is_student(): return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    drive = PlacementDrive.query.get(drive_id)

    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    # 1. Prevent Multiple Applications
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({"error": "You have already applied to this drive."}), 400

    # 2. CGPA Eligibility Validation
    if float(student.cgpa) < float(drive.min_cgpa):
        return jsonify({"error": f"Not eligible. Minimum CGPA required is {drive.min_cgpa}"}), 403
    
    
    student_branch = student.department.strip().upper() if student.department else ""
    allowed_branches_str = drive.eligible_departments.strip().upper() if drive.eligible_departments else ""

    # Agar requirement "ALL" nahi hai, tabhi check karo
    if allowed_branches_str != "ALL":
        # String ko comma se tod kar ek list bana lo: "CSE, ECE" -> ['CSE', 'ECE']
        allowed_list = [branch.strip() for branch in allowed_branches_str.split(",")]
        
        if student_branch not in allowed_list:
            return jsonify({"error": f"Not eligible. Open only to: {drive.eligible_departments}"}), 403

    # Grab the resume URL from the request
    data = request.get_json() or {}
    resume_url = data.get("resume_url", getattr(student, 'resume_link', ''))

    # Save the application
    new_app = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="Applied",
        resume_url=resume_url
    )
    db.session.add(new_app)
    db.session.commit()

    return jsonify({"message": "Successfully applied!"}), 201



# GET COMPANY DETAILS & ACTIVE DRIVES

@student_bp.route("/company/<int:company_id>", methods=["GET"])
@jwt_required()
def get_company_details(company_id):
    if not is_student(): return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = StudentProfile.query.filter_by(user_id=user_id).first()

    company = CompanyProfile.query.get(company_id)
    if not company: return jsonify({"error": "Company not found"}), 404

    # Fetch approved drives for this specific company
    approved_drives = PlacementDrive.query.filter_by(company_id=company.id, status="Approved").all()

    drives_data = []
    for drive in approved_drives:
        drives_data.append({
            "id": drive.id,
            "title": drive.job_title,
            "eligibility": f"{drive.eligible_departments}, CGPA: {drive.min_cgpa}+",
            "package": drive.package_salary or "Not Disclosed",
            "day": drive.application_deadline.strftime("%d"),
            "month": drive.application_deadline.strftime("%b")
        })

    return jsonify({
        "studentName": student.full_name,
        "company": {
            "name": company.company_name,
            "website": company.website or "No website provided",
            "description": company.description or "No description available.",
            "location": "India", # Placeholder (Not in DB schema)
            "size": "Verified",  # Placeholder 
            "industry": "Technology", # Placeholder
            "drives": drives_data
        }
    }), 200



# GET SINGLE DRIVE DETAILS

@student_bp.route("/drive/<int:drive_id>", methods=["GET"])
@jwt_required()
def get_drive_details(drive_id):
    if not is_student(): return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = StudentProfile.query.filter_by(user_id=user_id).first()

    drive = PlacementDrive.query.get(drive_id)
    if not drive: return jsonify({"error": "Drive not found"}), 404

    company = CompanyProfile.query.get(drive.company_id)

    # Check if the student has already applied to this drive
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    has_applied = True if existing_app else False

    return jsonify({
        "id": drive.id,
        "companyId": company.id,
        "companyName": company.company_name,
        "jobTitle": drive.job_title,
        "salary": drive.package_salary or "Not Disclosed",
        "location": drive.location or "Not Specified",
        "deadline": drive.application_deadline.strftime("%d %b %Y"),
        "description": drive.job_description,
        "requirements": [
            f"Eligible Departments: {drive.eligible_departments}",
            f"Minimum CGPA: {drive.min_cgpa}",
            f"Graduation Year: {drive.eligible_year}"
        ],
        "applied": has_applied
    }), 200


# GET APPLICATION HISTORY

@student_bp.route("/history", methods=["GET"])
@jwt_required()
def get_application_history():
    if not is_student(): return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = StudentProfile.query.filter_by(user_id=user_id).first()

    if not student: return jsonify({"error": "Student not found"}), 404

    # Fetch all applications and join with Drive and Company tables
    apps_query = db.session.query(Application, PlacementDrive, CompanyProfile)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(Application.student_id == student.id).all()

    history_list = []
    for app, drive, company in apps_query:
        history_list.append({
            "id": drive.id,
            "company": company.company_name,
            "role": drive.job_title,
            "mode": "In-person", # Placeholder (Not in DB)
            "status": app.status,
            "remark": "Application tracked" # Placeholder (Not in DB)
        })

    return jsonify({
        "studentName": student.full_name,
        "department": student.department or "Not Specified",
        "historyList": history_list
    }), 200




# controllers/student_controller.py mein export wala function check karo
@student_bp.route("/export_history", methods=["POST"])
@jwt_required()
def trigger_export():
    user_id = get_jwt_identity() # JWT se user_id mili
    
    # 1. Database se asali User aur uska Email nikalo
    user = User.query.get(user_id)
    student = StudentProfile.query.filter_by(user_id=user_id).first()

    if not user or not student:
        return jsonify({"message": "User not found"}), 404

    # 2. YAHAN HAI SABSE BADI BAAT:
    # Check karo ki user.email mein kya hai. 
    # Agar wahan purana email hai, toh Celery ko wahi purana email jayega.
    print(f"DEBUG: Triggering export for email in DB: {user.email}") # Terminal mein check karo ye kya print karta hai
    
    from tasks import export_student_history_csv
    export_student_history_csv.delay(student.id, user.email)
    
    return jsonify({"message": "Export started!"}), 202



@student_bp.route("/profile", methods=["GET", "POST"])
@jwt_required()
def manage_profile():
    user_id = get_jwt_identity()
    student = StudentProfile.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"message": "Student not found"}), 404

    # GET REQUEST: Profile data dikhane ke liye
    if request.method == "GET":
        return jsonify({
            "name": getattr(student, 'full_name', ''),      
            "cgpa": getattr(student, 'cgpa', ''),
            "branch": getattr(student, 'department', ''),  
            "resume_path": getattr(student, 'resume_link', '') 
        }), 200

   
    if request.method == "POST":
        # Form data parse karna (Kyunki file upload JSON me nahi hoti)
        if request.form.get("name"):
            student.full_name = request.form.get("name")
            
        if request.form.get("cgpa"):
            student.cgpa = request.form.get("cgpa")
        
        if request.form.get("branch") and hasattr(student, 'department'):
            student.department = request.form.get("branch")

        # File Upload Logic (PDF only)
        file = request.files.get("resume")
        if file and file.filename.endswith('.pdf'):
            # Folder ensure karo
            upload_folder = os.path.join('static', 'resumes')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Safe filename with student ID
            filename = secure_filename(f"resume_{student.id}_{file.filename}")
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            
            student.resume_link = f"/static/resumes/{filename}" 

        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200