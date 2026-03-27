import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Subject and course logic ---
COURSE_REQUIREMENTS = {
    "medicine": ["english", "biology", "chemistry", "physics"],
    "engineering": ["english", "mathematics", "physics", "chemistry"],
    "economics": ["english", "mathematics", "economics", "government"],
    "computer science": ["english", "mathematics", "physics", "computer science"],
    # Add more courses here
}

SUBJECT_ALIASES = {
    "maths": "mathematics",
    "bio": "biology",
    "cs": "computer science",
    # Add more aliases here
}

def normalize_subjects(subjects):
    return [SUBJECT_ALIASES.get(s.lower(), s.lower()) for s in subjects]

def get_required_subjects(course_name):
    return COURSE_REQUIREMENTS.get(course_name.lower(), [])

def detect_subjects(text):
    words = text.lower().replace(",", " ").split()
    return [w for w in words if w in SUBJECT_ALIASES.values() or w in sum(COURSE_REQUIREMENTS.values(), [])]

def detect_course(text):
    text = text.lower()
    for course in COURSE_REQUIREMENTS.keys():
        if course in text:
            return course
    return None

# --- Root route ---
@app.route("/", methods=["GET"])
def home():
    return "🤖 AI Course Advisor is running! Use the /chat endpoint to talk."

# --- Chat endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    # Detect subjects + course
    user_subjects = normalize_subjects(detect_subjects(user_input))
    course_request = detect_course(user_input)

    # System info for AI
    system_info = ""
    if course_request:
        required = get_required_subjects(course_request)
        missing = [sub for sub in required if sub not in user_subjects]
        system_info += (
            f"\nCourse: {course_request.title()}\n"
            f"Required subjects: {', '.join(required)}\n"
            f"Missing subjects: {', '.join(missing) if missing else 'None'}\n"
        )
    if user_subjects:
        system_info += f"User subjects: {', '.join(user_subjects)}\n"

    # AI Response
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
        reply = "⚠️ AI is temporarily unavailable. Please try again."

    return jsonify({"response": reply})

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)