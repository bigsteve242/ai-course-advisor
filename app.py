import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import difflib

app = Flask(__name__)

# --- OpenAI Setup ---
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- Courses ---
COURSES = {
    "medicine": ["english", "biology", "chemistry", "physics"],
    "engineering": ["english", "mathematics", "physics", "chemistry"],
    "economics": ["english", "mathematics", "economics", "government"],
    "computer science": ["english", "mathematics", "physics", "chemistry"],
    "law": ["english", "literature", "government", "crs"],
    "nursing": ["english", "biology", "chemistry", "physics"],
    "accounting": ["english", "mathematics", "economics", "commerce"],
}

ALL_SUBJECTS = list(set(sum(COURSES.values(), [])))

# --- Fix typos (AI-like behavior) ---
def correct_word(word):
    match = difflib.get_close_matches(word, ALL_SUBJECTS, n=1, cutoff=0.6)
    return match[0] if match else word

# --- Detect subjects ---
def detect_subjects(text):
    words = text.lower().replace(",", " ").split()
    subjects = []

    for word in words:
        word = correct_word(word)
        if word in ALL_SUBJECTS:
            subjects.append(word)

    return list(set(subjects))

# --- Detect course ---
def detect_course(text):
    text = text.lower()
    for course in COURSES.keys():
        if course in text:
            return course
    return None

# --- Recommend courses ---
def recommend_courses(user_subjects):
    matches = []

    for course, required in COURSES.items():
        if all(sub in user_subjects for sub in required):
            matches.append(course)

    return matches

# --- HOME ---
@app.route("/")
def home():
    return render_template("index.html")

# --- CHAT ---
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    user_subjects = detect_subjects(user_input)
    course_request = detect_course(user_input)

    system_info = ""

    if course_request:
        required = COURSES[course_request]
        missing = [s for s in required if s not in user_subjects]

        system_info += f"\nCourse: {course_request}\n"
        system_info += f"Required: {', '.join(required)}\n"
        system_info += f"Missing: {', '.join(missing) if missing else 'None'}\n"

    if user_subjects:
        system_info += f"\nUser subjects: {', '.join(user_subjects)}\n"

    # Recommend courses automatically
    recommendations = recommend_courses(user_subjects)
    if recommendations:
        system_info += f"\nPossible courses: {', '.join(recommendations)}\n"

    # --- AI ---
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smart Nigerian academic advisor. "
                        "Guide students on JAMB subject combinations and courses. "
                        "Be friendly, conversational, and helpful.\n"
                        + system_info
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
    print("🔥 ERROR:", str(e))
    reply = f"⚠️ Error: {str(e)}"

    return jsonify({"response": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)