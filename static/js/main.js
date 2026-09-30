// EcoClean Global Frontend Utilities & Auth Management

// Toast Notification Helper
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-emerald-600 text-white' : (type === 'error' ? 'bg-red-600 text-white' : 'bg-slate-800 text-white');
    const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info');

    toast.className = `${bgClass} px-4 py-3 rounded-2xl shadow-xl flex items-center space-x-3 text-xs sm:text-sm font-medium pointer-events-auto transform transition-all duration-300 translate-y-2 opacity-0`;
    toast.innerHTML = `
        <i class="fa-solid ${icon} text-base"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    // Auto remove
    setTimeout(() => {
        toast.classList.add('translate-y-2', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

// Global Auth State Loader
async function checkAuthStatus() {
    try {
        const res = await fetch('/api/me');
        const data = await res.json();

        const unauthNav = document.getElementById('unauthNav');
        const authNav = document.getElementById('authNav');
        const navUserName = document.getElementById('navUserName');
        const navUserBadge = document.getElementById('navUserBadge');
        const navAvatar = document.getElementById('navAvatar');

        if (data.authenticated) {
            if (unauthNav) unauthNav.classList.add('hidden');
            if (authNav) authNav.classList.remove('hidden');
            if (authNav) authNav.classList.add('flex');

            if (navUserName) navUserName.textContent = data.data.name || 'User';
            if (navUserBadge) navUserBadge.textContent = data.role === 'user' ? 'Citizen' : (data.role === 'collector' ? 'Collector' : 'Admin');
            if (navAvatar) navAvatar.textContent = (data.data.name || 'U').charAt(0).toUpperCase();

            // Load notifications for citizen user
            if (data.role === 'user') {
                loadNotifications();
            }
        } else {
            if (unauthNav) unauthNav.classList.remove('hidden');
            if (unauthNav) unauthNav.classList.add('flex');
            if (authNav) authNav.classList.add('hidden');
        }
    } catch (e) {
        console.error("Auth check error:", e);
    }
}

// User Notifications (especially "Task Completed" notification)
async function loadNotifications() {
    try {
        const res = await fetch('/api/user/notifications');
        const data = await res.json();
        if (!data.success) return;

        const notifBadge = document.getElementById('notifBadge');
        const notifList = document.getElementById('notifList');

        if (data.unread_count > 0) {
            if (notifBadge) notifBadge.classList.remove('hidden');
        } else {
            if (notifBadge) notifBadge.classList.add('hidden');
        }

        if (notifList) {
            if (data.notifications.length === 0) {
                notifList.innerHTML = `<p class="text-center text-slate-400 py-6 text-xs">No notifications yet.</p>`;
            } else {
                notifList.innerHTML = data.notifications.map(n => `
                    <div class="p-3 hover:bg-slate-50 transition ${n.is_read ? 'opacity-70' : 'bg-emerald-50/40'}">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-bold text-slate-800 text-xs">${n.title}</span>
                            <span class="text-[10px] text-slate-400">${n.created_at ? n.created_at.slice(11, 16) : ''}</span>
                        </div>
                        <p class="text-xs text-slate-600 leading-relaxed">${n.message}</p>
                    </div>
                `).join('');
            }
        }
    } catch (e) {
        console.error("Failed to load notifications:", e);
    }
}

// Notification Dropdown Toggle & Mark Read
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();

    const notifBtn = document.getElementById('notifBtn');
    const notifMenu = document.getElementById('notifMenu');
    const markReadBtn = document.getElementById('markReadBtn');

    if (notifBtn && notifMenu) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notifMenu.classList.toggle('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!notifMenu.contains(e.target) && !notifBtn.contains(e.target)) {
                notifMenu.classList.add('hidden');
            }
        });
    }

    if (markReadBtn) {
        markReadBtn.addEventListener('click', async () => {
            await fetch('/api/user/notifications/mark-read', { method: 'POST' });
            loadNotifications();
        });
    }
});

// Authentication Handlers
async function handleUserLogin(e) {
    e.preventDefault();
    const identifier = document.getElementById('userLoginId').value.trim();
    const password = document.getElementById('userLoginPass').value;

    try {
        const res = await fetch('/api/login/user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });
        const data = await res.json();
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            showToast(data.message || 'Invalid citizen credentials.', 'error');
        }
    } catch (err) {
        showToast('Connection error. Please try again.', 'error');
    }
}

async function handleUserRegister(e) {
    e.preventDefault();
    const name = document.getElementById('regName').value.trim();
    const age = document.getElementById('regAge').value;
    const gender = document.getElementById('regGender').value;
    const area = document.getElementById('regArea').value;
    const email = document.getElementById('regEmail').value.trim();
    const phone = document.getElementById('regPhone').value.trim();
    const password = document.getElementById('regPassword').value;

    try {
        const res = await fetch('/api/register/user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, gender, area, email, phone, password })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 800);
        } else {
            showToast(data.message || 'Registration failed.', 'error');
        }
    } catch (err) {
        showToast('Registration error. Please verify your details.', 'error');
    }
}

async function handleCollectorLogin(e) {
    e.preventDefault();
    const identifier = document.getElementById('colLoginId').value.trim();
    const password = document.getElementById('colLoginPass').value;

    try {
        const res = await fetch('/api/login/collector', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });
        const data = await res.json();
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            showToast(data.message || 'Invalid collector credentials.', 'error');
        }
    } catch (err) {
        showToast('Connection error.', 'error');
    }
}

async function handleAdminLogin(e) {
    e.preventDefault();
    const identifier = document.getElementById('adminLoginId').value.trim();
    const password = document.getElementById('adminLoginPass').value;

    try {
        const res = await fetch('/api/login/admin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });
        const data = await res.json();
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            showToast(data.message || 'Invalid admin credentials.', 'error');
        }
    } catch (err) {
        showToast('Connection error.', 'error');
    }
}

// Quick demo login shortcut
async function quickLogin(role, identifier, password) {
    let endpoint = `/api/login/${role}`;
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });
        const data = await res.json();
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Failed to execute demo login.', 'error');
    }
}
