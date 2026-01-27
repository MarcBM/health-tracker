/**
 * Dashboard functionality
 * Fetches and displays dashboard data on page load
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fetch dashboard data when page loads
    fetchDashboardData();
});

async function fetchDashboardData() {
    try {
        console.log('Fetching dashboard data...');
        
        const response = await fetch('/data/dashboard', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Dashboard data received:', data);
            
            // Log each section separately for easier debugging
            console.log('Calories data:', data.calories);
            console.log('Steps data:', data.steps);
            console.log('Cardio data:', data.cardio);
            console.log('Strength data:', data.strength);
            console.log('Physio data:', data.physio);
            console.log('Weight data:', data.weight);
            
            // Update dashboard sections with real data
            updateStepsDisplay(data.steps);
            updateCardioDisplay(data.cardio);
            updatePhysioDisplay(data.physio);
            handleCaloriesData(data.calories);
            handleStrengthData(data.strength);
            handleWeightData(data.weight)
            
        } else {
            console.error('Failed to fetch dashboard data:', response.status, response.statusText);
            const errorData = await response.json();
            console.error('Error details:', errorData);
        }
    } catch (error) {
        console.error('Network error while fetching dashboard data:', error);
    }
} 