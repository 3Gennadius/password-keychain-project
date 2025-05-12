// File: frontend/js/profile.js

document.addEventListener('DOMContentLoaded', () => {
  const userField    = document.getElementById('username');
  const emailField   = document.getElementById('email');
  const btnProfile   = document.getElementById('open-profile-modal');
  const btnPassword  = document.getElementById('open-password-modal');

  // Utility to show a temporary tooltip or hint
  function flashTooltip(el, msg, type = 'info') {
    const tip = document.createElement('span');
    tip.className = `copy-tooltip ${type}`;
    tip.textContent = msg;
    el.parentNode.appendChild(tip);
    setTimeout(() => tip.remove(), 1500);
  }

  //  Load and display existing profile data
  (async () => {
    try {
      const resp = await fetch('/profile/api', { credentials: 'include' });
      if (!resp.ok) throw new Error(resp.statusText);
      const { username, email } = await resp.json();
      userField.value  = username;
      emailField.value = email;
    } catch (err) {
      console.error('Failed to load profile data:', err);
    }
  })();

  //  Make fields readonly and enable click-to-copy
  [userField, emailField].forEach(el => {
    el.readOnly = true;
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => {
      navigator.clipboard.writeText(el.value)
        .then(() => flashTooltip(el, 'Copied!', 'success'))
        .catch(() => flashTooltip(el, 'Copy failed', 'error'));
    });
  });

  //  Modal open/close logic
  function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove('hidden');
  }
  window.closeModal = id => {
    const m = document.getElementById(id);
    if (m) m.classList.add('hidden');
  };
  btnProfile?.addEventListener('click', () => openModal('profile-modal'));
  btnPassword?.addEventListener('click', () => openModal('password-modal'));

  // Checkbox logic to enable action buttons
  function setupCheckbox(cbId, btnSelector) {
    const cb = document.getElementById(cbId);
    const btn = document.querySelector(btnSelector);
    if (!cb || !btn) return;
    btn.disabled = true;
    cb.checked = false;
    cb.addEventListener('change', () => {
      btn.disabled = !cb.checked;
    });
    btn.addEventListener('click', e => {
      if (!cb.checked) {
        e.preventDefault();
        flashTooltip(cb, 'Please confirm to proceed.', 'error');
      }
    });
  }
  setupCheckbox('confirm-profile-change', '#profile-modal .btn-save');
  setupCheckbox('confirm-password-change', '#password-modal .btn-save');

  //  Handle Profile Credentials form submission
  const profileForm = document.querySelector('#profile-modal form');
  if (profileForm) {
    profileForm.addEventListener('submit', async e => {
      e.preventDefault();
      const newUsername = profileForm.new_username.value.trim();
      const newEmail    = profileForm.new_email.value.trim();
      const confirm     = document.getElementById('confirm-profile-change').checked;

      if (!confirm) {
        flashTooltip(profileForm, 'You must confirm changes.', 'error');
        return;
      }
      if (!newUsername && !newEmail) {
        flashTooltip(profileForm, 'Enter a new username and/or email.', 'error');
        return;
      }
      if (newEmail && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(newEmail)) {
        flashTooltip(profileForm.new_email, 'Invalid email format.', 'error');
        return;
      }

      const formData = new URLSearchParams({
        new_username: newUsername,
        new_email:    newEmail,
        confirm_profile_change: confirm ? 'on' : ''
      });

      try {
        const resp = await fetch('/profile/update-credentials', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData.toString(),
          credentials: 'include'
        });

        if (resp.ok) {
          document.getElementById('confirm-profile-change').checked = false;
          document.querySelector('#profile-modal .btn-save').disabled = true;
          profileForm.reset();
          closeModal('profile-modal');
          window.location.reload();
        } else {
          let err = 'Update failed.';
          if (resp.status === 400) {
            const data = await resp.json();
            err = data.error || Object.values(data.errors || {})[0] || err;
          }
          flashTooltip(profileForm, err, 'error');
        }
      } catch (err) {
        console.error('Profile update error:', err);
        flashTooltip(profileForm, 'Network error.', 'error');
      }
    });
  }

  //  Handle Password Change form submission
  const passwordForm = document.querySelector('#password-modal form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async e => {
      e.preventDefault();

      // Grab by the actual IDs in your modal
      const oldPw     = document.getElementById('current-password').value.trim();
      const newPw     = document.getElementById('new-password').value.trim();
      const confirmPw = document.getElementById('confirm-password').value.trim();
      const confirm   = document.getElementById('confirm-password-change').checked;

      // Client-side checks
      if (!confirm) {
        flashTooltip(passwordForm, 'You must confirm to change password.', 'error');
        return;
      }
      if (!oldPw || !newPw || !confirmPw) {
        flashTooltip(passwordForm, 'Fill out all password fields.', 'error');
        return;
      }
      if (newPw !== confirmPw) {
        flashTooltip(document.getElementById('new-password'), 'Passwords do not match.', 'error');
        return;
      }

      const formData = new URLSearchParams({
        old_password:     oldPw,
        new_password:     newPw,
        confirm_password: confirmPw
      });

      try {
        const resp = await fetch('/profile/change-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData.toString(),
          credentials: 'include'
        });

        if (resp.ok) {
          document.getElementById('confirm-password-change').checked = false;
          document.querySelector('#password-modal .btn-save').disabled = true;
          passwordForm.reset();
          closeModal('password-modal');
          window.location.reload();
        } else {
          let err = 'Password change failed.';
          if (resp.status === 400) {
            const data = await resp.json();
            err = data.error || Object.values(data.errors || {})[0] || err;
          }
          flashTooltip(passwordForm, err, 'error');
        }
      } catch (err) {
        console.error('Password change error:', err);
        flashTooltip(passwordForm, 'Network error.', 'error');
      }
    });
  }
});
