/**
 * Login form functionality
 * Handles JSON API authentication with mobile-optimized UX
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const button = document.getElementById('loginButton');
    
    // Show loading state
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Signing In...';
    
    // Clear any existing error alerts
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Set the auth cookie
            document.cookie = `access_token=Bearer ${data.access_token}; path=/; max-age=${24 * 60 * 60}; SameSite=Lax`;
            
            // Redirect to dashboard
            window.location.href = '/';
        } else {
            // Handle error response
            const errorData = await response.json();
            window.NotificationSystem.error(errorData.detail || 'Login failed');
        }
    } catch (error) {
        window.NotificationSystem.error('Network error. Please try again.');
    } finally {
        // Reset button state
        button.disabled = false;
        button.innerHTML = originalText;
    }
}