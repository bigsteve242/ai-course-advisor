from flask import Flask, render_template, request, jsonify
from model import normalize_subjects, get_required_subjects, can_study, recommend_courses
from difflib import get_close_matches
from model import data
import spacy

# Safe spaCy loading (no download needed)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = spacy.blank("en")

app = Flask(__name__)

# Expanded subject recognition
KNOWN_SUBJECTS = [
    "mathematics", "math", "maths",
    "physics", "phy",
    "chemistry", "chem",
    "biology", "bio",
    "economics", "econ",
    "literature", "lit",
    "government", "govt",
    "crs",
    "english"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip().lower()

    # Process input with spaCy
    doc = nlp(user_input)

    # Detect subjects
    user_subjects = []
    for token in doc:
        word = token.text.lower()
        if word in KNOWN_SUBJECTS:
            user_subjects.append(word)

    user_subjects = normalize_subjects(user_subjects)

    # Detect course using fuzzy matching
    matches = get_close_matches(user_input, [c.lower() for c in data['course']], n=1, cutoff=0.6)
    course_request = None
    if matches:
        course_request = data[data['course'].str.lower() == matches[0]]['course'].iloc[0]

    # Generate response
    if course_request and user_subjects:
        if can_study(course_request, user_subjects):
            response = f"✅ You can study {course_request} with your subjects."
        else:
            required = get_required_subjects(course_request)
            response = f"❌ You cannot study {course_request} with your subjects. Required: {', '.join(required)}"
    elif course_request:
        required = get_required_subjects(course_request)
        response = f"To study {course_request}, you need: {', '.join(required)}"
    elif user_subjects:
        courses = recommend_courses(user_subjects)
        if courses:
            response = "Based on your subjects you can study: " + ", ".join(courses)
        else:
            response = "No matching courses found for your subjects."
    else:
        response = "Please tell me your subjects or a course you are interested in."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)