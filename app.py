from flask import Flask, request, jsonify, render_template
import os

# OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)

# ----- Courses and required subjects -----
COURSES = {
    "medicine": ["english", "biology", "chemistry", "physics"],
    "engineering": ["english", "mathematics", "physics", "chemistry"],
    "economics": ["english", "mathematics", "economics", "government"],
    "law": ["english", "government", "literature", "history"],
    "computer science": ["english", "mathematics", "physics", "computer science"],
    "accounting": ["english", "mathematics", "accounting", "economics"],
    "biology": ["english", "biology", "chemistry"],
    "chemistry": ["english", "chemistry", "biology"],
    "physics": ["english", "physics", "mathematics"],
}

# ----- Helper functions -----
def normalize_subjects(subjects):
    return [s.lower().strip() for s in subjects]

def detect_subjects(text):
    """Detect subjects mentioned in user input"""
    words = text.lower().split()
    detected = [subj for subj in sum(COURSES.values(), []) if subj in words]
    return list(set(detected))

def detect_course(text):
    """Detect course mentioned in user input"""
    for course in COURSES.keys():
        if course in text.lower():
            return course
    return None

def recommend_courses(user_subjects):
    """Return courses user can study based on subjects already had"""
    possible = []
    for course, required in COURSES.items():
        match_count = sum(1 for subj in required if subj.lower() in user_subjects)
        if match_count > 0:
            missing = [subj for subj in required if subj.lower() not in user_subjects]
            possible.append({
                "course": course,
                "matched": match_count,
                "missing": missing
            })
    # Sort by most matches first
    possible.sort(key=lambda x: x["matched"], reverse=True)
    return possible

# ----- Routes -----
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    # Detect subjects + course
    user_subjects = detect_subjects(user_input)
    user_subjects = normalize_subjects(user_subjects)
    course_request = detect_course(user_input)

    # AI prompt preparation
    system_info = ""
    if course_request:
        required = COURSES.get(course_request, [])
        system_info += f"\nCourse: {course_request.title()}\nRequired subjects: {', '.join(required)}\n"

    if user_subjects:
        system_info += f"User subjects: {', '.join(user_subjects)}\n"

    # Add recommended courses
    if user_subjects:
        courses_suggested = recommend_courses(user_subjects)
        if courses_suggested:
            reply_lines = []
            for c in courses_suggested[:5]:  # top 5 suggestions
                if c["missing"]:
                    reply_lines.append(
                        f"📚 {c['course'].title()} - Missing: {', '.join(c['missing'])}"
                    )
                else:
                    reply_lines.append(f"✅ You can study {c['course'].title()}")
            system_info += "\n".join(reply_lines)
        else:
            system_info += "❌ No matching courses found. Try adding more subjects."

    # Call AI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly and knowledgeable academic advisor chatbot. "
                        "Help students choose courses based on their subjects. "
                        "Be clear and educational."
                        + system_info
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content

    except Exception as e:
        reply = "⚠️ AI is temporarily unavailable. Please try again."

    return jsonify({"response": reply})

# ----- Run app -----
if __name__ == "__main__":
    app.run(debug=True)