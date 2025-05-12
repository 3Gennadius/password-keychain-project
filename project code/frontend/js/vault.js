
// vault.js - Updated Modal Logic and Full Implementation

// DOM Elements
const tableBody = document.getElementById('tableBody');
const addForm = document.getElementById('addForm');
const editModal = document.getElementById('edit-modal');
const deleteModal = document.getElementById('delete-modal');
const confirmCheckbox = document.getElementById('confirm-changes');
const saveChangesBtn = document.querySelector('.btn-save');
const discardBtn = document.querySelector('.btn-discard');
const deleteConfirmBtn = document.querySelector('.btn-confirm-delete');
const deleteCancelBtn = document.querySelector('.btn-cancel-delete');

// Utility Functions
function closeModal(modal) {
    modal.classList.add('hidden');
}

function openModal(modal) {
    modal.classList.remove('hidden');
}

// Close modals on outside click
window.addEventListener('click', (e) => {
    if (e.target === editModal) closeModal(editModal);
    if (e.target === deleteModal) closeModal(deleteModal);
});


// Load Vault Entries

async function loadVaultEntries() {
    try {
        const response = await fetch('/passwords/api', {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        const entries = await response.json();
        renderTable(entries);
    } catch (error) {
        console.error('Failed to load vault entries:', error);
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Unable to load entries.</td></tr>`;
    }
}


// Render Table Rows
function renderTable(entries) {
    tableBody.innerHTML = '';

    if (entries.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No saved passwords. Add your first one!</td></tr>`;
        return;
    }

    const strengthMap = analyzeStrength(entries);

    entries.forEach(entry => {
        const row = document.createElement('tr');

        

        row.appendChild(createCell(entry.website));
        row.appendChild(createCell(entry.username));
        row.appendChild(createCell(entry.password));

        const strengthCell = createCell(strengthMap[entry.entry_id]);
        strengthCell.className = (strengthMap[entry.entry_id] === 'Strong') ? 'strong' : 'weak';
        row.appendChild(strengthCell);

        row.appendChild(createCell(entry.last_updated || new Date().toLocaleDateString()));

        const actionsCell = document.createElement('td');

        const editBtn = createButton('Edit', 'edit-btn', () => openEditModal(entry));
        actionsCell.appendChild(editBtn);

        const deleteBtn = createButton('Delete', 'delete-btn', () => openDeleteModal(entry.entry_id));
        actionsCell.appendChild(deleteBtn);

        row.appendChild(actionsCell);
        tableBody.appendChild(row);
    });
}

function createCell(text) {
    const cell = document.createElement('td');
    cell.textContent = text;
    return cell;
}

function createButton(text, className, onClick) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = className;
    btn.addEventListener('click', onClick);
    return btn;
}

// Analyze Entry Strength
function analyzeStrength(entries) {
    const usernames = {}, passwords = {}, combos = {}, strengthMap = {};

    entries.forEach(entry => {
        usernames[entry.username] = (usernames[entry.username] || 0) + 1;
        passwords[entry.password] = (passwords[entry.password] || 0) + 1;
        const combo = `${entry.username}:${entry.password}`;
        combos[combo] = (combos[combo] || 0) + 1;
    });

    entries.forEach(entry => {
        const weak = usernames[entry.username] > 1 || passwords[entry.password] > 1 || combos[`${entry.username}:${entry.password}`] > 1;
        strengthMap[entry.entry_id] = weak ? 'Weak' : 'Strong';
    });

    return strengthMap;
}


// Add Entry
addForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const website = document.getElementById('add-website').value.trim();
    const username = document.getElementById('add-username').value.trim();
    const password = document.getElementById('add-password').value.trim();

    try {
        const response = await fetch('/passwords/api', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ website, username, password })
        });

        if (response.ok) {
            loadVaultEntries();
            addForm.reset();
        } else {
            console.error('Failed to add entry.');
        }
    } catch (error) {
        console.error('Error adding entry:', error);
    }
});


// Edit Modal Logic

function openEditModal(entry) {
    document.getElementById('edit-entry-id').value = entry.entry_id;
    document.getElementById('edit-website').value = entry.website;
    document.getElementById('edit-username').value = entry.username;
    document.getElementById('edit-password').value = entry.password;

    confirmCheckbox.checked = false;
    saveChangesBtn.disabled = true;
    openModal(editModal);
}

confirmCheckbox.addEventListener('change', (e) => {
    saveChangesBtn.disabled = !e.target.checked;
});

discardBtn.addEventListener('click', () => {
    closeModal(editModal);
});

saveChangesBtn.addEventListener('click', async () => {
    const entryId = document.getElementById('edit-entry-id').value;
    const website = document.getElementById('edit-website').value.trim();
    const username = document.getElementById('edit-username').value.trim();
    const password = document.getElementById('edit-password').value.trim();

    try {
        const response = await fetch(`/passwords/api/${entryId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ website: website, username, password })
        });

        if (response.ok) {
            closeModal(editModal);
            loadVaultEntries();
        } else {
            console.error('Failed to update entry.');
        }
    } catch (error) {
        console.error('Error updating entry:', error);
    }
});




// Delete Modal Logic
function openDeleteModal(entryId) {
    document.getElementById('delete-entry-id').value = entryId;
    openModal(deleteModal);
}

deleteConfirmBtn.addEventListener('click', async () => {
    const entryId = document.getElementById('delete-entry-id').value;

    try {
        const response = await fetch(`/passwords/api/${entryId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            closeModal(deleteModal);
            loadVaultEntries();
        } else {
            console.error('Failed to delete entry.');
        }
    } catch (error) {
        console.error('Error deleting entry:', error);
    }
});

deleteCancelBtn.addEventListener('click', () => {
    closeModal(deleteModal);
});


// Initial Load






loadVaultEntries();


window.editEntry = function(id) {

    openEditModal(id);
};

window.deleteEntry = function(id) {

    openDeleteModal(id);
};

window.saveEditedEntry = function() {

    performSaveEdit();
};

window.closeEditModal = function() {
    document.getElementById('edit-modal').classList.add('hidden');
};

window.confirmDeleteEntry = function() {

    performDelete();
};

window.closeDeleteModal = function() {
    document.getElementById('delete-modal').classList.add('hidden');
};

window.editEntry = editEntry;
window.deleteEntry = deleteEntry;
window.saveEditedEntry = saveEditedEntry;
window.closeEditModal = closeEditModal;
window.confirmDeleteEntry = confirmDeleteEntry;
window.closeDeleteModal = closeDeleteModal;
