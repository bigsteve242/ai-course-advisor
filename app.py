# app.py
from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Sample course requirements ---
COURSES = {
    "medicine": ["english", "biology", "chemistry", "physics"],
    "engineering": ["english", "mathematics", "physics", "chemistry"],
    "economics": ["english", "mathematics", "economics", "government"],
    # add more courses here
}

# --- Helper functions ---
def normalize_subjects(subjects):
    return [s.strip().lower() for s in subjects]

def detect_subjects(user_input):
    # simple word-based detection; can expand
    keywords = ["english", "mathematics", "math", "physics", "chemistry", "biology", "government", "economics"]
    detected = [k for k in keywords if k in user_input.lower()]
    # normalize "math" -> "mathematics"
    return ["mathematics" if s == "math" else s for s in detected]

def detect_course(user_input):
    for course in COURSES:
        if course in user_input.lower():
            return course
    return None

def get_required_subjects(course_name):
    return COURSES.get(course_name.lower(), [])

# --- Routes ---
@app.route("/")
def home():
    return "🤖 AI Course Advisor is running! Use the /chat endpoint to talk."

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    
    # Detect subjects + requested course
    user_subjects = normalize_subjects(detect_subjects(user_input))
    course_request = detect_course(user_input)

    system_info = ""
    if course_request:
        required = get_required_subjects(course_request)
        missing = [sub for sub in required if sub not in user_subjects]
        system_info += f"Course: {course_request.capitalize()}\n"
        system_info += f"Required subjects: {', '.join(required)}\n"
        if missing:
            system_info += f"Missing subjects: {', '.join(missing)}\n"
        else:
            system_info += "You have all required subjects!\n"

    if user_subjects:
        system_info += f"User subjects: {', '.join(user_subjects)}\n"

    # AI response
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly academic advisor. "
                        "Help students choose courses based on their subjects.\n"
                        + system_info
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content

    except Exception as e:
        print("🔥 ERROR:", str(e))
        reply = "⚠️ AI error. Try again."

    return jsonify({"response": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)