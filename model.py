import pandas as pd
from difflib import get_close_matches

# Load dataset
DATA_FILE = "dataset.csv"
data = pd.read_csv(DATA_FILE)

# Subject synonyms for normalization
SUBJECT_SYNONYMS = {
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "biology": "Biology",
    "bio": "Biology",
    "economics": "Economics",
    "literature": "Literature",
    "government": "Government",
    "crs": "CRS",
    "english": "English"
}

def normalize_subjects(subjects):
    """Standardize subject names and remove duplicates."""
    return list({SUBJECT_SYNONYMS.get(s.lower(), s.capitalize()) for s in subjects})

def get_required_subjects(course_name):
    """Return required subjects for a course (fuzzy matching allowed)."""
    matches = get_close_matches(course_name.lower(), data['course'].str.lower(), n=1, cutoff=0.6)
    if not matches:
        return []
    row = data[data['course'].str.lower() == matches[0]].iloc[0]
    return [s.strip() for s in row['subjects'].split()]

def can_study(course_name, user_subjects):
    """Check if the student can study the course with given subjects."""
    required = [s.lower() for s in get_required_subjects(course_name) if s.lower() != "english"]
    user_norm = [s.lower() for s in normalize_subjects(user_subjects)]
    return all(sub in user_norm for sub in required)

def recommend_courses(user_subjects, threshold=0.8):
    """Return a list of courses matching user's subjects."""
    user_norm = [s.lower() for s in normalize_subjects(user_subjects)]
    recommendations = []
    for _, row in data.iterrows():
        required = [s.lower() for s in row['subjects'].split() if s.lower() != "english"]
        match_ratio = sum(1 for sub in required if sub in user_norm) / len(required)
        if match_ratio >= threshold:
            recommendations.append(row['course'])
    return recommendations