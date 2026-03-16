import spacy
from model import normalize_subjects, get_required_subjects, can_study, recommend_courses

nlp = spacy.load("en_core_web_sm")

# Known subjects for token detection
KNOWN_SUBJECTS = [
    "mathematics", "math", "physics", "chemistry", "biology",
    "economics", "literature", "government", "crs", "english", "bio"
]

def main():
    print("=== University Course Advisor ===")
    print("Type your subjects or a course name to get advice.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Detect subjects
        doc = nlp(user_input)
        user_subjects = [token.text for token in doc if token.text.lower() in KNOWN_SUBJECTS]
        user_subjects = normalize_subjects(user_subjects)

        # Detect course using fuzzy matching
        from difflib import get_close_matches
        from model import data
        matches = get_close_matches(user_input.lower(), [c.lower() for c in data['course']], n=1, cutoff=0.6)
        course_request = data[data['course'].str.lower() == matches[0]]['course'].iloc[0] if matches else None

        # Generate response
        if course_request and user_subjects:
            if can_study(course_request, user_subjects):
                print(f"Advisor: ✅ You can study {course_request} with your subjects.")
            else:
                required = get_required_subjects(course_request)
                print(f"Advisor: ❌ You cannot study {course_request} with your subjects.")
                print("Required subjects:", ", ".join(required))
        elif course_request:
            required = get_required_subjects(course_request)
            print(f"Advisor: To study {course_request}, you need: {', '.join(required)}")
        elif user_subjects:
            courses = recommend_courses(user_subjects)
            if courses:
                print("Advisor: Based on your subjects you can study:")
                for c in courses:
                    print("-", c)
            else:
                print("Advisor: No matching courses found for your subjects.")
        else:
            print("Advisor: Please tell me your subjects or a course you are interested in.")

if __name__ == "__main__":
    main()