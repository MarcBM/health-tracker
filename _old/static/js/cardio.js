/**
 * Cardio Dashboard Module
 * Handles all cardio-related display logic and data processing
 */

/**
 * Main function to update all cardio display cards with real data
 * @param {Object} cardioData - Cardio data from API
 */
function updateCardioDisplay(cardioData) {
    if (!cardioData) {
        console.warn('No cardio data available');
        return;
    }
    
    console.log('Updating cardio display with:', cardioData);
    
    // Update Card 1: Total Cardio Minutes (low + high)
    updateCardioTotalMinutes(cardioData.last_7_days);
    
    // Update Card 2: Low Intensity Minutes
    updateCardioLowIntensity(cardioData.last_7_days);
    
    // Update Card 3: High Intensity Minutes
    updateCardioHighIntensity(cardioData.last_7_days);
    
    // Update Card 4: Current Cardio Streak
    updateCardioCurrentStreak(cardioData.current_streak, cardioData.longest_streak);
    
    // Update Card 5: Longest Cardio Streak Record
    updateCardioLongestStreak(cardioData.longest_streak);
}

/**
 * Updates the "Total Cardio Minutes" card with combined low + high intensity
 * @param {Object} last7DaysData - Contains low_intensity and high_intensity totals
 */
function updateCardioTotalMinutes(last7DaysData) {
    const card = document.getElementById('cardio-total-minutes-card');
    if (!card || !last7DaysData) return;
    
    const lowMinutes = last7DaysData.low_intensity || 0;
    const highMinutes = last7DaysData.high_intensity || 0;
    const totalMinutes = lowMinutes + highMinutes;
    const goal = 150; // Weekly cardio goal (could be made configurable)
    const percentage = goal > 0 ? Math.round((totalMinutes / goal) * 100) : 0;
    const goalMet = totalMinutes >= goal;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = totalMinutes;
    }
    
    // Update metric label
    const metricLabel = card.querySelector('.metric-label');
    if (metricLabel) {
        metricLabel.textContent = `of ${goal} min goal last 7 days`;
    }
    
    // Update metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange) {
        metricChange.className = `metric-change ${goalMet ? 'positive' : 'negative'}`;
        metricChange.innerHTML = goalMet 
            ? `<i class="bi bi-check-circle"></i> ${percentage}% of goal achieved`
            : `<i class="bi bi-x-circle"></i> ${percentage}% of goal achieved`;
    }
}

/**
 * Updates the "Low Intensity Minutes" card
 * @param {Object} last7DaysData - Contains low_intensity total
 */
function updateCardioLowIntensity(last7DaysData) {
    const card = document.getElementById('cardio-low-intensity-card');
    if (!card || !last7DaysData) return;
    
    const lowMinutes = last7DaysData.low_intensity || 0;
    const goal = 120; // Low intensity goal (could be made configurable)
    const percentage = goal > 0 ? Math.round((lowMinutes / goal) * 100) : 0;
    const goalMet = lowMinutes >= goal;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = lowMinutes;
    }
    
    // Update metric label
    const metricLabel = card.querySelector('.metric-label');
    if (metricLabel) {
        metricLabel.textContent = `of ${goal} min goal last 7 days`;
    }
    
    // Update metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange) {
        metricChange.className = `metric-change ${goalMet ? 'positive' : 'negative'}`;
        metricChange.innerHTML = goalMet 
            ? `<i class="bi bi-trending-up"></i> ${percentage}% of goal achieved`
            : `<i class="bi bi-trending-down"></i> ${percentage}% of goal achieved`;
    }
}

/**
 * Updates the "High Intensity Minutes" card
 * @param {Object} last7DaysData - Contains high_intensity total
 */
function updateCardioHighIntensity(last7DaysData) {
    const card = document.getElementById('cardio-high-intensity-card');
    if (!card || !last7DaysData) return;
    
    const highMinutes = last7DaysData.high_intensity || 0;
    const goal = 30; // High intensity goal (could be made configurable)
    const percentage = goal > 0 ? Math.round((highMinutes / goal) * 100) : 0;
    const goalMet = highMinutes >= goal;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = highMinutes;
    }
    
    // Update metric label
    const metricLabel = card.querySelector('.metric-label');
    if (metricLabel) {
        metricLabel.textContent = `of ${goal} min goal last 7 days`;
    }
    
    // Update metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange) {
        metricChange.className = `metric-change ${goalMet ? 'positive' : 'negative'}`;
        metricChange.innerHTML = goalMet 
            ? `<i class="bi bi-fire"></i> ${percentage}% of goal achieved`
            : `<i class="bi bi-fire"></i> ${percentage}% of goal achieved`;
    }
}

/**
 * Updates the "Cardio Streak" card with current streak status
 * @param {number} currentStreak - Number of consecutive days with 15+ minutes
 * @param {Object} longestStreakData - Longest streak data to compare against
 */
function updateCardioCurrentStreak(currentStreak, longestStreakData) {
    const card = document.getElementById('cardio-current-streak-card');
    if (!card) return;
    
    const streak = currentStreak || 0;
    const hasStreak = streak > 0;
    const longestStreak = longestStreakData ? longestStreakData.streak || 0 : 0;
    const isRecordStreak = streak > 0 && streak === longestStreak;
    
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
        } else if (hasStreak) {
            metricChange.className = 'metric-change positive';
            if (streak >= 7) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Amazing streak!`;
            } else if (streak >= 3) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Good streak!`;
            } else {
                metricChange.innerHTML = `<i class="bi bi-check-circle"></i> Keep it up!`;
            }
        } else {
            metricChange.className = 'metric-change neutral';
            metricChange.innerHTML = `<i class="bi bi-dash-circle"></i> Start a new streak!`;
        }
    }
}

/**
 * Updates the "Cardio Streak Record" card with historical best
 * @param {Object} longestStreakData - Contains streak length and end_date
 */
function updateCardioLongestStreak(longestStreakData) {
    const card = document.getElementById('cardio-longest-streak-card');
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
        updateCardioDisplay
    };
}