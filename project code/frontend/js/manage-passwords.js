
// CSRF Token Handling
const csrfMeta = document.querySelector('meta[name="csrf-token"]');
const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : null;

// DOM Element References
const addForm = document.getElementById('addForm');
const websiteInput = document.getElementById('add-website');
const usernameInput = document.getElementById('add-username');
const passwordInput = document.getElementById('add-password');
// Form Submit Handler
addForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const website = websiteInput.value.trim();
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!website || !username || !password) {
        alert('All fields must be filled out before adding a new entry.');
        return;
    }

    const headers = { 'Content-Type': 'application/json' };
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;

    try {
        const response = await fetch('/passwords/api', {
            method: 'POST',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify({ website, username, password })
        });

        if (response.ok) {
            alert('Password entry added successfully.');
            websiteInput.value = '';
            usernameInput.value = '';
            passwordInput.value = '';
            fetchEntries(); // Refresh entries after adding
        } else {
            const errorData = await response.json();
            alert('Failed to add entry: ' + JSON.stringify(errorData.errors));
        }
    } catch (err) {
        console.error('Error adding entry:', err);
        alert('An error occurred while adding the entry.');
    }
});
// Vault Search & Filter Logic
let cachedEntries = [];

const searchInput = document.getElementById('search-field');
const filterDropdown = document.getElementById('filter-dropdown');
const entriesContainer = document.getElementById('entries-container');

async function fetchEntries() {
    try {
        const response = await fetch('/passwords/api');
        if (!response.ok) throw new Error('Failed to fetch entries.');
        const data = await response.json();

        // Add password strength evaluation
        cachedEntries = data.map(entry => ({
            ...entry,
            password_strength: checkWeakEntry(entry, 
                data.map(e => e.username.trim()), 
                data.map(e => e.password.trim())
            ) ? 'weak' : 'strong'
        }));

        renderEntries();
    } catch (error) {
        console.error('Error fetching entries:', error);
    }
}

function renderEntries() {
    const searchTerm = searchInput?.value.trim().toLowerCase() || '';
    const filterValue = filterDropdown?.value || 'all';

    const filtered = cachedEntries.filter(entry => {
        const matchesSearch = entry.website.toLowerCase().includes(searchTerm) ||
                              entry.username.toLowerCase().includes(searchTerm);

        const matchesFilter = 
            filterValue === 'all' || 
            (filterValue === 'weak' && entry.password_strength === 'weak') || 
            (filterValue === 'strong' && entry.password_strength === 'strong');

        return matchesSearch && matchesFilter;
    });

    if (!entriesContainer) return;

    entriesContainer.innerHTML = '';

    if (filtered.length === 0) {
        entriesContainer.innerHTML = '<p>No matching entries found.</p>';
        return;
    }

    filtered.forEach(entry => {
        const entryDiv = document.createElement('div');
        entryDiv.className = 'entry-card';
        entryDiv.innerHTML = `
            <h3>${sanitize(entry.website)}</h3>
            <p>Username: ${sanitize(entry.username)}</p>
            <p>Password: ${sanitize(entry.password)}</p>
            <p>Strength: ${formatStrength(entry.password_strength)}</p>
        `;
        entriesContainer.appendChild(entryDiv);
    });
}

// Password Strength Checks

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

function formatStrength(strength) {
    return strength === 'weak' 
        ? '<span style="color:red;">Weak</span>' 
        : '<span style="color:green;">Strong</span>';
}

async function fetchFilteredEntries(searchTerm, filterValue) {
    try {
        const response = await fetch(`/passwords/api/search?search=${encodeURIComponent(searchTerm)}&strength=${filterValue}`);
        if (!response.ok) throw new Error('Failed to fetch entries.');
        const data = await response.json();
        renderEntries(data);
    } catch (error) {
        console.error('Error fetching filtered entries:', error);
    }
}

fetchEntries();
