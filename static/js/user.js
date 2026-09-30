// EcoClean Citizen User Portal Script

let currentCitizen = null;
let currentComplaints = [];

document.addEventListener('DOMContentLoaded', () => {
    initUserPortal();
});

async function initUserPortal() {
    await loadUserProfile();
    await loadUserRewards();
    await loadUserComplaints();
    await loadAreaDetails();
}

// Tab Switching Logic
function switchUserTab(tabName) {
    const tabButtons = {
        'report': document.getElementById('tabBtnReport'),
        'rewards': document.getElementById('tabBtnRewards'),
        'tracking': document.getElementById('tabBtnTracking'),
        'area': document.getElementById('tabBtnArea'),
        'profile': document.getElementById('tabBtnProfile')
    };

    const tabContents = {
        'report': document.getElementById('tabContentReport'),
        'rewards': document.getElementById('tabContentRewards'),
        'tracking': document.getElementById('tabContentTracking'),
        'area': document.getElementById('tabContentArea'),
        'profile': document.getElementById('tabContentProfile')
    };

    // Reset styles
    Object.keys(tabButtons).forEach(key => {
        if (tabButtons[key]) {
            tabButtons[key].className = "user-tab-btn flex-1 min-w-[130px] py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2 text-slate-600 hover:text-emerald-700 hover:bg-slate-50 transition";
        }
        if (tabContents[key]) {
            tabContents[key].classList.add('hidden');
        }
    });

    // Activate selected
    if (tabButtons[tabName]) {
        tabButtons[tabName].className = "user-tab-btn flex-1 min-w-[130px] py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2 bg-emerald-600 text-white shadow-sm transition";
    }
    if (tabContents[tabName]) {
        tabContents[tabName].classList.remove('hidden');
    }

    // Refresh data if relevant
    if (tabName === 'tracking') {
        loadUserComplaints();
    } else if (tabName === 'rewards') {
        loadUserRewards();
    } else if (tabName === 'area') {
        loadAreaDetails();
    }
}

// 1. User Profile & Details
async function loadUserProfile() {
    try {
        const res = await fetch('/api/user/profile');
        const data = await res.json();
        if (!data.success) return;

        currentCitizen = data.user;

        // Populate Header
        document.getElementById('userNameHeader').textContent = currentCitizen.name;
        document.getElementById('userUniqueIdHeader').textContent = currentCitizen.unique_id;
        document.getElementById('userAreaHeader').textContent = currentCitizen.area;
        document.getElementById('userAvatarText').textContent = currentCitizen.name.charAt(0).toUpperCase();

        // Populate Profile Tab
        document.getElementById('profUniqueId').textContent = currentCitizen.unique_id;
        document.getElementById('profName').textContent = currentCitizen.name;
        document.getElementById('profAge').textContent = currentCitizen.age || 'N/A';
        document.getElementById('profGender').textContent = currentCitizen.gender || 'Not specified';
        document.getElementById('profArea').textContent = currentCitizen.area;
        document.getElementById('profEmail').textContent = currentCitizen.email;
        document.getElementById('profPhone').textContent = currentCitizen.phone;

        // Preselect report area dropdown
        const reportAreaSelect = document.getElementById('reportArea');
        if (reportAreaSelect && currentCitizen.area) {
            reportAreaSelect.value = currentCitizen.area;
        }

    } catch (e) {
        console.error("Failed to load user profile:", e);
    }
}

function openEditProfileModal() {
    if (!currentCitizen) return;
    document.getElementById('editName').value = currentCitizen.name;
    document.getElementById('editAge').value = currentCitizen.age || '';
    document.getElementById('editGender').value = currentCitizen.gender || 'Male';
    document.getElementById('editArea').value = currentCitizen.area;
    document.getElementById('editPhone').value = currentCitizen.phone;
    document.getElementById('editProfileModal').classList.remove('hidden');
}

function closeEditProfileModal() {
    document.getElementById('editProfileModal').classList.add('hidden');
}

async function submitEditProfile(e) {
    e.preventDefault();
    const name = document.getElementById('editName').value.trim();
    const age = document.getElementById('editAge').value;
    const gender = document.getElementById('editGender').value;
    const area = document.getElementById('editArea').value;
    const phone = document.getElementById('editPhone').value.trim();

    try {
        const res = await fetch('/api/user/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, gender, area, phone })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Profile updated successfully!', 'success');
            closeEditProfileModal();
            await loadUserProfile();
        } else {
            showToast(data.message || 'Update failed.', 'error');
        }
    } catch (err) {
        showToast('Error updating profile.', 'error');
    }
}

// 2. Picture Submission Option & Preview
function previewComplaintImage(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            document.getElementById('imagePreview').src = event.target.result;
            document.getElementById('imagePlaceholder').classList.add('hidden');
            document.getElementById('imagePreviewContainer').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

function clearComplaintImage(e) {
    e.stopPropagation();
    document.getElementById('reportPicture').value = '';
    document.getElementById('imagePreview').src = '';
    document.getElementById('imagePlaceholder').classList.remove('hidden');
    document.getElementById('imagePreviewContainer').classList.add('hidden');
}

// 3. Submit Complaint
async function submitUserComplaint(e) {
    e.preventDefault();
    const area = document.getElementById('reportArea').value;
    const description = document.getElementById('reportDesc').value.trim();
    const pictureFile = document.getElementById('reportPicture').files[0];

    const submitBtn = document.getElementById('submitReportBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Submitting...`;

    const formData = new FormData();
    formData.append('area', area);
    formData.append('description', description);
    if (pictureFile) {
        formData.append('picture', pictureFile);
    }

    try {
        const res = await fetch('/api/user/report', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Complaint filed! Assigned ID: ${data.complaint_id}`, 'success');
            // Reset form
            document.getElementById('reportComplaintForm').reset();
            clearComplaintImage(new Event('clear'));
            // Refresh components
            await loadUserRewards();
            await loadUserComplaints();
            // Switch to Tracking
            setTimeout(() => {
                switchUserTab('tracking');
            }, 600);
        } else {
            showToast(data.message || 'Failed to submit complaint.', 'error');
        }
    } catch (err) {
        showToast('Submission error. Please check your connection.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> <span>Submit Waste Complaint</span>`;
    }
}

// 4. Rewards & Badges (25 = Bronze, 50 = Silver, 100 = Gold)
async function loadUserRewards() {
    try {
        const res = await fetch('/api/user/rewards');
        const data = await res.json();
        if (!data.success) return;

        // Update header & count
        document.getElementById('userReportsCountHeader').textContent = data.total_complaints;
        document.getElementById('rewardTotalFiled').textContent = data.total_complaints;
        document.getElementById('rewardCurrentTierText').textContent = `Current Rank: ${data.current_badge}`;
        document.getElementById('rewardNextTierText').textContent = data.total_complaints >= 100 ? 'Highest Level Achieved!' : `Next Goal: ${data.next_target} Reports`;
        document.getElementById('rewardProgressBar').style.width = `${data.progress_pct}%`;

        // Update Header Badge Icon & Tier
        const badgeIconHeader = document.getElementById('userBadgeIconHeader');
        const badgeTierHeader = document.getElementById('userBadgeTierHeader');
        if (data.total_complaints >= 100) {
            badgeIconHeader.textContent = '🥇';
            badgeTierHeader.textContent = 'Gold';
        } else if (data.total_complaints >= 50) {
            badgeIconHeader.textContent = '🥈';
            badgeTierHeader.textContent = 'Silver';
        } else if (data.total_complaints >= 25) {
            badgeIconHeader.textContent = '🥉';
            badgeTierHeader.textContent = 'Bronze';
        } else {
            badgeIconHeader.textContent = '🌱';
            badgeTierHeader.textContent = 'Cadet';
        }

        // Render Badges
        const container = document.getElementById('badgesContainer');
        container.innerHTML = data.badges.map(b => {
            const glowClass = b.unlocked ? (b.required === 25 ? 'badge-bronze-glow bg-amber-50/70 border-amber-400' : (b.required === 50 ? 'badge-silver-glow bg-slate-50 border-slate-400' : 'badge-gold-glow bg-yellow-50/70 border-yellow-400')) : 'opacity-50 grayscale border-slate-200 bg-slate-50';
            const statusPill = b.unlocked 
                ? `<span class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 flex items-center space-x-1"><i class="fa-solid fa-check"></i> <span>Unlocked</span></span>`
                : `<span class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-200 text-slate-600 flex items-center space-x-1"><i class="fa-solid fa-lock"></i> <span>${b.required} required</span></span>`;

            return `
                <div class="rounded-3xl p-6 border transition duration-300 relative ${glowClass}">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-4xl">${b.icon}</span>
                        ${statusPill}
                    </div>
                    <h4 class="text-lg font-bold font-heading text-slate-800">${b.name}</h4>
                    <p class="text-xs text-slate-500 mt-1">${b.description}</p>
                    <div class="mt-4 pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold">
                        <span class="text-slate-500">Requirement</span>
                        <span class="text-slate-800 font-bold">${b.required} Filed Reports</span>
                    </div>
                </div>
            `;
        }).join('');

    } catch (e) {
        console.error("Failed to load rewards:", e);
    }
}

// 5. Tracking / Completed (48h Countdown & Notify User when Collector clears)
async function loadUserComplaints() {
    try {
        const res = await fetch('/api/user/complaints');
        const data = await res.json();
        if (!data.success) return;

        currentComplaints = data.complaints;

        // Check if any complaint was completed and notified
        const completedAlertDot = document.getElementById('completedAlertDot');
        const taskCompletedBanner = document.getElementById('taskCompletedBanner');
        const taskCompletedBannerText = document.getElementById('taskCompletedBannerText');

        const newlyCompleted = currentComplaints.filter(c => c.status === 'Completed');
        if (newlyCompleted.length > 0) {
            if (completedAlertDot) completedAlertDot.classList.remove('hidden');
            if (taskCompletedBanner) {
                taskCompletedBanner.classList.remove('hidden');
                taskCompletedBannerText.textContent = `Collector cleared complaint ${newlyCompleted[0].complaint_id} in ${newlyCompleted[0].area} with verified photo proof.`;
            }
        }

        // Render Tracking List
        const trackingList = document.getElementById('trackingList');
        if (currentComplaints.length === 0) {
            trackingList.innerHTML = `
                <div class="text-center py-12">
                    <div class="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3 text-2xl">
                        <i class="fa-regular fa-clipboard"></i>
                    </div>
                    <p class="text-sm font-semibold text-slate-700">No complaints filed yet</p>
                    <p class="text-xs text-slate-400 mt-1">Submit your first waste complaint in the Report Box tab.</p>
                </div>
            `;
        } else {
            trackingList.innerHTML = currentComplaints.map(c => renderTrackingCard(c)).join('');
        }

        // Render Complaint History in Profile tab
        const historyList = document.getElementById('complaintHistoryList');
        const historyCountBadge = document.getElementById('historyCountBadge');
        if (historyCountBadge) historyCountBadge.textContent = `${currentComplaints.length} Total`;

        if (historyList) {
            if (currentComplaints.length === 0) {
                historyList.innerHTML = `<p class="text-center text-slate-400 py-10 text-xs">No complaints filed yet.</p>`;
            } else {
                historyList.innerHTML = currentComplaints.map(c => `
                    <div class="p-4 rounded-2xl border border-slate-200 hover:border-slate-300 transition bg-slate-50/50">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-slate-800 font-mono">${c.complaint_id}</span>
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${c.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' : (c.status === 'In Progress' ? 'bg-teal-100 text-teal-800' : 'bg-amber-100 text-amber-800')}">
                                ${c.status}
                            </span>
                        </div>
                        <p class="text-xs text-slate-700 line-clamp-2 mb-2">${c.description}</p>
                        <div class="flex flex-wrap items-center justify-between text-[11px] text-slate-400 border-t border-slate-200/60 pt-2 mt-2">
                            <span><i class="fa-solid fa-location-dot mr-1"></i> ${c.area}</span>
                            <span><i class="fa-regular fa-calendar mr-1"></i> ${c.created_at ? c.created_at.slice(0, 10) : ''}</span>
                        </div>
                    </div>
                `).join('');
            }
        }

    } catch (e) {
        console.error("Failed to load complaints:", e);
    }
}

function renderTrackingCard(c) {
    const isCompleted = c.status === 'Completed';
    const isInProgress = c.status === 'In Progress';

    // 48h Countdown Badge
    let slaBadge = '';
    if (isCompleted) {
        slaBadge = `<span class="px-3 py-1 rounded-xl text-xs font-bold bg-emerald-100 text-emerald-800 flex items-center space-x-1.5"><i class="fa-solid fa-circle-check"></i> <span>Task Completed</span></span>`;
    } else if (c.is_overdue) {
        slaBadge = `<span class="px-3 py-1 rounded-xl text-xs font-bold bg-red-100 text-red-800 flex items-center space-x-1.5"><i class="fa-solid fa-triangle-exclamation"></i> <span>${c.sla_time_left}</span></span>`;
    } else {
        slaBadge = `<span class="px-3 py-1 rounded-xl text-xs font-bold bg-amber-100 text-amber-900 flex items-center space-x-1.5"><i class="fa-solid fa-stopwatch sla-pulse"></i> <span>${c.sla_time_left}</span></span>`;
    }

    // Step progression stages
    const step1Class = "bg-emerald-600 text-white";
    const step2Class = isInProgress || isCompleted ? "bg-emerald-600 text-white" : "bg-slate-200 text-slate-500";
    const step3Class = isCompleted ? "bg-emerald-600 text-white" : "bg-slate-200 text-slate-500";

    return `
        <div class="glass-card rounded-3xl p-6 border ${isCompleted ? 'border-emerald-200 bg-emerald-50/20' : 'border-slate-200'}">
            <!-- Header -->
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="font-mono text-sm font-bold text-slate-900">${c.complaint_id}</span>
                        <span class="text-xs text-slate-400">•</span>
                        <span class="text-xs font-medium text-slate-600"><i class="fa-solid fa-location-dot text-emerald-600 mr-1"></i> ${c.area}</span>
                    </div>
                    <span class="text-[11px] text-slate-400">Filed on: ${c.created_at || 'Recently'}</span>
                </div>
                <div>${slaBadge}</div>
            </div>

            <!-- Complaint Body -->
            <p class="text-xs sm:text-sm text-slate-700 mt-4 leading-relaxed font-medium">
                ${c.description}
            </p>

            <!-- Before and After Photos -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
                <!-- User Uploaded Photo -->
                <div class="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                    <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                        📸 Reported Photo by You
                    </span>
                    ${c.image_path ? `
                        <img src="${c.image_path}" alt="Reported Waste" class="h-44 w-full object-cover rounded-xl shadow-xs border border-slate-200 cursor-pointer" onclick="window.open('${c.image_path}')">
                    ` : `
                        <div class="h-44 rounded-xl border border-dashed border-slate-200 flex items-center justify-center text-xs text-slate-400">
                            No photo submitted
                        </div>
                    `}
                </div>

                <!-- Collector Verified Resolution Photo -->
                <div class="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                    <span class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block mb-2 flex items-center space-x-1">
                        <i class="fa-solid fa-shield-check"></i>
                        <span>✨ Collector Verified Cleaned Photo</span>
                    </span>
                    ${c.resolved_image_path ? `
                        <img src="${c.resolved_image_path}" alt="Resolved Area" class="h-44 w-full object-cover rounded-xl shadow-xs border border-emerald-300 ring-2 ring-emerald-500/20 cursor-pointer" onclick="window.open('${c.resolved_image_path}')">
                        <p class="text-[11px] text-emerald-800 font-medium mt-2 bg-emerald-50 p-2 rounded-lg border border-emerald-200">
                            "${c.resolved_notes || 'Cleaned and disinfected.'}"
                        </p>
                    ` : `
                        <div class="h-44 rounded-xl border border-dashed border-slate-200 flex flex-col items-center justify-center text-xs text-slate-400 p-4 text-center">
                            <i class="fa-solid fa-broom text-xl mb-1 text-slate-300"></i>
                            <span>Collector is scheduled to upload proof of cleanup.</span>
                        </div>
                    `}
                </div>
            </div>

            <!-- 3-Stage Progress Timeline -->
            <div class="mt-6 pt-5 border-t border-slate-100">
                <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-3">48-Hour Resolution Progress</span>
                <div class="grid grid-cols-3 gap-2 text-center text-xs">
                    <div class="flex flex-col items-center space-y-1">
                        <div class="w-7 h-7 rounded-full ${step1Class} flex items-center justify-center font-bold text-xs">1</div>
                        <span class="font-semibold text-slate-700 text-[11px]">Reported</span>
                    </div>
                    <div class="flex flex-col items-center space-y-1">
                        <div class="w-7 h-7 rounded-full ${step2Class} flex items-center justify-center font-bold text-xs">2</div>
                        <span class="font-semibold text-slate-700 text-[11px]">Collector Dispatched</span>
                    </div>
                    <div class="flex flex-col items-center space-y-1">
                        <div class="w-7 h-7 rounded-full ${step3Class} flex items-center justify-center font-bold text-xs">3</div>
                        <span class="font-semibold text-slate-700 text-[11px]">Task Completed</span>
                    </div>
                </div>

                <div class="w-full bg-slate-200 h-2 rounded-full mt-3 overflow-hidden">
                    <div class="h-full bg-emerald-500 transition-all duration-500" style="width: ${isCompleted ? '100%' : (isInProgress ? '60%' : '25%')}"></div>
                </div>
            </div>

            <!-- Assigned Collector Info Footer -->
            <div class="mt-4 pt-3 flex flex-wrap items-center justify-between text-xs text-slate-500">
                <span>
                    <i class="fa-solid fa-truck-pickup text-emerald-600 mr-1"></i>
                    Assigned Collector: <strong class="text-slate-700">${c.assigned_collector_name || 'Municipal Field Team'}</strong>
                </span>
                ${isCompleted ? `
                    <span class="text-emerald-700 font-semibold">
                        <i class="fa-solid fa-calendar-check mr-1"></i> Completed on ${c.resolved_at || 'Recently'}
                    </span>
                ` : `
                    <span class="text-amber-700 font-semibold">
                        <i class="fa-solid fa-hourglass-half mr-1"></i> SLA Window Active
                    </span>
                `}
            </div>
        </div>
    `;
}

// 6. Area Details (Dumping Spots & Assigned Municipal Collectors)
async function loadAreaDetails(selectedArea = null) {
    try {
        let url = '/api/user/area-details';
        if (selectedArea) url += `?area=${encodeURIComponent(selectedArea)}`;

        const res = await fetch(url);
        const data = await res.json();
        if (!data.success) return;

        // Populate Area Selector
        const selector = document.getElementById('areaDetailsSelector');
        if (selector && data.available_areas) {
            selector.innerHTML = data.available_areas.map(a => `
                <option value="${a}" ${a === data.current_area ? 'selected' : ''}>${a}</option>
            `).join('');
        }

        // Render Dumping Spots
        const spotsList = document.getElementById('dumpingSpotsList');
        if (spotsList) {
            if (data.dumping_spots.length === 0) {
                spotsList.innerHTML = `<p class="text-center text-slate-400 py-6 text-xs">No major dumping hotspots logged in this area.</p>`;
            } else {
                spotsList.innerHTML = data.dumping_spots.map(s => {
                    const sevBadge = s.severity === 'Critical' ? 'bg-red-100 text-red-800' : (s.severity === 'High' ? 'bg-orange-100 text-orange-800' : (s.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-emerald-100 text-emerald-800'));
                    return `
                        <div class="p-4 rounded-2xl border border-slate-200 bg-slate-50/50">
                            <div class="flex items-center justify-between mb-1">
                                <h4 class="font-bold text-slate-800 text-xs sm:text-sm">${s.spot_name}</h4>
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${sevBadge}">
                                    ${s.severity} Waste Load
                                </span>
                            </div>
                            <p class="text-xs text-slate-600 mt-1"><i class="fa-solid fa-map-pin text-emerald-600 mr-1"></i> Landmark: ${s.location_landmark || 'General sector'}</p>
                            <p class="text-xs text-slate-500 mt-1 italic">${s.notes || ''}</p>
                        </div>
                    `;
                }).join('');
            }
        }

        // Render Assigned Collectors
        const collectorsList = document.getElementById('areaCollectorsList');
        if (collectorsList) {
            if (data.collectors.length === 0) {
                collectorsList.innerHTML = `<p class="text-center text-slate-400 py-6 text-xs">Municipal team currently rotating in this sector.</p>`;
            } else {
                collectorsList.innerHTML = data.collectors.map(c => `
                    <div class="p-4 rounded-2xl border border-emerald-100 bg-emerald-50/30 flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold text-sm">
                                🚛
                            </div>
                            <div>
                                <h4 class="font-bold text-slate-800 text-sm">${c.name}</h4>
                                <p class="text-xs text-slate-500 font-mono">ID: ${c.unique_id} • ${c.gender}</p>
                            </div>
                        </div>
                        <div class="text-right text-xs">
                            <a href="tel:${c.phone}" class="inline-flex items-center space-x-1 font-semibold text-emerald-700 bg-white px-3 py-1.5 rounded-xl border border-emerald-200 hover:bg-emerald-50 transition shadow-xs">
                                <i class="fa-solid fa-phone text-xs"></i>
                                <span>${c.phone}</span>
                            </a>
                        </div>
                    </div>
                `).join('');
            }
        }

    } catch (e) {
        console.error("Failed to load area details:", e);
    }
}
