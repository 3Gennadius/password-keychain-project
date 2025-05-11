document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const errorMessage = document.getElementById('error-message');

  form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission
    errorMessage.textContent = ''; // Clear previous errors

    const formData = new FormData(form);

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        body: formData,
      });

      if (response.redirected) {
        // Successful login, backend redirects to dashboard
        window.location.href = response.url;
        return;
      }

      const responseText = await response.text();

      // Try to extract flash or error messages from the HTML response
      const parser = new DOMParser();
      const doc = parser.parseFromString(responseText, 'text/html');
      const flashMessage = doc.querySelector('.flash-message, #flash, .alert, .error, .success');

      if (flashMessage) {
        errorMessage.textContent = flashMessage.textContent.trim();
      } else {
        // Fallback message
        errorMessage.textContent = 'Invalid username and/or password';
      }
    } catch (error) {
      console.error('Error during login:', error);
      errorMessage.textContent = 'An unexpected error occurred. Please try again later.';
    }
  });
});
