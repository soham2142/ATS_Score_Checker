from flask import Flask, render_template, request
import pdfplumber
import docx
import re

app = Flask(__name__)

def extract_text(file):
    text = ""
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text
    return text.lower()

def analyze(resume_text, jd_text):
    resume_words = set(re.findall(r'\b\w+\b', resume_text))
    jd_words = set(re.findall(r'\b\w+\b', jd_text))

    matched = resume_words & jd_words
    missing = list(jd_words - resume_words)

    score = int((len(matched) / len(jd_words)) * 100) if jd_words else 0

    feedback = []

    # Skills mismatch
    if missing:
        feedback.append({
            "title": "Skills mismatch detected",
            "message": "Your resume lacks several skills mentioned in the job description.",
            "details": missing[:8],
            "suggestion": (
                "Add these skills in your Skills section or naturally mention them "
                "inside project and experience descriptions."
            )
        })

    # Job fit warning
    if score < 60:
        feedback.append({
            "title": "Low job-role alignment",
            "message": (
                "Your resume content does not strongly align with the target job role."
            ),
            "details": [],
            "suggestion": (
                "Customize your resume for this role by mirroring keywords, tools, "
                "and responsibilities from the job description."
            )
        })

    # Good match message
    if score >= 80:
        feedback.append({
            "title": "Strong ATS compatibility",
            "message": "Your resume aligns well with the job description.",
            "details": [],
            "suggestion": (
                "Minor keyword tuning and quantified achievements can further "
                "improve your chances."
            )
        })

    return score, feedback

@app.route("/", methods=["GET", "POST"])
def index():
    show_report = False
    score = 0
    feedback = []

    if request.method == "POST":
        resume = request.files.get("resume")
        jd = request.form.get("jd")

        if resume and jd:
            resume_text = extract_text(resume)
            score, feedback = analyze(resume_text, jd.lower())
            show_report = True

    return render_template(
        "index.html",
        show_report=show_report,
        score=score,
        feedback=feedback
    )

if __name__ == "__main__":
    app.run(debug=True)
