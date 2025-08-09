/**
 * Calorie Chart
 * Renders last 7 days as stacked areas for actuals (green, yellow, orange)
 * overlaid with stacked goal lines (same categories).
 */

let calorieChart = null;

function prepareCaloriesChartData(caloriesArray) {
    if (!Array.isArray(caloriesArray)) {
        return {
            labels: [],
            dayNames: [],
            actual: { green: [], yellow: [], orange: [] },
            goal: { green: [], yellow: [], orange: [] },
            cumulativeActual: { green: [], yellow: [], orange: [] },
            cumulativeGoal: { green: [], yellow: [], orange: [] }
        };
    }

    const sorted = caloriesArray
        .slice()
        .sort((a, b) => new Date(a.date) - new Date(b.date));

    const labels = [];
    const dayNames = [];
    const aG = [], aY = [], aO = [];
    const gG = [], gY = [], gO = [];

    for (const d of sorted) {
        labels.push(d.date);
        dayNames.push(d.day_of_week || '');
        aG.push(d.calories_green_actual || 0);
        aY.push(d.calories_yellow_actual || 0);
        aO.push(d.calories_orange_actual || 0);
        gG.push(d.calories_green_goal || 0);
        gY.push(d.calories_yellow_goal || 0);
        gO.push(d.calories_orange_goal || 0);
    }

    // Build cumulative series for stacked areas/lines
    const cAG = aG;
    const cAY = aG.map((v, i) => v + aY[i]);
    const cAO = aG.map((v, i) => v + aY[i] + aO[i]);
    const cGG = gG;
    const cGY = gG.map((v, i) => v + gY[i]);
    const cGO = gG.map((v, i) => v + gY[i] + gO[i]);

    return {
        labels,
        dayNames,
        actual: { green: aG, yellow: aY, orange: aO },
        goal: { green: gG, yellow: gY, orange: gO },
        cumulativeActual: { green: cAG, yellow: cAY, orange: cAO },
        cumulativeGoal: { green: cGG, yellow: cGY, orange: cGO }
    };
}

function createCaloriesChart(calorieData) {
    const container = document.getElementById('calories-chart-container');
    if (!container) {
        console.error('Calories chart container not found');
        return;
    }

    // Clear any existing content and create canvas
    container.innerHTML = '<canvas id="calories-chart" width="400" height="200"></canvas>';
    const ctx = document.getElementById('calories-chart').getContext('2d');

    const chartData = prepareCaloriesChartData(calorieData);
    if (!chartData.labels.length) {
        container.innerHTML = `
            <div class="text-center text-muted p-4">
                <i class="bi bi-pie-chart fs-1 mb-3"></i>
                <p>No calorie data available for the last 7 days</p>
                <small>Enter calorie data to see trends here</small>
            </div>
        `;
        return;
    }

    // Colors
    const colSuccess = '#198754'; // green
    const colWarning = '#ffc107'; // yellow
    const colOrange = '#fd7e14'; // orange

    const areaSuccess = 'rgba(25, 135, 84, 0.30)';
    const areaWarning = 'rgba(255, 193, 7, 0.30)';
    const areaOrange = 'rgba(253, 126, 20, 0.30)';

    // Destroy prior chart if any
    if (calorieChart) {
        try { calorieChart.destroy(); } catch (e) {}
        calorieChart = null;
    }

    // Build datasets: actuals (stacked filled areas via cumulative + fill to previous), goals (stacked lines)
    const datasets = [
        // Actuals (areas)
        {
            label: 'Green Calories',
            data: chartData.cumulativeActual.green,
            borderColor: colSuccess,
            backgroundColor: areaSuccess,
            borderWidth: 2,
            fill: 'origin',
            tension: 0,
            pointRadius: 0,
            order: 1
        },
        {
            label: 'Yellow Calories',
            data: chartData.cumulativeActual.yellow,
            borderColor: colWarning,
            backgroundColor: areaWarning,
            borderWidth: 2,
            fill: '-1', // fill to previous dataset
            tension: 0,
            pointRadius: 0,
            order: 1
        },
        {
            label: 'Orange Calories',
            data: chartData.cumulativeActual.orange,
            borderColor: colOrange,
            backgroundColor: areaOrange,
            borderWidth: 2,
            fill: '-1', // fill to previous dataset
            tension: 0,
            pointRadius: 0,
            order: 1
        },
        // Goals (lines only)
        {
            label: 'Green Goal',
            data: chartData.cumulativeGoal.green,
            borderColor: colSuccess,
            backgroundColor: 'transparent',
            borderDash: [6, 4],
            borderWidth: 2,
            fill: false,
            tension: 0,
            pointRadius: 0,
            order: 2
        },
        {
            label: 'Yellow Goal',
            data: chartData.cumulativeGoal.yellow,
            borderColor: colWarning,
            backgroundColor: 'transparent',
            borderDash: [6, 4],
            borderWidth: 2,
            fill: false,
            tension: 0,
            pointRadius: 0,
            order: 2
        },
        {
            label: 'Orange Goal',
            data: chartData.cumulativeGoal.orange,
            borderColor: colOrange,
            backgroundColor: 'transparent',
            borderDash: [6, 4],
            borderWidth: 2,
            fill: false,
            tension: 0,
            pointRadius: 0,
            order: 2
        }
    ];

    calorieChart = new Chart(ctx, {
        type: 'line',
        data: {
            // Use day-of-week labels on the x-axis as requested
            labels: chartData.dayNames,
            datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 0 },
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    displayColors: false,
                    footerFont: { weight: '700' },
                    filter: function(item) {
                        // Show only the three actual series as items; we compute diffs ourselves
                        return /Calories$/.test(item.dataset.label);
                    },
                    itemSort: function(a, b) {
                        const order = { 'Green Calories': 1, 'Yellow Calories': 2, 'Orange Calories': 3 };
                        return (order[a.dataset.label] || 100) - (order[b.dataset.label] || 100);
                    },
                    callbacks: {
                        title: function(items) {
                            return (items && items.length) ? (items[0].label || '') : '';
                        },
                        beforeFooter: function() {
                            return ['────────────'];
                        },
                        label: function(context) {
                            const i = context.dataIndex;
                            const mapName = {
                                'Green Calories': 'green',
                                'Yellow Calories': 'yellow',
                                'Orange Calories': 'orange'
                            };
                            const key = mapName[context.dataset.label];
                            const actual = chartData.actual[key][i] || 0;
                            const goal = chartData.goal[key][i] || 0;
                            const diff = actual - goal;
                            const sign = diff > 0 ? '+' : '';
                            const labelName = context.dataset.label.split(' ')[0]; // Green/Yellow/Orange
                            return `${labelName}: ${sign}${diff}`;
                        },
                        labelTextColor: function(context) {
                            const i = context.dataIndex;
                            const mapName = {
                                'Green Calories': 'green',
                                'Yellow Calories': 'yellow',
                                'Orange Calories': 'orange'
                            };
                            const key = mapName[context.dataset.label];
                            const actual = chartData.actual[key][i] || 0;
                            const goal = chartData.goal[key][i] || 0;
                            const diff = actual - goal;
                            return diff > 0 ? '#dc3545' : '#198754'; // red if above goal, green if below/at
                        },
                        footer: function(items) {
                            if (!items || !items.length) return [];
                            const i = items[0].dataIndex;
                            const totalActual = (chartData.actual.green[i] || 0) + (chartData.actual.yellow[i] || 0) + (chartData.actual.orange[i] || 0);
                            const totalGoal = (chartData.goal.green[i] || 0) + (chartData.goal.yellow[i] || 0) + (chartData.goal.orange[i] || 0);
                            const totalDiff = totalActual - totalGoal;
                            const sign = totalDiff > 0 ? '+' : '';
                            return [`Total: ${totalActual} (${sign}${totalDiff})`];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    grid: { display: false },
                    ticks: { padding: 2 }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0,0,0,0.1)' },
                    ticks: { callback: function(value) { return value; }, padding: 2 }
                }
            },
            interaction: { mode: 'nearest', axis: 'x', intersect: false }
        }
    });
}

function handleCaloriesData(caloriesData) {
    if (!caloriesData || !Array.isArray(caloriesData) || caloriesData.length === 0) {
        const container = document.getElementById('calories-chart-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-pie-chart fs-1 mb-3"></i>
                    <p>No calorie data available</p>
                    <small>Enter calories to view your 7-day trend</small>
                </div>
            `;
        }
        return;
    }
    createCaloriesChart(caloriesData);
}


