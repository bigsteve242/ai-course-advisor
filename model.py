# model.py
import pandas as pd

# Load the CSV
DATA_FILE = "data/courses.csv"  # Ensure your CSV is saved here
data = pd.read_csv(DATA_FILE)

# Normalize subjects to lowercase for comparison
def normalize_subjects(subjects):
    return [s.lower().strip() for s in subjects]

# Get required subjects for a course
def get_required_subjects(course_name):
    row = data[data['course'].str.lower() == course_name.lower()]
    if not row.empty:
        return [sub.strip().lower() for sub in row['required_subjects'].iloc[0].split(',')]
    return []

# Check if user can study the course
def can_study(course_name, user_subjects):
    required = get_required_subjects(course_name)
    return all(r in user_subjects for r in required)

# Recommend courses based on user's subjects
def recommend_courses(user_subjects):
    user_subjects = normalize_subjects(user_subjects)
    recommendations = []
    for _, row in data.iterrows():
        required = [s.strip().lower() for s in row['required_subjects'].split(',')]
        if all(r in user_subjects for r in required):
            recommendations.append(f"{row['course']} - {row['description']}")
    return recommendations