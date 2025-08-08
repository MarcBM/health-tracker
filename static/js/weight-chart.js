/**
 * Weight Chart functionality
 * Creates and manages the weight progression line chart using Chart.js
 */

// Global variable to store the chart instance
let weightChart = null;

// Draw labeled downward ticks at starts of time windows (e.g., 7d, 30d, etc.)
const segmentLabelsPlugin = {
    id: 'segmentLabels',
    afterDatasetsDraw(chart, args, opts) {
        const markers = (opts && opts.markers) || [];
        if (!markers.length) return;

        const { ctx, chartArea, scales } = chart;
        const xScale = scales.x;
        const yScale = scales.y;

        ctx.save();
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.font = '12px system-ui, -apple-system, Segoe UI, Roboto, sans-serif';

        const meta = chart.getDatasetMeta(0);
        // Compute layouts left-to-right and dynamically deepen labels only when needed to avoid overlap
        const ordered = markers.slice().sort((a, b) => a.x - b.x);
        const placedBoxes = []; // track placed label boxes
        const layouts = [];
        ordered.forEach((marker) => {
            const isLoss = marker.delta < 0;
            const textColor = isLoss ? '#198754' : '#dc3545'; // green for loss, red for gain

            // Pixel coordinates for the start point: use actual element position for precise alignment
            const elem = meta && meta.data && meta.data[marker.index];
            const x = elem && typeof elem.x === 'number' ? elem.x : xScale.getPixelForValue(marker.x);
            const y = elem && typeof elem.y === 'number' ? elem.y : yScale.getPixelForValue(marker.y);

            // Label text: show only weight change (no timeframe label)
            const text = `${marker.delta > 0 ? '+' : ''}${marker.delta.toFixed(1)} kg`;

            // Measure and determine label box size
            const padX = 4; const padY = 2;
            const metrics = ctx.measureText(text);
            const boxW = metrics.width + padX * 2;
            const boxH = 14 + padY * 2;
            const maxY2 = chartArea.bottom - (boxH + 4); // keep box inside chart area

            // Dynamic depth: start shallow, deepen only if overlapping with already placed labels
            const baseTick = 14;
            const step = 24; // deeper by 24px per collision level
            let tickLen = baseTick;
            let y2 = Math.min(y + tickLen, maxY2);
            let boxX = x - boxW / 2;
            // Clamp horizontally
            let clampedBoxX = Math.max(chartArea.left, Math.min(boxX, chartArea.right - boxW));
            let boxY = y2 + 2;

            const overlaps = (r1, r2) => !(r1.x2 < r2.x1 || r2.x2 < r1.x1 || r1.y2 < r2.y1 || r2.y2 < r1.y1);
            let safety = 0;
            while (placedBoxes.some(r => overlaps(r, { x1: clampedBoxX, y1: boxY, x2: clampedBoxX + boxW, y2: boxY + boxH })) && safety < 10) {
                tickLen += step;
                y2 = Math.min(y + tickLen, maxY2);
                boxY = y2 + 2;
                // If we've hit max depth, break to avoid infinite loop
                if (y2 >= maxY2) break;
                safety++;
            }
            // Save layout and register box for future overlap checks
            layouts.push({ x, y, y2, boxX: clampedBoxX, boxY, boxW, boxH, text, textColor });
            placedBoxes.push({ x1: clampedBoxX, y1: boxY, x2: clampedBoxX + boxW, y2: boxY + boxH });
        });

        // Draw ticks beneath labels
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 1;
        layouts.forEach(l => {
            ctx.beginPath();
            ctx.moveTo(l.x, l.y);
            ctx.lineTo(l.x, l.y2);
            ctx.stroke();
        });

        // Draw label boxes and text on top
        layouts.forEach(l => {
            ctx.fillStyle = 'rgba(255,255,255,0.85)';
            ctx.strokeStyle = 'rgba(0,0,0,0.2)';
            ctx.lineWidth = 1;
            ctx.fillRect(l.boxX, l.boxY, l.boxW, l.boxH);
            ctx.strokeRect(l.boxX, l.boxY, l.boxW, l.boxH);

            ctx.fillStyle = l.textColor;
            ctx.fillText(l.text, l.boxX + l.boxW / 2, l.boxY + 2);
        });

        ctx.restore();
    }
};

// Register custom plugin globally (safe to call once)
if (typeof Chart !== 'undefined' && Chart.register) {
    Chart.register(segmentLabelsPlugin);
}

// Build markers: 7d, 30d, 90d, 180d, 365d, then every extra 365d back to start
function buildSegmentMarkers(points) {
    if (!points || !points.length) return [];

    const end = points[points.length - 1]; // last recorded point
    const first = points[0];
    const dayMs = 24 * 60 * 60 * 1000;
    const spanDays = Math.round((end.x - first.x) / dayMs);

    const windows = [
        { days: 7,   label: '7d' },
        { days: 30,  label: '30d' },
        { days: 90,  label: '3m' },
        { days: 180, label: '6m' }
    ];

    const findPointAtOrBefore = (targetDate) => {
        for (let i = points.length - 1; i >= 0; i--) {
            if (points[i].x <= targetDate) return points[i];
        }
        return null;
    };

    const markers = [];
    // Always include a marker at the start of dataset to show total change
    if (first && end) {
        markers.push({
            x: first.x,
            y: first.y,
            index: first.index,
            label: 'start',
            delta: end.y - first.y
        });
    }
    for (const w of windows) {
        // Treat the last point as "yesterday" and build inclusive windows.
        // Example: 7d window => start at (yesterday - 6 days).
        const inclusiveDaysBack = Math.max(0, w.days - 1);
        const startT = new Date(end.x.getTime() - inclusiveDaysBack * dayMs);
        const startPt = findPointAtOrBefore(startT);
        if (!startPt) continue;

        // If the 1y marker coincides with the dataset start, skip it to avoid duplicate with 'start' marker
        if ((w.label === '1y' || w.days === 365) && startPt.index === first.index) {
            continue;
        }

        const delta = end.y - startPt.y; // negative = loss
        markers.push({
            x: startPt.x,
            y: startPt.y,
            index: startPt.index,
            label: w.label,
            delta
        });
    }

    return markers;
}

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

    // Build points for marker computations [{ x: Date, y: number }]
    const points = chartData.labels.map((d, i) => ({ x: new Date(d), y: chartData.weights[i], index: i }));
    const markers = buildSegmentMarkers(points);

    // Show point markers only where labels exist
    const pointRadiusForIndex = new Array(chartData.weights.length).fill(0);
    markers.forEach(m => { if (typeof m.index === 'number') pointRadiusForIndex[m.index] = 3; });
    
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
                pointRadius: 0, // hide all points by default
                pointHoverRadius: 0,
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
                },
                // Custom segment labels plugin
                segmentLabels: { markers }
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

    // Apply scriptable point radius after chart creation (Chart.js v4 supports arrays)
    if (weightChart && weightChart.data && weightChart.data.datasets && weightChart.data.datasets[0]) {
        weightChart.data.datasets[0].pointRadius = pointRadiusForIndex;
        weightChart.update();
    }
    
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