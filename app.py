from flask import Flask, request, jsonify
import os
import openai

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Example subjects database
SUBJECTS_DB = {
    "Mathematics": ["English", "Mathematics", "Economics", "Government"],
    "Physics": ["English", "Mathematics", "Physics", "Chemistry"],
    "Medicine": ["English", "Biology", "Chemistry", "Physics"],
}

# Detect subjects from user input
def detect_subjects(text):
    subjects = []
    for subject in ["Mathematics", "Physics", "Chemistry", "Biology", "Economics", "English", "Government"]:
        if subject.lower() in text.lower():
            subjects.append(subject)
    return subjects

def normalize_subjects(subjects):
    return list(set(subjects))  # remove duplicates

def detect_course(text):
    for course in SUBJECTS_DB.keys():
        if course.lower() in text.lower():
            return course
    return None

def get_required_subjects(course):
    return SUBJECTS_DB.get(course, [])

# API endpoint for chatbot
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    # Detect subjects + course
    user_subjects = detect_subjects(user_input)
    user_subjects = normalize_subjects(user_subjects)
    course_request = detect_course(user_input)

    system_info = ""

    if course_request:
        required = get_required_subjects(course_request)
        system_info += f"\nCourse: {course_request}\nRequired subjects: {', '.join(required)}\n"

    if user_subjects:
        system_info += f"User subjects: {', '.join(user_subjects)}\n"

    # AI Response using OpenAI
    try:
        response = openai.chat.completions.create(
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
        print("OpenAI Error:", e)
        reply = "⚠️ AI is temporarily unavailable. Please try again."

    return jsonify({"response": reply})

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))