const BASE_URL = "http://127.0.0.1:5000";

/* ------------------------------
   APP STATE
------------------------------ */
let currentMode = "ask"; // default mode

/* ------------------------------
   PAGE SWITCH
------------------------------ */
function goToApp() {
  document.getElementById("landingPage").classList.add("hidden");
  document.getElementById("appPage").classList.remove("hidden");
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
    const response = await fetch(`${BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: question,
        mode: currentMode
      })
    });

    const data = await response.json();

    if (data.answer) {
      output.innerHTML = marked.parse(data.answer);
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
