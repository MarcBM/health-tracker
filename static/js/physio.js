/**
 * Physio Dashboard Module
 * Handles all physio-related display logic and data processing
 */

/**
 * Main function to update all physio display cards with real data
 * @param {Object} physioData - Physio data from API
 */
function updatePhysioDisplay(physioData) {
    if (!physioData) {
        console.warn('No physio data available');
        return;
    }
    
    console.log('Updating physio display with:', physioData);
    
    // Update Card 1: Physio Active Status
    updatePhysioActiveStatus(physioData.current_active);
    
    // Update Card 2: Current Physio Streak
    updatePhysioCurrentStreak(physioData.current_streak, physioData.longest_streak, physioData.current_active);
    
    // Update Card 3: Longest Physio Streak Record
    updatePhysioLongestStreak(physioData.longest_streak);
}

/**
 * Updates the "Physio Active Status" card with current status
 * @param {boolean|null} currentActive - Current physio active status
 */
function updatePhysioActiveStatus(currentActive) {
    const card = document.getElementById('physio-active-status-card');
    if (!card) return;
    
    // Update metric value and styling based on status
    const metricValue = card.querySelector('.metric-value');
    const metricLabel = card.querySelector('.metric-label');
    const metricChange = card.querySelector('.metric-change');
    
    if (metricValue && metricLabel && metricChange) {
        if (currentActive === true) {
            metricValue.textContent = 'ACTIVE';
            metricValue.style.color = 'var(--success-color)';
            metricLabel.textContent = 'currently prescribed physio';
            metricChange.className = 'metric-change positive';
            metricChange.innerHTML = '<i class="bi bi-check-circle"></i> Follow exercise plan';
        } else if (currentActive === false) {
            metricValue.textContent = 'INACTIVE';
            metricValue.style.color = 'var(--secondary-color)';
            metricLabel.textContent = 'no physio currently prescribed';
            metricChange.className = 'metric-change neutral';
            metricChange.innerHTML = '<i class="bi bi-pause-circle"></i> No exercises needed';
        } else {
            metricValue.textContent = 'UNKNOWN';
            metricValue.style.color = 'var(--warning-color)';
            metricLabel.textContent = 'status not recorded';
            metricChange.className = 'metric-change neutral';
            metricChange.innerHTML = '<i class="bi bi-question-circle"></i> Update status';
        }
    }
}

/**
 * Updates the "Physio Streak" card with current streak status
 * @param {number} currentStreak - Number of consecutive days completed
 * @param {Object} longestStreakData - Longest streak data to compare against
 * @param {boolean|null} currentActive - Current physio active status for context
 */
function updatePhysioCurrentStreak(currentStreak, longestStreakData, currentActive) {
    const card = document.getElementById('physio-current-streak-card');
    if (!card) return;
    
    const streak = currentStreak || 0;
    const longestStreak = longestStreakData ? longestStreakData.streak || 0 : 0;
    const isRecordStreak = streak > 0 && streak === longestStreak;
    const isActive = currentActive === true;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = streak;
    }
    
    // Update metric change with dynamic messages
    const metricChange = card.querySelector('.metric-change');
    if (metricChange) {
        if (isRecordStreak) {
            metricChange.className = 'metric-change positive';
            metricChange.innerHTML = `<i class="bi bi-trophy"></i> Personal record streak!`;
        } else if (streak > 0) {
            metricChange.className = 'metric-change positive';
            if (streak >= 21) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Outstanding commitment!`;
            } else if (streak >= 14) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Excellent streak!`;
            } else if (streak >= 7) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Great progress!`;
            } else if (streak >= 3) {
                metricChange.innerHTML = `<i class="bi bi-check-circle"></i> Building momentum!`;
            } else {
                metricChange.innerHTML = `<i class="bi bi-check-circle"></i> Good start!`;
            }
        } else {
            if (isActive) {
                metricChange.className = 'metric-change neutral';
                metricChange.innerHTML = `<i class="bi bi-arrow-clockwise"></i> Begin your routine!`;
            } else {
                metricChange.className = 'metric-change neutral';
                metricChange.innerHTML = `<i class="bi bi-pause-circle"></i> No active physio`;
            }
        }
    }
}

/**
 * Updates the "Physio Streak Record" card with historical best
 * @param {Object} longestStreakData - Contains streak length and end_date
 */
function updatePhysioLongestStreak(longestStreakData) {
    const card = document.getElementById('physio-longest-streak-card');
    if (!card || !longestStreakData) return;
    
    const streak = longestStreakData.streak || 0;
    const endDate = longestStreakData.end_date ? new Date(longestStreakData.end_date) : null;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = streak;
    }
    
    // Update date in metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange && endDate) {
        const dateStr = endDate.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long' 
        });
        metricChange.innerHTML = `<i class="bi bi-calendar-event"></i> ${dateStr}`;
    } else if (metricChange) {
        metricChange.innerHTML = `<i class="bi bi-dash-circle"></i> No streak yet`;
    }
}

// Export main function for potential module usage (if needed in the future)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updatePhysioDisplay
    };
}