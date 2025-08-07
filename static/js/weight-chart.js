/**
 * Weight Chart functionality
 * Creates and manages the weight progression line chart using Chart.js
 */

// Global variable to store the chart instance
let weightChart = null;

/**
 * Create the weight chart with the provided data
 * @param {Array} weightData - Array of weight entries with date and weight_kg
 */
function createWeightChart(weightData) {
    console.log('Creating weight chart with data:', weightData);
    
    // Get the canvas element
    const canvas = document.getElementById('weight-chart-container');
    if (!canvas) {
        console.error('Weight chart container not found');
        return;
    }
    
    // Clear any existing content
    canvas.innerHTML = '<canvas id="weight-chart" width="400" height="200"></canvas>';
    
    const ctx = document.getElementById('weight-chart').getContext('2d');
    
    // Prepare data for Chart.js
    const chartData = prepareWeightChartData(weightData);
    
    // Create the chart
    weightChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Weight (kg)',
                data: chartData.weights,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0, // No curve - straight lines to show gaps clearly
                pointBackgroundColor: 'rgb(75, 192, 192)',
                pointBorderColor: '#fff',
                pointBorderWidth: 1,
                pointRadius: 2,
                pointHoverRadius: 4,
                spanGaps: false // Ensure gaps are shown
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Hide the legend since there's only one dataset
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        title: function() {
                            return null; // Hide the title completely
                        },
                        label: function(context) {
                            return `${context.parsed.y} kg`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'MMM d'
                        }
                    },
                    title: {
                        display: false
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true, // Start at zero for proper scale
                    title: {
                        display: false
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + ' kg';
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            elements: {
                point: {
                    hoverRadius: 8
                }
            }
        }
    });
    
    console.log('Weight chart created successfully');
}

/**
 * Prepare weight data for Chart.js format
 * @param {Array} weightData - Raw weight data from API
 * @returns {Object} Formatted data for Chart.js
 */
function prepareWeightChartData(weightData) {
    if (!weightData || !Array.isArray(weightData)) {
        console.warn('Invalid weight data provided');
        return { labels: [], weights: [] };
    }
    
    // Sort data by date to ensure chronological order
    const sortedData = weightData.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    const labels = [];
    const weights = [];
    
    sortedData.forEach(entry => {
        if (entry.weight_kg !== null && entry.weight_kg !== undefined) {
            labels.push(entry.date);
            weights.push(entry.weight_kg);
        }
    });
    
    return { labels, weights };
}

/**
 * Handle weight data from dashboard API
 * This function is called by dashboard.js when weight data is received
 */
function handleWeightData(weightData) {
    console.log('Handling weight data:', weightData);
    
    if (weightData && weightData.weight_history) {
        createWeightChart(weightData.weight_history);
    } else {
        console.warn('No weight history data available');
        // Show placeholder message
        const container = document.getElementById('weight-chart-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-graph-up fs-1 mb-3"></i>
                    <p>No weight data available yet</p>
                    <small>Start tracking your weight to see your progress here</small>
                </div>
            `;
        }
    }
} 