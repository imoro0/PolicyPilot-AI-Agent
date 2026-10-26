
const themeToggle = document.getElementById("themeToggle");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const conversationContent = document.getElementById("conversationContent");
const questionCards = document.querySelectorAll(".question-card");

const THEME_KEY = "policypilot_theme";


// ---------- Theme ----------

function applyTheme(theme) {
    const isDark = theme === "dark";

    document.body.classList.toggle("dark-theme", isDark);

    themeToggle.setAttribute(
        "aria-label",
        isDark ? "Switch to light theme" : "Switch to dark theme"
    );

    themeToggle.setAttribute("aria-pressed", String(isDark));
}

const savedTheme = localStorage.getItem(THEME_KEY) || "light";
applyTheme(savedTheme);

themeToggle.addEventListener("click", () => {
    const isDark = document.body.classList.contains("dark-theme");
    const newTheme = isDark ? "light" : "dark";

    localStorage.setItem(THEME_KEY, newTheme);
    applyTheme(newTheme);
});


// ---------- Chat UI ----------

function showEmptyState() {
    conversationContent.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">
                <span>▰</span>
                <span>▰</span>
            </div>

            <h3>Start a conversation</h3>

            <p>
                Choose a quick question above or type your own question
                in the input box below.
            </p>
        </div>
    `;
}


function addMessage(role, content) {
    const message = document.createElement("div");
    message.className = `chat-message ${role}`;

    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = role === "user" ? "You" : "PolicyPilot";

    const text = document.createElement("div");
    text.className = "message-text";
    text.textContent = content;

    message.append(label, text);
    conversationContent.appendChild(message);

    message.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}


// ---------- Demo Response ----------

// Phase 11 mein is demo function ko FastAPI request se replace karenge.

const API_URL = "http://127.0.0.1:8000/chat";

async function getDemoResponse(question) {
    const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question,
            session_id: "default"
        })
    });

    if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    return data.answer;
}


function sendQuestion(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || sendButton.disabled) {
        return;
    }

    // Remove the welcome state on the first message.
    const emptyState = conversationContent.querySelector(".empty-state");

    if (emptyState) {
        conversationContent.innerHTML = "";
    }

    addMessage("user", cleanQuestion);

    questionInput.value = "";
    sendButton.disabled = true;
    sendButton.innerHTML = "<span>…</span> Thinking";

    // Temporary demo response; no backend request is made here.
   
(async () => {
    try {
        const answer = await getDemoResponse(cleanQuestion);
        addMessage("assistant", answer);
    } catch (error) {
        console.error("Chat API error:", error);

        addMessage(
            "assistant",
            "I couldn't connect to PolicyPilot right now. Please make sure the backend is running and try again."
        );
    } finally {
        sendButton.disabled = false;
        sendButton.innerHTML = "<span>➤</span> Send";
        questionInput.focus();
    }
})();

}


// ---------- Quick Questions ----------

questionCards.forEach((card) => {
    card.addEventListener("click", () => {
        const question = card.dataset.question;

        if (question) {
            sendQuestion(question);
        }
    });
});


// ---------- Custom Question Input ----------

sendButton.addEventListener("click", () => {
    sendQuestion(questionInput.value);
});

questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendQuestion(questionInput.value);
    }
});


// Initial state
showEmptyState();
