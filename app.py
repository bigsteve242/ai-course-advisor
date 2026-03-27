from flask import Flask, render_template, request, jsonify
from model import normalize_subjects, get_required_subjects, can_study, recommend_courses, data

app = Flask(__name__)

# Known subjects
KNOWN_SUBJECTS = [
    "mathematics", "math", "physics", "chemistry", "biology",
    "economics", "literature", "government", "crs", "english", "bio"
]

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").lower().strip()

    # -------- Detect subjects (NO spaCy) --------
    user_subjects = [sub for sub in KNOWN_SUBJECTS if sub in user_input]
    user_subjects = normalize_subjects(user_subjects)

    # -------- Detect course --------
    course_request = None
    for row in data:
        if row["Course"].lower() in user_input:
            course_request = row["Course"]
            break

    # -------- Response logic --------
    if course_request and user_subjects:
        if can_study(course_request, user_subjects):
            response = f"✅ You can study {course_request}."
        else:
            required = get_required_subjects(course_request)
            missing = [sub for sub in required if sub not in user_subjects]

            response = (
                f"❌ You cannot study {course_request}.\n"
                f"Required: {', '.join(required)}\n"
                f"Missing: {', '.join(missing)}"
            )

    elif course_request:
        required = get_required_subjects(course_request)
        response = f"📚 To study {course_request}, you need: {', '.join(required)}"

    elif user_subjects:
        courses = recommend_courses(user_subjects)

        if courses:
            response = "🎓 You can study:\n" + ", ".join(courses)
        else:
            response = "❌ No matching courses found."

    else:
        response = "🤖 Tell me your subjects or desired course."

    return jsonify({"response": response})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)