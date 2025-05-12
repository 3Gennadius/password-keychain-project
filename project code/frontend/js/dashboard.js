document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('dashboard-table-body');
    const apiEndpoint = '/passwords/api';

    function renderTable(data) {
        if (!data.length) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No entries found.</td></tr>';
            return;
        }

        tableBody.innerHTML = '';

        const usernames = data.map(entry => entry.username.trim());
        const passwords = data.map(entry => entry.password.trim());

        data.forEach(entry => {
            const isWeak = checkWeakEntry(entry, usernames, passwords);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${sanitize(entry.website)}</td>
                <td>${sanitize(entry.username)}</td>
                <td>${sanitize(entry.password)}</td>
                <td>${formatStrength(isWeak)}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    function checkWeakEntry(entry, allUsernames, allPasswords) {
        const username = entry.username.trim();
        const password = entry.password.trim();

        const duplicateUsername = allUsernames.filter(u => u === username).length > 1;
        const duplicatePassword = allPasswords.filter(p => p === password).length > 1;
        const usernameEqualsPassword = username === password;

        return (
            !isStrongPassword(password) ||
            usernameEqualsPassword ||
            duplicateUsername ||
            duplicatePassword
        );
    }

    function isStrongPassword(password) {
        if (password.length < 8) return false;
        if (!/[A-Z]/.test(password)) return false;
        if (!/\d/.test(password)) return false;
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return false;
        return true;
    }

    function sanitize(str) {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    }

    function formatStrength(isWeak) {
        return isWeak 
            ? '<span style="color:red;">Weak</span>' 
            : '<span style="color:green;">Strong</span>';
    }

    // Fetch and render table data + handle security section
    fetch(apiEndpoint, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        renderTable(data);

        const securitySection = document.getElementById('security-section');
        const securityMessage = document.getElementById('security-message');
        const actionButton = document.getElementById('security-action-btn');

        if (!Array.isArray(data) || data.length === 0) {
            // Vault is empty
            securitySection.style.display = 'block';
            securityMessage.textContent = 'Your vault is currently empty. Start storing your credentials securely.';
            actionButton.textContent = 'Go to Vault';
            actionButton.href = 'manage-passwords.html';
            return;
        }

        const hasWeak = data.some(entry => checkWeakEntry(entry, 
            data.map(e => e.username.trim()), 
            data.map(e => e.password.trim())
        ));

        securitySection.style.display = 'block';
        if (hasWeak) {
            securityMessage.textContent = 'Weak passwords detected. Consider updating them for better security.';
            actionButton.textContent = 'Update Entries';
            actionButton.href = 'manage-passwords.html';
        } else {
            securityMessage.textContent = 'All your credentials meet the security standards.';
            actionButton.textContent = 'Go to Vault';
            actionButton.href = 'manage-passwords.html';
        }
    })
    .catch(error => {
        console.error('Error fetching password data:', error);
        const securitySection = document.getElementById('security-section');
        if (securitySection) {
            securitySection.style.display = 'none';
        }
    });
});
