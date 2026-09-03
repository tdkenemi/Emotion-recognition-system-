/**
 * EmotionAI - Admin Dashboard JavaScript
 * Tác giả: Triệu Duy Khang | ĐH Nguyễn Tất Thành - Khoa CNTT
 */
(() => {
    'use strict';

    const EMOTIONS = [
        { key: 'Tức giận', emoji: '😠', color: '#f87171' },
        { key: 'Ghê tởm',  emoji: '🤢', color: '#a3e635' },
        { key: 'Sợ hãi',   emoji: '😨', color: '#c084fc' },
        { key: 'Vui vẻ',   emoji: '😊', color: '#fbbf24' },
        { key: 'Bình thường', emoji: '😐', color: '#94a3b8' },
        { key: 'Buồn bã',  emoji: '😢', color: '#60a5fa' },
        { key: 'Bất ngờ',  emoji: '😮', color: '#34d399' }
    ];

    const state = {
        history: [],
        feedbacks: [],
        users: [],
        token: localStorage.getItem('emotionai_token'),
        currentPage: 1,
        perPage: 20,
        totalPages: 1,
        usersPage: 1,
        usersTotalPages: 1,
        autoRefreshInterval: null,
        charts: {}
    };

    const $ = id => document.getElementById(id);

    function init() {
        if (!state.token) {
            window.location.href = '/';
            return;
        }
        bindEvents();
        loadAll();
    }

    function bindEvents() {
        $('btn-logout')?.addEventListener('click', () => {
            localStorage.removeItem('emotionai_token');
            window.location.href = '/';
        });
        $('btn-auto-refresh')?.addEventListener('click', toggleAutoRefresh);
        $('btn-export-csv')?.addEventListener('click', exportToCSV);
        $('btn-refresh-now')?.addEventListener('click', () => loadAll());

        // Admin Tabs
        document.querySelectorAll('.admin-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => switchAdminTab(btn.dataset.tab));
        });

        // Filter & Search
        $('filter-emotion')?.addEventListener('change', () => loadHistory(1));
        $('search-history')?.addEventListener('input', debounce(() => filterHistoryLocal(), 300));
    }

    function debounce(fn, delay) {
        let timer;
        return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
    }

    function showToast(message, type = 'success') {
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        const t = document.createElement('div');
        t.className = `toast toast-${type}`;
        t.innerHTML = `<span class="toast-icon-wrap">${icons[type]}</span><div class="toast-body"><div class="toast-msg">${message}</div></div>`;
        $('toast-container').appendChild(t);
        setTimeout(() => t.remove(), 3500);
    }

    function switchAdminTab(tab) {
        document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
        document.querySelectorAll('.admin-tab-content').forEach(c => {
            c.classList.toggle('active', c.id === `tab-${tab}`);
        });
        if (tab === 'users') loadUsers();
    }

    // =========================================================================
    // LOAD DATA
    // =========================================================================
    async function loadAll() {
        await Promise.all([loadStats(), loadTrend(), loadHistory(state.currentPage), loadFeedback()]);
        updateLastUpdated();
    }

    async function apiGet(url) {
        const res = await fetch(url, { headers: { 'Authorization': `Bearer ${state.token}` } });
        if (res.status === 401 || res.status === 403) {
            localStorage.removeItem('emotionai_token');
            window.location.href = '/';
        }
        return res.json();
    }

    async function loadStats() {
        try {
            const s = await apiGet('/api/stats');
            renderStats(s);
            renderDoughnutChart(s.emotion_distribution || {});
            renderBarChart(s.emotion_distribution || {});
        } catch { showToast('Lỗi tải thống kê', 'error'); }
    }

    async function loadTrend() {
        try {
            const d = await apiGet('/api/stats/trend');
            renderTrendChart(d.trend || []);
        } catch {}
    }

    async function loadHistory(page = 1) {
        const emotion = $('filter-emotion')?.value || '';
        const url = `/api/history?page=${page}&per_page=${state.perPage}${emotion ? `&emotion=${encodeURIComponent(emotion)}` : ''}`;
        try {
            const d = await apiGet(url);
            state.history = d.history || [];
            state.feedbacks = d.feedbacks || [];
            state.currentPage = d.pagination?.page || 1;
            state.totalPages = d.pagination?.total_pages || 1;
            renderHistoryTable();
            renderFeedbackTable();
            renderPagination('pagination-history', state.currentPage, state.totalPages, p => loadHistory(p));
        } catch { showToast('Lỗi tải lịch sử', 'error'); }
    }

    async function loadFeedback() {
        // Already loaded in loadHistory
    }

    async function loadUsers() {
        try {
            const d = await apiGet(`/api/users?page=${state.usersPage}&per_page=20`);
            state.users = d.users || [];
            state.usersTotalPages = d.pagination?.total_pages || 1;
            renderUsersTable();
            renderPagination('pagination-users', state.usersPage, state.usersTotalPages, p => {
                state.usersPage = p;
                loadUsers();
            });
        } catch { showToast('Lỗi tải danh sách users', 'error'); }
    }

    function updateLastUpdated() {
        const el = $('last-updated-text');
        if (el) el.innerText = `Cập nhật lần cuối: ${new Date().toLocaleTimeString('vi-VN')}`;
    }

    // =========================================================================
    // RENDER STATS
    // =========================================================================
    function renderStats(s) {
        animateNumber('stat-total', s.total_analyses || 0);
        animateNumber('stat-feedback', s.total_feedbacks || 0);
        if (s.accuracy_percent !== null && s.accuracy_percent !== undefined) {
            $('stat-accuracy').innerText = `${s.accuracy_percent}%`;
        } else {
            $('stat-accuracy').innerText = 'N/A';
        }
        animateNumber('stat-users', s.user_count || 0);
    }

    function animateNumber(id, target) {
        const el = $(id);
        if (!el) return;
        let start = 0;
        const duration = 1200;
        const step = target / (duration / 16);
        const timer = setInterval(() => {
            start = Math.min(start + step, target);
            el.innerText = Math.floor(start).toLocaleString('vi-VN');
            if (start >= target) clearInterval(timer);
        }, 16);
    }

    // =========================================================================
    // RENDER CHARTS
    // =========================================================================
    const CHART_DEFAULTS = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#9ca3af', font: { family: 'Inter', size: 12 } } },
            tooltip: { callbacks: {} }
        }
    };

    function renderDoughnutChart(distribution) {
        const ctx = $('chart-doughnut')?.getContext('2d');
        if (!ctx) return;
        if (state.charts.doughnut) state.charts.doughnut.destroy();

        const ordered = EMOTIONS.map(e => ({ label: `${e.emoji} ${e.key}`, count: distribution[e.key] || 0, color: e.color }));
        state.charts.doughnut = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ordered.map(o => o.label),
                datasets: [{ data: ordered.map(o => o.count), backgroundColor: ordered.map(o => o.color), borderWidth: 0, hoverOffset: 8 }]
            },
            options: {
                ...CHART_DEFAULTS,
                cutout: '65%',
                plugins: { ...CHART_DEFAULTS.plugins, legend: { position: 'right', labels: { color: '#9ca3af', boxWidth: 14 } } }
            }
        });
    }

    function renderTrendChart(trend) {
        const ctx = $('chart-trend')?.getContext('2d');
        if (!ctx) return;
        if (state.charts.trend) state.charts.trend.destroy();

        state.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trend.map(t => t.date),
                datasets: [{
                    label: 'Lượt phân tích',
                    data: trend.map(t => t.count),
                    borderColor: '#7c3aed',
                    backgroundColor: 'rgba(124,58,237,0.12)',
                    borderWidth: 2.5,
                    pointBackgroundColor: '#7c3aed',
                    pointRadius: 5,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.04)' } },
                    y: { ticks: { color: '#9ca3af', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.04)' }, beginAtZero: true }
                },
                plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } }
            }
        });
    }

    function renderBarChart(distribution) {
        const ctx = $('chart-bar')?.getContext('2d');
        if (!ctx) return;
        if (state.charts.bar) state.charts.bar.destroy();

        const ordered = EMOTIONS.map(e => ({ label: `${e.emoji} ${e.key}`, count: distribution[e.key] || 0, color: e.color }));
        state.charts.bar = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ordered.map(o => o.label),
                datasets: [{
                    data: ordered.map(o => o.count),
                    backgroundColor: ordered.map(o => o.color + '99'),
                    borderColor: ordered.map(o => o.color),
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    x: { ticks: { color: '#9ca3af', font: { size: 11 } }, grid: { display: false } },
                    y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.04)' }, beginAtZero: true }
                },
                plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } }
            }
        });
    }

    // =========================================================================
    // RENDER TABLES
    // =========================================================================
    function renderHistoryTable() {
        const tbody = $('tbody-history');
        if (!tbody) return;
        tbody.innerHTML = state.history.length ? state.history.map(row => `
            <tr>
                <td>${row.time}</td>
                <td style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${row.filename}">${row.filename}</td>
                <td><span class="badge badge-ai">${getEmoji(row.ai_prediction)} ${row.ai_prediction}</span></td>
                <td>${row.confidence ? row.confidence.toFixed(1) + '%' : '-'}</td>
                <td>${row.user || '<span style="color:var(--text-muted)">Khách</span>'}</td>
                <td style="font-size:0.8rem;color:var(--text-muted);">${row.ip || '-'}</td>
                <td>
                    <button class="btn btn-danger" style="padding:3px 8px;font-size:0.75rem;"
                        onclick="deleteRecord('${row._id}', this)">🗑️</button>
                </td>
            </tr>
        `).join('') : emptyRow(7, 'Chưa có lịch sử phân tích');
    }

    function renderFeedbackTable() {
        const tbody = $('tbody-feedback');
        if (!tbody) return;
        tbody.innerHTML = state.feedbacks.length ? state.feedbacks.map(row => `
            <tr>
                <td>${row.time}</td>
                <td style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${row.filename}</td>
                <td><span class="badge badge-ai">${getEmoji(row.ai_prediction)} ${row.ai_prediction}</span></td>
                <td><span class="badge ${row.is_correct ? 'badge-correct' : 'badge-wrong'}">${getEmoji(row.correct_emotion)} ${row.correct_emotion}</span></td>
                <td>${row.is_correct ? '✅ Đúng' : '❌ Sai'}</td>
                <td>${row.user || '<span style="color:var(--text-muted)">Khách</span>'}</td>
            </tr>
        `).join('') : emptyRow(6, 'Chưa có feedback nào');
    }

    function renderUsersTable() {
        const tbody = $('tbody-users');
        if (!tbody) return;
        tbody.innerHTML = state.users.length ? state.users.map(u => `
            <tr>
                <td><strong>${u.username}</strong></td>
                <td><span class="badge ${u.role === 'admin' ? 'badge-ai' : 'badge-pending'}">${u.role === 'admin' ? '👑 Admin' : '👤 User'}</span></td>
                <td style="color:var(--text-muted);font-size:0.88rem;">${u.created_at || '—'}</td>
            </tr>
        `).join('') : emptyRow(3, 'Chưa có người dùng');
    }

    function emptyRow(cols, msg) {
        return `<tr><td colspan="${cols}" style="text-align:center;color:var(--text-muted);padding:40px;">${msg}</td></tr>`;
    }

    function getEmoji(key) {
        return EMOTIONS.find(e => e.key === key)?.emoji || '❓';
    }

    // =========================================================================
    // PAGINATION
    // =========================================================================
    function renderPagination(containerId, current, total, onPageClick) {
        const container = $(containerId);
        if (!container || total <= 1) { if (container) container.innerHTML = ''; return; }

        let html = '';
        if (current > 1) html += `<button class="btn btn-secondary" style="padding:5px 10px;font-size:0.8rem;" data-page="${current - 1}">‹ Trước</button>`;

        const start = Math.max(1, current - 2);
        const end = Math.min(total, current + 2);

        if (start > 1) html += `<button class="btn btn-secondary" style="padding:5px 10px;font-size:0.8rem;" data-page="1">1</button><span style="color:var(--text-muted);padding:0 4px;">…</span>`;
        for (let i = start; i <= end; i++) {
            html += `<button class="btn ${i === current ? 'btn-primary' : 'btn-secondary'}" style="padding:5px 10px;font-size:0.8rem;" data-page="${i}">${i}</button>`;
        }
        if (end < total) html += `<span style="color:var(--text-muted);padding:0 4px;">…</span><button class="btn btn-secondary" style="padding:5px 10px;font-size:0.8rem;" data-page="${total}">${total}</button>`;

        if (current < total) html += `<button class="btn btn-secondary" style="padding:5px 10px;font-size:0.8rem;" data-page="${current + 1}">Tiếp ›</button>`;

        container.innerHTML = html;
        container.querySelectorAll('[data-page]').forEach(btn => {
            btn.addEventListener('click', () => onPageClick(parseInt(btn.dataset.page)));
        });
    }

    // =========================================================================
    // FILTER (client-side search)
    // =========================================================================
    function filterHistoryLocal() {
        const q = $('search-history')?.value?.toLowerCase() || '';
        const rows = $('tbody-history')?.querySelectorAll('tr') || [];
        rows.forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
        });
    }

    // =========================================================================
    // DELETE RECORD
    // =========================================================================
    window.deleteRecord = async function(id, btn) {
        if (!confirm('Xác nhận xóa bản ghi này?')) return;
        btn.disabled = true;
        btn.innerText = '...';
        try {
            const res = await fetch(`/api/history/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${state.token}` }
            });
            if (res.ok) {
                btn.closest('tr').remove();
                showToast('Đã xóa bản ghi', 'success');
            } else {
                showToast('Không thể xóa', 'error');
                btn.disabled = false;
                btn.innerText = '🗑️';
            }
        } catch {
            showToast('Lỗi mạng', 'error');
            btn.disabled = false;
            btn.innerText = '🗑️';
        }
    };

    // =========================================================================
    // AUTO REFRESH
    // =========================================================================
    function toggleAutoRefresh() {
        const btn = $('btn-auto-refresh');
        if (state.autoRefreshInterval) {
            clearInterval(state.autoRefreshInterval);
            state.autoRefreshInterval = null;
            btn.innerText = '🔄 Auto-Refresh: TẮT';
            btn.className = 'btn btn-secondary';
        } else {
            state.autoRefreshInterval = setInterval(loadAll, 30000);
            btn.innerText = '🔄 Auto-Refresh: BẬT (30s)';
            btn.className = 'btn btn-primary';
            showToast('Đã bật tự động làm mới mỗi 30 giây', 'success');
        }
    }

    // =========================================================================
    // EXPORT CSV
    // =========================================================================
    function exportToCSV() {
        if (!state.history.length) { showToast('Không có dữ liệu để xuất', 'warning'); return; }
        const header = 'Thời gian,Tên File,AI Dự đoán,Độ tự tin,User,IP\n';
        const rows = state.history.map(r =>
            `"${r.time}","${r.filename}","${r.ai_prediction}",${r.confidence || 0},"${r.user || ''}","${r.ip || ''}"`
        ).join('\n');
        const blob = new Blob(['\uFEFF' + header + rows], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `emotionai_history_${new Date().toISOString().slice(0,10)}.csv`;
        link.click();
        URL.revokeObjectURL(url);
        showToast('Đã tải xuống CSV thành công', 'success');
    }

    // Run
    document.addEventListener('DOMContentLoaded', init);
    if (document.readyState !== 'loading') init();
})();
