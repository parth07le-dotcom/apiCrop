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

            // Upload directly to Vercel Blob
            // Note: This requires the BLOB_READ_WRITE_TOKEN to be set in Vercel env vars
            // and a token generation endpoint or public access (if configured). 
            // For simplicity in this demo, we assume the token is available via an API or 
            // we use the 'client' upload which typically needs a token handler.

            // However, Vercel Blob client upload requires a server-side route to issue a token.
            // Let's assume we have '/api/upload_token' or similar. 
            // IF NOT, and we want to keep it simple, we might need to rely on the server handling it
            // BUT the server has the 4.5MB limit. 

            // Wait, to use client-side upload, we need `handleUpload` on the server.
            // Let's implement the client upload using the standard pattern:

            const newBlob = await upload(selectedFile.name, selectedFile, {
                access: 'public',
                handleUploadUrl: '/api/upload_token', // We need to ensure this exists!
            });

            console.log("Blob uploaded:", newBlob.url);
            payload = { file_url: newBlob.url };
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
            const errText = await response.text();
            try {
                const errData = JSON.parse(errText);
                throw new Error(errData.error || `Server error: ${response.status}`);
            } catch (e) {
                // If it's not JSON, it's likely an HTML error page or empty
                throw new Error(`Server error ${response.status}: ${errText.substring(0, 100)}...`);
            }
        }

        const responseText = await response.text();
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            throw new Error(`Invalid JSON response: ${responseText.substring(0, 100)}...`);
        }
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
