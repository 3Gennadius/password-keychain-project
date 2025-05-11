// Toggle Navigation Menu for Mobile
function toggleNav() {
    const nav = document.getElementById("myTopnav");
    nav.classList.toggle("responsive");
}

// Leave this completely untouched (Security Score Visualization)
function updateSecurityScore(score) {
    const circle = document.querySelector('.progress-ring__progress');
    const text = document.getElementById("security-score");

    const circumference = 2 * Math.PI * 60;
    const offset = circumference - (score / 100) * circumference;

    circle.style.strokeDashoffset = offset;

    let color;
    if (score < 40) {
        color = "#ff5555"; // Red
    } else if (score < 70) {
        color = "#ffbf47"; // Orange
    } else if (score < 85) {
        color = "#f7d358"; // Yellow
    } else {
        color = "#66bb6a"; // Green
    }

    circle.style.stroke = color;
    text.style.color = color;
    text.textContent = `${score}%`;
    text.style.display = 'block';
    text.style.visibility = 'visible';
}

// Adjust Security Score Colors for Dark Mode
function applyDarkModeToSecurityScore(score) {
    if (!document.documentElement.classList.contains('dark-mode')) return;

    const circle = document.querySelector('.progress-ring__progress');
    const text = document.getElementById("security-score");
    let color;

    if (score < 40) {
        color = "#ff5555";
    } else if (score < 70) {
        color = "#ffbf47";
    } else if (score < 85) {
        color = "#f7d358";
    } else {
        color = "#66bb6a";
    }

    circle.style.stroke = color;
    text.style.color = color;
}

// Initialize on Page Load
document.addEventListener("DOMContentLoaded", () => {
    const scoreEl = document.getElementById("security-score");
    if (scoreEl) {
        const currentScore = parseInt(scoreEl.textContent, 10);
        applyDarkModeToSecurityScore(currentScore);
    }

    const darkCheckbox = document.getElementById("dark-mode-toggle");
    if (darkCheckbox) {
        darkCheckbox.addEventListener("change", () => {
            const score = scoreEl ? parseInt(scoreEl.textContent, 10) : 0;
            applyDarkModeToSecurityScore(score);
        });
    }
});
