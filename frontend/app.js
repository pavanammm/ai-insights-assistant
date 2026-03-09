let SESSION_ID = crypto.randomUUID();
let currentChart = null;
let currentData = null;
let currentGroupBy = null;

document.getElementById('sessionDisplay').textContent = SESSION_ID.slice(0, 8) + '...';

function newSession() {
    SESSION_ID = crypto.randomUUID();
    document.getElementById('sessionDisplay').textContent = SESSION_ID.slice(0, 8) + '...';
    document.getElementById('resultContainer').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
    updateStatPills(null);
}

function fillQuery(text) {
    document.getElementById('questionInput').value = text;
    runQuery();
}

async function runQuery() {
    const question = document.getElementById('questionInput').value.trim();
    if (!question) return;

    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('resultContainer').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/query?query=${encodeURIComponent(question)}&session_id=${SESSION_ID}`,
            { method: 'POST' }
        );

        const data = await response.json();
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('resultContainer').classList.remove('hidden');

        renderResult(data);

    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('resultContainer').classList.remove('hidden');
        document.getElementById('scalarContainer').classList.remove('hidden');
        document.getElementById('scalarContainer').innerHTML =
            `<div class="scalar-number" style="color:var(--accent3)">!</div>
             <div class="scalar-label">Connection error</div>`;
        console.error(error);
    }
}

function renderResult(data) {
    const result = data.result;
    const intent = data.intent || {};
    currentGroupBy = intent.group_by || null;

    // Reset all containers
    ['chartContainer', 'tableContainer', 'scalarContainer'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });

    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }

    // Update intent panel
    document.getElementById('intentJson').textContent = JSON.stringify(intent, null, 2);
    document.getElementById('intentJson').classList.add('hidden');
    const intentToggle = document.querySelector('.intent-toggle');
    if (intentToggle) intentToggle.textContent = '▶ EXTRACTED INTENT';

    // Sidebar + chips
    updateStatPills(data);
    renderFollowupChips(intent);

    // Route rendering
    if (result === null || result === undefined) {
        renderScalar('—', 'no data');
        updateMeta('No results');
        return;
    }

    if (typeof result === 'number') {
        renderScalar(result.toLocaleString(), 'tickets matched');
        updateMeta('Scalar result');
        renderViewToggle(false);
        return;
    }

    if (typeof result === 'object' && !Array.isArray(result)) {
        renderDerivedResult(result);
        updateMeta('Derived metric');
        return;
    }

    if (Array.isArray(result)) {
        currentData = result;

        if (result.length === 0) {
            renderScalar('0', 'results found');
            updateMeta('No results');
            return;
        }

        const keys = Object.keys(result[0]);
        const isGrouped = keys.length === 2 && keys.includes('count');

        if (isGrouped) {
            renderGroupedResult(result, keys[0]);
            updateMeta(`${result.length} groups`);
            renderViewToggle(true);
            showChart();
        } else {
            renderTable(result);
            updateMeta(`${result.length} rows`);
            renderViewToggle(false);
            document.getElementById('tableContainer').classList.remove('hidden');
        }
    }
}

function renderScalar(value, label) {
    const el = document.getElementById('scalarContainer');
    el.innerHTML = `
        <div class="scalar-number">${value}</div>
        <div class="scalar-label">${label}</div>
    `;
    el.classList.remove('hidden');
}

function renderDerivedResult(result) {
    const el = document.getElementById('scalarContainer');
    el.innerHTML = `
        <div class="scalar-number">${result.percentage}%</div>
        <div class="scalar-label">completed within 24h</div>
        <div style="margin-top:16px; font-family:var(--font-mono); font-size:12px; color:var(--text-dim)">
            ${result.completed_within_24h?.toLocaleString()} of ${result.total?.toLocaleString()} tickets
        </div>
    `;
    el.classList.remove('hidden');
}

function renderGroupedResult(data, labelKey) {
    currentData = data;

    const labels = data.map(r => String(r[labelKey]));
    const values = data.map(r => r.count);
    const colors = getChartColors(data.length);

    const isTimeSeries = ['month', 'year', 'weekday'].includes(currentGroupBy);
    const chartType = isTimeSeries ? 'line' : (data.length <= 5 ? 'doughnut' : 'bar');

    const canvas = document.getElementById('mainChart');
    const ctx = canvas.getContext('2d');

    Chart.defaults.color = '#6b7280';
    Chart.defaults.font.family = 'DM Mono';

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: chartType === 'doughnut',
                labels: {
                    color: '#e8eaf0',
                    font: { family: 'DM Mono', size: 11 },
                    padding: 16,
                    usePointStyle: true,
                }
            },
            tooltip: {
                backgroundColor: '#181c24',
                borderColor: '#232830',
                borderWidth: 1,
                titleColor: '#e8ff47',
                bodyColor: '#e8eaf0',
                padding: 10,
            }
        }
    };

    if (chartType === 'bar') {
        currentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.map(c => c + '33'),
                    borderColor: colors,
                    borderWidth: 2,
                    borderRadius: 6,
                    hoverBackgroundColor: colors.map(c => c + '66'),
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    x: {
                        grid: { color: '#232830' },
                        ticks: { color: '#6b7280', font: { family: 'DM Mono', size: 11 } }
                    },
                    y: {
                        grid: { color: '#232830' },
                        ticks: { color: '#6b7280', font: { family: 'DM Mono', size: 11 } },
                        beginAtZero: true
                    }
                }
            }
        });

    } else if (chartType === 'line') {
        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    data: values,
                    borderColor: '#e8ff47',
                    backgroundColor: 'rgba(232,255,71,0.08)',
                    borderWidth: 2,
                    pointBackgroundColor: '#e8ff47',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.3,
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    x: {
                        grid: { color: '#232830' },
                        ticks: { color: '#6b7280', font: { family: 'DM Mono', size: 11 } }
                    },
                    y: {
                        grid: { color: '#232830' },
                        ticks: { color: '#6b7280', font: { family: 'DM Mono', size: 11 } },
                        beginAtZero: true
                    }
                }
            }
        });

    } else if (chartType === 'doughnut') {
        currentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.map(c => c + '99'),
                    borderColor: colors,
                    borderWidth: 2,
                    hoverOffset: 8,
                }]
            },
            options: {
                ...commonOptions,
                cutout: '65%',
            }
        });
    }

    // Always build table too so toggle works
    renderTable(data);
}

function showChart() {
    document.getElementById('chartContainer').classList.remove('hidden');
    document.getElementById('tableContainer').classList.add('hidden');
    const btnChart = document.getElementById('btnChart');
    const btnTable = document.getElementById('btnTable');
    if (btnChart) btnChart.classList.add('active');
    if (btnTable) btnTable.classList.remove('active');
}

function showTable() {
    document.getElementById('chartContainer').classList.add('hidden');
    document.getElementById('tableContainer').classList.remove('hidden');
    const btnChart = document.getElementById('btnChart');
    const btnTable = document.getElementById('btnTable');
    if (btnChart) btnChart.classList.remove('active');
    if (btnTable) btnTable.classList.add('active');
}

function renderTable(data) {
    const container = document.getElementById('tableContainer');
    const keys = Object.keys(data[0]);

    const headerCells = keys.map(k =>
        `<th>${k.replace(/_/g, ' ')}</th>`
    ).join('');

    const rows = data.map(row =>
        `<tr>${keys.map(k => `<td>${row[k] ?? '—'}</td>`).join('')}</tr>`
    ).join('');

    container.innerHTML = `
        <table>
            <thead><tr>${headerCells}</tr></thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

function renderViewToggle(hasChart) {
    const el = document.getElementById('viewToggle');

    if (!hasChart) {
        el.innerHTML = currentData
            ? `<button class="csv-btn" onclick="downloadCSV()">↓ CSV</button>`
            : '';
        return;
    }

    el.innerHTML = `
        <button class="toggle-btn active" id="btnChart" onclick="showChart()">◫ Chart</button>
        <button class="toggle-btn" id="btnTable" onclick="showTable()">≡ Table</button>
        <button class="csv-btn" onclick="downloadCSV()">↓ CSV</button>
    `;
}

function updateMeta(text) {
    document.getElementById('resultMeta').innerHTML =
        `<strong>${text}</strong> · ${new Date().toLocaleTimeString()}`;
}

function updateStatPills(data) {
    const el = document.getElementById('statPills');
    if (!data || !data.intent) {
        el.innerHTML = `<div class="stat-pill dimmed">Awaiting query...</div>`;
        return;
    }

    const intent = data.intent;
    const pills = [];

    if (intent.metric) {
        pills.push(`<div class="stat-pill">
            <span class="pill-label">Metric</span>
            <span class="pill-value">${intent.metric.replace('_', ' ')}</span>
        </div>`);
    }

    if (intent.filters && Object.keys(intent.filters).length > 0) {
        const filterText = Object.entries(intent.filters)
            .map(([k, v]) => `${k}: ${v}`).join('\n');
        pills.push(`<div class="stat-pill">
            <span class="pill-label">Filters</span>
            <span style="font-family:var(--font-mono);font-size:11px;color:var(--accent2)">${filterText}</span>
        </div>`);
    }

    if (intent.group_by) {
        pills.push(`<div class="stat-pill">
            <span class="pill-label">Group By</span>
            <span class="pill-value" style="font-size:14px">${intent.group_by}</span>
        </div>`);
    }

    if (data.latency_ms !== undefined) {
        pills.push(`<div class="stat-pill">
            <span class="pill-label">Latency</span>
            <span class="pill-value" style="font-size:14px;color:var(--accent2)">${data.latency_ms}ms</span>
        </div>`);
    }

    el.innerHTML = pills.join('') || `<div class="stat-pill dimmed">No active filters</div>`;
}

function renderFollowupChips(intent) {
    const el = document.getElementById('followupChips');
    const chips = [];

    if (intent.metric === 'ticket_count') {
        if (intent.group_by !== 'type') chips.push('break it down by type');
        if (intent.group_by !== 'priority') chips.push('break it down by priority');
        if (intent.group_by !== 'month') chips.push('show by month');
        if (intent.group_by !== 'county') chips.push('group by county');
        if (!intent.filters?.priority) chips.push('only CRITICAL priority');
        chips.push('now show the ticket list');
    } else {
        chips.push('just give me the count');
        chips.push('break it down by type');
        if (!intent.filters?.type) chips.push('only EMER type');
    }

    el.innerHTML = chips.slice(0, 4).map(c =>
        `<div class="chip" onclick="fillQuery('${c}')">${c}</div>`
    ).join('');
}

function toggleIntent() {
    const json = document.getElementById('intentJson');
    const btn = document.querySelector('.intent-toggle');
    const hidden = json.classList.toggle('hidden');
    btn.textContent = (hidden ? '▶' : '▼') + ' EXTRACTED INTENT';
}

function downloadCSV() {
    if (!currentData || currentData.length === 0) return;
    const keys = Object.keys(currentData[0]);
    const rows = [
        keys.join(','),
        ...currentData.map(r =>
            keys.map(k => `"${r[k] ?? ''}"`).join(',')
        )
    ];
    const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `insights_${Date.now()}.csv`;
    a.click();
}

function getChartColors(n) {
    const palette = [
        '#1a56db', '#0e9f6e', '#e74694',
        '#9061f9', '#ff8a4c', '#31c48d', '#f05252'
    ];
    const result = [];
    for (let i = 0; i < n; i++) result.push(palette[i % palette.length]);
    return result;
}