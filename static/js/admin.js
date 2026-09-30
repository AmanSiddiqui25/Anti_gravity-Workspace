// EcoClean Municipal Admin Central Portal Script

let adminData = {
    alertsGrouped: {},
    allAreas: [],
    users: [],
    collectors: []
};

let currentAlertFilter = 'High';

document.addEventListener('DOMContentLoaded', () => {
    initAdminPortal();
});

async function initAdminPortal() {
    await loadAdminDashboard();
    await loadWasteAreaAlerts();
    await loadAdminLoggers();
    await loadAdminEmployees();
}

// Tab Switching
function switchAdminTab(tabName) {
    const tabButtons = {
        'dashboard': document.getElementById('tabBtnAdminDashboard'),
        'alerts': document.getElementById('tabBtnAdminAlerts'),
        'loggers': document.getElementById('tabBtnAdminLoggers'),
        'employees': document.getElementById('tabBtnAdminEmployees')
    };

    const tabContents = {
        'dashboard': document.getElementById('tabContentAdminDashboard'),
        'alerts': document.getElementById('tabContentAdminAlerts'),
        'loggers': document.getElementById('tabContentAdminLoggers'),
        'employees': document.getElementById('tabContentAdminEmployees')
    };

    Object.keys(tabButtons).forEach(key => {
        if (tabButtons[key]) {
            tabButtons[key].className = "admin-tab-btn flex-1 min-w-[150px] py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2 text-slate-600 hover:text-indigo-700 hover:bg-slate-50 transition";
        }
        if (tabContents[key]) {
            tabContents[key].classList.add('hidden');
        }
    });

    if (tabButtons[tabName]) {
        tabButtons[tabName].className = "admin-tab-btn flex-1 min-w-[150px] py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2 bg-indigo-600 text-white shadow-sm transition";
    }
    if (tabContents[tabName]) {
        tabContents[tabName].classList.remove('hidden');
    }

    if (tabName === 'alerts') {
        loadWasteAreaAlerts();
    } else if (tabName === 'loggers') {
        loadAdminLoggers();
    } else if (tabName === 'employees') {
        loadAdminEmployees();
    }
}

// 1. Dashboard: Total numbers of = Users, Complains, Collector, Resolve complains
async function loadAdminDashboard() {
    try {
        const res = await fetch('/api/admin/dashboard');
        const data = await res.json();
        if (!data.success) return;

        // Total Numbers
        document.getElementById('statTotalUsers').textContent = data.counts.total_users;
        document.getElementById('statTotalComplaints').textContent = data.counts.total_complaints;
        document.getElementById('statTotalCollectors').textContent = data.counts.total_collectors;
        document.getElementById('statTotalResolved').textContent = data.counts.total_resolved;

        // Recent Activity Feed
        const feed = document.getElementById('adminRecentComplaintsList');
        if (data.recent_complaints.length === 0) {
            feed.innerHTML = `<p class="text-xs text-slate-400 py-6 text-center">No recent complaints.</p>`;
        } else {
            feed.innerHTML = data.recent_complaints.map(c => `
                <div class="p-3.5 rounded-2xl border border-slate-200/80 bg-slate-50/40 hover:bg-slate-50 transition flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <span class="w-8 h-8 rounded-xl ${c.status === 'Completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'} flex items-center justify-center text-xs font-bold">
                            ${c.status === 'Completed' ? '✓' : '!'}
                        </span>
                        <div>
                            <div class="flex items-center space-x-2">
                                <span class="text-xs font-mono font-bold text-slate-900">${c.complaint_id}</span>
                                <span class="text-xs text-slate-400">•</span>
                                <span class="text-xs font-semibold text-slate-700">${c.area}</span>
                            </div>
                            <p class="text-[11px] text-slate-500 line-clamp-1">${c.description}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${c.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
                            ${c.status}
                        </span>
                        <span class="block text-[10px] text-slate-400 mt-1">${c.created_at ? c.created_at.slice(5, 16) : ''}</span>
                    </div>
                </div>
            `).join('');
        }

    } catch (e) {
        console.error("Failed to load admin dashboard:", e);
    }
}

// 2. Waste Area Alert (4 Categories: High Red, Medium Orange, Low Yellow, Clear Green)
async function loadWasteAreaAlerts() {
    try {
        const res = await fetch('/api/admin/waste-area-alert');
        const data = await res.json();
        if (!data.success) return;

        adminData.alertsGrouped = data.grouped;
        adminData.allAreas = data.all_areas;

        // Update Button Counts
        document.getElementById('badgeCountHigh').textContent = data.summary.high_count;
        document.getElementById('badgeCountMedium').textContent = data.summary.medium_count;
        document.getElementById('badgeCountLow').textContent = data.summary.low_count;
        document.getElementById('badgeCountClear').textContent = data.summary.clear_count;

        // Render current filter
        renderAlertAreas(currentAlertFilter);

    } catch (e) {
        console.error("Failed to load waste area alerts:", e);
    }
}

function filterAreaAlerts(category) {
    currentAlertFilter = category;

    // Reset button states
    const btnHigh = document.getElementById('btnAlertHigh');
    const btnMedium = document.getElementById('btnAlertMedium');
    const btnLow = document.getElementById('btnAlertLow');
    const btnClear = document.getElementById('btnAlertClear');
    const btnAll = document.getElementById('btnAlertAll');

    [btnHigh, btnMedium, btnLow, btnClear].forEach(b => {
        b.className = "alert-btn bg-slate-50 text-slate-700 border border-slate-200 py-4 px-4 rounded-2xl text-center transition flex flex-col items-center justify-center space-y-1";
    });

    if (category === 'High') {
        btnHigh.className = "alert-btn active-high py-4 px-4 rounded-2xl border text-center transition flex flex-col items-center justify-center space-y-1";
    } else if (category === 'Medium') {
        btnMedium.className = "alert-btn active-medium py-4 px-4 rounded-2xl border text-center transition flex flex-col items-center justify-center space-y-1";
    } else if (category === 'Low') {
        btnLow.className = "alert-btn active-low py-4 px-4 rounded-2xl border text-center transition flex flex-col items-center justify-center space-y-1";
    } else if (category === 'Clear') {
        btnClear.className = "alert-btn active-clear py-4 px-4 rounded-2xl border text-center transition flex flex-col items-center justify-center space-y-1";
    }

    renderAlertAreas(category);
}

function renderAlertAreas(category) {
    const container = document.getElementById('areaAlertsContainer');
    const title = document.getElementById('currentAlertCategoryTitle');
    const countBadge = document.getElementById('currentAlertCategoryCount');

    let areasToShow = [];
    if (category === 'ALL') {
        areasToShow = adminData.allAreas;
        title.innerHTML = `Showing: All Municipal Areas Combined`;
    } else {
        areasToShow = adminData.alertsGrouped[category] || [];
        const colorLabel = category === 'High' ? '<span class="text-red-600 font-bold">🔴 High Alert (Red)</span>' 
            : (category === 'Medium' ? '<span class="text-orange-600 font-bold">🟠 Medium Alert (Orange)</span>' 
            : (category === 'Low' ? '<span class="text-yellow-600 font-bold">🟡 Low Alert (Yellow)</span>' 
            : '<span class="text-emerald-600 font-bold">🟢 Clear & Clean (Green)</span>'));
        title.innerHTML = `Showing: ${colorLabel}`;
    }

    countBadge.textContent = `${areasToShow.length} Areas`;

    if (areasToShow.length === 0) {
        container.innerHTML = `
            <div class="col-span-2 text-center py-12 bg-white rounded-3xl border border-slate-200">
                <i class="fa-solid fa-circle-info text-3xl text-slate-300 mb-2"></i>
                <p class="text-sm font-semibold text-slate-600">No areas currently in this alert tier.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = areasToShow.map(area => {
        let borderClass = 'border-slate-200';
        let alertBadge = '';

        if (area.category === 'High') {
            borderClass = 'border-red-400 bg-red-50/20 ring-1 ring-red-500/20';
            alertBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-red-600 text-white shadow-xs">🔴 High Alert (${area.active_count} active)</span>`;
        } else if (area.category === 'Medium') {
            borderClass = 'border-orange-400 bg-orange-50/20 ring-1 ring-orange-500/20';
            alertBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-orange-500 text-white shadow-xs">🟠 Medium Alert (${area.active_count} active)</span>`;
        } else if (area.category === 'Low') {
            borderClass = 'border-yellow-400 bg-yellow-50/20 ring-1 ring-yellow-500/20';
            alertBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-yellow-400 text-slate-900 shadow-xs">🟡 Low Alert (${area.active_count} active)</span>`;
        } else {
            borderClass = 'border-emerald-300 bg-emerald-50/20 ring-1 ring-emerald-500/20';
            alertBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-600 text-white shadow-xs">🟢 Clear (0 active)</span>`;
        }

        return `
            <div class="glass-card rounded-3xl p-6 border ${borderClass} flex flex-col justify-between">
                <div>
                    <!-- Card Header -->
                    <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                        <div>
                            <h4 class="text-lg font-bold font-heading text-slate-900">${area.area_name}</h4>
                            <span class="text-xs text-slate-500">
                                Assigned Collector: <strong class="text-slate-800">${area.collector_name}</strong> 
                                ${area.collector_phone !== 'N/A' ? `(${area.collector_phone})` : ''}
                            </span>
                        </div>
                        <div>${alertBadge}</div>
                    </div>

                    <!-- Complaint stats breakdown -->
                    <div class="grid grid-cols-3 gap-2 text-center text-xs mb-4 bg-slate-50 p-3 rounded-2xl border border-slate-100">
                        <div>
                            <span class="text-slate-400 block text-[10px] font-bold uppercase">Active Pending</span>
                            <span class="text-base font-extrabold text-slate-800">${area.active_count}</span>
                        </div>
                        <div>
                            <span class="text-slate-400 block text-[10px] font-bold uppercase">Resolved</span>
                            <span class="text-base font-extrabold text-emerald-600">${area.resolved_count}</span>
                        </div>
                        <div>
                            <span class="text-slate-400 block text-[10px] font-bold uppercase">Total Filed</span>
                            <span class="text-base font-extrabold text-slate-800">${area.total_count}</span>
                        </div>
                    </div>

                    <!-- Area Reported Complaints preview -->
                    <div>
                        <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">User Reported Issues:</span>
                        <div class="space-y-1.5 max-h-36 overflow-y-auto pr-1 text-xs">
                            ${area.complaints.length > 0 ? area.complaints.map(c => `
                                <div class="p-2 rounded-xl bg-white border border-slate-200/80 flex items-center justify-between">
                                    <div class="flex items-center space-x-2">
                                        <span class="font-mono text-[10px] font-bold text-slate-500">${c.complaint_id}</span>
                                        <span class="text-slate-700 line-clamp-1 text-[11px]">${c.description}</span>
                                    </div>
                                    <span class="text-[10px] font-semibold ${c.status === 'Completed' ? 'text-emerald-600' : 'text-amber-600'}">${c.status}</span>
                                </div>
                            `).join('') : '<p class="text-slate-400 text-xs italic">No open complaints reported.</p>'}
                        </div>
                    </div>
                </div>

                <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span><i class="fa-solid fa-clock-rotate-left mr-1"></i> Continuous Monitoring</span>
                    <span class="text-indigo-600 font-semibold">Priority: ${area.category}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 3. Loggers (Users table)
async function loadAdminLoggers() {
    try {
        const res = await fetch('/api/admin/loggers');
        const data = await res.json();
        if (!data.success) return;

        adminData.users = data.users;
        renderLoggersTable(adminData.users);

    } catch (e) {
        console.error("Failed to load user loggers:", e);
    }
}

function renderLoggersTable(users) {
    const tbody = document.getElementById('loggersTableBody');
    if (!tbody) return;

    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="p-6 text-center text-slate-400">No user records found.</td></tr>`;
        return;
    }

    tbody.innerHTML = users.map(u => `
        <tr class="hover:bg-slate-50 transition">
            <td class="p-3 font-mono font-bold text-indigo-700">${u.unique_id}</td>
            <td class="p-3 font-semibold text-slate-900">${u.name}</td>
            <td class="p-3 text-slate-600">${u.age || '-'}</td>
            <td class="p-3 text-slate-600">${u.gender || '-'}</td>
            <td class="p-3 text-slate-800 font-medium">${u.area}</td>
            <td class="p-3 text-slate-600">${u.email}</td>
            <td class="p-3 text-slate-600">${u.phone}</td>
            <td class="p-3 text-center">
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold ${u.total_reports >= 25 ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-700'}">
                    ${u.total_reports} Filed
                </span>
            </td>
            <td class="p-3 text-slate-400 text-[11px]">${u.created_at ? u.created_at.slice(0, 10) : ''}</td>
        </tr>
    `).join('');
}

function searchLoggersTable() {
    const query = document.getElementById('loggerSearchInput').value.toLowerCase().trim();
    if (!query) {
        renderLoggersTable(adminData.users);
        return;
    }
    const filtered = adminData.users.filter(u => 
        (u.name && u.name.toLowerCase().includes(query)) ||
        (u.unique_id && u.unique_id.toLowerCase().includes(query)) ||
        (u.area && u.area.toLowerCase().includes(query)) ||
        (u.email && u.email.toLowerCase().includes(query)) ||
        (u.phone && u.phone.includes(query))
    );
    renderLoggersTable(filtered);
}

// 4. Employees (Waste Collector table)
async function loadAdminEmployees() {
    try {
        const res = await fetch('/api/admin/employees');
        const data = await res.json();
        if (!data.success) return;

        adminData.collectors = data.collectors;
        renderEmployeesTable(adminData.collectors);

    } catch (e) {
        console.error("Failed to load collector employees:", e);
    }
}

function renderEmployeesTable(collectors) {
    const tbody = document.getElementById('employeesTableBody');
    if (!tbody) return;

    if (collectors.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="p-6 text-center text-slate-400">No collector employees registered.</td></tr>`;
        return;
    }

    tbody.innerHTML = collectors.map(c => `
        <tr class="hover:bg-slate-50 transition">
            <td class="p-3 font-mono font-bold text-teal-700">${c.unique_id}</td>
            <td class="p-3 font-semibold text-slate-900">${c.name}</td>
            <td class="p-3 text-slate-600">${c.gender || '-'}</td>
            <td class="p-3 text-slate-600">${c.phone}</td>
            <td class="p-3 text-slate-600">${c.email}</td>
            <td class="p-3 text-teal-800 font-bold">${c.area_assigned}</td>
            <td class="p-3 text-center text-slate-700 font-medium">${c.total_assigned}</td>
            <td class="p-3 text-center font-bold text-emerald-600">${c.total_resolved}</td>
            <td class="p-3 text-center font-black text-amber-600">🪙 ${c.coins}</td>
        </tr>
    `).join('');
}

function searchEmployeesTable() {
    const query = document.getElementById('employeeSearchInput').value.toLowerCase().trim();
    if (!query) {
        renderEmployeesTable(adminData.collectors);
        return;
    }
    const filtered = adminData.collectors.filter(c => 
        (c.name && c.name.toLowerCase().includes(query)) ||
        (c.unique_id && c.unique_id.toLowerCase().includes(query)) ||
        (c.area_assigned && c.area_assigned.toLowerCase().includes(query)) ||
        (c.email && c.email.toLowerCase().includes(query)) ||
        (c.phone && c.phone.includes(query))
    );
    renderEmployeesTable(filtered);
}

// Add Collector Modal Handlers
function openAddCollectorModal() {
    document.getElementById('addCollectorModal').classList.remove('hidden');
}

function closeAddCollectorModal() {
    document.getElementById('addCollectorModal').classList.add('hidden');
}

async function submitAddCollector(e) {
    e.preventDefault();
    const name = document.getElementById('newColName').value.trim();
    const gender = document.getElementById('newColGender').value;
    const phone = document.getElementById('newColPhone').value.trim();
    const email = document.getElementById('newColEmail').value.trim();
    const area_assigned = document.getElementById('newColArea').value;
    const password = document.getElementById('newColPass').value;

    try {
        const res = await fetch('/api/admin/employees', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, gender, phone, email, area_assigned, password })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            closeAddCollectorModal();
            await loadAdminEmployees();
            await loadAdminDashboard();
        } else {
            showToast(data.message || 'Registration failed.', 'error');
        }
    } catch (err) {
        showToast('Error registering employee.', 'error');
    }
}
