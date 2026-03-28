import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)

# --- OpenAI Setup ---
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set in environment variables")

client = OpenAI(api_key=api_key)

# --- Course Requirements ---
COURSES = {
    "medicine": ["english", "biology", "chemistry", "physics"],
    "engineering": ["english", "mathematics", "physics", "chemistry"],
    "economics": ["english", "mathematics", "economics", "government"],
    "computer science": ["english", "mathematics", "physics", "chemistry"],
    "law": ["english", "literature", "government", "crs"],
    "nursing": ["english", "biology", "chemistry", "physics"],
    "accounting": ["english", "mathematics", "economics", "commerce"],
}

# --- Subject Aliases ---
ALIASES = {
    "maths": "mathematics",
    "bio": "biology",
    "chem": "chemistry",
    "phy": "physics",
    "eng": "english",
    "econ": "economics",
    "govt": "government",
    "lit": "literature"
}

# --- Detect Subjects ---
def detect_subjects(text):
    words = text.lower().replace(",", " ").split()
    subjects = []

    all_subjects = set(sum(COURSES.values(), []))

    for word in words:
        word = ALIASES.get(word, word)
        if word in all_subjects:
            subjects.append(word)

    return list(set(subjects))

# --- Detect Course ---
def detect_course(text):
    text = text.lower()
    for course in COURSES.keys():
        if course in text:
            return course
    return None

# --- HOME ROUTE (UI) ---
@app.route("/")
def home():
    return render_template("index.html")

# --- CHAT ROUTE ---
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    user_subjects = detect_subjects(user_input)
    course_request = detect_course(user_input)

    system_info = ""

    if course_request:
        required = COURSES[course_request]
        missing = [s for s in required if s not in user_subjects]

        system_info += f"\nCourse: {course_request}\n"
        system_info += f"Required subjects: {', '.join(required)}\n"
        system_info += f"Missing subjects: {', '.join(missing) if missing else 'None'}\n"

    if user_subjects:
        system_info += f"User subjects: {', '.join(user_subjects)}\n"

    # --- AI RESPONSE ---
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smart academic advisor chatbot. "
                        "Guide students on what courses they can study based on their subjects. "
                        "Be friendly, clear, and helpful.\n"
                        + system_info
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print("Error:", e)
        reply = "⚠️ AI is temporarily unavailable. Please try again."

    return jsonify({"response": reply})


# --- RUN APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)