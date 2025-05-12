document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const errorMessage = document.getElementById('error-message');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorMessage.textContent = '';

    const formData = new FormData(form);
    const username = formData.get('username')?.trim();
    const email = formData.get('email')?.trim();
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');

    // Client-Side Validations 
    if (!username || username.length < 3) {
      errorMessage.textContent = 'Username must be at least 3 characters long.';
      errorMessage.style.color = 'red';
      return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      errorMessage.textContent = 'Please enter a valid email address.';
      errorMessage.style.color = 'red';
      return;
    }

    if (password.length < 8) {
      errorMessage.textContent = 'Password must be at least 8 characters long.';
      errorMessage.style.color = 'red';
      return;
    }

    if (password !== confirmPassword) {
      errorMessage.textContent = 'Passwords do not match.';
      errorMessage.style.color = 'red';
      return;
    }

    // Optional: Password Strength Validation (at least 1 uppercase, 1 number)
    const strongPasswordPattern = /^(?=.*[A-Z])(?=.*\d).+$/;
    if (!strongPasswordPattern.test(password)) {
      errorMessage.textContent = 'Password must contain at least one uppercase letter and one number.';
      errorMessage.style.color = 'red';
      return;
    }

    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });

      const result = await response.json();

      if (response.ok && result.success) {
        window.location.href = result.redirect_url || '/login';
      } else {
        errorMessage.textContent = result.message || 'Registration failed. Please check your inputs.';
        errorMessage.style.color = 'red';
      }
    } catch (error) {
      errorMessage.textContent = 'Server error. Please try again later.';
      errorMessage.style.color = 'red';
    }
  });
});
