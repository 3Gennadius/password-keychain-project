document.addEventListener('DOMContentLoaded', () => {
    const avatarUploadBtn = document.getElementById('avatar-upload-btn');
    const fileInput = document.getElementById('avatar');

    if (avatarUploadBtn && fileInput) {
        avatarUploadBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            const file = fileInput.files[0];
            if (!file) {
                showQuickMessage('Please select a file to upload.', 'error');
                return;
            }

            // Disable button to prevent multiple uploads
            avatarUploadBtn.disabled = true;
            avatarUploadBtn.textContent = 'Uploading...';

            const formData = new FormData();
            formData.append('avatar', file);

            try {
                const response = await fetch('/profile/upload-avatar', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    showQuickMessage('Avatar uploaded successfully!', 'success');
                    fileInput.value = '';
                    setTimeout(() => location.reload(), 1000); // Small delay before reload
                } else {
                    const result = await response.json();
                    showQuickMessage(result.error || 'Failed to upload avatar.', 'error');
                }
            } catch (error) {
                showQuickMessage('Upload failed. Please try again.', 'error');
            } finally {
                avatarUploadBtn.disabled = false;
                avatarUploadBtn.textContent = 'Upload Avatar';
            }
        });
    }
});

// Toast Message Function for Quick Feedback
function showQuickMessage(message, type = 'success') {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.backgroundColor = '#333';
        toast.style.color = '#fff';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '5px';
        toast.style.display = 'none';
        toast.style.zIndex = '1000';
        toast.style.fontSize = '14px';
        toast.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
        toast.style.transition = 'opacity 0.5s ease';
        document.body.appendChild(toast);
    }

    toast.style.backgroundColor = type === 'error' ? '#d9534f' : '#5cb85c';
    toast.textContent = message;
    toast.style.display = 'block';
    toast.style.opacity = '1';

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.style.display = 'none';
        }, 500);
    }, 3000);
}
