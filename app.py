from flask import Flask, render_template, request, jsonify
import spacy

from model import normalize_subjects, get_required_subjects, can_study, recommend_courses, data

# ------------------ Load spaCy safely ------------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# ------------------ App setup ------------------
app = Flask(__name__)

# Known subjects for detection
KNOWN_SUBJECTS = [
    "mathematics", "math", "physics", "chemistry", "biology",
    "economics", "literature", "government", "crs", "english", "bio"
]

# ------------------ Routes ------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").lower().strip()

    # -------- Detect subjects using spaCy --------
    doc = nlp(user_input)
    user_subjects = []

    for token in doc:
        if token.text.lower() in KNOWN_SUBJECTS:
            user_subjects.append(token.text.lower())

    user_subjects = normalize_subjects(user_subjects)

    # -------- Detect course --------
    course_request = None

    for row in data:
        if row["Course"].lower() in user_input:
            course_request = row["Course"]
            break

    # -------- Generate response --------
    if course_request and user_subjects:
        if can_study(course_request, user_subjects):
            response = f"✅ You can study {course_request} with your subjects."
        else:
            required = get_required_subjects(course_request)
            missing = [sub for sub in required if sub not in user_subjects]

            response = (
                f"❌ You cannot study {course_request}.\n"
                f"Required subjects: {', '.join(required)}\n"
                f"Missing: {', '.join(missing)}"
            )

    elif course_request:
        required = get_required_subjects(course_request)
        response = f"📚 To study {course_request}, you need: {', '.join(required)}"

    elif user_subjects:
        courses = recommend_courses(user_subjects)

        if courses:
            response = "🎓 Based on your subjects, you can study:\n" + ", ".join(courses)
        else:
            response = "❌ No courses match your subjects."

    else:
        response = "🤖 Please tell me your subjects or the course you're interested in."

    return jsonify({"response": response})


# ------------------ Run app ------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)