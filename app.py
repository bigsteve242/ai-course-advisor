# app.py
from flask import Flask, render_template, request, jsonify
from model import normalize_subjects, get_required_subjects, can_study, recommend_courses
import spacy
from difflib import get_close_matches

app = Flask(__name__)

# Load spaCy model safely
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Known subjects for detection
KNOWN_SUBJECTS = [
    "mathematics", "math", "physics", "chemistry", "biology",
    "economics", "literature", "government", "crs", "english", "bio"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    
    # Detect subjects
    doc = nlp(user_input)
    user_subjects = [token.text.lower() for token in doc if token.text.lower() in KNOWN_SUBJECTS]
    user_subjects = normalize_subjects(user_subjects)

    # Detect course from input
    matches = get_close_matches(user_input.lower(), [c.lower() for c in data['course']], n=1, cutoff=0.6)
    course_request = matches[0] if matches else None

    # Generate response
    if course_request and user_subjects:
        if can_study(course_request, user_subjects):
            description = data[data['course'].str.lower() == course_request]['description'].iloc[0]
            response = f"✅ You can study {course_request.title()}.\n💡 About this course: {description}"
        else:
            required = get_required_subjects(course_request)
            response = f"❌ You cannot study {course_request.title()} with your subjects ({', '.join(user_subjects)}).\n" \
                       f"Required subjects: {', '.join(required)}"
    elif course_request:
        required = get_required_subjects(course_request)
        description = data[data['course'].str.lower() == course_request]['description'].iloc[0]
        response = f"To study {course_request.title()}, you need: {', '.join(required)}\n💡 About this course: {description}"
    elif user_subjects:
        courses = recommend_courses(user_subjects)
        if courses:
            response = "Based on your subjects, you can study:\n" + "\n".join(courses)
        else:
            response = "No matching courses found for your subjects."
    else:
        response = "Please tell me your subjects or a course you are interested in."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)