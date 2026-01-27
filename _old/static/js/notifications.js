/**
 * Generic notifications system
 * Handles temporary and permanent notifications with auto-dismiss functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeNotifications();
    initializeMissingDataChecks();
});

function initializeNotifications() {
    // Auto-dismiss temporary notifications
    const tempNotifications = document.querySelectorAll('[data-notification-type="temporary"]');
    tempNotifications.forEach(notification => {
        const duration = parseInt(notification.dataset.duration) || 4000;
        setTimeout(() => {
            dismissNotification(notification);
        }, duration);
    });
}

function dismissNotification(notification) {
    if (notification && notification.classList.contains('alert')) {
        // Use Bootstrap alert for proper animation
        const bsAlert = new bootstrap.Alert(notification);
        bsAlert.close();
    } else if (notification) {
        // Fallback for non-Bootstrap alerts
        notification.style.transition = 'opacity 0.3s ease';
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

function showNotification(message, type = 'info', duration = 4000, permanent = false) {
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        console.warn('Notification container not found');
        return;
    }

    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show mb-3`;
    notification.setAttribute('role', 'alert');
    
    if (!permanent) {
        notification.setAttribute('data-notification-type', 'temporary');
        notification.setAttribute('data-duration', duration);
    } else {
        notification.setAttribute('data-notification-type', 'permanent');
    }

    // Icon mapping
    const icons = {
        success: 'bi-check-circle',
        danger: 'bi-exclamation-triangle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };

    notification.innerHTML = `
        <i class="bi ${icons[type] || icons.info} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    notificationContainer.appendChild(notification);

    // Auto-dismiss if temporary
    if (!permanent) {
        setTimeout(() => {
            dismissNotification(notification);
        }, duration);
    }

    return notification;
}

// Utility functions for common notification types
function showSuccess(message, duration = 4000) {
    return showNotification(message, 'success', duration);
}

function showError(message, permanent = false) {
    return showNotification(message, 'danger', 4000, permanent);
}

function showWarning(message, duration = 6000) {
    return showNotification(message, 'warning', duration);
}

function showInfo(message, duration = 4000) {
    return showNotification(message, 'info', duration);
}

// Missing data checking functionality
async function checkMissingData(scope = 'dashboard') {
    try {
        const response = await fetch(`/missing-data?scope=${scope}`);
        if (!response.ok) return;
        
        const data = await response.json();
        
        if (data.missing_days && data.missing_days.length > 0) {
            // Create individual persistent notifications for each missing day
            data.missing_days.forEach(dayInfo => {
                let message;
                let linkUrl;
                
                if (scope === 'dashboard') {
                    // Full day missing - link to data entry for that date
                    message = `No data entered for ${dayInfo.display_name}`;
                    linkUrl = `/data-entry?date=${dayInfo.date}`;
                } else {
                    // Specific section data missing - link to data entry for that date with section focus
                    message = `Missing ${scope} data for ${dayInfo.display_name}`;
                    linkUrl = `/data-entry?date=${dayInfo.date}&focus=${scope}`;
                }
                
                // Create persistent warning with action link
                showMissingDataWarning(message, linkUrl, dayInfo.date, scope);
            });
        }
    } catch (error) {
        console.warn('Failed to check missing data:', error);
    }
}

// Create persistent missing data notification with action link
function showMissingDataWarning(message, linkUrl, date, scope) {
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        console.warn('Notification container not found');
        return;
    }

    // Create unique ID for this notification to avoid duplicates
    const notificationId = `missing-data-${scope}-${date}`;
    
    // Remove existing notification for this day/scope if it exists
    const existingNotification = document.getElementById(notificationId);
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.id = notificationId;
    notification.className = 'alert alert-warning alert-dismissible fade show mb-3';
    notification.setAttribute('role', 'alert');
    notification.setAttribute('data-notification-type', 'permanent');

    notification.innerHTML = `
        <i class="bi bi-exclamation-triangle me-2"></i>
        ${message}
        <a href="${linkUrl}" class="alert-link ms-2">
            <i class="bi bi-plus-circle me-1"></i>Add data
        </a>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    notificationContainer.appendChild(notification);
    return notification;
}

function initializeMissingDataChecks() {
    // Only run missing data checks for users with edit permissions
    const userCanEdit = document.body.hasAttribute('data-user-can-edit');
    if (!userCanEdit) {
        return;
    }
    
    // Look for elements with data-check-missing-data attribute
    const elementsToCheck = document.querySelectorAll('[data-check-missing-data]');
    
    elementsToCheck.forEach(element => {
        const scope = element.getAttribute('data-check-missing-data');
        if (scope) {
            // Run missing data check for this scope
            checkMissingData(scope);
        }
    });
}

// Export functions for global use
window.NotificationSystem = {
    show: showNotification,
    success: showSuccess,
    error: showError,
    warning: showWarning,
    info: showInfo,
    dismiss: dismissNotification,
    checkMissingData: checkMissingData
};