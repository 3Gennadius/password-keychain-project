
// =========================
// CSRF Token Handling (Optional)
// =========================
const csrfMeta = document.querySelector('meta[name="csrf-token"]');
const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : null;

// =========================
// DOM Element References
// =========================
const addForm = document.getElementById('addForm');
const websiteInput = document.getElementById('add-website');
const usernameInput = document.getElementById('add-username');
const passwordInput = document.getElementById('add-password');

// =========================
// Form Submit Handler
// =========================
addForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const website = websiteInput.value.trim();
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    console.log("DEBUG - Website value before fetch:", website);

    if (!website || !username || !password) {
        alert('All fields must be filled out before adding a new entry.');
        return;
    }

    const headers = {
        'Content-Type': 'application/json'
    };

    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }

    try {
        const response = await fetch('/passwords/api', {
            method: 'POST',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify({
                website: website,
                username: username,
                password: password
            })
        });

        if (response.ok) {
            alert('Password entry added successfully.');
            // Clear inputs after successful submission
            websiteInput.value = '';
            usernameInput.value = '';
            passwordInput.value = '';
        } else {
            const errorData = await response.json();
            alert('Failed to add entry: ' + JSON.stringify(errorData.errors));
        }
    } catch (err) {
        console.error('Error adding entry:', err);
        alert('An error occurred while adding the entry.');
    }
});



// =========================
// Vault Search & Filter Logic (Lightweight Integration)
// =========================

let cachedEntries = [];

const searchInput = document.getElementById('search-field'); // Ensure this exists in HTML
const filterDropdown = document.getElementById('filter-dropdown'); // Ensure this exists in HTML
const entriesContainer = document.getElementById('entries-container'); // Ensure this exists in HTML

async function fetchEntries() {
    try {
        const response = await fetch('/passwords/api');
        if (!response.ok) throw new Error('Failed to fetch entries.');
        const data = await response.json();
        cachedEntries = data;
        renderEntries();
    } catch (error) {
        console.error('Error fetching entries:', error);
    }
}

function renderEntries() {
    const searchTerm = searchInput?.value.trim().toLowerCase() || '';
    const filterValue = filterDropdown?.value || 'all';

    const filtered = cachedEntries.filter(entry => {
        const matchesSearch = 
            entry.website.toLowerCase().includes(searchTerm) || 
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
            <h3>${entry.website}</h3>
            <p>Username: ${entry.username}</p>
            <p>Password Strength: ${entry.password_strength}</p>
        `;
        entriesContainer.appendChild(entryDiv);
    });
}

searchInput?.addEventListener('input', renderEntries);
filterDropdown?.addEventListener('change', renderEntries);

document.addEventListener('DOMContentLoaded', fetchEntries);
