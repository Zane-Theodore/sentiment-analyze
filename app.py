from flask import Flask, request, jsonify, render_template
import boto3
import os
from dotenv import load_dotenv

# Load key từ file .env
load_dotenv()

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_REGION", "ap-southeast-1")

# Tạo client AWS Comprehend
comprehend = boto3.client(
    'comprehend',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.json.get("text", "")
    if not text.strip():
        return jsonify({"error": "Vui lòng nhập văn bản"}), 400

    try:
        result = comprehend.detect_sentiment(Text=text, LanguageCode="en")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
