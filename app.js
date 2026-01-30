// import { upload } from 'https://esm.sh/@vercel/blob@0.22.1/client';

console.log("App.js loaded, initializing...");

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const urlInput = document.getElementById('url-input');
const processBtn = document.getElementById('process-btn');
const statusText = document.getElementById('status-text');
const progressBar = document.getElementById('loading-bar');
const progress = document.getElementById('progress');
const galleryGrid = document.getElementById('gallery-grid');
const countBadge = document.getElementById('count-badge');

let selectedFile = null;
let mode = 'upload'; // 'upload' or 'url'

// --- Tabs ---
window.switchTab = function (newMode) {
    mode = newMode;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

    if (mode === 'upload') {
        document.querySelector('.tab:nth-child(1)').classList.add('active');
        document.getElementById('upload-panel').style.display = 'block';
        document.getElementById('url-panel').style.display = 'none';
    } else {
        document.querySelector('.tab:nth-child(2)').classList.add('active');
        document.getElementById('upload-panel').style.display = 'none';
        document.getElementById('url-panel').style.display = 'flex';
    }
}

// --- Drag & Drop ---
dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    selectedFile = file;
    dropzone.innerHTML = `
        <div style="font-size: 2rem">📄</div>
        <p style="color: white; font-weight: 600">${file.name}</p>
        <p style="font-size: 0.8rem">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
    `;
    statusText.innerText = "File selected. Ready to process.";
}

// --- Processing ---
window.startProcessing = async function () {
    processBtn.disabled = true;
    progressBar.style.display = 'block';
    progress.style.width = '1%';
    statusText.innerText = "Initializing...";
    galleryGrid.innerHTML = '';

    try {
        let payload = {};

        if (mode === 'upload') {
            if (!selectedFile) throw new Error("Please select a file first.");

            statusText.innerText = `Uploading ${selectedFile.name}...`;

            statusText.innerText = `Preparing ${selectedFile.name}...`;

            // Convert file to Base64 for direct upload
            const toBase64 = file => new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => resolve(reader.result);
                reader.onerror = error => reject(error);
            });

            const base64Data = await toBase64(selectedFile);

            // console.log("File converted to Base64");
            payload = { pdf_base64: base64Data };
            progress.style.width = '55%';

        } else {
            const url = urlInput.value.trim();
            if (!url) throw new Error("Please enter a URL.");
            payload = { file_url: url };
        }

        statusText.innerText = "Extracting assets... (Processing PDF)";

        // Simulating "Processing" progress
        let fakeProgress = 60;
        const progressInterval = setInterval(() => {
            if (fakeProgress < 95) {
                fakeProgress += 1;
                progress.style.width = `${fakeProgress}%`;
            }
        }, 300);

        // API Call to Python Backend
        // The backend now just receives the URL (from Blob or Input)
        const response = await fetch('/api/logo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        progress.style.width = '100%';

        if (data.success) {
            statusText.innerText = "Done! Assets extracted.";
            renderGallery(data.data.logos || []);
        } else {
            throw new Error(data.error || "Unknown error occurred");
        }

    } catch (err) {
        statusText.innerText = `Error: ${err.message}`;
        statusText.style.color = 'var(--error)';
        progress.style.backgroundColor = 'var(--error)';
        console.error(err);
    } finally {
        processBtn.disabled = false;
    }
}

function renderGallery(urls) {
    if (!urls || urls.length === 0) {
        galleryGrid.innerHTML = '<div class="empty-state">No logos found or extracted.</div>';
        return;
    }

    countBadge.innerText = `(${urls.length})`;

    urls.forEach(url => {
        const div = document.createElement('div');
        div.className = 'gallery-item';
        div.onclick = () => window.open(url, '_blank');
        div.innerHTML = `<img src="${url}" loading="lazy" alt="Extracted Logo">`;
        galleryGrid.appendChild(div);
    });
}
