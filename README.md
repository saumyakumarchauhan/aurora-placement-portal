
# 🎓 Aurora Placement Portal

<div align="center">

### A Modern Full-Stack Placement Management System

Streamlining university recruitment with a premium Glassmorphism UI, role-based access control, and asynchronous background processing.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![Flask](https://img.shields.io/badge/Flask-Framework-black.svg)]()
[![Vue.js](https://img.shields.io/badge/Vue.js-3-green.svg)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-NeonDB-blue.svg)]()
[![Redis](https://img.shields.io/badge/Redis-Upstash-red.svg)]()
[![Celery](https://img.shields.io/badge/Celery-Async%20Tasks-green.svg)]()

</div>

---

# 🚀 Live Deployment & Demo

### 🌐 Production URL

https://placement-portal-5swj.onrender.com

> Log in with Admin credentials to access the dashboard.

### 🎥 Project Demonstration

*(Add your YouTube demo thumbnail and link here)*

---

# ✨ Key Features

## 👨‍💼 Admin Portal
- Approve or reject company registrations
- Approve placement drives
- Monitor student applications
- Trigger report generation
- Manage system operations

## 🏢 Company Portal
- Company registration and authentication
- Placement drive creation
- Application tracking
- Candidate management

## 🎓 Student Portal
- Student registration and login
- Browse active placement drives
- Apply to placement opportunities
- Track application status

## ⚡ Background Processing
- Asynchronous task execution using Celery
- CSV report generation
- Automated email delivery
- Non-blocking system operations

---

# 🛠️ Complete Tech Stack

This application utilizes a modern monolithic architecture, separating heavy background processes from the main web thread to ensure maximum performance.

| Layer | Technology |
|---------|-----------|
| Frontend | Vue.js 3 |
| UI Framework | Bootstrap 5.3 |
| Styling | Custom Aurora Glassmorphism Theme |
| Icons | FontAwesome 6 |
| Backend | Flask |
| Authentication | Flask-JWT-Extended |
| Email Service | Flask-Mail |
| Database | NeonDB (Serverless PostgreSQL) |
| ORM | SQLAlchemy |
| Cache | Upstash Redis |
| Task Queue | Celery |
| Deployment | Render |

---

# 🗄️ Database Schema

The Aurora Placement Portal follows a normalized relational database design implemented using **SQLAlchemy ORM** and **PostgreSQL (NeonDB)**. The schema is designed to efficiently manage students, companies, placement drives, applications, authentication, and administrative workflows while ensuring scalability and data consistency.

<p align="center">
  <img src="docs/ER.png" alt="Aurora Placement Portal Database Schema" width="1000">
</p>

**Core Entities:**
- Students
- Companies
- Placement Drives
- Applications
- Users & Roles
- Authentication & Sessions

---

# 🎨 Wireframe & System Architecture

Aurora follows a modern full-stack architecture where the **Vue.js frontend**, **Flask backend**, **PostgreSQL database**, **Redis cache**, and **Celery workers** work together to provide a seamless placement management experience.

### Architecture Diagram

🔗 **View Full Architecture Diagram**

[System Architecture & Wireframe](https://drive.google.com/file/d/153ClVUgNdeeCMm9s-YWM42--PjnZCf9S/view?usp=sharing)

### Architecture Overview

```text
┌───────────────┐
│    Vue.js     │
│   Frontend    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│     Flask     │
│   Backend     │
└───────┬───────┘
        │
 ┌──────┴──────┐
 ▼             ▼
PostgreSQL   Redis
 (NeonDB)   (Upstash)
                 │
                 ▼
             Celery
            Workers
                 │
                 ▼
         Reports & Emails
```

---

# 🔄 Data Flow Execution

```text
User Action
    ↓
Vue.js Frontend
    ↓
Fetch API Request
    ↓
Flask Backend
    ↓
JWT Validation
    ↓
PostgreSQL (NeonDB)
    ↓
JSON Response
    ↓
Dynamic UI Update
```

### Detailed Flow

1. User clicks an action button on the UI.
2. Vue.js intercepts the click and sends an asynchronous fetch() POST request.
3. Flask validates the JWT token in the request headers.
4. Flask updates the PostgreSQL database (via NeonDB).
5. Flask responds with a success JSON payload.
6. Vue.js dynamically updates the UI without reloading the page.

---

# 📖 How to Use the Portal (Step-by-Step)

## Step 1: Master Initialization

1. Navigate to the `/login` route on your live URL.
2. Enter the default Admin email and password.
3. Click **Initialize Session** to log in to the master control panel.

---

## Step 2: Approving Companies

When a new Company registers, their account is locked in a Pending state.

1. Navigate to the **Companies** tab in the sidebar.
2. Locate the newly registered company.
3. Click **Approve** to grant them access.

---

## Step 3: Publishing Placement Drives

Once approved, the company logs in and creates a new placement drive.

1. Go to the **Dashboard** or **All Drives** section.
2. Review the drive details.
3. Click **Approve**.

This instantly makes the drive visible to all registered students.

---

## Step 4: Managing Student Applications

Students register, log in, browse active drives, and click Apply.

Admins and Companies can view the live applicant list for each specific drive.

---

## Step 5: System Maintenance & Background Tasks

Once a drive deadline passes:

1. Admin clicks **Close Drive**
2. Navigate to the **System Maintenance** card
3. Click **Run Reports**

This triggers the Celery worker which:

- Securely queries the database
- Generates placement CSV reports
- Sends email reports
- Prevents website freezing

---

# 💻 Local Development Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/saumyakumarchauhan/placement-portal.git
cd placement-portal
```

## 2️⃣ Create a Virtual Environment

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory.

```env
FLASK_SECRET_KEY=your_secret_key

JWT_SECRET_KEY=your_jwt_secret

SQLALCHEMY_DATABASE_URI=postgresql://user:pass@your-neon-db-url

CACHE_REDIS_URL=rediss://default:pass@your-upstash-url?ssl_cert_reqs=none

ADMIN_EMAIL=admin@example.com

ADMIN_PASSWORD=admin123
```

## 5️⃣ Start the Application

### Terminal 1 - Flask Web Server

```bash
python app.py
```

### Terminal 2 - Celery Worker

```bash
celery -A celery_worker.celery worker --loglevel=info
```

---

# 📂 Project Structure

```text
placement-portal/
│
├── app.py
├── celery_worker.py
├── tasks.py
├── extensions.py
├── requirements.txt
├── .env
│
├── controllers/
├── models/
├── templates/
├── static/
│
└── README.md
```

---

# 🔐 Security Features

- JWT Authentication
- Role-Based Access Control
- Secure Session Management
- Protected API Routes
- Password Hashing
- Environment Variable Configuration

---

# 📈 Future Enhancements

- AI Resume Parsing
- Interview Scheduling System
- Real-Time Notifications
- Placement Analytics Dashboard
- Resume Scoring
- Student Recommendation Engine

---

# 👨‍💻 Author

**Saumyakumar Chauhan**

- B.Tech CSE, IIIT Kota
- BS Data Science, IIT Madras

---

# 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, distribute, and sublicense this software, provided that the original copyright and license notice are included in all copies or substantial portions of the software.

For more details, see the [LICENSE](LICENSE) file.

---

<div align="center">

### ⭐ If you like this project, consider giving it a star! ⭐

</div>
