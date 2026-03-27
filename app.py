import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client using your environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Example course requirements
COURSES = {
    "medicine": ["english", "biology", "chemistry", "physics"],
    "economics": ["english", "mathematics", "economics", "government"],
    "physics": ["english", "mathematics", "physics", "chemistry"],
    "computer science": ["english", "mathematics", "physics", "chemistry"],
    # Add more courses here
}

# Utility functions
def normalize_subjects(subjects):
    return [s.lower().strip() for s in subjects]

def detect_subjects(user_input):
    words = user_input.lower().split()
    # Filter words that match known subjects
    known_subjects = ["english", "mathematics", "physics", "chemistry", "biology", "government", "economics"]
    return [w for w in words if w in known_subjects]

def detect_course(user_input):
    for course in COURSES.keys():
        if course in user_input.lower():
            return course
    return None

def get_required_subjects(course):
    return COURSES.get(course, [])

# Root route
@app.route("/")
def index():
    return "🟢 AI Chatbot is live! Use POST /chat to interact."

# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    # Detect subjects and requested course
    user_subjects = normalize_subjects(detect_subjects(user_input))
    course_request = detect_course(user_input)

    system_info = ""
    missing_subjects = []

    if course_request:
        required = get_required_subjects(course_request)
        missing_subjects = [s for s in required if s not in user_subjects]
        system_info += f"\nCourse: {course_request.title()}\nRequired subjects: {', '.join(required)}\n"
        if missing_subjects:
            system_info += f"Missing subjects: {', '.join(missing_subjects)}\n"
        else:
            system_info += "✅ You have all required subjects!\n"

    if user_subjects:
        system_info += f"User subjects: {', '.join(user_subjects)}\n"

    # AI Response using OpenAI GPT-4o-mini
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intelligent academic advisor chatbot. "
                        "Help students choose courses based on their subjects. "
                        "Be clear, friendly, and educational."
                        + system_info
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        reply = "⚠️ AI is temporarily unavailable. Please try again."

    return jsonify({"response": reply})

# Run app
if __name__ == "__main__":
    app.run(debug=True)