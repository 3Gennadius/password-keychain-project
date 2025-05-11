document.addEventListener('DOMContentLoaded', () => {
  const confirmBtn = document.getElementById('confirm-btn');
  const cancelBtn = document.getElementById('cancel-btn');
  const confirmLogout = document.getElementById('confirm-logout');
  const postLogout = document.getElementById('post-logout');

  confirmBtn.addEventListener('click', async () => {
    try {
      const response = await fetch('/auth/logout', {
        method: 'GET',
        credentials: 'include', // Include cookies for session
      });

      // Clear any tokens or sensitive data stored on the client side
      localStorage.clear();
      sessionStorage.clear();

      if (response.redirected) {
        // Logout successful, show confirmation screen
        confirmLogout.style.display = 'none';
        postLogout.style.display = 'block';
      } else {
        // Even if not redirected, show confirmation
        confirmLogout.style.display = 'none';
        postLogout.style.display = 'block';
      }
    } catch (error) {
      console.error('Logout failed:', error);
      alert('Logout failed. Please try again.');
    }
  });

  cancelBtn.addEventListener('click', () => {
    // Redirect back to dashboard or homepage if the user cancels
    window.location.href = '/dashboard.html';
  });
});
