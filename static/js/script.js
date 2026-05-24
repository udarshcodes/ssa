document.addEventListener('DOMContentLoaded', function() {
    console.log("StudyForge loaded!");


    async function fetchAndDisplayDashboardData() {
        const dashboardDataContainer = document.getElementById('dashboard-data');
        if (!dashboardDataContainer) {
            return;
        }

        try {
            const response = await fetch('/api/study_dashboard_data');
            const data = await response.json();

            let html = '';


            html += '<h4 class="mt-4">Study Time Per Topic (minutes)</h4>';
            if (data.study_time_per_topic && data.study_time_per_topic.length > 0) {

                const maxTime = Math.max(...data.study_time_per_topic.map(item => item.total_minutes));
                html += '<ul class="list-group mb-3">';
                data.study_time_per_topic.forEach(item => {
                    const barWidth = (item.total_minutes / maxTime) * 100;
                    html += `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span>${item.topic_name}</span>
                            <div class="progress" style="width: 70%;">
                                <div class="progress-bar" role="progressbar" style="width: ${barWidth}%;" aria-valuenow="${item.total_minutes}" aria-valuemin="0" aria-valuemax="${maxTime}">
                                    ${item.total_minutes} min
                                </div>
                            </div>
                        </li>
                    `;
                });
                html += '</ul>';
            } else {
                html += '<p class="text-muted">No study time recorded yet.</p>';
            }


            html += '<h4 class="mt-4">Average Understanding Per Topic (1=Poor, 5=Excellent)</h4>';
            if (data.avg_understanding_per_topic && data.avg_understanding_per_topic.length > 0) {
                html += '<ul class="list-group mb-3">';
                data.avg_understanding_per_topic.forEach(item => {
                    html += `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span>${item.topic_name}</span>
                            <span class="badge bg-secondary rounded-pill">${item.avg_understanding.toFixed(1)}</span>
                        </li>
                    `;
                });
                html += '</ul>';
            } else {
                html += '<p class="text-muted">No understanding data yet.</p>';
            }


            html += '<h4 class="mt-4">Recent Quiz Scores</h4>';
            if (data.recent_quiz_scores && data.recent_quiz_scores.length > 0) {
                html += '<ul class="list-group">';
                data.recent_quiz_scores.forEach(item => {
                    const topicName = item.topic_name ? item.topic_name : 'All Topics';
                    html += `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span>${topicName} - ${item.attempt_date.split(' ')[0]}</span>
                            <span class="badge bg-info text-dark rounded-pill">${item.score} / ${item.total_questions}</span>
                        </li>
                    `;
                });
                html += '</ul>';
            } else {
                html += '<p class="text-muted">No quiz attempts recorded yet.</p>';
            }

            dashboardDataContainer.innerHTML = html;

        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            dashboardDataContainer.innerHTML = '<p class="text-danger">Failed to load dashboard data.</p>';
        }
    }


    fetchAndDisplayDashboardData();
});
