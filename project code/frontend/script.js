// Toggle Navigation Menu for Mobile
function toggleNav() {
    const nav = document.getElementById("myTopnav");
    nav.classList.toggle("responsive");
  }

function updateSecurityScore(score) {
    const circle = document.querySelector('.progress-ring__progress');
    const text = document.getElementById("security-score");

    // Calculate stroke-dashoffset (lower value = more filled)
    const circumference = 2 * Math.PI * 60;
    const offset = circumference - (score / 100) * circumference;

    // Apply offset for animation
    circle.style.strokeDashoffset = offset;

    // Change text percentage
    text.textContent = score + "%";

    // Change color dynamically based on score
    let color;
    if (score < 40) {
        color = "#ff3e3e"; // Red (Weak)
    } else if (score < 70) {
        color = "#ffae42"; // Orange (Moderate)
    } else if (score < 85) {
        color = "#f1c40f"; // Yellow (Good)
    } else {
        color = "#4CAF50"; // Green (Strong)
    }
    
    circle.style.stroke = color;
    text.style.color = color;
}

// Example Usage:
updateSecurityScore(45); // Change dynamically based on password strength