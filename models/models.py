from extensions import db
from datetime import datetime



# user table (unified model for admin, company, student)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_active = db.Column(db.Boolean, default=True)
    deactivated_reason = db.Column(db.String(255), nullable=True)

    # ONE TO ONE RELATIONSHIPS
    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    company_profile = db.relationship(
        "CompanyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# Student Profile

class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    resume_link = db.Column(db.String(255), nullable=True)
    year_of_study = db.Column(db.Integer, nullable=False)

    user = db.relationship(
        "User",
        back_populates="student_profile"
    )

# Company Profile

class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)

    approval_status = db.Column(
        db.String(20),
        default="Pending",
        index=True
    )

    user = db.relationship(
        "User",
        back_populates="company_profile"
    )

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(
        db.Integer, 
        db.ForeignKey("company_profiles.id"),
        nullable=False
    )

    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable = False)

    min_cgpa = db.Column(db.Float, nullable=False)
    eligible_departments = db.Column(db.String(255), nullable=False)
    eligible_year = db.Column(db.Integer, nullable = False)

    package_salary = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable = True)

    application_deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    # pending / approved / rejected / closed
    status = db.Column(db.String(20), default = "Pending", index=True)

    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approved_on = db.Column(db.DateTime, nullable=True)

    applications = db.relationship(
        "Application",
        backref="drive",
        lazy = True,
        cascade = "all, delete-orphan"
    )

    # application table

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    student_id  = db.Column(
        db.Integer, 
        db.ForeignKey("student_profiles.id"),
        nullable = False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("placement_drives.id"),
        nullable = False
    )



    applied_on = db.Column(db.DateTime, default= datetime.utcnow)
   
    resume_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default = "Applied", index = True)
    remark = db.Column(db.String(255), nullable = True)
    interview_date = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "drive_id",
            name="unique_student_drive_application"
        ),
    )

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)






