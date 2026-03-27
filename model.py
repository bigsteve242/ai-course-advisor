import csv

DATA_FILE = "data/courses.csv"

data = []

# Load CSV manually
with open(DATA_FILE, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)


def normalize_subjects(subjects):
    return [s.strip().lower() for s in subjects]


def get_required_subjects(course_name):
    for row in data:
        if row["Course"].lower() == course_name.lower():
            return [s.strip().lower() for s in row["RequiredSubjects"].split(",")]
    return []


def can_study(course_name, user_subjects):
    required = get_required_subjects(course_name)
    return all(sub in user_subjects for sub in required)


def recommend_courses(user_subjects):
    user_subjects = [s.lower() for s in user_subjects]
    courses = []

    for row in data:
        required = [s.strip().lower() for s in row["RequiredSubjects"].split(",")]

        if all(r in user_subjects for r in required):
            courses.append(row["Course"])

    return courses