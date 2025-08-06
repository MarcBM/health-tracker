/**
 * Steps Dashboard Module
 * Handles all steps-related display logic and data processing
 */

/**
 * Main function to update all steps display cards with real data
 * @param {Object} stepsData - Steps data from API
 */
function updateStepsDisplay(stepsData) {
    if (!stepsData) {
        console.warn('No steps data available');
        return;
    }
    
    console.log('Updating steps display with:', stepsData);
    
    // Update Card 1: Steps Yesterday vs Goal
    updateStepsYesterday(stepsData.yesterday);
    
    // Update Card 2: 7-Day Average vs Previous 7-Day Average  
    updateStepsAverages(stepsData.averages);
    
    // Update Card 3: Personal Record with Date
    updateStepsPersonalRecord(stepsData.highest);
    
    // Update Card 4: Current Step Goal Streak
    updateStepsCurrentStreak(stepsData.current_streak, stepsData.yesterday, stepsData.longest_streak);
    
    // Update Card 5: Longest Step Goal Streak Record
    updateStepsLongestStreak(stepsData.longest_streak);
}

/**
 * Updates the "Steps Yesterday" card with actual vs goal data
 * @param {Object} yesterdayData - Contains actual and goal steps for yesterday
 */
function updateStepsYesterday(yesterdayData) {
    const card = document.getElementById('steps-yesterday-card');
    if (!card || !yesterdayData) return;
    
    const actual = yesterdayData.actual || 0;
    const goal = yesterdayData.goal || 0;
    const isMissing = actual === 0;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = isMissing ? 'MISSING' : actual.toLocaleString();
    }
    
    // Update metric label
    const metricLabel = card.querySelector('.metric-label');
    if (metricLabel) {
        if (isMissing) {
            metricLabel.textContent = '';
        } else {
            metricLabel.textContent = `of ${goal.toLocaleString()} goal`;
        }
    }
    
    // Update metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange) {
        if (isMissing) {
            metricChange.className = 'metric-change neutral';
            metricChange.innerHTML = `<i class="bi bi-exclamation-triangle"></i> No data recorded`;
        } else {
            const percentage = goal > 0 ? Math.round((actual / goal) * 100) : 0;
            const goalMet = actual >= goal;
            metricChange.className = `metric-change ${goalMet ? 'positive' : 'negative'}`;
            metricChange.innerHTML = goalMet 
                ? `<i class="bi bi-check-circle"></i> ${percentage}% of goal achieved`
                : `<i class="bi bi-x-circle"></i> ${percentage}% of goal achieved`;
        }
    }
}

/**
 * Updates the "7-Day Average" card with trend comparison
 * @param {Object} averagesData - Contains last_7_days and previous_7_days averages
 */
function updateStepsAverages(averagesData) {
    const card = document.getElementById('steps-averages-card');
    if (!card || !averagesData) return;
    
    const last7 = averagesData.last_7_days || 0;
    const prev7 = averagesData.previous_7_days || 0;
    const change = prev7 > 0 ? ((last7 - prev7) / prev7) * 100 : 0;
    const isPositive = change >= 0;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = Math.round(last7).toLocaleString();
    }
    
    // Update metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange) {
        metricChange.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
        const sign = isPositive ? '+' : '';
        const icon = isPositive ? 'bi-trending-up' : 'bi-trending-down';
        metricChange.innerHTML = `<i class="bi ${icon}"></i> ${sign}${Math.round(change)}% vs previous 7 days`;
    }
}

/**
 * Updates the "Personal Record" card with highest steps and date
 * @param {Object} highestData - Contains steps and date of personal record
 */
function updateStepsPersonalRecord(highestData) {
    const card = document.getElementById('steps-record-card');
    if (!card || !highestData) return;
    
    const steps = highestData.steps || 0;
    const date = highestData.date ? new Date(highestData.date) : null;
    
    // Update metric value
    const metricValue = card.querySelector('.metric-value');
    if (metricValue) {
        metricValue.textContent = steps.toLocaleString();
    }
    
    // Update date in metric change
    const metricChange = card.querySelector('.metric-change');
    if (metricChange && date) {
        const dateStr = date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        metricChange.innerHTML = `<i class="bi bi-calendar-event"></i> ${dateStr}`;
    }
}

/**
 * Updates the "Step Goal Streak" card with current streak status
 * @param {number} currentStreak - Number of consecutive days meeting goal
 * @param {Object} yesterdayData - Yesterday's data to check if goal was met
 * @param {Object} longestStreakData - Longest streak data to compare against
 */
function updateStepsCurrentStreak(currentStreak, yesterdayData, longestStreakData) {
    const card = document.getElementById('steps-current-streak-card');
    if (!card) return;
    
    const streak = currentStreak || 0;
    const goalMet = yesterdayData && yesterdayData.actual >= yesterdayData.goal;
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
        } else if (goalMet) {
            metricChange.className = 'metric-change positive';
            if (streak >= 14) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Amazing streak!`;
            } else if (streak >= 7) {
                metricChange.innerHTML = `<i class="bi bi-fire"></i> Great streak!`;
            } else if (streak >= 3) {
                metricChange.innerHTML = `<i class="bi bi-check-circle"></i> Good streak!`;
            } else {
                metricChange.innerHTML = `<i class="bi bi-check-circle"></i> Keep it up!`;
            }
        } else {
            metricChange.className = 'metric-change neutral';
            if (streak === 0) {
                metricChange.innerHTML = `<i class="bi bi-dash-circle"></i> Start a new streak!`;
            } else {
                metricChange.innerHTML = `<i class="bi bi-x-circle"></i> Goal not met yesterday`;
            }
        }
    }
}

/**
 * Updates the "Longest Streak Record" card with historical best
 * @param {Object} longestStreakData - Contains streak length and end_date
 */
function updateStepsLongestStreak(longestStreakData) {
    const card = document.getElementById('steps-longest-streak-card');
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
    }
}

// Export main function for potential module usage (if needed in the future)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateStepsDisplay
    };
}