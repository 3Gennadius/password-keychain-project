document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const errorMessage = document.getElementById('error-message');

  form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission

    // Clear previous messages
    errorMessage.textContent = '';

    // Collect form data
    const formData = new FormData(form);

    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        body: formData,
      });

      if (response.redirected && response.url.includes('register.html')) {
    errorMessage.textContent = 'Pssswords do not match or do not meet security standards, please try again';
    return;
    }

      if (response.redirected) {
        // Successful registration, backend redirects to login
        window.location.href = response.url;
        return;
      }

      const responseText = await response.text();

      // Attempt to extract flash messages from HTML response
      const parser = new DOMParser();
      const doc = parser.parseFromString(responseText, 'text/html');
      const flashMessage = doc.querySelector('.flash-message, #flash, .alert, .error, .success');

      if (flashMessage) {
        errorMessage.textContent = flashMessage.textContent.trim();
      } else {
        // Generic fallback
        errorMessage.textContent = 'Registration failed. Please check your input and try again.';
      }

    } catch (error) {
      console.error('Error during registration:', error);
      errorMessage.textContent = 'An unexpected error occurred. Please try again later.';
    }
  });
});
