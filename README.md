# Portal for Academia–Industry Collaboration for Skill Mapping, Internships & Placement

An intelligent Django web application connecting **Students**, **Faculty/College Administration**, and **Industry/Companies** to bridge the academic-industry curriculum gap through **Smart Automation**.

---

## 🌟 Key Prioritization & Features Implemented

### 1. Most Required / Core Features (High Priority)
- **Role-Based Authentication**: Unified custom user model (`STUDENT`, `FACULTY`, `COMPANY`) with role-specific registrations and smart dashboard redirection.
- **Student Skill Mapping & Profile**: Self-mapping of technical competencies with proficiency weights (Beginner = 1 pt, Intermediate = 2 pts, Advanced = 3 pts), CGPA, Branch, Year, Projects, and Certifications.
- **Company Opportunity Desk**: Post internships and job openings with required skills, minimum proficiency levels, CGPA cutoffs, and allowed branches.
- **Recruitment & Applicant Pipeline**: Company view with candidate applications automatically ranked by Skill Match Score descending; status updates (`SHORTLISTED`, `INTERVIEW_SCHEDULED`, `SELECTED`, `REJECTED`).
- **Interview Scheduling Engine**: Set interview date/time, mode (`Online` / `Offline`), and Google Meet / Teams link with automated student notification.
- **Placement Tracking**: Placement records tracking annual package (LPA), company, role, and acceptance status.

### 2. Smart Automation (Core Differentiators)
- **Automated Skill Gap Analysis Engine (`skills/automation.py`)**:
  - Compares student's skills against job requirements in real-time.
  - Calculates Match Percentage ($0-100\%$) using weighted proficiency scoring.
  - Pinpoints **Matched Skills** (with target level met vs partial credit) and **Missing Skills**.
  - Attaches **Curated Learning Resources** (documentation, free tutorials, and project ideas) directly to missing skills.
- **Smart Internship Recommendations**:
  - Dynamically computes and ranks all active postings for each logged-in student, showing top recommendations on their dashboard.
- **Automated Placement Eligibility Checker**:
  - Multi-factor evaluation evaluating CGPA criteria, Department/Branch eligibility, and technical readiness (&ge; 50%).
  - Flags status as `ELIGIBLE`, `SKILLS IMPROVEMENT REQUIRED`, or `NOT ELIGIBLE` with clear reasons.
- **Resume Skill Extraction Parser**:
  - Upload PDF or text resume; rule-based NLP taxonomy extractor detects technical skills and allows 1-click import into student profile.
- **Automated In-App Notifications**:
  - Real-time alerts on status updates, interview schedules with meeting links, and matching job postings.
- **Institutional Analytics (Chart.js)**:
  - Faculty dashboard with **Industry Demand vs Student Supply** bar chart, **Recruitment Funnel** doughnut chart, and department placement breakdown.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Current: Python 3.13)
- Django 6.0+

### 2. Run the Development Server
```bash
python manage.py runserver
```
Then open your browser at: **`http://127.0.0.1:8000/`**

---

## 🔑 Demo Accounts & Pre-Seeded Test Credentials

| Role | Username | Password | Purpose / Highlights |
| :--- | :--- | :--- | :--- |
| **Faculty / Admin** | `faculty_admin` | `admin123` | Institutional Analytics, Chart.js Skill Gap, Student Talent Pool |
| **Company 1 (Nexas Tech)** | `nexas_tech` | `company123` | Recruiter Desk, Review Candidates, Schedule Interviews |
| **Company 2 (DataStride AI)**| `datastride_ai` | `company123` | AI/ML Job Postings, Candidate Review |
| **Student 1 (Rahul - Backend)**| `rahul_cse` | `student123` | CGPA 8.4, CSE. Perfect for demonstrating **Skill Gap Analysis** (missing Django) |
| **Student 2 (Priya - Frontend)**| `priya_it` | `student123` | CGPA 9.1, IT. **Interview Scheduled** & **Placed** demo |
| **Student 3 (Arjun - AI/ML)** | `arjun_ai` | `student123` | CGPA 7.8, AI&DS. High match for ML Engineer Intern |

To re-seed test data at any time:
```bash
python manage.py seed_data
```

---

## 🧪 Automated Testing
Run the test suite verifying all smart automation algorithms, eligibility checks, and application workflows:
```bash
python manage.py test
```

---

## 📁 Project Architecture
```
jango_project/
├── manage.py
├── config/                  # Project configuration, URLs, WSGI/ASGI, settings
├── accounts/                # Custom User, Profiles (Student, Company, Faculty), Auth
├── skills/                  # Skill taxonomy, StudentSkills, Smart Gap Analysis, Resume Parser
│   ├── automation.py        # Core algorithms: Gap Engine, Recommendations, Eligibility Checker
├── internships/             # Postings, Requirements, Applications, Interview Scheduling, Placements
├── analytics/               # Faculty Institutional Analytics, Chart.js Data APIs, Student Readiness Pool
├── notifications/           # In-app notifications engine & context processor
├── templates/               # Responsive Bootstrap 5 + Chart.js templates
└── media/                   # Uploaded student resumes
```
