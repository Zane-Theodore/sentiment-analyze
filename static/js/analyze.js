async function analyze(e) {
    e.preventDefault();

    const text = document.getElementById("text").value.trim();
    if (!text) {
        showError("Vui lòng nhập văn bản để phân tích!");
        return;
    }

    document.getElementById("loading").style.display = "block";
    document.getElementById("analyzeBtn").disabled = true;
    document.getElementById("error").classList.remove("show");
    document.getElementById("result").classList.remove("show");

    try {
        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        if (!res.ok) throw new Error(await res.text());

        const data = await res.json();
        displayResult(data);
    } catch (error) {
        showError("Lỗi phân tích: " + error.message);
    } finally {
        document.getElementById("loading").style.display = "none";
        document.getElementById("analyzeBtn").disabled = false;
    }
}

function displayResult(data) {
    const result = document.getElementById("result");
    const sentiment = data.Sentiment;
    const scores = data.SentimentScore;

    const classes = ["result", `sentiment-${sentiment.toLowerCase()}`];
    const icons = {
        POSITIVE: '<i class="fas fa-smile sentiment-icon"></i>',
        NEGATIVE: '<i class="fas fa-frown sentiment-icon"></i>',
        NEUTRAL: '<i class="fas fa-minus sentiment-icon"></i>',
        MIXED: '<i class="fas fa-question sentiment-icon"></i>',
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

    result.className = classes.join(" ");
    result.classList.add("show");
}

function showError(message) {
    const errorBox = document.getElementById("error");
    errorBox.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    errorBox.classList.add("show");
}
