import os
import pdfplumber
import requests
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -------------------------------
# Flask app setup
# -------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/extract-text", methods=["POST"])
def extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    extracted_text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""

    return jsonify({"text": extracted_text})

@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.json
        resume_text = data.get("resume_text", "")

        if not resume_text:
            return jsonify({"error": "No resume text provided"}), 400

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"parts": [{"text": f"Generate 5 interview questions based on this resume:\n\n{resume_text}"}]}
            ]
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            return jsonify({"error": "Gemini API error", "details": response.text}), 500

        result = response.json()
        questions = result.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")

        return jsonify({"questions": questions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
