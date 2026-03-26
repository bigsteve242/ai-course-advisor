import os
from flask import Flask, render_template, request
import pandas as pd
import spacy
from spacy.cli import download

# Ensure spaCy model is installed
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Path to CSV
DATA_FILE = os.path.join("data", "courses.csv")
data = pd.read_csv(DATA_FILE)

app = Flask(__name__)

# Import your functions from model.py
from model import normalize_subjects, get_required_subjects, can_study, recommend_courses

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        subjects = request.form.get("subjects", "")
        subjects = normalize_subjects(subjects)
        result = recommend_courses(subjects)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)