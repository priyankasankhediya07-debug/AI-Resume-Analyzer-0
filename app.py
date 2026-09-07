# ============================================================
# AI RESUME SCREENING & SKILLS GAP ANALYSIS
# Recruiter + Candidate Backend
# ============================================================

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

import os
import json
import re
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# PDF
import fitz

# DOCX
from docx import Document

# PDF REPORT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Separate folders so existing files/folders do not conflict
UPLOAD_FOLDER = os.path.join(BASE_DIR, "candidate_uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "generated_reports")

JOBS_FILE = os.path.join(BASE_DIR, "recruiter_jobs.json")


# Create folders safely
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


# ============================================================
# ALLOWED FILES
# ============================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx"
}


def allowed_file(filename):

    if not filename:
        return False

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# DATABASE - JSON
# ============================================================

def load_jobs():

    if not os.path.exists(JOBS_FILE):
        return []

    try:

        with open(
            JOBS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print("JOB DATABASE ERROR:", error)

        return []


def save_jobs(jobs):

    with open(
        JOBS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            jobs,
            file,
            indent=4,
            ensure_ascii=False
        )


jobs = load_jobs()


# ============================================================
# LAST ANALYSIS
# ============================================================

last_result = {}


# ============================================================
# SKILLS DATABASE
# ============================================================

SKILLS_DATABASE = [

    # Programming
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "php",
    "ruby",
    "go",

    # Web
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node",
    "node.js",
    "express",
    "flask",
    "django",
    "fastapi",

    # Database
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "sqlite",
    "redis",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "opencv",
    "nlp",

    # Cloud
    "aws",
    "azure",
    "google cloud",
    "gcp",
    "cloud computing",

    # DevOps
    "docker",
    "kubernetes",
    "devops",
    "jenkins",
    "ci/cd",
    "linux",

    # Version Control
    "git",
    "github",
    "gitlab",

    # Cyber Security
    "cyber security",
    "cybersecurity",
    "ethical hacking",
    "network security",
    "penetration testing",
    "penetration testing",

    # Mobile
    "android",
    "flutter",
    "react native",
    "kotlin",
    "swift",

    # Design
    "ui/ux",
    "figma",
    "adobe xd",
    "canva",

    # Analytics
    "power bi",
    "tableau",
    "excel",
    "business analytics",

    # Marketing
    "marketing",
    "seo",
    "sales",
    "branding",
    "digital marketing",

    # Finance
    "finance",
    "accounting",
    "investment",
    "banking",

    # HR
    "recruitment",
    "human resources",
    "hr",
    "talent acquisition",

    # IoT
    "iot",
    "arduino",
    "raspberry pi",

    # Blockchain
    "blockchain",
    "web3",
    "solidity",

    # Soft skills
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "project management",
    "agile",
    "scrum"
]


# ============================================================
# DOMAIN DATABASE
# ============================================================

DOMAIN_KEYWORDS = {

    "Software Development": [
        "python",
        "java",
        "javascript",
        "html",
        "css",
        "react",
        "node",
        "flask",
        "django",
        "fastapi",
        "sql"
    ],

    "Data Science & AI": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "pandas",
        "numpy",
        "tensorflow",
        "pytorch",
        "scikit-learn"
    ],

    "Cyber Security": [
        "cyber security",
        "cybersecurity",
        "ethical hacking",
        "penetration testing",
        "network security"
    ],

    "Cloud Computing": [
        "aws",
        "azure",
        "google cloud",
        "gcp",
        "cloud computing"
    ],

    "DevOps": [
        "docker",
        "kubernetes",
        "devops",
        "jenkins",
        "linux",
        "ci/cd"
    ],

    "Mobile App Development": [
        "android",
        "flutter",
        "react native",
        "kotlin",
        "swift"
    ],

    "UI/UX Design": [
        "ui/ux",
        "figma",
        "adobe xd",
        "canva"
    ],

    "Business Analytics": [
        "power bi",
        "tableau",
        "business analytics",
        "excel",
        "data analysis"
    ],

    "Marketing": [
        "marketing",
        "seo",
        "sales",
        "branding",
        "digital marketing"
    ],

    "Finance": [
        "finance",
        "accounting",
        "investment",
        "banking"
    ],

    "Human Resources": [
        "recruitment",
        "human resources",
        "talent acquisition",
        "hr"
    ],

    "Internet of Things": [
        "iot",
        "arduino",
        "raspberry pi"
    ],

    "Blockchain": [
        "blockchain",
        "web3",
        "solidity"
    ],

    "Project Management": [
        "project management",
        "agile",
        "scrum"
    ],

    "Education": [
        "teacher",
        "education",
        "training"
    ],

    "Healthcare": [
        "healthcare",
        "hospital",
        "medical",
        "nursing",
        "patient care"
    ]
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_path):

    text = ""

    try:

        document = fitz.open(file_path)

        for page in document:

            text += page.get_text()

        document.close()

    except Exception as error:

        print("PDF EXTRACTION ERROR:", error)

    return text


def extract_docx_text(file_path):

    text = ""

    try:

        document = Document(file_path)

        # Paragraphs
        for paragraph in document.paragraphs:

            text += paragraph.text + "\n"

        # Tables
        for table in document.tables:

            for row in table.rows:

                for cell in row.cells:

                    text += cell.text + "\n"

    except Exception as error:

        print("DOCX EXTRACTION ERROR:", error)

    return text


def extract_doc_text(file_path):

    """
    Old .doc files are difficult to parse directly without
    additional Windows-specific tools.

    We return a helpful message instead of crashing.
    """

    return ""


def extract_resume_text(file_path):

    extension = file_path.rsplit(".", 1)[1].lower()

    if extension == "pdf":

        return extract_pdf_text(file_path)

    elif extension == "docx":

        return extract_docx_text(file_path)

    elif extension == "doc":

        return extract_doc_text(file_path)

    return ""


# ============================================================
# SKILL DETECTION
# ============================================================

def detect_skills(text):

    text_lower = text.lower()

    detected = []

    for skill in SKILLS_DATABASE:

        if skill.lower() in text_lower:

            formatted_skill = skill.title()

            if formatted_skill not in detected:

                detected.append(formatted_skill)

    return detected


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(text):

    text_lower = text.lower()

    domain_scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in text_lower:

                score += 1

        domain_scores[domain] = score


    if not domain_scores:
        return "General"


    best_domain = max(
        domain_scores,
        key=domain_scores.get
    )


    if domain_scores[best_domain] == 0:

        return "General"


    return best_domain


# ============================================================
# EMAIL EXTRACTION
# ============================================================

def extract_email(text):

    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(
        pattern,
        text
    )

    if match:

        return match.group(0)

    return "Not detected"


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phone(text):

    pattern = r"(?:(?:\+91[\s-]?)?[6-9]\d{9})"

    match = re.search(
        pattern,
        text
    )

    if match:

        return match.group(0)

    return "Not detected"


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


    # Try first few lines
    for line in lines[:10]:

        lower = line.lower()

        if (
            "resume" in lower
            or "curriculum vitae" in lower
            or "cv" == lower
            or "email" in lower
            or "phone" in lower
            or "mobile" in lower
        ):

            continue


        # Avoid very long lines
        if len(line) > 60:

            continue


        # Name generally contains letters/spaces
        if re.match(
            r"^[A-Za-z][A-Za-z .'-]{2,50}$",
            line
        ):

            return line


    return "Candidate"


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text):

    text_lower = text.lower()

    patterns = [

        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",

        r"experience\s*[:\-]?\s*(\d+)\+?\s*(?:years?|yrs?)"
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text_lower
        )

        if match:

            try:

                return int(match.group(1))

            except:

                pass


    # Internship indicates beginner-level experience
    if "internship" in text_lower:

        return 0


    return 0


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education(text):

    text_lower = text.lower()

    education_keywords = [

        "b.tech",
        "btech",
        "b.e",
        "be ",
        "bca",
        "mca",
        "m.tech",
        "mtech",
        "mba",
        "b.sc",
        "bsc",
        "m.sc",
        "msc",
        "bachelor",
        "master",
        "phd"
    ]


    found = []

    for education in education_keywords:

        if education.lower() in text_lower:

            found.append(
                education.upper()
            )


    if found:

        return list(dict.fromkeys(found))


    return []


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    text,
    detected_skills,
    domain
):

    text_lower = text.lower()

    score = 0


    # ---------------- SKILLS ----------------

    score += min(
        len(detected_skills) * 4,
        40
    )


    # ---------------- PROJECTS ----------------

    if "project" in text_lower:

        score += 15


    # ---------------- CERTIFICATION ----------------

    if (
        "certificate" in text_lower
        or "certification" in text_lower
    ):

        score += 10


    # ---------------- EDUCATION ----------------

    if any(
        keyword in text_lower
        for keyword in [
            "b.tech",
            "btech",
            "bca",
            "mca",
            "bachelor",
            "master"
        ]
    ):

        score += 10


    # ---------------- EXPERIENCE ----------------

    if (
        "experience" in text_lower
        or "internship" in text_lower
    ):

        score += 10


    # ---------------- LEADERSHIP ----------------

    if (
        "leadership" in text_lower
        or "team leader" in text_lower
    ):

        score += 5


    return min(
        score,
        100
    )


# ============================================================
# RESUME STRENGTH
# ============================================================

def get_strength(score):

    if score >= 85:

        return "Excellent"

    elif score >= 70:

        return "Good"

    elif score >= 50:

        return "Average"

    return "Needs Improvement"


# ============================================================
# MISSING SKILLS
# ============================================================

def find_missing_skills(
    required_skills,
    resume_text
):

    resume_text = resume_text.lower()

    missing = []

    for skill in required_skills:

        if skill.lower() not in resume_text:

            missing.append(skill)


    return missing


# ============================================================
# CANDIDATE MATCH SCORE
# ============================================================

def calculate_candidate_match(
    resume_text,
    required_skills,
    job_description="",
    experience_requirement=""
):

    resume_lower = resume_text.lower()

    required_skills = [
        skill.strip()
        for skill in required_skills
        if skill.strip()
    ]


    # ---------------- SKILL MATCH ----------------

    matched_skills = []

    missing_skills = []


    for skill in required_skills:

        if skill.lower() in resume_lower:

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)


    if required_skills:

        skill_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 70

    else:

        skill_score = 0


    # ---------------- DESCRIPTION MATCH ----------------

    description_words = re.findall(
        r"[a-zA-Z]{4,}",
        job_description.lower()
    )


    description_matches = 0

    unique_words = set(
        description_words
    )


    for word in unique_words:

        if word in resume_lower:

            description_matches += 1


    if unique_words:

        description_score = min(
            (
                description_matches
                / len(unique_words)
            ) * 15,
            15
        )

    else:

        description_score = 0


    # ---------------- EXPERIENCE ----------------

    candidate_experience = extract_experience(
        resume_text
    )


    experience_score = 0


    if experience_requirement:

        requirement = experience_requirement.lower()


        if "fresher" in requirement:

            experience_score = 10


        elif "0 - 2" in requirement:

            if candidate_experience <= 2:

                experience_score = 10

            elif candidate_experience <= 4:

                experience_score = 5


        elif "2 - 5" in requirement:

            if 2 <= candidate_experience <= 5:

                experience_score = 10

            elif candidate_experience > 5:

                experience_score = 5


        elif "5+" in requirement:

            if candidate_experience >= 5:

                experience_score = 10

            elif candidate_experience >= 3:

                experience_score = 5

    else:

        experience_score = 10


    final_score = (
        skill_score
        + description_score
        + experience_score
    )


    final_score = round(
        min(final_score, 100)
    )


    return {
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "candidate_experience": candidate_experience
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Resume Screening</title>
    </head>

    <body style="
        background:#111;
        color:white;
        font-family:Arial;
        text-align:center;
        padding:100px;
    ">

        <h1>AI Resume Screening & Skills Gap Analysis</h1>

        <p>Backend is running successfully.</p>

        <p>
            <a
                href="/recruiter.html"
                style="color:#e50914;"
            >
                Open Recruiter Portal
            </a>
        </p>

        <p>
            <a
                href="/analyzer.html"
                style="color:#e50914;"
            >
                Open Candidate Analyzer
            </a>
        </p>

    </body>
    </html>
    """


# ============================================================
# SERVE FRONTEND FILES
# ============================================================

@app.route("/<path:filename>")
def serve_frontend(filename):

    allowed_frontend_files = {

        "index.html",
        "analyzer.html",
        "recruiter.html",
        "about.html",
        "style.css",
        "script.js",
        "recruiter.js"
    }


    if filename in allowed_frontend_files:

        file_path = os.path.join(
            BASE_DIR,
            filename
        )


        if os.path.exists(file_path):

            return send_from_directory(
                BASE_DIR,
                filename
            )


    return jsonify({
        "error": "File not found"
    }), 404


# ============================================================
# CANDIDATE ANALYZER
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze_resume():

    global last_result


    try:

        file = request.files.get(
            "resume"
        )


        if not file:

            return jsonify({
                "success": False,
                "error": "No resume uploaded"
            }), 400


        if not allowed_file(
            file.filename
        ):

            return jsonify({
                "success": False,
                "error":
                "Only PDF, DOC and DOCX files are supported."
            }), 400


        original_name = secure_filename(
            file.filename
        )


        unique_name = (
            uuid.uuid4().hex
            + "_"
            + original_name
        )


        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )


        file.save(file_path)


        text = extract_resume_text(
            file_path
        )


        if not text.strip():

            return jsonify({
                "success": False,
                "error":
                "Could not extract text from resume. "
                "For best results use PDF or DOCX."
            }), 400


        detected_skills = detect_skills(
            text
        )


        domain = detect_domain(
            text
        )


        ats_score = calculate_ats_score(
            text,
            detected_skills,
            domain
        )


        strength = get_strength(
            ats_score
        )


        missing_skills = []


        if domain == "Software Development":

            required = [
                "Python",
                "HTML",
                "CSS",
                "JavaScript",
                "SQL"
            ]


        elif domain == "Data Science & AI":

            required = [
                "Python",
                "Pandas",
                "Numpy",
                "SQL",
                "Power BI"
            ]


        elif domain == "Marketing":

            required = [
                "SEO",
                "Communication",
                "Sales",
                "Branding"
            ]


        elif domain == "Finance":

            required = [
                "Excel",
                "Accounting",
                "Finance",
                "Power BI"
            ]


        elif domain == "Human Resources":

            required = [
                "Communication",
                "Recruitment",
                "Leadership"
            ]


        else:

            required = []


        missing_skills = find_missing_skills(
            required,
            text
        )


        recommendations = []


        if len(detected_skills) < 5:

            recommendations.append(
                "Add more relevant technical skills."
            )


        if "project" not in text.lower():

            recommendations.append(
                "Add relevant projects with measurable results."
            )


        if (
            "certificate" not in text.lower()
            and "certification" not in text.lower()
        ):

            recommendations.append(
                "Add relevant certifications if available."
            )


        recommendations.append(
            "Improve technical keywords according to the target job."
        )


        last_result = {

            "filename": original_name,

            "ats_score": ats_score,

            "domain": domain,

            "strength": strength,

            "skills": detected_skills,

            "missing_skills": missing_skills,

            "recommendations": recommendations
        }


        return jsonify({

            "success": True,

            "filename": original_name,

            "domain": domain,

            "skills": detected_skills,

            "missing_skills": missing_skills,

            "ats_score": ats_score,

            "strength": strength,

            "recommendations": recommendations

        })


    except Exception as error:

        print(
            "ANALYZE ERROR:",
            str(error)
        )


        return jsonify({

            "success": False,

            "error":
            "Backend error while analyzing resume.",

            "details": str(error)

        }), 500


# ============================================================
# CREATE JOB
# ============================================================

@app.route(
    "/api/create-job",
    methods=["POST"]
)
def create_job():

    global jobs


    try:

        data = request.get_json(
            silent=True
        ) or {}


        job_title = str(
            data.get(
                "job_title",
                ""
            )
        ).strip()


        company_name = str(
            data.get(
                "company_name",
                ""
            )
        ).strip()


        experience = str(
            data.get(
                "experience",
                ""
            )
        ).strip()


        work_mode = str(
            data.get(
                "work_mode",
                "Remote"
            )
        ).strip()


        required_skills = data.get(
            "required_skills",
            []
        )


        job_description = str(
            data.get(
                "job_description",
                ""
            )
        ).strip()


        location = str(
            data.get(
                "location",
                ""
            )
        ).strip()


        education = str(
            data.get(
                "education",
                ""
            )
        ).strip()


        if isinstance(
            required_skills,
            str
        ):

            required_skills = [
                skill.strip()
                for skill in required_skills.split(",")
                if skill.strip()
            ]


        if not job_title:

            return jsonify({
                "success": False,
                "error":
                "Job title is required."
            }), 400


        if not company_name:

            return jsonify({
                "success": False,
                "error":
                "Company name is required."
            }), 400


        if not required_skills:

            return jsonify({
                "success": False,
                "error":
                "Please enter required skills."
            }), 400


        job = {

            "id": str(uuid.uuid4()),

            "job_title": job_title,

            "company_name": company_name,

            "experience": experience,

            "work_mode": work_mode,

            "required_skills": required_skills,

            "job_description": job_description,

            "location": location,

            "education": education,

            "company_details": {

                "company_name": company_name,

                "industry": "Technology",

                "location": location,

                "description":
                f"{company_name} is hiring for "
                f"{job_title}.",

                "work_mode": work_mode,

                "benefits": [
                    "Professional Growth",
                    "Collaborative Environment",
                    "Learning Opportunities"
                ]
            },

            "candidates": [],

            "shortlisted": [],

            "interviews": [],

            "created_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }


        jobs.append(job)

        save_jobs(jobs)


        return jsonify({

            "success": True,

            "message":
            "Job created successfully.",

            "job": job

        })


    except Exception as error:

        print(
            "CREATE JOB ERROR:",
            str(error)
        )


        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# GET ALL JOBS
# ============================================================

@app.route(
    "/api/jobs",
    methods=["GET"]
)
def get_jobs():

    return jsonify({

        "success": True,

        "jobs": jobs,

        "total_jobs": len(jobs)

    })


# ============================================================
# GET SINGLE JOB
# ============================================================

@app.route(
    "/api/jobs/<job_id>",
    methods=["GET"]
)
def get_job(job_id):

    for job in jobs:

        if str(job["id"]) == str(job_id):

            return jsonify({

                "success": True,

                "job": job

            })


    return jsonify({

        "success": False,

        "error": "Job not found."

    }), 404


# ============================================================
# SCREEN CANDIDATE RESUMES
# ============================================================

@app.route(
    "/api/screen-candidates",
    methods=["POST"]
)
def screen_candidates():

    global jobs
    global last_result


    try:

        job_id = request.form.get(
            "job_id"
        )


        if not job_id:

            return jsonify({

                "success": False,

                "error":
                "Job ID is required."

            }), 400


        selected_job = None


        for job in jobs:

            if str(job["id"]) == str(job_id):

                selected_job = job

                break


        if not selected_job:

            return jsonify({

                "success": False,

                "error":
                "Selected job not found."

            }), 404


        files = request.files.getlist(
            "resumes"
        )


        if not files:

            return jsonify({

                "success": False,

                "error":
                "No candidate resumes uploaded."

            }), 400


        results = []


        for file in files:

            if not file.filename:

                continue


            if not allowed_file(
                file.filename
            ):

                continue


            original_name = secure_filename(
                file.filename
            )


            unique_name = (
                uuid.uuid4().hex
                + "_"
                + original_name
            )


            file_path = os.path.join(
                UPLOAD_FOLDER,
                unique_name
            )


            file.save(file_path)


            resume_text = extract_resume_text(
                file_path
            )


            if not resume_text.strip():

                continue


            detected_skills = detect_skills(
                resume_text
            )


            domain = detect_domain(
                resume_text
            )


            match_data = calculate_candidate_match(

                resume_text,

                selected_job[
                    "required_skills"
                ],

                selected_job[
                    "job_description"
                ],

                selected_job[
                    "experience"
                ]
            )


            candidate = {

                "candidate_id":
                str(uuid.uuid4()),

                "filename":
                original_name,

                "name":
                extract_name(
                    resume_text
                ),

                "email":
                extract_email(
                    resume_text
                ),

                "phone":
                extract_phone(
                    resume_text
                ),

                "skills":
                detected_skills,

                "domain":
                domain,

                "experience":
                match_data[
                    "candidate_experience"
                ],

                "education":
                extract_education(
                    resume_text
                ),

                "match_score":
                match_data[
                    "match_score"
                ],

                "matched_skills":
                match_data[
                    "matched_skills"
                ],

                "missing_skills":
                match_data[
                    "missing_skills"
                ],

                "status":
                "Screened",

                "resume_file":
                unique_name,

                "screened_at":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }


            results.append(
                candidate
            )


        # Sort highest score first
        results.sort(
            key=lambda candidate:
            candidate["match_score"],
            reverse=True
        )


        # Top 5
        top_candidates = results[:5]


        # Save all candidates
        selected_job["candidates"] = results


        # Automatically identify top 5
        selected_job["shortlisted"] = [
            candidate["candidate_id"]
            for candidate in top_candidates
        ]


        save_jobs(jobs)


        last_result = {

            "job_id": job_id,

            "candidates": results,

            "top_candidates":
            top_candidates
        }


        return jsonify({

            "success": True,

            "message":
            "Candidate screening completed.",

            "total_candidates":
            len(results),

            "top_5":
            top_candidates,

            "all_candidates":
            results

        })


    except Exception as error:

        print(
            "SCREENING ERROR:",
            str(error)
        )


        return jsonify({

            "success": False,

            "error":
            "Error while screening candidates.",

            "details":
            str(error)

        }), 500


# ============================================================
# GET TOP 5 CANDIDATES
# ============================================================

@app.route(
    "/api/jobs/<job_id>/top-candidates",
    methods=["GET"]
)
def top_candidates(job_id):

    for job in jobs:

        if str(job["id"]) == str(job_id):

            candidates = job.get(
                "candidates",
                []
            )


            candidates = sorted(

                candidates,

                key=lambda candidate:
                candidate.get(
                    "match_score",
                    0
                ),

                reverse=True
            )


            return jsonify({

                "success": True,

                "top_5":
                candidates[:5],

                "total":
                len(candidates)

            })


    return jsonify({

        "success": False,

        "error":
        "Job not found."

    }), 404


# ============================================================
# SHORTLIST CANDIDATE
# ============================================================

@app.route(
    "/api/shortlist",
    methods=["POST"]
)
def shortlist_candidate():

    global jobs


    try:

        data = request.get_json(
            silent=True
        ) or {}


        job_id = data.get(
            "job_id"
        )


        candidate_id = data.get(
            "candidate_id"
        )


        if not job_id or not candidate_id:

            return jsonify({

                "success": False,

                "error":
                "Job ID and Candidate ID are required."

            }), 400


        for job in jobs:

            if str(job["id"]) != str(job_id):

                continue


            for candidate in job.get(
                "candidates",
                []
            ):

                if str(
                    candidate["candidate_id"]
                ) == str(candidate_id):

                    candidate["status"] = (
                        "Shortlisted"
                    )


                    if candidate_id not in job[
                        "shortlisted"
                    ]:

                        job[
                            "shortlisted"
                        ].append(
                            candidate_id
                        )


                    save_jobs(jobs)


                    return jsonify({

                        "success": True,

                        "message":
                        "Candidate shortlisted.",

                        "candidate":
                        candidate

                    })


        return jsonify({

            "success": False,

            "error":
            "Candidate not found."

        }), 404


    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# INTERVIEW SCHEDULING
# ============================================================

@app.route(
    "/api/schedule-interview",
    methods=["POST"]
)
def schedule_interview():

    global jobs


    try:

        data = request.get_json(
            silent=True
        ) or {}


        job_id = data.get(
            "job_id"
        )


        candidate_id = data.get(
            "candidate_id"
        )


        interview_date = data.get(
            "date"
        )


        interview_time = data.get(
            "time"
        )


        mode = data.get(
            "mode",
            "Online"
        )


        meeting_link = data.get(
            "meeting_link",
            ""
        )


        if not job_id:

            return jsonify({

                "success": False,

                "error":
                "Job ID is required."

            }), 400


        if not candidate_id:

            return jsonify({

                "success": False,

                "error":
                "Candidate ID is required."

            }), 400


        if not interview_date:

            return jsonify({

                "success": False,

                "error":
                "Interview date is required."

            }), 400


        if not interview_time:

            return jsonify({

                "success": False,

                "error":
                "Interview time is required."

            }), 400


        for job in jobs:

            if str(job["id"]) != str(job_id):

                continue


            candidate = None


            for item in job.get(
                "candidates",
                []
            ):

                if str(
                    item["candidate_id"]
                ) == str(candidate_id):

                    candidate = item

                    break


            if not candidate:

                return jsonify({

                    "success": False,

                    "error":
                    "Candidate not found."

                }), 404


            interview = {

                "interview_id":
                str(uuid.uuid4()),

                "candidate_id":
                candidate_id,

                "candidate_name":
                candidate.get(
                    "name",
                    "Candidate"
                ),

                "candidate_email":
                candidate.get(
                    "email",
                    ""
                ),

                "job_title":
                job["job_title"],

                "company_name":
                job["company_name"],

                "date":
                interview_date,

                "time":
                interview_time,

                "mode":
                mode,

                "meeting_link":
                meeting_link,

                "status":
                "Scheduled",

                "created_at":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }


            job.setdefault(
                "interviews",
                []
            ).append(
                interview
            )


            candidate["status"] = (
                "Interview Scheduled"
            )


            save_jobs(jobs)


            return jsonify({

                "success": True,

                "message":
                "Interview scheduled successfully.",

                "interview":
                interview

            })


        return jsonify({

            "success": False,

            "error":
            "Job not found."

        }), 404


    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# COMPANY DETAILS
# ============================================================

@app.route(
    "/api/company-details/<job_id>",
    methods=["GET"]
)
def company_details(job_id):

    for job in jobs:

        if str(job["id"]) == str(job_id):

            return jsonify({

                "success": True,

                "company":
                job.get(
                    "company_details",
                    {}
                ),

                "job": {

                    "title":
                    job["job_title"],

                    "location":
                    job["location"],

                    "work_mode":
                    job["work_mode"],

                    "experience":
                    job["experience"],

                    "education":
                    job["education"]
                }

            })


    return jsonify({

        "success": False,

        "error":
        "Job not found."

    }), 404


# ============================================================
# CANDIDATE INVITATION DETAILS
# ============================================================

@app.route(
    "/api/candidate-invitation",
    methods=["POST"]
)
def candidate_invitation():

    try:

        data = request.get_json(
            silent=True
        ) or {}


        candidate_name = data.get(
            "candidate_name",
            "Candidate"
        )


        company_name = data.get(
            "company_name",
            "Company"
        )


        job_title = data.get(
            "job_title",
            "Job Opportunity"
        )


        interview_date = data.get(
            "date",
            "To be confirmed"
        )


        interview_time = data.get(
            "time",
            "To be confirmed"
        )


        mode = data.get(
            "mode",
            "Online"
        )


        meeting_link = data.get(
            "meeting_link",
            ""
        )


        message = f"""
Hello {candidate_name},

Congratulations!

Based on our AI-assisted resume screening,
your profile has been shortlisted for the
following opportunity:

Company: {company_name}
Position: {job_title}

Interview Date: {interview_date}
Interview Time: {interview_time}
Interview Mode: {mode}

"""


        if meeting_link:

            message += (
                f"Meeting Link: {meeting_link}\n\n"
            )


        message += """
Please be available at the scheduled time.

Best regards,
Recruitment Team
"""


        return jsonify({

            "success": True,

            "candidate":
            candidate_name,

            "message":
            message.strip()

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# AI ASSISTANT
# ============================================================

@app.route(
    "/api/assistant",
    methods=["POST"]
)
def recruiter_assistant():

    try:

        data = request.get_json(
            silent=True
        ) or {}


        question = str(
            data.get(
                "question",
                ""
            )
        ).strip()


        job_id = data.get(
            "job_id"
        )


        if not question:

            return jsonify({

                "success": False,

                "error":
                "Please enter a question."

            }), 400


        job = None


        if job_id:

            for item in jobs:

                if str(
                    item["id"]
                ) == str(job_id):

                    job = item

                    break


        q = question.lower()


        # ---------------- JOB SKILLS ----------------

        if (
            "skill" in q
            or "skills" in q
        ):

            if job:

                answer = (
                    "Required skills for "
                    f"{job['job_title']}: "
                    + ", ".join(
                        job["required_skills"]
                    )
                )

            else:

                answer = (
                    "Please select a job to "
                    "view its required skills."
                )


        # ---------------- TOP CANDIDATE ----------------

        elif (
            "top" in q
            or "best candidate" in q
            or "strongest" in q
        ):

            if job and job.get(
                "candidates"
            ):

                ranked = sorted(

                    job["candidates"],

                    key=lambda x:
                    x.get(
                        "match_score",
                        0
                    ),

                    reverse=True
                )


                best = ranked[0]


                answer = (
                    f"Top candidate is "
                    f"{best['name']} "
                    f"with a "
                    f"{best['match_score']}% "
                    f"job match."
                )

            else:

                answer = (
                    "No candidates have been "
                    "screened yet."
                )


        # ---------------- MISSING SKILLS ----------------

        elif (
            "gap" in q
            or "missing" in q
        ):

            if job and job.get(
                "candidates"
            ):

                ranked = sorted(

                    job["candidates"],

                    key=lambda x:
                    x.get(
                        "match_score",
                        0
                    ),

                    reverse=True
                )


                best = ranked[0]


                missing = best.get(
                    "missing_skills",
                    []
                )


                if missing:

                    answer = (
                        f"{best['name']} "
                        "is missing: "
                        + ", ".join(missing)
                    )

                else:

                    answer = (
                        "The top candidate "
                        "matches all required skills."
                    )

            else:

                answer = (
                    "Screen candidates first "
                    "to calculate skill gaps."
                )


        # ---------------- INTERVIEW ----------------

        elif (
            "interview" in q
            or "schedule" in q
        ):

            answer = (
                "You can schedule an interview "
                "from the shortlisted candidate "
                "section by selecting the date, "
                "time and interview mode."
            )


        # ---------------- COMPANY ----------------

        elif (
            "company" in q
            or "about" in q
        ):

            if job:

                answer = (
                    f"{job['company_name']} "
                    f"is hiring for "
                    f"{job['job_title']}. "
                    f"Work mode: "
                    f"{job['work_mode']}. "
                    f"Location: "
                    f"{job['location']}."
                )

            else:

                answer = (
                    "Select a job to view "
                    "company information."
                )


        # ---------------- GENERAL ----------------

        else:

            answer = (
                "I can help you with job "
                "requirements, candidate ranking, "
                "skill gaps, interview scheduling "
                "and company information."
            )


        return jsonify({

            "success": True,

            "question":
            question,

            "answer":
            answer

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================

@app.route(
    "/download-report",
    methods=["GET"]
)
def download_report():

    global last_result


    if not last_result:

        return jsonify({

            "success": False,

            "error":
            "Please analyze a resume first."

        }), 400


    filename = (
        "resume_analysis_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".pdf"
    )


    pdf_path = os.path.join(
        REPORT_FOLDER,
        filename
    )


    c = canvas.Canvas(
        pdf_path,
        pagesize=A4
    )


    width, height = A4


    y = height - 60


    c.setFont(
        "Helvetica-Bold",
        20
    )


    c.drawString(
        50,
        y,
        "AI Resume Screening"
    )


    y -= 30


    c.setFont(
        "Helvetica-Bold",
        14
    )


    c.drawString(
        50,
        y,
        "& Skills Gap Analysis Report"
    )


    y -= 50


    c.setFont(
        "Helvetica",
        12
    )


    if "filename" in last_result:

        c.drawString(
            50,
            y,
            "Resume: "
            + str(
                last_result["filename"]
            )
        )

        y -= 25


    if "ats_score" in last_result:

        c.drawString(
            50,
            y,
            "ATS Score: "
            + str(
                last_result["ats_score"]
            )
            + "/100"
        )

        y -= 25


    if "domain" in last_result:

        c.drawString(
            50,
            y,
            "Domain: "
            + str(
                last_result["domain"]
            )
        )

        y -= 25


    if "strength" in last_result:

        c.drawString(
            50,
            y,
            "Resume Strength: "
            + str(
                last_result["strength"]
            )
        )

        y -= 35


    # Skills
    c.setFont(
        "Helvetica-Bold",
        12
    )

    c.drawString(
        50,
        y,
        "Detected Skills:"
    )


    y -= 20


    c.setFont(
        "Helvetica",
        10
    )


    skills = last_result.get(
        "skills",
        []
    )


    skill_text = ", ".join(
        skills
    )


    # Simple line wrapping
    lines = wrap_text(
        skill_text,
        90
    )


    for line in lines:

        c.drawString(
            60,
            y,
            line
        )

        y -= 15


    y -= 15


    # Missing skills
    c.setFont(
        "Helvetica-Bold",
        12
    )


    c.drawString(
        50,
        y,
        "Missing Skills:"
    )


    y -= 20


    c.setFont(
        "Helvetica",
        10
    )


    missing = last_result.get(
        "missing_skills",
        []
    )


    missing_text = ", ".join(
        missing
    )


    lines = wrap_text(
        missing_text or "None",
        90
    )


    for line in lines:

        c.drawString(
            60,
            y,
            line
        )

        y -= 15


    y -= 15


    # Recommendations
    c.setFont(
        "Helvetica-Bold",
        12
    )


    c.drawString(
        50,
        y,
        "Recommendations:"
    )


    y -= 20


    c.setFont(
        "Helvetica",
        10
    )


    recommendations = last_result.get(
        "recommendations",
        []
    )


    for recommendation in recommendations:

        lines = wrap_text(
            "• " + recommendation,
            85
        )


        for line in lines:

            c.drawString(
                60,
                y,
                line
            )

            y -= 15


        y -= 5


    c.save()


    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=filename
    )


# ============================================================
# TEXT WRAPPER
# ============================================================

def wrap_text(
    text,
    max_length=90
):

    if not text:

        return [""]


    words = text.split()

    lines = []

    current = ""


    for word in words:

        if len(
            current + " " + word
        ) <= max_length:

            if current:

                current += " " + word

            else:

                current = word

        else:

            lines.append(
                current
            )

            current = word


    if current:

        lines.append(
            current
        )


    return lines


# ============================================================
# DASHBOARD STATS
# ============================================================

@app.route(
    "/api/dashboard-stats",
    methods=["GET"]
)
def dashboard_stats():

    total_resumes = 0
    total_shortlisted = 0
    total_interviews = 0


    for job in jobs:

        total_resumes += len(
            job.get(
                "candidates",
                []
            )
        )


        total_shortlisted += len(
            job.get(
                "shortlisted",
                []
            )
        )


        total_interviews += len(
            job.get(
                "interviews",
                []
            )
        )


    return jsonify({

        "success": True,

        "active_jobs":
        len(jobs),

        "total_resumes":
        total_resumes,

        "shortlisted":
        total_shortlisted,

        "interviews":
        total_interviews

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "message":
        "AI Resume Screening backend is running.",

        "backend":
        "Flask",

        "pdf_support":
        True,

        "docx_support":
        True,

        "recruiter_api":
        True,

        "screening":
        True,

        "top_5_matching":
        True,

        "interview_scheduling":
        True,

        "ai_assistant":
        True

    })


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "error":
        "Requested resource was not found."

    }), 404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success": False,

        "error":
        "Internal server error."

    }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print(
        "AI RESUME SCREENING & SKILLS GAP ANALYSIS"
    )
    print("=" * 65)

    print(
        "Backend: Flask"
    )

    print(
        "PDF Support: Enabled"
    )

    print(
        "DOCX Support: Enabled"
    )

    print(
        "Recruiter API: Enabled"
    )

    print(
        "AI Screening: Enabled"
    )

    print(
        "Top 5 Candidate Matching: Enabled"
    )

    print(
        "Interview Scheduling: Enabled"
    )

    print(
        "AI Assistant: Enabled"
    )

    print(
        "Running at: http://127.0.0.1:5000"
    )

    print(
        "Recruiter: http://127.0.0.1:5000/recruiter.html"
    )

    print(
        "Candidate: http://127.0.0.1:5000/analyzer.html"
    )

    print("=" * 65)
    print()


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )