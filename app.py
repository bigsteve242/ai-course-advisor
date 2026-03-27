from flask import Flask, render_template, request, jsonify
from difflib import get_close_matches
from model import normalize_subjects, get_required_subjects, can_study, recommend_courses, data

app = Flask(__name__)

# ------------------ Known subjects ------------------
KNOWN_SUBJECTS = [
    "mathematics", "math", "physics", "chemistry", "biology",
    "economics", "literature", "government", "crs", "english"
]

# ------------------ Detect subjects (SMART) ------------------
def detect_subjects(user_input):
    words = user_input.lower().split()
    detected = []

    for word in words:
        if word in KNOWN_SUBJECTS:
            detected.append(word)
        else:
            match = get_close_matches(word, KNOWN_SUBJECTS, n=1, cutoff=0.7)
            if match:
                detected.append(match[0])

    return list(set(detected))


# ------------------ Detect course (SMART) ------------------
def detect_course(user_input):
    courses = [row["Course"] for row in data]
    matches = get_close_matches(user_input.lower(), [c.lower() for c in courses], n=1, cutoff=0.5)

    if matches:
        for c in courses:
            if c.lower() == matches[0]:
                return c
    return None


# ------------------ Routes ------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    # Detect subjects and course
    user_subjects = detect_subjects(user_input)
    user_subjects = normalize_subjects(user_subjects)
    course_request = detect_course(user_input)

    # ------------------ Smart Response Logic ------------------
    if course_request and user_subjects:
        if can_study(course_request, user_subjects):
            response = f"✅ Yes! You can study {course_request} with your subjects."
        else:
            required = get_required_subjects(course_request)
            missing = [sub for sub in required if sub not in user_subjects]

            response = (
                f"❌ You cannot study {course_request}.\n"
                f"Required subjects: {', '.join(required)}\n"
                f"Missing subjects: {', '.join(missing)}"
            )

    elif course_request:
        required = get_required_subjects(course_request)

        if required:
            response = (
                f"📚 To study {course_request}, you need:\n"
                f"{', '.join(required)}"
            )
        else:
            response = f"🤔 I don't have data for {course_request} yet."

    elif user_subjects:
        courses = recommend_courses(user_subjects)

        if courses:
            response = (
                "🎓 Based on your subjects, you can study:\n"
                + ", ".join(courses[:10])
            )
        else:
            response = "❌ No matching courses found. Try adding more subjects."

    else:
        response = (
            "🤖 I didn’t understand.\n"
            "👉 Try:\n"
            "- 'I have maths, physics, chemistry'\n"
            "- 'Can I study medicine with biology and chemistry?'"
        )

    return jsonify({"response": response})


# ------------------ Run App ------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)