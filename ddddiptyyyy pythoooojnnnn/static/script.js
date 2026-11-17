let sentimentChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadEvents();
    loadAnalysis();

    // Event Creation Handler
    document.getElementById('eventForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('event_name').value,
            date: document.getElementById('event_date').value,
            venue: document.getElementById('event_venue').value,
            description: document.getElementById('event_desc').value
        };

        const res = await fetch('/api/add_event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();
        alert(result.message);
        document.getElementById('eventForm').reset();
        loadEvents();
    });

    // Feedback Submission Handler
    document.getElementById('feedbackForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            event_id: document.getElementById('event_select').value,
            student_name: document.getElementById('student_name').value,
            rating: document.getElementById('rating').value,
            comments: document.getElementById('comments').value
        };

        const res = await fetch('/api/add_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();
        alert(result.message);
        document.getElementById('feedbackForm').reset();
        loadAnalysis();
    });
});

async function loadEvents() {
    const res = await fetch('/api/events');
    const events = await res.json();
    
    const select = document.getElementById('event_select');
    select.innerHTML = '<option value="">Select Event</option>';

    events.forEach(evt => {
        select.innerHTML += `<option value="${evt['Event ID']}">${evt['Event Name']} (${evt['Date']})</option>`;
    });
}

async function loadAnalysis() {
    const res = await fetch('/api/analysis');
    const data = await res.json();
    const statsGrid = document.getElementById('statsGrid');

    if (!data.has_data) return;

    statsGrid.innerHTML = `
        <div class="stat-box"><h3>Total Feedbacks</h3><p>${data.total_feedbacks}</p></div>
        <div class="stat-box"><h3>Average Rating</h3><p>${data.avg_rating} / 5</p></div>
        <div class="stat-box"><h3>Positive Comments</h3><p style="color: green;">${data.positive}</p></div>
        <div class="stat-box"><h3>Negative Comments</h3><p style="color: red;">${data.negative}</p></div>
    `;

    renderChart(data.positive, data.neutral, data.negative);
}

function renderChart(pos, neu, neg) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    if (sentimentChart) sentimentChart.destroy();

    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [pos, neu, neg],
                backgroundColor: ['#2ecc71', '#f1c40f', '#e74c3c']
            }]
        },
        options: { responsive: true }
    });
}