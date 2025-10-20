from flask import Flask, request, jsonify, render_template_string
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

HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Phân tích Cảm xúc - AWS Comprehend</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .content {
            padding: 40px;
        }

        .input-group {
            margin-bottom: 30px;
        }

        .input-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #374151;
            font-size: 1.1em;
        }

        textarea {
            width: 100%;
            height: 150px;
            padding: 20px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: all 0.3s ease;
        }

        textarea:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .analyze-btn {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            padding: 16px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
        }

        .analyze-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4f46e5;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .result {
            display: none;
            margin-top: 30px;
            padding: 25px;
            border-radius: 12px;
            background: #f8fafc;
            border-left: 5px solid;
        }

        .result.show {
            display: block;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .sentiment-positive {
            border-left-color: #10b981;
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        }

        .sentiment-negative {
            border-left-color: #ef4444;
            background: linear-gradient(135deg, #fee2e2, #fecaca);
        }

        .sentiment-neutral {
            border-left-color: #f59e0b;
            background: linear-gradient(135deg, #fef3c7, #fde68a);
        }

        .sentiment-mixed {
            border-left-color: #8b5cf6;
            background: linear-gradient(135deg, #ede9fe, #ddd6fe);
        }

        .result-title {
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .sentiment-icon {
            font-size: 1.5em;
        }

        .scores-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .score-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .score-label {
            font-size: 0.9em;
            color: #6b7280;
            margin-bottom: 5px;
        }

        .score-value {
            font-size: 1.3em;
            font-weight: 700;
            color: #1f2937;
        }

        .error {
            display: none;
            margin-top: 20px;
            padding: 20px;
            border-radius: 12px;
            background: #fee2e2;
            border-left: 5px solid #ef4444;
            color: #dc2626;
        }

        .error.show {
            display: block;
            animation: slideIn 0.5s ease;
        }

        @media (max-width: 768px) {
            .content { padding: 20px; }
            .header h1 { font-size: 2em; }
            .scores-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-brain"></i> Phân tích Cảm xúc</h1>
            <p>Powered by AWS Comprehend Medical</p>
        </div>
        
        <div class="content">
            <form onsubmit="return analyze(event)">
                <div class="input-group">
                    <label for="text"><i class="fas fa-edit"></i> Nhập đoạn văn bản (Tiếng Anh):</label>
                    <textarea 
                        id="text" 
                        placeholder="Ví dụ: I love this product! It's amazing and works perfectly..."
                        required
                    ></textarea>
                </div>
                
                <button type="submit" class="analyze-btn" id="analyzeBtn">
                    <i class="fas fa-magic"></i> Phân tích Cảm xúc
                </button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Đang phân tích...</p>
                </div>
            </form>
            
            <div id="error" class="error"></div>
            <div id="result" class="result"></div>
        </div>
    </div>

    <script>
        async function analyze(e) {
            e.preventDefault();
            
            const text = document.getElementById("text").value.trim();
            if (!text) {
                showError("Vui lòng nhập văn bản để phân tích!");
                return;
            }
            
            // Show loading
            document.getElementById("loading").style.display = "block";
            document.getElementById("analyzeBtn").disabled = true;
            document.getElementById("error").classList.remove("show");
            document.getElementById("result").classList.remove("show");
            
            try {
                const res = await fetch("/analyze", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text})
                });
                
                if (!res.ok) {
                    throw new Error(await res.text());
                }
                
                const data = await res.json();
                displayResult(data);
                
            } catch (error) {
                showError("Lỗi phân tích: " + error.message);
            } finally {
                // Hide loading
                document.getElementById("loading").style.display = "none";
                document.getElementById("analyzeBtn").disabled = false;
            }
        }
        
        function displayResult(data) {
            const result = document.getElementById("result");
            const sentiment = data.Sentiment;
            const scores = data.SentimentScore;
            
            // Set sentiment class and icon
            const classes = ['result', `sentiment-${sentiment.toLowerCase()}`];
            const icons = {
                POSITIVE: '<i class="fas fa-smile sentiment-icon"></i>',
                NEGATIVE: '<i class="fas fa-frown sentiment-icon"></i>',
                NEUTRAL: '<i class="fas fa-minus sentiment-icon"></i>',
                MIXED: '<i class="fas fa-question sentiment-icon"></i>'
            };
            
            result.innerHTML = `
                <div class="result-title">
                    ${icons[sentiment]} ${sentiment}
                </div>
                <div class="scores-grid">
                    <div class="score-card">
                        <div class="score-label">Positive</div>
                        <div class="score-value">${(scores.Positive * 100).toFixed(1)}%</div>
                    </div>
                    <div class="score-card">
                        <div class="score-label">Negative</div>
                        <div class="score-value">${(scores.Negative * 100).toFixed(1)}%</div>
                    </div>
                    <div class="score-card">
                        <div class="score-label">Neutral</div>
                        <div class="score-value">${(scores.Neutral * 100).toFixed(1)}%</div>
                    </div>
                    <div class="score-card">
                        <div class="score-label">Mixed</div>
                        <div class="score-value">${(scores.Mixed * 100).toFixed(1)}%</div>
                    </div>
                </div>
            `;
            
            result.className = classes.join(' ');
            result.classList.add("show");
        }
        
        function showError(message) {
            document.getElementById("error").innerHTML = `
                <i class="fas fa-exclamation-triangle"></i> ${message}
            `;
            document.getElementById("error").classList.add("show");
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

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