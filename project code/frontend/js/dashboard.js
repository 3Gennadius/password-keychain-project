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
            const strength = calculateStrength(entry, usernames, passwords);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${sanitize(entry.website)}</td>
                <td>${sanitize(entry.username)}</td>
                <td>${sanitize(entry.password)}</td>
                <td>${formatStrength(strength)}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    function calculateStrength(entry, allUsernames, allPasswords) {
        const username = entry.username.trim();
        const password = entry.password.trim();

        const duplicateUsername = allUsernames.filter(u => u === username).length > 1;
        const duplicatePassword = allPasswords.filter(p => p === password).length > 1;
        const usernameEqualsPassword = username === password;

        return (duplicateUsername || duplicatePassword || usernameEqualsPassword) ? 'Weak' : 'Strong';
    }

    function formatStrength(strength) {
        const color = strength === 'Strong' ? 'green' : 'red';
        return `<span style="color: ${color}; font-weight: bold;">${sanitize(strength)}</span>`;
    }

    function sanitize(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    function loadData() {
        fetch(apiEndpoint)
            .then(response => response.json())
            .then(data => renderTable(data))
            .catch(error => {
                console.error('Error fetching dashboard data:', error);
                tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Error loading data.</td></tr>';
            });
    }

    loadData();
});
