/**
 * Password change form functionality
 * Handles JSON API password updates with validation
 */

document.addEventListener('DOMContentLoaded', function() {
    const passwordForm = document.getElementById('passwordChangeForm');
    
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
    }
});

async function handlePasswordChange(e) {
    e.preventDefault();
    
    const oldPassword = document.getElementById('old_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const button = document.getElementById('changePasswordButton');
    
    // Clear any existing alerts
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Client-side validation for password confirmation
    if (newPassword !== confirmPassword) {
        window.NotificationSystem.error('New passwords don\'t match. Please try again.');
        return;
    }
    
    // Client-side validation for password length
    if (newPassword.length < 8) {
        window.NotificationSystem.error('New password must be at least 8 characters long.');
        return;
    }
    
    // Show loading state
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Changing Password...';
    
    try {
        const response = await fetch('/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Redirect immediately to dashboard with success message
            window.location.href = '/?success=password_changed';
        } else {
            // Handle error response
            const errorData = await response.json();
            
            if (response.status === 401) {
                // Unauthorized - redirect to login
                window.location.href = '/login';
                return;
            }
            
            window.NotificationSystem.error(errorData.detail || 'Failed to change password');
        }
    } catch (error) {
        window.NotificationSystem.error('Network error. Please try again.');
    } finally {
        // Reset button state
        button.disabled = false;
        button.innerHTML = originalText;
    }
}