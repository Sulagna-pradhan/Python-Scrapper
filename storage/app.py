#Upload file to Telegram channel directly from browser with progress bar and anti-flood protection.

import os
import asyncio
from flask import Flask, render_template_string, request, jsonify
from telegram import Bot
from werkzeug.utils import secure_filename

app = Flask(__name__)

TOKEN = ""
CHANNEL_ID = -121231
UPLOAD_FOLDER = ''
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 75 * 1024 * 1024

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"success": False, "error": "File exceeds the 50MB server limit."}), 413


HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Cloud Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
</head>
<body class="text-slate-200 min-h-screen p-4 md:p-10">
    <div class="max-w-3xl mx-auto">
        <header class="mb-10 text-center">
            <h1 class="text-4xl font-bold text-white mb-2 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">Telegram Dashboard</h1>
            <div class="flex items-center justify-center gap-3">
                <p class="text-slate-400">Sequential Uploader (Anti-Flood Protection)</p>
                <div id="queuePulse" class="hidden flex items-center gap-2">
                    <span class="relative flex h-3 w-3"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span></span>
                    <span class="text-[10px] font-bold text-amber-500 uppercase">Processing</span>
                </div>
            </div>
        </header>

        <div id="dropzone" class="relative group border-2 border-dashed border-slate-700 bg-slate-800/40 rounded-3xl p-12 text-center hover:border-blue-500 hover:bg-slate-800/60 transition-all duration-300 cursor-pointer mb-8">
            <input type="file" id="fileInput" class="hidden" multiple>
            <div class="space-y-4">
                <div class="w-16 h-16 bg-blue-500/10 text-blue-500 rounded-2xl flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
                </div>
                <div>
                    <p class="text-lg font-semibold text-white tracking-tight">Drop files here or click</p>
                    <p class="text-sm text-slate-500 italic">Sequential Upload (Max 50MB per file)</p>
                </div>
            </div>
        </div>

        <div id="fileQueue" class="space-y-4"></div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const dropzone = document.getElementById('dropzone');
        const fileQueue = document.getElementById('fileQueue');
        const queuePulse = document.getElementById('queuePulse');
        
        let uploadQueue = [];
        let isProcessing = false;
        const abortControllers = {};

        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => {
            const files = Array.from(e.target.files);
            files.forEach(file => {
                const id = Math.random().toString(36).substring(7);
                addToFileUI(file, id);
                uploadQueue.push({ file, id });
            });
            startQueue();
        };

        function addToFileUI(file, id) {
            const card = document.createElement('div');
            card.id = `card-${id}`;
            card.className = "bg-slate-800 border border-slate-700 rounded-2xl p-5 shadow-xl transition-all duration-500";
            card.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <div class="min-w-0">
                        <h3 class="text-sm font-semibold text-white truncate">${file.name}</h3>
                        <p class="text-[11px] text-slate-500">${(file.size / (1024*1024)).toFixed(2)} MB</p>
                    </div>
                    <button onclick="stopOrRemove('${id}')" id="btn-${id}" class="text-xs font-bold text-slate-500 bg-slate-700/50 px-3 py-1 rounded-full hover:bg-red-500/10 hover:text-red-400 transition-colors">WAITING</button>
                </div>
                <div class="relative h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                    <div id="bar-${id}" class="absolute h-full w-0 bg-blue-500 transition-all duration-200"></div>
                </div>
                <div id="status-${id}" class="mt-2 text-[10px] text-slate-500 uppercase tracking-widest font-bold">In Queue</div>
            `;
            fileQueue.prepend(card);
        }

        async function startQueue() {
            if (isProcessing || uploadQueue.length === 0) return;
            isProcessing = true;
            queuePulse.classList.remove('hidden');

            while (uploadQueue.length > 0) {
                const item = uploadQueue.shift();
                
                // Update button UI for active file
                const btn = document.getElementById(`btn-${item.id}`);
                if (btn) {
                    btn.innerText = "STOP";
                    btn.classList.replace('text-slate-500', 'text-red-400');
                }

                await uploadToServer(item.file, item.id);
                
                // Anti-flood pause
                if (uploadQueue.length > 0) {
                    await new Promise(res => setTimeout(res, 1500));
                }
            }

            isProcessing = false;
            queuePulse.classList.add('hidden');
        }

        async function uploadToServer(file, id) {
            const controller = new AbortController();
            abortControllers[id] = controller;
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await axios.post('/upload', formData, {
                    signal: controller.signal,
                    onUploadProgress: (p) => {
                        const percent = Math.round((p.loaded * 100) / p.total);
                        document.getElementById(`bar-${id}`).style.width = `${percent}%`;
                        document.getElementById(`status-${id}`).innerText = `Transfer: ${percent}%`;
                    }
                });

                if (response.data.success) {
                    const statusText = document.getElementById(`status-${id}`);
                    statusText.innerHTML = `<span class="text-emerald-400">Synced</span> <a href="${response.data.url}" target="_blank" class="ml-2 text-blue-400 underline lowercase font-normal italic">View on TG</a>`;
                    document.getElementById(`bar-${id}`).classList.replace('bg-blue-500', 'bg-emerald-500');
                    const btn = document.getElementById(`btn-${id}`);
                    btn.innerText = "REMOVE";
                    btn.className = "text-xs font-bold text-slate-400 hover:text-white px-3 py-1 transition-colors";
                    btn.onclick = () => document.getElementById(`card-${id}`).remove();
                }
            } catch (err) {
                const statusText = document.getElementById(`status-${id}`);
                if (axios.isCancel(err)) {
                    statusText.innerHTML = "<span class='text-orange-400 italic'>Stopped by user</span>";
                } else {
                    const errorMsg = err.response?.data?.error || "Connection Error";
                    statusText.innerHTML = `<span class='text-red-400'>${errorMsg}</span>`;
                }
                document.getElementById(`bar-${id}`).classList.replace('bg-blue-500', 'bg-red-500/50');
                document.getElementById(`btn-${id}`).innerText = "FAILED";
            }
        }

        function stopOrRemove(id) {
            if (abortControllers[id]) {
                abortControllers[id].abort();
                delete abortControllers[id];
            } else {
                uploadQueue = uploadQueue.filter(q => q.id !== id);
                document.getElementById(`card-${id}`).remove();
            }
        }
    </script>
</body>
</html>
"""

async def send_to_tg(path):
    bot = Bot(token=TOKEN)
    async with bot:
        with open(path, 'rb') as f:
            msg = await bot.send_document(chat_id=CHANNEL_ID, document=f)
            clean_id = str(CHANNEL_ID).replace("-100", "")
            return {
                "file_id": msg.document.file_id, 
                "url": f"https://t.me/c/{clean_id}/{msg.message_id}"
            }

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file received"}), 400
        
    file = request.files['file']
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(save_path)
    
    try:
        data = asyncio.run(send_to_tg(save_path))
        return jsonify({"success": True, **data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

if __name__ == '__main__':
    # Run the server
    app.run(debug=True, port=5000)