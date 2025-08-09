/**
 * Strength Chart functionality
 * Renders a doughnut chart of all-time strength workout type distribution
 * and overlays the last 7 days workout count centered over the chart.
 */

let strengthChart = null;

function prepareStrengthChartData(workoutTypeCounts) {
    if (!workoutTypeCounts || typeof workoutTypeCounts !== 'object') {
        return { labels: [], values: [] };
    }

    const entries = Object.entries(workoutTypeCounts)
        .filter(([label, count]) => label && count && count > 0)
        .sort((a, b) => b[1] - a[1]);

    const labels = entries.map(([label]) => label);
    const values = entries.map(([, count]) => count);

    return { labels, values };
}

function createStrengthChart(data) {
    const container = document.getElementById('strength-chart-container');
    if (!container) {
        console.error('Strength chart container not found');
        return;
    }

    // Clear any existing content
    container.innerHTML = '';

    // Create canvas for chart
    const canvas = document.createElement('canvas');
    canvas.id = 'strength-chart';
    canvas.width = 400;
    canvas.height = 200;
    container.appendChild(canvas);

    // Create centered overlay for last 7 days count
    const overlay = document.createElement('div');
    overlay.id = 'strength-chart-overlay';
    overlay.style.position = 'absolute';
    overlay.style.top = '50%';
    overlay.style.left = '50%';
    overlay.style.transform = 'translate(-50%, -50%)';
    overlay.style.textAlign = 'center';
    overlay.style.pointerEvents = 'none';

    const last7 = (data && typeof data.last_7_days_count === 'number') ? data.last_7_days_count : 0;
    const colorClass = last7 >= 5 ? 'text-success' : 'text-danger';
    overlay.innerHTML = `
        <div style="line-height:1">
            <div class="${colorClass}" style="font-size: 2rem; font-weight: 700;">${last7}</div>
            <div class="text-muted" style="font-size: 0.8rem;">last 7 days</div>
        </div>
    `;
    container.appendChild(overlay);

    const ctx = canvas.getContext('2d');

    const chartData = prepareStrengthChartData(data && data.workout_type_counts);

    if (!chartData.labels.length) {
        // No data for chart, show placeholder message (keep overlay visible)
        const placeholder = document.createElement('div');
        placeholder.className = 'text-center text-muted p-2';
        placeholder.style.position = 'absolute';
        placeholder.style.bottom = '8px';
        placeholder.style.left = '50%';
        placeholder.style.transform = 'translateX(-50%)';
        placeholder.innerHTML = '<small>No strength data yet</small>';
        container.appendChild(placeholder);
        return;
    }

    // Palette: Bootstrap-aligned colors
    const backgroundColors = [
        'rgba(13, 110, 253, 0.65)',   // primary
        'rgba(25, 135, 84, 0.65)',    // success
        'rgba(255, 193, 7, 0.75)',    // warning
        'rgba(220, 53, 69, 0.65)',    // danger (preferred as 4th)
        'rgba(108, 117, 125, 0.65)',  // secondary
        'rgba(111, 66, 193, 0.65)',   // purple
        'rgba(32, 201, 151, 0.65)',   // teal
        'rgba(23, 162, 184, 0.65)'    // info-ish (moved later)
    ];
    const borderColors = backgroundColors.map(c => c.replace(/0\.\d+\)/, '1)'));

    // Destroy existing chart if present (for re-renders)
    if (strengthChart) {
        try { strengthChart.destroy(); } catch (e) { /* noop */ }
        strengthChart = null;
    }

    strengthChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: chartData.labels.map((_, i) => backgroundColors[i % backgroundColors.length]),
                borderColor: chartData.labels.map((_, i) => borderColors[i % borderColors.length]),
                borderWidth: 1,
                hoverOffset: 6,
                cutout: '65%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 0 },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(items) {
                            return (items && items.length) ? (items[0].label || '') : '';
                        },
                        label: function(context) {
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0) || 1;
                            const pct = ((value / total) * 100).toFixed(0);
                            return `${value} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

function handleStrengthData(strengthData) {
    if (!strengthData) {
        const container = document.getElementById('strength-chart-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-activity fs-1 mb-2"></i>
                    <p>No strength data available</p>
                    <small>Track your strength workouts to see distribution here</small>
                </div>
            `;
        }
        return;
    }

    createStrengthChart(strengthData);
}


