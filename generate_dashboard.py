#!/usr/bin/env python3
"""
Generate a simple local dashboard that reads critique JSON files and errors.log,
shows an event list, time-series chart, live counter, and detail panel.
"""

import json
import glob
import re
from pathlib import Path
from datetime import datetime

# ----------------------------------------------------------------------
# 1. Gather all events (critiques + errors.log entries)
# ----------------------------------------------------------------------
events = []

# Helper to parse timestamp from critique files
def parse_timestamp(ts_str):
    """Convert timestamp like '20260616_135233' to datetime object."""
    try:
        return datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.min

# Read all critique JSON files
critiques_dir = Path("critiques")
for json_path in critiques_dir.glob("*.json"):
    try:
        data = json.load(json_path.open())
        # Extract basic fields
        ts_raw = data.get("timestamp", "")
        dt = parse_timestamp(ts_raw)

        # Determine type (error vs. critique)
        result = data.get("result", "")
        if "Error:" in result or "cannot import" in result.lower():
            ev_type = "error"
        else:
            ev_type = "critique"

        snippet = (data.get("critique", "")[:200] + "...")[:200]
        # Truncate snippet to fit UI
        snippet = snippet.replace("\n", " ").replace("\r", " ")

        events.append({
            "timestamp_raw": ts_raw,
            "timestamp_dt": dt.isoformat(),
            "type": ev_type,
            "file": data.get("task_file", "unknown"),
            "snippet": snippet,
            "detail_url": str(json_path.name),
            "full_data": data
        })
    except Exception:
        # Skip malformed files
        continue

# Read errors.log if it exists
log_path = Path("errors.log")
if log_path.exists():
    with log_path.open() as f:
        for line in f.readlines():
            # Match timestamp pattern [YYYY-MM-DDTHH:MM:SS.xxx] - Error detected:
            m = re.search(r"\[(.*?)\]\s*- Error detected:", line)
            if m:
                ts_str = m.group(1)  # ISO format already
                try:
                    dt = datetime.fromisoformat(ts_str)
                except ValueError:
                    dt = datetime.min
                events.append({
                    "timestamp_raw": ts_str,
                    "timestamp_dt": dt.isoformat(),
                    "type": "error_log",
                    "file": "errors.log",
                    "snippet": line.strip(),
                    "detail_url": "errors.log",
                    "full_data": {"raw_line": line.strip()}
                })

# Sort events chronologically
events.sort(key=lambda e: e["timestamp_dt"])

# ----------------------------------------------------------------------
# 2. Generate HTML dashboard with embedded data
# ----------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Codebase Index Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #event-list { max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
        .event-item { margin: 5px 0; cursor: pointer; padding: 5px; border-radius: 4px; }
        .event-item:hover { background: #f0f0f0; }
        #detail-panel { margin-top: 30px; max-width: 800px; }
        #chart-container { height: 300px; margin-top: 30px; }
        .event-type-critique { color: #2a7ae2; }
        .event-type-error { color: #e91e63; }
        .event-type-error-log { color: #607d8b; }
        .counter { font-size: 1.2em; margin-top: 10px; }
    </style>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Codebase Index Dashboard</h1>
    <div class="counter">Total Events: <span id="event-count"></span></div>
    <div class="counter">Last updated: <span id="last-updated"></span></div>

    <div id="event-list">
        <!-- Event items will be injected here -->
    </div>

    <div id="chart-container">
        <canvas id="event-chart"></canvas>
    </div>

    <div id="detail-panel">
        <h2>Event Detail</h2>
        <pre id="detail-json">No event selected.</pre>
    </div>

    <script>
        // Embedded events data (JSON)
        const events = EVENTS_JSON_PLACEHOLDER;

        // Populate event list & handle clicks
        const listEl = document.getElementById('event-list');
        const detailEl = document.getElementById('detail-json');
        events.forEach((e, idx) => {
            const div = document.createElement('div');
            div.className = 'event-item event-type-' + e.type;
            div.textContent = e.timestamp_raw + ' - ' + e.type.toUpperCase() + ' - ' + e.file;
            div.dataset.idx = idx;
            div.onclick = function() {
                const event = events[idx];
                detailEl.textContent = JSON.stringify(event.full_data, null, 2);
                // Highlight selected
                const items = listEl.querySelectorAll('.event-item');
                items.forEach(i => i.classList.remove('selected'));
                div.classList.add('selected');
            };
            listEl.appendChild(div);
        });

        // Display total count
        document.getElementById('event-count').textContent = events.length;

        // Build chart data (count per day)
        const chartData = {
            labels: [],
            datasets: [{
                label: 'Events per Day',
                data: [],
                backgroundColor: '#4caf50'
            }]
        };

        // Extract dates (YYYY-MM-DD) for chart
        const dateCounts = {};
        events.forEach(e => {
            const date = e.timestamp_dt.substring(0, 10);
            dateCounts[date] = (dateCounts[date] || 0) + 1;
        });
        const sortedDates = Object.keys(dateCounts).sort();
        chartData.labels = sortedDates;
        chartData.datasets[0].data = sortedDates.map(d => dateCounts[d]);

        // Render chart
        const ctx = document.getElementById('event-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: { type: 'category' }
                }
            }
        });
    </script>
</body>
</html>"""

# Convert events list to JSON string safe for embedding
events_json_str = json.dumps(events, indent=2)

# Replace placeholder
rendered_html = HTML_TEMPLATE.replace("EVENTS_JSON_PLACEHOLDER", events_json_str)

# Write out the dashboard
output_path = Path("dashboard.html")
output_path.write_text(rendered_html, encoding="utf-8")
print(f"Dashboard generated: {output_path.resolve()}")