// --- 工具函式 ---
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    toast.innerHTML = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}

function gatherFormData() {
    const data = {
        npc_id: document.getElementById('npc_id').value.trim(),
        npc_name: document.getElementById('npc_name').value.trim(),
        action: document.getElementById('action').value.trim(),
        opening: document.getElementById('opening').value.trim(),
        options: []
    };
    document.querySelectorAll('#options-list .option-card').forEach(card => {
        data.options.push({
            title: card.querySelector('.opt-title').value.trim(),
            end_action: "loop",
            dialogue: [
                ["player", card.querySelector('.player-msg').value.trim()],
                ["npc", card.querySelector('.npc-msg').value.trim()]
            ]
        });
    });
    const leave = document.getElementById('leave-option');
    data.options.push({
        title: leave.querySelector('.opt-title').value.trim(),
        end_action: "exit",
        dialogue: [
            ["player", leave.querySelector('.player-msg').value.trim()],
            ["npc", leave.querySelector('.npc-msg').value.trim()]
        ]
    });
    return data;
}

function validate() {
    let valid = true;
    document.querySelectorAll('.required-field').forEach(f => {
        if (f.value.trim() === "") { f.classList.add('is-invalid'); valid = false; }
        else { f.classList.remove('is-invalid'); }
    });
    return valid;
}

// --- 介面操作 ---
function addOption(data = null) {
    const tpl = document.getElementById('opt-tpl').innerHTML;
    const div = document.createElement('div');
    div.innerHTML = tpl;
    const card = div.firstElementChild;
    document.getElementById('options-list').appendChild(card);
    if (data) {
        card.querySelector('.opt-title').value = data.title;
        card.querySelector('.player-msg').value = data.dialogue[0][1];
        card.querySelector('.player-msg').dataset.modified = "true";
        card.querySelector('.npc-msg').value = data.dialogue[1][1];
    }
}

function syncDialogue(titleInput) {
    const card = titleInput.closest('.option-card');
    const playerInput = card.querySelector('.player-msg');
    if (!playerInput.dataset.modified) playerInput.value = titleInput.value;
}

document.addEventListener('input', e => {
    if (e.target.classList.contains('player-msg')) e.target.dataset.modified = "true";
    if (e.target.value.trim() !== "") e.target.classList.remove('is-invalid');
});

function clearAllContent() {
    if (!confirm("⚠️ 確定要清空目前所有編輯內容嗎？")) return;
    ['npc_id', 'npc_name', 'action', 'opening'].forEach(id => {
        const el = document.getElementById(id); el.value = ""; el.classList.remove('is-invalid');
    });
    document.getElementById('options-list').innerHTML = "";
    const leave = document.getElementById('leave-option');
    leave.querySelectorAll('input').forEach(i => { i.value = ""; i.classList.remove('is-invalid'); });
    addOption();
    showToast("🧹 內容已完全清空");
}

// --- API 連動 ---
function saveToServer() {
    if (!validate()) return alert("請填寫所有欄位");
    const data = gatherFormData();
    const filename = `${data.npc_id}.json`;
    const existing = Array.from(document.querySelectorAll('.file-item span:first-child'))
                          .map(el => el.innerText.replace('📄 ', '').trim());
    
    if (existing.includes(filename) && !confirm(`⚠️ 檔案 [${filename}] 已存在，確定覆蓋？`)) return;

    fetch('/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) })
    .then(res => res.json()).then(() => { showToast("💾 存檔成功"); refreshFileList(); });
}

function copySQFToClipboard(event) {
    if (!validate()) return alert("請填寫所有欄位");
    const btn = event.currentTarget;
    fetch('/copy_sqf', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(gatherFormData()) })
    .then(res => res.json()).then(res => {
        navigator.clipboard.writeText(res.sqf).then(() => {
            showToast("📋 已複製到剪貼簿");
            const oldText = btn.innerHTML;
            btn.innerHTML = "✅ 已複製"; btn.classList.replace('btn-warning', 'btn-success');
            setTimeout(() => { btn.innerHTML = oldText; btn.classList.replace('btn-success', 'btn-warning'); }, 1500);
        });
    });
}

function refreshFileList() {
    fetch('/list_files').then(res => res.json()).then(files => {
        const list = document.getElementById('file-list');
        list.innerHTML = files.map(f => `
            <div class="file-item" onclick="loadFile('${f}')">
                <span>📄 ${f}</span>
                <span class="btn-file-delete" onclick="deleteFile(event, '${f}')">×</span>
            </div>
        `).join('');
    });
}

function deleteFile(event, filename) {
    event.stopPropagation();
    if (!confirm(`確定刪除 [${filename}]？`)) return;
    fetch(`/delete/${filename}`, { method: 'DELETE' }).then(res => res.json()).then(() => {
        showToast("🗑️ 檔案已刪除"); refreshFileList();
    });
}

function loadFile(filename) {
    if (!confirm(`載入 ${filename}？`)) return;
    fetch(`/load/${filename}`).then(res => res.json()).then(data => {
        document.getElementById('npc_id').value = data.npc_id;
        document.getElementById('npc_name').value = data.npc_name;
        document.getElementById('action').value = data.action;
        document.getElementById('opening').value = data.opening;
        document.getElementById('options-list').innerHTML = "";
        data.options.forEach(opt => {
            if (opt.end_action === "exit") {
                const lv = document.getElementById('leave-option');
                lv.querySelector('.opt-title').value = opt.title;
                lv.querySelector('.player-msg').value = opt.dialogue[0][1];
                lv.querySelector('.npc-msg').value = opt.dialogue[1][1];
            } else { addOption(opt); }
        });
    });
}

window.onload = () => { refreshFileList(); addOption(); };