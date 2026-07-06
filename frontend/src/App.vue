<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from './stores/auth';
import api from './api';

const auth = useAuthStore();
const isAppReady = ref(false);

const username = ref('');
const password = ref('');
const loginError = ref('');
const secretData = ref(null);

const activeTab = ref('home');

onMounted(async () => {
  try {
    await auth.attemptSilentRefresh();
  } catch (err) {
    console.log('No existing session found.');
  } finally {
    isAppReady.value = true;
  }
});

const handleLogin = async () => {
  try {
    loginError.value = '';
    await auth.login(username.value, password.value);
    username.value = '';
    password.value = '';
    activeTab.value = 'home';
  } catch (err) {
    loginError.value = 'Login failed. Please check your credentials.';
  }
};

const handleLogout = async () => {
  await auth.logout();
  secretData.value = null;
};

const fetchProtectedData = async () => {
  try {
    const response = await api.get('protected/');
    secretData.value = response.data;
  } catch (err) {
    console.error('Error fetching data:', err);
  }
};
</script>

<template>
  <div v-if="!isAppReady" class="loading">
    Restoring session...
  </div>

  <div v-else-if="!auth.isAuthenticated" class="login-container">
    <section class="login-card">
      <h2>System Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required />
        </div>
        <p v-if="loginError" class="error-text">{{ loginError }}</p>
        <button type="submit" class="btn-primary">Log In</button>
      </form>
    </section>
  </div>

  <div v-else class="dashboard-grid" :class="auth.isAdmin ? 'admin-theme' : 'user-theme'">

    <header class="db-header">
      <div class="logo">
        <span v-if="auth.isAdmin">AdminPortal</span>
        <span v-else>UserPortal</span>
      </div>
      <div class="user-info">
        <span class="badge">{{ auth.isAdmin ? 'Administrator' : 'Standard User' }}</span>
        <button @click="handleLogout" class="btn-logout">Log Out</button>
      </div>
    </header>

    <aside class="db-sidebar">
      <nav>
        <ul>
          <li>
            <button :class="{ active: activeTab === 'home' }" @click="activeTab = 'home'">
              Overview
            </button>
          </li>
          <li>
            <button :class="{ active: activeTab === 'data' }" @click="activeTab = 'data'">
              Data Interface
            </button>
          </li>
          <li v-if="auth.isAdmin">
            <button :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
              System Settings
            </button>
          </li>
        </ul>
      </nav>
    </aside>

    <main class="db-main">
      <section v-if="activeTab === 'home'">
        <h2>Welcome back!</h2>
        <p>This is the main overview of your dashboard. Use the left navigation to switch between sections.</p>
        <div class="info-box">
          <strong>System status:</strong> Operational (API connected via HttpOnly cookie)
        </div>
      </section>

      <section v-if="activeTab === 'data'">
        <h2>Secure Data Request</h2>
        <p>Click the button to load verified data live from the protected Django backend.</p>
        <button @click="fetchProtectedData" class="btn-action">
          {{ auth.isAdmin ? 'Request Admin Log Data' : 'Load My Profile Data' }}
        </button>

        <div v-if="secretData" class="data-preview">
          <h3>Server response:</h3>
          <pre>{{ JSON.stringify(secretData, null, 2) }}</pre>
        </div>
      </section>

      <section v-if="activeTab === 'settings' && auth.isAdmin">
        <h2>System Settings</h2>
        <p>This section is visible exclusively to administrators. Administrative tools could be placed here.</p>
        <ul class="settings-list">
          <li>Option 1</li>
          <li>Option 2</li>
          <li>Option 3</li>
        </ul>
      </section>
    </main>

    <footer class="db-footer">
      <p>&copy; 2026 Fullstack Template Engine. All rights reserved.</p>
    </footer>

  </div>
</template>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: system-ui, -apple-system, sans-serif;
  background-color: #E6F2DD;
  color: #2D3E3A;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.1rem;
  color: #659287;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #E6F2DD;
}
.login-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(101, 146, 135, 0.15);
  width: 100%;
  max-width: 400px;
  border: 1px solid #B1D3B9;
}
.login-card h2 {
  margin-top: 0;
  margin-bottom: 25px;
  font-size: 1.3rem;
  text-align: center;
  color: #659287;
}
.form-group { margin-bottom: 18px; }
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  color: #659287;
}
.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #B1D3B9;
  border-radius: 4px;
  box-sizing: border-box;
  background-color: #fcfdfb;
  color: #2D3E3A; /* dark pastel contrast tone for readability */
  font-size: 1fr;
  outline: none;
}
.form-group input:focus {
  border-color: #88BDA4;
  background-color: #ffffff; /* slight brightening on focus */
}
.btn-primary {
  width: 100%;
  padding: 11px;
  background-color: #659287;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-primary:hover {
  background-color: #537a70;
}
.error-text { color: #bf5a5a; font-size: 0.85rem; margin-bottom: 10px; }

/* --- DASHBOARD GRID LAYOUT --- */
.dashboard-grid {
  display: grid;
  grid-template-rows: 60px 1fr 40px;
  grid-template-columns: 240px 1fr;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  height: 100vh;
}

.db-header { grid-area: header; }
.db-sidebar { grid-area: sidebar; }
.db-main { grid-area: main; }
.db-footer { grid-area: footer; }

/* --- HEADER --- */
.db-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #659287; /* primary color */
  color: white;
  z-index: 10;
}
.db-header .logo { font-size: 1.1rem; font-weight: bold; letter-spacing: 0.5px; }
.db-header .user-info { display: flex; align-items: center; gap: 15px; }
.db-header .badge {
  background-color: #88BDA4;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}
.btn-logout {
  background-color: #E6F2DD;
  color: #659287;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.2s;
}
.btn-logout:hover { background-color: #B1D3B9; }

/* --- SIDEBAR --- */
.db-sidebar {
  background-color: #88BDA4; /* secondary color */
  padding: 20px 0;
}
.db-sidebar ul { list-style: none; padding: 0; margin: 0; }
.db-sidebar li { margin-bottom: 4px; }
.db-sidebar button {
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  color: #E6F2DD;
  padding: 12px 20px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.db-sidebar button:hover {
  background-color: rgba(230, 242, 221, 0.15);
  color: white;
}
.db-sidebar button.active {
  background-color: #E6F2DD;
  color: #659287;
  font-weight: bold;
}

/* --- MAIN CONTENT AREA --- */
.db-main {
  padding: 35px;
  overflow-y: auto;
  background-color: #fbfdfa; /* very light pastel off-white */
}
.db-main h2 { margin-top: 0; color: #659287; font-size: 1.4rem; }
.db-main p { color: #536b65; line-height: 1.6; font-size: 0.95rem; }
.info-box {
  background-color: #E6F2DD;
  padding: 15px;
  border-radius: 6px;
  margin-top: 25px;
  border-left: 4px solid #B1D3B9;
  font-size: 0.9rem;
  color: #536b65;
}
.btn-action {
  background-color: #659287;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 15px;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}
.btn-action:hover { background-color: #537a70; }

/* --- SETTINGS LIST (button-style entries) --- */
.settings-list {
  list-style: none;
  padding: 0;
  margin: 20px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.settings-list li {
  background-color: #88BDA4;
  color: #E6F2DD;
  padding: 10px 16px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.9rem;
  width: 160px;
  text-align: center;
  box-sizing: border-box;
}

/* --- DATA PREVIEW --- */
.data-preview { margin-top: 25px; background: #ffffff; border: 1px solid #B1D3B9; padding: 18px; border-radius: 6px; }
.data-preview h3 { margin-top: 0; font-size: 0.95rem; color: #659287; }
.data-preview pre { margin: 0; background-color: #E6F2DD; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 0.85rem; overflow-x: auto; color: #4a5e59; }

/* --- FOOTER --- */
.db-footer {
  background-color: #E6F2DD;
  border-top: 1px solid #B1D3B9;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.8rem;
  color: #659287;
}

/* --- ROLE-BASED THEMING --- */
/* Admin mode uses a darker mint accent tone */
.admin-theme .db-sidebar button.active {
  background-color: #E6F2DD;
  color: #659287;
  box-shadow: inset 4px 0 0 #659287;
}

/* User mode uses a lighter pastel green accent tone */
.user-theme .db-sidebar button.active {
  background-color: #E6F2DD;
  color: #88BDA4;
  box-shadow: inset 4px 0 0 #B1D3B9;
}

/* --- RESPONSIVENESS --- */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: 60px auto 1fr 40px;
    grid-template-areas:
      "header"
      "sidebar"
      "main"
      "footer";
  }
  .db-sidebar { padding: 8px; }
  .db-sidebar ul { display: flex; justify-content: space-around; }
  .db-sidebar li { margin-bottom: 0; }
  .db-sidebar button { padding: 10px 14px; font-size: 0.85rem; text-align: center; }
  .admin-theme .db-sidebar button.active, .user-theme .db-sidebar button.active { box-shadow: none; }
}
</style>