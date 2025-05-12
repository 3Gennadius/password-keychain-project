document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('contact-form');
  const responseEl = document.getElementById('contact-response');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    responseEl.textContent = '';
    responseEl.classList.remove('error', 'success');

    // Gather & trim values
    const name    = form.name.value.trim();
    const email   = form.email.value.trim();
    const message = form.message.value.trim();

    // Front-end validation with specific field feedback
    if (!name) {
      responseEl.textContent = '❌ Please enter your name.';
      responseEl.classList.add('error');
      form.name.focus();
      return;
    }
    if (!email) {
      responseEl.textContent = '❌ Please enter your email.';
      responseEl.classList.add('error');
      form.email.focus();
      return;
    }
    // Simple email regex
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      responseEl.textContent = '❌ Please enter a valid email address.';
      responseEl.classList.add('error');
      form.email.focus();
      return;
    }
    if (!message) {
      responseEl.textContent = '❌ Please enter a message.';
      responseEl.classList.add('error');
      form.message.focus();
      return;
    }

    // Submit to backend for sanitization & auto-reply
    try {
      const resp = await fetch('/contact/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message }),
        credentials: 'include'
      });

      if (resp.ok) {
        // Success—backend sent both support and auto-reply emails
        responseEl.textContent = '✅ Your message has been sent! We’ll be in touch shortly.';
        responseEl.classList.add('success');
        form.reset();
      } else {
        // Backend returned an error
        const data = await resp.json();
        const err = data.error || (data.errors && Object.values(data.errors)[0]) || 'Submission failed.';
        responseEl.textContent = `❌ ${err}`;
        responseEl.classList.add('error');
      }
    } catch (err) {
      console.error('Contact form submission error:', err);
      responseEl.textContent = '❌ Network error—please try again later.';
      responseEl.classList.add('error');
    }
  });
});
