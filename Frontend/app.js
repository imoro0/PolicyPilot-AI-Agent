
const themeToggle = document.getElementById("themeToggle");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const conversationContent = document.getElementById("conversationContent");
const questionCards = document.querySelectorAll(".question-card");

const imageButton = document.getElementById("imageButton");
const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const imageFileName = document.getElementById("imageFileName");
const removeImageButton = document.getElementById("removeImageButton");
const voiceButton = document.getElementById("voiceButton");
const mediaStatus = document.getElementById("mediaStatus");

const THEME_KEY = "policypilot_theme";
const API_URL = "http://127.0.0.1:8000/chat";
const IMAGE_API_URL = "http://127.0.0.1:8000/chat/image";
const AUDIO_API_URL = "http://127.0.0.1:8000/chat/audio";
const TABULAR_API_URL = "http://127.0.0.1:8000/chat/file";

const tabularFile = document.getElementById("tabularFile");
const fileUploadBtn = document.getElementById("fileUploadBtn");
const selectedFileName = document.getElementById("selectedFileName");

let selectedImage = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let isBusy = false;


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

applyTheme(localStorage.getItem(THEME_KEY) || "light");

themeToggle.addEventListener("click", () => {
    const theme = document.body.classList.contains("dark-theme")
        ? "light"
        : "dark";

    localStorage.setItem(THEME_KEY, theme);
    applyTheme(theme);
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

function clearEmptyState() {
    const emptyState = conversationContent.querySelector(".empty-state");

    if (emptyState) {
        conversationContent.innerHTML = "";
    }
}

function addMessage(role, content) {
    clearEmptyState();

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

function setStatus(message = "") {
    mediaStatus.textContent = message;
    mediaStatus.hidden = !message;
}

function setBusy(busy) {
    isBusy = busy;
    sendButton.disabled = busy;
    imageButton.disabled = busy;
    voiceButton.disabled = busy;

    sendButton.innerHTML = busy
        ? "<span>…</span> Thinking"
        : "<span>➤</span> Send";
}


// ---------- Existing text chat ----------

async function getChatResponse(question) {
    const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            question,
            session_id: "default"
        })
    });

    if (!response.ok) {
        throw new Error(`Chat request failed: ${response.status}`);
    }

    const data = await response.json();
    return data.answer;
}

async function sendQuestion(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || isBusy) return;

    addMessage("user", cleanQuestion);
    questionInput.value = "";
    setBusy(true);
    setStatus("");

    try {
        const answer = await getChatResponse(cleanQuestion);
        addMessage("assistant", answer);
    } catch (error) {
        console.error("Chat API error:", error);
        addMessage(
            "assistant",
            "I couldn't connect to PolicyPilot. Please check that the backend is running."
        );
    } finally {
        setBusy(false);
        questionInput.focus();
    }
}


// ---------- Image upload ----------

imageButton.addEventListener("click", () => {
    if (!isBusy) imageInput.click();
});

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];

    if (!file) return;

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif"
    ];

    if (!allowedTypes.includes(file.type)) {
        setStatus("Please select a JPG, PNG, WEBP, or GIF image.");
        imageInput.value = "";
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        setStatus("Please select an image smaller than 10 MB.");
        imageInput.value = "";
        return;
    }

    selectedImage = file;
    imageFileName.textContent = `Selected: ${file.name}`;
    imagePreview.hidden = false;
    setStatus("Image selected. Type a question or send the image.");
});

removeImageButton.addEventListener("click", () => {
    selectedImage = null;
    imageInput.value = "";
    imagePreview.hidden = true;
    imageFileName.textContent = "";
    setStatus("");
});

async function sendImageQuestion() {
    if (!selectedImage || isBusy) return;

    const question = questionInput.value.trim()
        || "Please explain the text in this image.";

    const imageToSend = selectedImage;

    addMessage(
        "user",
        `Image: ${imageToSend.name}\nQuestion: ${question}`
    );

    questionInput.value = "";
    selectedImage = null;
    imageInput.value = "";
    imagePreview.hidden = true;
    imageFileName.textContent = "";

    setBusy(true);
    setStatus("Processing image...");

    try {
        const formData = new FormData();
        formData.append("image", imageToSend);
        formData.append("question", question);
        formData.append("session_id", "default");

        const response = await fetch(IMAGE_API_URL, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Image request failed: ${response.status}`);
        }

        const data = await response.json();
        addMessage("assistant", data.answer);
    } catch (error) {
        console.error("Image API error:", error);
        addMessage("assistant", `Image processing failed: ${error.message}`);
    } finally {
        setBusy(false);
        setStatus("");
        questionInput.focus();
    }
}


async function sendTabularFile() {
    if (!tabularFile.files.length || isBusy) return;

    const file = tabularFile.files[0];
    const question = questionInput.value.trim();

    if (!question) {
        setStatus("Please enter a question about your uploaded file.");
        questionInput.focus();
        return;
    }

    if (file.size > 20 * 1024 * 1024) {
        setStatus("Please select a file smaller than 20 MB.");
        return;
    }

    addMessage(
        "user",
        `File: ${file.name}\nQuestion: ${question}`
    );

    questionInput.value = "";

    setBusy(true);
    setStatus("Analyzing your file...");

    try {
        const formData = new FormData();

        formData.append("file", file);
        formData.append("question", question);

        const response = await fetch(TABULAR_API_URL, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || `File request failed: ${response.status}`
            );
        }

        addMessage("assistant", data.answer);

        

    } catch (error) {
        console.error("File API error:", error);

        addMessage(
            "assistant",
            `File processing failed: ${error.message}`
        );

    } finally {
        setBusy(false);
        setStatus("");
        questionInput.focus();
    }
}


// ---------- Microphone recording ----------

voiceButton.addEventListener("click", async () => {
    if (isBusy) return;

    if (isRecording) {
        mediaRecorder.stop();
        return;
    }

    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        setStatus("Your browser does not support microphone recording.");
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        audioChunks = [];

        const preferredType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
            ? "audio/webm;codecs=opus"
            : "audio/webm";

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: preferredType
        });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, {
                type: mediaRecorder.mimeType || "audio/webm"
            });

            stream.getTracks().forEach(track => track.stop());

            isRecording = false;
            voiceButton.textContent = "🎙";
            voiceButton.title = "Record voice question";
            voiceButton.setAttribute("aria-label", "Record voice question");

            if (audioBlob.size > 0) {
                await sendVoiceQuestion(audioBlob);
            } else {
                setStatus("No audio was recorded. Please try again.");
            }
        };

        mediaRecorder.start();
        isRecording = true;
        voiceButton.textContent = "⏹";
        voiceButton.title = "Stop recording";
        voiceButton.setAttribute("aria-label", "Stop recording");
        setStatus("Recording... Press the microphone button again to stop.");
    } catch (error) {
        console.error("Microphone error:", error);
        setStatus("Microphone access was denied or is unavailable.");
    }
});

async function sendVoiceQuestion(audioBlob) {
    setBusy(true);
    setStatus("Transcribing your voice...");

    try {
        const formData = new FormData();
        formData.append("audio", audioBlob, "voice.webm");
        formData.append("session_id", "default");

        const response = await fetch(AUDIO_API_URL, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Voice request failed: ${response.status}`);
        }

        const data = await response.json();

        if (data.transcript) {
            addMessage("user", `Voice transcription: ${data.transcript}`);
        }

        addMessage("assistant", data.answer);
    } catch (error) {
        console.error("Voice API error:", error);
        addMessage(
            "assistant",
            `Voice processing failed: ${error.message}. The audio endpoint must be added to the backend.`
        );
    } finally {
        setBusy(false);
        setStatus("");
    }
}


// ---------- Quick questions ----------

questionCards.forEach((card) => {
    card.addEventListener("click", () => {
        const question = card.dataset.question;

        if (question) sendQuestion(question);
    });
});


// ---------- Input events ----------


sendButton.addEventListener("click", () => {
    if (tabularFile.files.length > 0) {
        sendTabularFile();
    } else if (selectedImage) {
        sendImageQuestion();
    } else {
        sendQuestion(questionInput.value);
    }
});


questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();

        if (tabularFile.files.length > 0) {
            sendTabularFile();
        } else if (selectedImage) {
            sendImageQuestion();
        } else {
            sendQuestion(questionInput.value);
        }
    }
});



fileUploadBtn.addEventListener("click", () => {
    tabularFile.click();
});

tabularFile.addEventListener("change", () => {
    const file = tabularFile.files[0];

    selectedFileName.textContent = file
        ? file.name
        : "No file selected";
});

// Initial state
showEmptyState();
