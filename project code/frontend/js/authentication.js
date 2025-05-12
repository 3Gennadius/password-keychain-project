
document.addEventListener('DOMContentLoaded', () => {

  // Avatar display logic in topnav
  const profileLink = document.querySelector('a[href="profile.html"]');

  async function updateProfileNav() {
    try {
      const resp = await fetch('/profile/api', { credentials: 'include' });
      if (!resp.ok) throw new Error('Failed to fetch user info.');

      const data = await resp.json();
      const avatarPath = data.avatar_path || 'avatars/default.png';

      if (profileLink) {
        const avatarImg = document.createElement('img');
        avatarImg.src = avatarPath;
        avatarImg.alt = 'Avatar';
        avatarImg.classList.add('nav-avatar'); // Style this class via CSS only

        if (!profileLink.querySelector('img')) {
          profileLink.prepend(avatarImg);
        }
      }
    } catch (err) {
      console.warn('Avatar fetch failed:', err);
    }
  }

  updateProfileNav();


});


// Mobile Nav Toggle

function toggleNav() {
  document.getElementById('myTopnav').classList.toggle('responsive');
}
window.toggleNav = toggleNav;


// Authentication & Nav Links
async function populateNavLinks() {
  const container = document.getElementById('nav-links');
  if (!container) return;

  // Determine auth state by probing a protected page
  let isAuthenticated = false;
  try {
    const resp = await fetch('/dashboard.html', {
      method: 'GET',
      credentials: 'include',
      redirect: 'manual'
    });
    isAuthenticated = (resp.status === 200);
  } catch {
    isAuthenticated = false;
  }

  // Base links
  const links = [
    { href: 'index.html', text: 'Home' },
    { href: 'about.html', text: 'About' },
    { href: 'contact.html', text: 'Contact' }
  ];

  if (isAuthenticated) {
    // Insert after Home
    links.splice(1, 0,
      { href: 'dashboard.html', text: 'Dashboard' },
      { href: 'manage-passwords.html', text: 'Vault' },
      { href: 'profile.html', text: 'Profile' },
      { href: 'logout.html', text: 'Logout' }
    );
  } else {
    // Add login/register for visitors
    links.push(
      { href: 'login.html', text: 'Login' },
      { href: 'register.html', text: 'Register' }
    );
  }


  // Render into the nav
  container.innerHTML = '';
  for (const { href, text } of links) {
    const a = document.createElement('a');
    a.href = href;
    a.textContent = text;
    container.appendChild(a);
  }
}
document.addEventListener('DOMContentLoaded', populateNavLinks);

  // Fetch and apply user's dark mode preference on page load
async function applyUserDarkMode() {
  try {
    const response = await fetch('/profile/dark-mode');
    const data = await response.json();

    if (data.dark_mode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  } catch (error) {
    console.error('Failed to fetch dark mode preference:', error);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (!darkModeToggle) return;

  // Fetch current preference from backend
  try {
    const response = await fetch('/profile/dark-mode');
    const data = await response.json();
    darkModeToggle.checked = data.dark_mode;
    document.body.classList.toggle('dark-mode', data.dark_mode);
  } catch (error) {
    console.warn('Failed to fetch dark mode preference:', error);
  }

  // Update preference on toggle
  darkModeToggle.addEventListener('change', async () => {
    const isDark = darkModeToggle.checked;
    document.body.classList.toggle('dark-mode', isDark);

    try {
      await fetch('/profile/dark-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dark_mode: isDark })
      });
    } catch (error) {
      console.error('Failed to update dark mode preference:', error);
    }
  });
});

// Save user's dark mode preference when toggled
async function setUserDarkMode(isDark) {
  try {
    await fetch('/profile/dark-mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dark_mode: isDark })
    });
  } catch (error) {
    console.error('Failed to set dark mode preference:', error);
  }
}


  //darkmode
  document.getElementById('dark-mode-toggle').addEventListener('change', (event) => {
  const isDark = event.target.checked;
  document.body.classList.toggle('dark-mode', isDark);
  setUserDarkMode(isDark);
  });


document.addEventListener('DOMContentLoaded', applyUserDarkMode);


