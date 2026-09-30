// EcoClean Waste Collector Portal Script

let currentCollector = null;
let collectorComplaints = [];

document.addEventListener('DOMContentLoaded', () => {
    initCollectorPortal();
});

async function initCollectorPortal() {
    await loadCollectorDashboard();
    await loadCollectorProfile();
}

// Tab Switching Logic
function switchColTab(tabName) {
    const tabButtons = {
        'dashboard': document.getElementById('tabBtnColDashboard'),
        'progress': document.getElementById('tabBtnColProgress'),
        'profile': document.getElementById('tabBtnColProfile')
    };

    const tabContents = {
        'dashboard': document.getElementById('tabContentColDashboard'),
        'progress': document.getElementById('tabContentColProgress'),
        'profile': document.getElementById('tabContentColProfile')
    };

    // Reset styles
    Object.keys(tabButtons).forEach(key => {
        if (tabButtons[key]) {
            tabButtons[key].className = "col-tab-btn flex-1 min-w-[150px] py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2 text-slate-600 hover:text-teal-700 hover:bg-slate-50 transition";
        }
        if (tabContents[key]) {
            tabContents[key].classList.add('hidden');
        }
    });

    // Activate selected
    if (tabButtons[tabName]) {
        tabButtons[tabName].className = "col-tab-btn flex-1 min-w-[150px] py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2 bg-teal-600 text-white shadow-sm transition";
    }
    if (tabContents[tabName]) {
        tabContents[tabName].classList.remove('hidden');
    }

    if (tabName === 'progress') {
        loadCollectorProgress();
    } else if (tabName === 'dashboard') {
        loadCollectorDashboard();
    } else if (tabName === 'profile') {
        loadCollectorProfile();
    }
}

// 1. Collector Dashboard & Data Loading
async function loadCollectorDashboard() {
    try {
        const res = await fetch('/api/collector/dashboard');
        const data = await res.json();
        if (!data.success) return;

        currentCollector = data.collector;

        // Header Update
        document.getElementById('colNameHeader').textContent = currentCollector.name;
        document.getElementById('colUniqueIdHeader').textContent = currentCollector.unique_id;
        document.getElementById('colAreaHeader').textContent = currentCollector.area_assigned;
        document.getElementById('colCoinsHeader').textContent = currentCollector.coins;
        document.getElementById('colProgressPctHeader').textContent = `${data.stats.progress_percentage}%`;

        // Stats Cards
        document.getElementById('statPendingCount').textContent = data.stats.pending_count;
        document.getElementById('statResolvedCount').textContent = data.stats.resolved_count;
        document.getElementById('statTotalCount').textContent = data.stats.total_assigned;
        document.getElementById('statAreaNameLabel').textContent = currentCollector.area_assigned;

        // Render Dashboard Pending Queue
        const pendingContainer = document.getElementById('dashboardPendingList');
        if (data.pending_complaints.length === 0) {
            pendingContainer.innerHTML = `<p class="text-center text-slate-400 py-8 text-xs">No pending complaints in your area!</p>`;
        } else {
            pendingContainer.innerHTML = data.pending_complaints.map(c => `
                <div class="p-4 rounded-2xl border border-amber-200/70 bg-amber-50/30 flex flex-col justify-between space-y-2">
                    <div class="flex items-center justify-between">
                        <span class="font-mono text-xs font-bold text-slate-800">${c.complaint_id}</span>
                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 uppercase">
                            ${c.status}
                        </span>
                    </div>
                    <p class="text-xs text-slate-700 leading-snug line-clamp-2">${c.description}</p>
                    <div class="flex items-center justify-between pt-2 border-t border-amber-200/40 text-[11px] text-slate-500">
                        <span>Reported by: <strong class="text-slate-700">${c.user_name}</strong></span>
                        <button onclick="switchColTab('progress')" class="text-teal-700 font-bold hover:underline">
                            Resolve with photo →
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Render Dashboard Resolved List
        const resolvedContainer = document.getElementById('dashboardResolvedList');
        if (data.resolved_complaints.length === 0) {
            resolvedContainer.innerHTML = `<p class="text-center text-slate-400 py-8 text-xs">No resolved tasks yet.</p>`;
        } else {
            resolvedContainer.innerHTML = data.resolved_complaints.map(c => `
                <div class="p-4 rounded-2xl border border-emerald-100 bg-emerald-50/30">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-mono text-xs font-bold text-slate-800">${c.complaint_id}</span>
                        <span class="text-[10px] text-emerald-700 font-bold flex items-center space-x-1">
                            <i class="fa-solid fa-circle-check"></i>
                            <span>Cleaned</span>
                        </span>
                    </div>
                    <p class="text-xs text-slate-600 line-clamp-1 mb-2">${c.description}</p>
                    ${c.resolved_image_path ? `
                        <div class="flex items-center space-x-3 mt-2 pt-2 border-t border-emerald-100">
                            <img src="${c.resolved_image_path}" class="w-12 h-12 rounded-lg object-cover border border-emerald-200 cursor-pointer" onclick="window.open('${c.resolved_image_path}')">
                            <span class="text-[11px] text-slate-500 italic">"${c.resolved_notes || 'Cleaned and disinfected'}"</span>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }

    } catch (e) {
        console.error("Failed to load collector dashboard:", e);
    }
}

// 2. Personal Progress & Resolution
async function loadCollectorProgress() {
    try {
        const res = await fetch('/api/collector/dashboard');
        const data = await res.json();
        if (!data.success) return;

        const pct = data.stats.progress_percentage;

        // Animate Progress Bar
        const fill = document.getElementById('colProgressBarFill');
        const label = document.getElementById('colProgressBarLabel');
        const bigPct = document.getElementById('colProgressBigPct');
        const badge = document.getElementById('progressTasksBadge');

        fill.style.width = `${pct}%`;
        label.textContent = `${pct}%`;
        bigPct.textContent = `${pct}%`;
        badge.textContent = `${data.pending_complaints.length} Pending Tasks`;

        // Render Action Complaints List
        const list = document.getElementById('colActionComplaintsList');
        if (data.pending_complaints.length === 0) {
            list.innerHTML = `
                <div class="text-center py-12">
                    <div class="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-3 text-2xl">
                        <i class="fa-solid fa-champagne-glasses"></i>
                    </div>
                    <h4 class="text-base font-bold text-slate-800">All Area Complaints Cleared!</h4>
                    <p class="text-xs text-slate-500 mt-1">Outstanding job! You have cleaned all reported waste points in ${currentCollector.area_assigned}.</p>
                </div>
            `;
            return;
        }

        list.innerHTML = data.pending_complaints.map(c => `
            <div class="glass-card rounded-3xl p-6 border border-slate-200 hover:border-teal-400 transition">
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="font-mono text-sm font-bold text-slate-900">${c.complaint_id}</span>
                            <span class="text-xs text-slate-400">•</span>
                            <span class="text-xs font-semibold text-teal-700">${c.area}</span>
                        </div>
                        <span class="text-[11px] text-slate-400">Reported by Citizen: <strong>${c.user_name}</strong></span>
                    </div>
                    <div>
                        <span class="px-3 py-1 rounded-xl text-xs font-bold bg-amber-100 text-amber-800 flex items-center space-x-1">
                            <i class="fa-solid fa-stopwatch sla-pulse"></i>
                            <span>48h SLA Action Required</span>
                        </span>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-4">
                    <div class="md:col-span-2">
                        <span class="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Issue Details</span>
                        <p class="text-xs sm:text-sm text-slate-800 leading-relaxed font-medium bg-slate-50 p-4 rounded-2xl border border-slate-100">
                            ${c.description}
                        </p>
                    </div>

                    <div>
                        <span class="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Citizen's Waste Photo</span>
                        ${c.image_path ? `
                            <img src="${c.image_path}" class="w-full h-32 object-cover rounded-2xl border border-slate-200 shadow-xs cursor-pointer" onclick="window.open('${c.image_path}')">
                        ` : `
                            <div class="w-full h-32 rounded-2xl border border-dashed border-slate-200 flex items-center justify-center text-xs text-slate-400">
                                No initial photo
                            </div>
                        `}
                    </div>
                </div>

                <div class="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
                    <span class="text-xs text-slate-500">
                        <i class="fa-solid fa-camera-rotate text-teal-600 mr-1"></i>
                        Requires verification photo of cleaned place to resolve
                    </span>
                    <button onclick="openResolveModal('${c.complaint_id}', '${c.area}')" class="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-md shadow-teal-600/20 transition flex items-center space-x-1.5">
                        <i class="fa-solid fa-check-double"></i>
                        <span>Resolve &amp; Upload Proof Photo</span>
                    </button>
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error("Failed to load progress:", e);
    }
}

// 3. Resolve Modal & Photo Proof Upload
function openResolveModal(complaintId, area) {
    document.getElementById('resolveComplaintId').value = complaintId;
    document.getElementById('modalComplaintIdDisplay').textContent = complaintId;
    document.getElementById('modalAreaDisplay').textContent = area;
    document.getElementById('resolvedPictureInput').value = '';
    document.getElementById('resolvedPreview').src = '';
    document.getElementById('resolvedPlaceholder').classList.remove('hidden');
    document.getElementById('resolvedPreviewContainer').classList.add('hidden');
    document.getElementById('resolveModal').classList.remove('hidden');
}

function closeResolveModal() {
    document.getElementById('resolveModal').classList.add('hidden');
}

function previewResolvedImage(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            document.getElementById('resolvedPreview').src = event.target.result;
            document.getElementById('resolvedPlaceholder').classList.add('hidden');
            document.getElementById('resolvedPreviewContainer').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

function clearResolvedImage(e) {
    e.stopPropagation();
    document.getElementById('resolvedPictureInput').value = '';
    document.getElementById('resolvedPreview').src = '';
    document.getElementById('resolvedPlaceholder').classList.remove('hidden');
    document.getElementById('resolvedPreviewContainer').classList.add('hidden');
}

async function submitResolveComplaint(e) {
    e.preventDefault();
    const complaintId = document.getElementById('resolveComplaintId').value;
    const notes = document.getElementById('resolvedNotes').value.trim();
    const pictureFile = document.getElementById('resolvedPictureInput').files[0];

    if (!pictureFile) {
        showToast('Proof photo is mandatory to verify place resolution.', 'error');
        return;
    }

    const submitBtn = document.getElementById('resolveSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Verifying...`;

    const formData = new FormData();
    formData.append('complaint_id', complaintId);
    formData.append('notes', notes);
    formData.append('resolved_picture', pictureFile);

    try {
        const res = await fetch('/api/collector/resolve-complaint', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            closeResolveModal();
            // Refresh data & progress
            await loadCollectorDashboard();
            await loadCollectorProgress();
            await loadCollectorProfile();
        } else {
            showToast(data.message || 'Failed to complete resolution.', 'error');
        }
    } catch (err) {
        showToast('Submission error.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-check-double"></i> <span>Confirm &amp; Complete Task</span>`;
    }
}

// 4. Collector Profile & Digital Coins Rewards
async function loadCollectorProfile() {
    try {
        const res = await fetch('/api/collector/profile');
        const data = await res.json();
        if (!data.success) return;

        const c = data.collector;
        const rewards = data.reward_details;

        // Details Card
        document.getElementById('colProfUniqueId').textContent = c.unique_id;
        document.getElementById('colProfName').textContent = c.name;
        document.getElementById('colProfGender').textContent = c.gender || 'N/A';
        document.getElementById('colProfArea').textContent = c.area_assigned;
        document.getElementById('colProfPhone').textContent = c.phone;
        document.getElementById('colProfEmail').textContent = c.email;

        // Rewards Section
        document.getElementById('rewardWalletCoins').textContent = rewards.coins;
        document.getElementById('rewardCashINR').textContent = `₹${rewards.cash_value_inr.toLocaleString()}`;
        document.getElementById('rewardCashUSD').textContent = `≈ $${rewards.cash_value_usd.toLocaleString()} USD`;

        const dailyStatus = document.getElementById('dailyCoinStatusText');
        if (rewards.daily_awarded_today) {
            dailyStatus.innerHTML = `<i class="fa-solid fa-circle-check text-white"></i> <span>Today's 1 Coin already awarded for &ge;70% completion! 🌟</span>`;
        } else {
            dailyStatus.innerHTML = `<i class="fa-solid fa-clock"></i> <span>Complete 70% of today's tasks to earn +1 coin today!</span>`;
        }

    } catch (e) {
        console.error("Failed to load collector profile:", e);
    }
}

function requestMonthEndPayout() {
    const coins = document.getElementById('rewardWalletCoins').textContent;
    const inr = document.getElementById('rewardCashINR').textContent;
    const usd = document.getElementById('rewardCashUSD').textContent;

    showToast(`Month-End Statement: ${coins} Digital Coins converted to ${inr} (${usd}). Scheduled for direct bank transfer on the 31st!`, 'success');
}
