const BASE_URL = "http://127.0.0.1:5000";

/* ------------------------------
   APP STATE
------------------------------ */
let currentMode = "ask";
let currentSessionId = null;
let authToken = localStorage.getItem('wayfinder_token');
let currentUser = JSON.parse(localStorage.getItem('wayfinder_user') || 'null');

/* ------------------------------
   INITIALIZATION
------------------------------ */
window.onload = function() {
  if (authToken && currentUser) {
    showApp();
  } else {
    showAuth();
  }
};

/* ------------------------------
   PAGE NAVIGATION
------------------------------ */
function showAuth() {
  document.getElementById("authPage").classList.remove("hidden");
  document.getElementById("landingPage").classList.add("hidden");
  document.getElementById("appPage").classList.add("hidden");
}

function showLanding() {
  document.getElementById("authPage").classList.add("hidden");
  document.getElementById("landingPage").classList.remove("hidden");
  document.getElementById("appPage").classList.add("hidden");
}

function showApp() {
  document.getElementById("authPage").classList.add("hidden");
  document.getElementById("landingPage").classList.add("hidden");
  document.getElementById("appPage").classList.remove("hidden");
  
  if (currentUser) {
    document.getElementById("userInfo").textContent = `Welcome, ${currentUser.name}`;
  }
}

function goToApp() {
  showApp();
}

/* ------------------------------
   AUTHENTICATION FUNCTIONS
------------------------------ */
function showLogin() {
  document.getElementById("loginForm").classList.remove("hidden");
  document.getElementById("registerForm").classList.add("hidden");
}

function showRegister() {
  document.getElementById("loginForm").classList.add("hidden");
  document.getElementById("registerForm").classList.remove("hidden");
}

async function login() {
  const emailField = document.getElementById("loginEmail");
  const passwordField = document.getElementById("loginPassword");
  
  if (!emailField || !passwordField) {
    alert("Form fields not found");
    return;
  }
  
  const email = emailField.value.trim();
  const password = passwordField.value.trim();
  
  console.log('Login attempt:', { email: email, passwordLength: password.length });
  
  if (!email || !password) {
    alert("Please fill all fields");
    return;
  }
  
  try {
    console.log('Sending login request to:', `${BASE_URL}/auth/login`);
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    
    console.log('Response status:', response.status);
    const data = await response.json();
    console.log('Response data:', data);
    
    if (data.success) {
      authToken = data.token;
      currentUser = data.user;
      localStorage.setItem('wayfinder_token', authToken);
      localStorage.setItem('wayfinder_user', JSON.stringify(currentUser));
      console.log('Login successful, redirecting to landing');
      
      // Clear form fields
      emailField.value = '';
      passwordField.value = '';
      
      showLanding();
    } else {
      console.log('Login failed:', data.error);
      alert(data.error || "Login failed");
    }
  } catch (err) {
    console.error('Login error:', err);
    alert("Login failed - Check console for details");
  }
}

async function register() {
  const name = document.getElementById("registerName").value;
  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;
  
  if (!name || !email || !password) {
    alert("Please fill all fields");
    return;
  }
  
  try {
    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });
    
    const data = await response.json();
    
    if (data.success) {
      authToken = data.token;
      currentUser = data.user;
      localStorage.setItem('wayfinder_token', authToken);
      localStorage.setItem('wayfinder_user', JSON.stringify(currentUser));
      showLanding();
    } else {
      alert(data.error || "Registration failed");
    }
  } catch (err) {
    alert("Registration failed");
  }
}

function logout() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('wayfinder_token');
  localStorage.removeItem('wayfinder_user');
  showAuth();
}
/* ------------------------------
   MODE HANDLER (FIXED)
------------------------------ */
function setMode(mode) {
  currentMode = mode;

  const output = document.getElementById("output");
  output.innerHTML = `<p class="text-chat-secondary text-center">
    Mode selected: <b>${mode.replace("_", " ")}</b><br/>
    Ask your question and click "Ask AI"
  </p>`;
}

/* ------------------------------
   ASK AI (ALL FEATURES USE THIS)
------------------------------ */
async function askQuestion() {
  const questionInput = document.getElementById("question");
  const output = document.getElementById("output");

  const question = questionInput.value.trim();
  if (!question) {
    alert("Please enter a question");
    return;
  }

  output.innerHTML = `<p class="text-chat-secondary text-center">Thinking...</p>`;

  try {
    const headers = { "Content-Type": "application/json" };
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(`${BASE_URL}/ask`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        question: question,
        mode: currentMode,
        session_id: currentSessionId
      })
    });

    const data = await response.json();

    if (data.answer) {
      output.innerHTML = marked.parse(data.answer);
      questionInput.value = "";
      currentSessionId = data.session_id; // Store session ID
    } else {
      output.innerHTML = `<p class="text-red-400">No response from AI</p>`;
    }

  } catch (err) {
    output.innerHTML = `<p class="text-red-400">Server error</p>`;
  }
}

/* ------------------------------
   RESUME ANALYZER (UNCHANGED)
------------------------------ */
async function analyzeResume() {
  const resumeInput = document.getElementById("resume");
  const output = document.getElementById("output");

  if (!resumeInput.files.length) {
    alert("Please upload a PDF resume");
    return;
  }

  output.innerHTML = `<p class="text-chat-secondary text-center">Analyzing resume...</p>`;

  const formData = new FormData();
  formData.append("resume", resumeInput.files[0]);

  try {
    const response = await fetch(`${BASE_URL}/analyze`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.career_analysis) {
      output.innerHTML = marked.parse(data.career_analysis);
    } else {
      output.innerHTML = `<p class="text-red-400">No analysis returned</p>`;
    }

  } catch (err) {
    output.innerHTML = `<p class="text-red-400">Server error</p>`;
  }
}

/* ------------------------------
   CHAT HISTORY FUNCTIONS
------------------------------ */
function toggleHistory() {
  const sidebar = document.getElementById("historySidebar");
  const overlay = document.getElementById("historyOverlay");
  
  if (sidebar.classList.contains("hidden")) {
    // Show sidebar
    sidebar.classList.remove("hidden");
    overlay.classList.remove("hidden");
    setTimeout(() => {
      sidebar.classList.remove("translate-x-full");
    }, 10);
    loadSessions();
  } else {
    // Hide sidebar
    sidebar.classList.add("translate-x-full");
    overlay.classList.add("hidden");
    setTimeout(() => {
      sidebar.classList.add("hidden");
    }, 300);
  }
}

async function loadSessions() {
  if (!currentUser) return;
  
  console.log('Loading sessions for user:', currentUser.id);
  try {
    const headers = {};
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(`${BASE_URL}/chat/sessions/${currentUser.id}`, {
      headers: headers
    });
    const data = await response.json();
    console.log('Sessions response:', data);
    
    const sessionsList = document.getElementById("sessionsList");
    
    if (data.sessions && data.sessions.length > 0) {
      sessionsList.innerHTML = data.sessions.map(session => `
        <div class="p-3 bg-chat-bg/50 rounded-lg border border-chat-border hover:border-white/20 cursor-pointer transition" 
             onclick="loadSession('${session._id}')">
          <p class="text-sm text-white truncate">${session.title}</p>
          <p class="text-xs text-chat-secondary mt-1">${new Date(session.created_at).toLocaleDateString()}</p>
          <button onclick="event.stopPropagation(); deleteSession('${session._id}')" 
                  class="text-xs text-red-400 hover:text-red-300 mt-1">Delete</button>
        </div>
      `).join("");
    } else {
      sessionsList.innerHTML = `<p class="text-chat-secondary text-center text-sm mt-8">No conversations yet</p>`;
    }
  } catch (err) {
    console.error("Failed to load sessions:", err);
    document.getElementById("sessionsList").innerHTML = `<p class="text-red-400 text-center text-sm mt-8">Error loading sessions</p>`;
  }
}

async function loadSession(sessionId) {
  // Handle legacy migration
  if (sessionId === "legacy") {
    if (confirm("Migrate your old chats to the new format?")) {
      try {
        const response = await fetch(`${BASE_URL}/migrate/${userId}`, { method: "POST" });
        const data = await response.json();
        alert(data.message);
        loadSessions(); // Refresh list
      } catch (err) {
        alert("Migration failed");
      }
    }
    return;
  }
  
  try {
    const response = await fetch(`${BASE_URL}/chat/session/${sessionId}/messages`);
    const data = await response.json();
    
    if (data.messages && data.messages.length > 0) {
      const lastMessage = data.messages[data.messages.length - 1];
      document.getElementById("question").value = lastMessage.question;
      document.getElementById("output").innerHTML = marked.parse(lastMessage.answer);
      currentSessionId = sessionId;
    }
    
    toggleHistory(); // Close sidebar
  } catch (err) {
    console.error("Failed to load session:", err);
  }
}

async function deleteSession(sessionId) {
  if (confirm("Delete this conversation?")) {
    try {
      await fetch(`${BASE_URL}/chat/session/${sessionId}`, { method: "DELETE" });
      loadSessions(); // Refresh list
    } catch (err) {
      alert("Failed to delete session");
    }
  }
}