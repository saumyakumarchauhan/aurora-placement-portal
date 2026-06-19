from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.models import CompanyProfile, PlacementDrive, Application, StudentProfile

    
company_bp = Blueprint("company_api", __name__, url_prefix="/api/company")

# Helper function to ensure the user is actually a company
def is_company():
    claims = get_jwt()
    return claims.get("role") == "company"


# FETCH DASHBOARD DATA

@company_bp.route("/data", methods=["GET"])
@jwt_required()
def get_dashboard_data():
    if not is_company():
        return jsonify({"error": "Unauthorized access"}), 403
        
    # Get the currently logged-in user's ID from the JWT token
    user_id = get_jwt_identity()
    
    # Find their company profile
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    # Fetch all placement drives created by THIS company
    all_drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    
    upcoming_drives = []
    closed_drives = []
    
    for i, drive in enumerate(all_drives):
        drive_data = {
            "id": drive.id,
            "srNo": f"{i+1}.",
            "name": drive.job_title
        }
        # If the status is closed, put it in the closed list. Otherwise, it's upcoming.
        if drive.status == "Closed":
            closed_drives.append(drive_data)
        else:
            upcoming_drives.append(drive_data)

    return jsonify({
        "companyName": company.company_name,
        "upcomingDrives": upcoming_drives,
        "closedDrives": closed_drives
    }), 200


# MARK DRIVE AS COMPLETE (Close Drive)

@company_bp.route("/mark_complete/<int:drive_id>", methods=["POST"])
@jwt_required()
def mark_drive_complete(drive_id):
    if not is_company(): return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    # Find the drive and ensure it belongs to this specific company
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    
    if not drive: 
        return jsonify({"error": "Drive not found"}), 404

    # Change the status to Closed
    drive.status = "Closed"
    db.session.commit()

    return jsonify({"message": "Drive successfully marked as complete!"}), 200



from datetime import datetime


# CREATE NEW DRIVE

@company_bp.route("/create_drive", methods=["POST"])
@jwt_required()
def create_drive():
    if not is_company():
        return jsonify({"error": "Unauthorized"}), 403
        
    user_id = get_jwt_identity()
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    data = request.get_json()
    
    try:
        # Parse the deadline string into a Python datetime object
        deadline_str = data.get("deadline")
        deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d')
        
        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=data.get("jobTitle"),
            job_description=data.get("description"),
            min_cgpa=float(data.get("minCgpa", 0.0)),
            eligible_departments=data.get("departments"),
            eligible_year=int(data.get("graduationYear", 0)),
            package_salary=data.get("packageSalary", ""),
            location=data.get("location", ""),
            application_deadline=deadline_date,
            status="Pending" # Requires Admin Approval
        )
        
        db.session.add(new_drive)
        db.session.commit()
        
        return jsonify({"message": "Drive created successfully! Awaiting Admin approval."}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    



# GET DRIVE DETAILS & APPLICANTS

@company_bp.route("/drive/<int:drive_id>", methods=["GET"])
@jwt_required()
def get_drive_details(drive_id):
    if not is_company(): return jsonify({"error": "Unauthorized"}), 403
    
    user_id = get_jwt_identity()
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    # Security check: Ensure this drive actually belongs to THIS company
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive: 
        return jsonify({"error": "Drive not found or access denied"}), 404

    # Fetch all students who applied to this specific drive
    apps_query = db.session.query(Application, StudentProfile)\
        .join(StudentProfile, Application.student_id == StudentProfile.id)\
        .filter(Application.drive_id == drive.id).all()

    applicants = []
    for i, (app, student) in enumerate(apps_query):
        applicants.append({
            "id": app.id,
            "student_id": student.id,
            "srNo": f"{i+1}.",
            "name": student.full_name,
            "department": student.department or "N/A",
            "cgpa": student.cgpa or "N/A",
            "status": app.status
        })

    return jsonify({
        "id": drive.id,
        "jobTitle": drive.job_title,
        "status": drive.status,
        "applicants": applicants
    }), 200


# UPDATE APPLICATION STATUS (Shortlist / Reject)

@company_bp.route("/update_application/<int:app_id>", methods=["POST"])
@jwt_required()
def update_application_status(app_id):
    if not is_company(): return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    new_status = data.get("status") # "Shortlisted", "Rejected", etc.
    
    app = Application.query.get(app_id)
    if app:
        app.status = new_status
        db.session.commit()
        return jsonify({"message": f"Student marked as {new_status}"}), 200
        
    return jsonify({"error": "Application not found"}), 404



# GET SINGLE STUDENT APPLICATION DETAILS

@company_bp.route("/student_application/<int:app_id>", methods=["GET"])
@jwt_required()
def get_student_application(app_id):
    if not is_company(): return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    # Fetch Application, Student, and Drive together
    result = db.session.query(Application, StudentProfile, PlacementDrive)\
        .join(StudentProfile, Application.student_id == StudentProfile.id)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .filter(Application.id == app_id, PlacementDrive.company_id == company.id).first()

    if not result:
        return jsonify({"error": "Application not found or access denied"}), 404

    app, student, drive = result

    return jsonify({
        "appId": app.id,
        "driveId": drive.id,
        "studentName": student.full_name,
        "department": student.department or "Not Specified",
        "driveName": f"Drive #{drive.id}",
        "jobTitle": drive.job_title,
        "status": app.status,
        # Fetching the resume from the Application table instead of Student Profile!
        "resumeUrl": getattr(app, "resume_url", "#") 
    }), 200

