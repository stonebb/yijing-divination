// ====== State ======
let currentMethod = "coin";
let divining = false;

const YAO_SYMBOLS = { yang: "━━━━━", yin: "━━ ━━" };

// ====== DOM Refs ======
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// ====== Tab Navigation ======
$$(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        $$(".nav-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        $$(".tab-content").forEach(t => t.classList.remove("active"));
        $(`#tab-${btn.dataset.tab}`).classList.add("active");
        if (btn.dataset.tab === "browse") loadHexagramGrid();
    });
});

// ====== Method Tabs ======
$$(".method-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        $$(".method-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentMethod = btn.dataset.method;
    });
});

// ====== Divination ======
$("#btn-divine").addEventListener("click", async () => {
    if (divining) return;
    const question = $("#question").value.trim();
    if (currentMethod === "coin") {
        await animateCoinDivination(question);
    } else {
        await quickDivination(question);
    }
});

async function quickDivination(question) {
    divining = true;
    const btn = $("#btn-divine");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 起卦中...';
    $("#divine-result").classList.add("hidden");

    const resp = await fetch("/api/divine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method: currentMethod, question }),
    });
    const data = await resp.json();
    showResult(data);

    divining = false;
    btn.disabled = false;
    btn.textContent = "开始起卦";
}

async function animateCoinDivination(question) {
    divining = true;
    const btn = $("#btn-divine");
    btn.disabled = true;

    $("#divine-result").classList.add("hidden");
    const animArea = $("#coin-animation");
    const linesEl = $("#yao-lines");
    const statusEl = $("#coin-status");
    animArea.classList.remove("hidden");
    linesEl.innerHTML = "";
    statusEl.textContent = "";

    const allLines = [];
    for (let i = 0; i < 6; i++) {
        btn.innerHTML = `<span class="spinner"></span> 投掷第 ${i + 1} 爻...`;
        statusEl.textContent = `第 ${i + 1} 次投掷...`;
        await sleep(350);

        const coinSum = randInt(6, 9);
        let value, changing, label;
        if (coinSum === 6)      { value = 0; changing = true;  label = "老阴 ◆"; }
        else if (coinSum === 7) { value = 1; changing = false; label = "少阳"; }
        else if (coinSum === 8) { value = 0; changing = false; label = "少阴"; }
        else                    { value = 1; changing = true;  label = "老阳 ◆"; }

        const coins = [];
        let rem = coinSum;
        for (let c = 0; c < 3; c++) {
            const cv = c === 2 ? rem : randInt(2, Math.min(3, rem - (2 - c) * 2));
            coins.push(cv);
            rem -= cv;
        }

        allLines.push({ position: i + 1, value, changing, label, coins, coin_sum: coinSum });

        linesEl.innerHTML = "";
        for (let j = 5; j >= 0; j--) {
            if (j >= allLines.length) {
                linesEl.innerHTML += '<div class="yao-line placeholder">···</div>';
            } else {
                const l = allLines[j];
                const cls = (l.value === 1 ? "yang" : "yin") + (l.changing ? " changing" : "");
                const sym = l.value === 1 ? YAO_SYMBOLS.yang : YAO_SYMBOLS.yin;
                const mark = l.changing ? (l.value === 1 ? " ○" : " ×") : "";
                linesEl.innerHTML += `<div class="yao-line ${cls}">${sym}${mark}</div>`;
            }
        }
        statusEl.textContent = `第 ${i + 1} 爻：${label}（${coins.join("+")}=${coinSum}）`;
        await sleep(500);
    }

    btn.innerHTML = '<span class="spinner"></span> 正在解读卦象...';
    statusEl.textContent = "解读中...";
    await sleep(600);

    // Get real server result
    const resp = await fetch("/api/divine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method: "coin", question }),
    });
    const data = await resp.json();
    data.lines = allLines;
    data.yao_drawing = buildYaoDrawing(allLines);
    showResult(data);

    animArea.classList.add("hidden");
    divining = false;
    btn.disabled = false;
    btn.textContent = "开始起卦";
}

function buildYaoDrawing(lines) {
    return [...lines].reverse().map(l => {
        let base = l.value === 1 ? YAO_SYMBOLS.yang : YAO_SYMBOLS.yin;
        if (l.changing) base += l.value === 1 ? " ○" : " ×";
        return base;
    }).join("\n");
}

// ====== Result Display ======
function showResult(data) {
    const main = data.main_hexagram;
    const change = data.changing_hexagram;
    const positions = data.changing_positions || [];
    const yaoCi = data.changing_yao_ci || [];
    const q = data.question || "";

    const hasChange = positions.length > 0 && change;

    let html = '<div class="result-container">';

    // ── Top: Hexagrams side by side ──
    html += '<div class="result-hex-row">';
    html += '<div class="result-hex-main">';
    html += `<div class="hex-badge">本卦</div>`;
    html += `<div class="result-symbol">${main.unicode_symbol}</div>`;
    html += `<div class="result-name">${main.name}</div>`;
    html += `<div class="result-short">${main.short_name}</div>`;
    html += `<div class="result-core">${main.core_meaning}</div>`;
    html += '</div>';

    if (hasChange) {
        html += '<div class="result-arrow-wrap"><span class="result-arrow">⟶</span></div>';
        html += '<div class="result-hex-change">';
        html += `<div class="hex-badge change">变卦</div>`;
        html += `<div class="result-symbol">${change.unicode_symbol}</div>`;
        html += `<div class="result-name">${change.name}</div>`;
        html += `<div class="result-short">${change.short_name}</div>`;
        html += `<div class="result-core">动爻：第${positions.join("、")}爻</div>`;
        html += '</div>';
    }
    html += '</div>';

    // ── Question ──
    if (q) html += `<div class="info-banner">📝 所问：${esc(q)}</div>`;

    // ── Yao Drawing ──
    html += '<div class="section-title"><span class="section-icon">☯</span> 卦象图</div>';
    html += '<div class="yao-drawing-display">';
    const drawingLines = data.yao_drawing.split("\n");
    for (const dl of drawingLines) {
        html += `<div class="yao-drawing-line">${esc(dl)}</div>`;
    }
    html += '</div>';

    // ── Keywords ──
    html += '<div class="section-title"><span class="section-icon">🏷</span> 关键词</div>';
    html += '<div class="tag-list">';
    html += (main.keywords || []).map(k => `<span class="tag">${esc(k)}</span>`).join("");
    html += '</div>';

    // ── Judgment ──
    html += '<div class="section-title"><span class="section-icon">📜</span> 卦辞</div>';
    html += `<blockquote class="judgment-text">${esc(main.judgment)}</blockquote>`;
    html += `<p class="judgment-interp">${esc(main.judgment_interpretation)}</p>`;

    // ── Image ──
    html += '<div class="section-title"><span class="section-icon">🌄</span> 象曰</div>';
    html += `<blockquote class="judgment-text">${esc(main.image)}</blockquote>`;
    html += `<p class="judgment-interp">${esc(main.image_interpretation)}</p>`;

    // ── Changing Yao ──
    if (yaoCi.length > 0) {
        html += '<div class="section-title"><span class="section-icon">✨</span> 动爻详解</div>';
        html += '<div class="yao-list">';
        for (const yao of yaoCi) {
            html += '<div class="yao-card changing-highlight">';
            html += `<div class="yao-header">${esc(yao.position_name)} <span class="yao-pos-text">${esc(yao.position || '')}</span></div>`;
            html += `<div class="yao-text">${esc(yao.text)}</div>`;
            html += `<div class="yao-interp">${esc(yao.interpretation)}</div>`;
            html += '</div>';
        }
        html += '</div>';
    }

    // ── All Yao ──
    html += '<div class="section-title"><span class="section-icon">📊</span> 全部爻辞</div>';
    html += '<div class="yao-list">';
    for (let i = 0; i < (main.yao_ci || []).length; i++) {
        const y = main.yao_ci[i];
        const isChanging = positions.includes(i + 1);
        html += `<div class="yao-card${isChanging ? ' changing-highlight' : ''}">`;
        html += `<div class="yao-header">${esc(y.position)}${isChanging ? ' <span class="changing-dot">● 动</span>' : ''}</div>`;
        html += `<div class="yao-text">${esc(y.text)}</div>`;
        html += `<div class="yao-interp">${esc(y.interpretation)}</div>`;
        html += '</div>';
    }
    html += '</div>';

    // ── Wisdom ──
    html += '<div class="section-title"><span class="section-icon">💡</span> 智慧提示</div>';
    html += `<p class="wisdom-text">${esc(main.core_meaning)}</p>`;
    if (q) {
        html += '<div class="info-banner wisdom">';
        if (yaoCi.length > 0) {
            html += `针对「${esc(q)}」，当前正处于转变的节点，动爻揭示了事情发展的关键动向。`;
        } else {
            html += `针对「${esc(q)}」，当前局势相对稳定，宜按卦辞所示的大方向行事。`;
        }
        html += '</div>';
    }
    html += '<div class="disclaimer">⚖ 易经算卦仅供参考，决断在于自己</div>';

    html += '</div>';

    const container = $("#divine-result");
    container.innerHTML = html;
    container.classList.remove("hidden");
    container.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ====== Hexagram Browser ======
async function loadHexagramGrid(query) {
    let hexagrams;
    if (query) {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        hexagrams = await resp.json();
    } else {
        const resp = await fetch("/api/hexagrams");
        hexagrams = await resp.json();
    }

    const grid = $("#hexagram-grid");
    if (!hexagrams || hexagrams.length === 0) {
        grid.innerHTML = '<div class="empty-state">🔍 未找到匹配的卦象</div>';
        return;
    }

    grid.innerHTML = hexagrams.map(h => `
        <div class="hex-card" data-id="${h.id}">
            <div class="hex-card-sym">${h.unicode_symbol}</div>
            <div class="hex-card-name">${h.name}</div>
            <div class="hex-card-meaning">${h.core_meaning}</div>
            <div class="hex-card-tags">${(h.keywords||[]).slice(0, 3).map(k => `<span class="tag tiny">${esc(k)}</span>`).join("")}</div>
        </div>
    `).join("");

    grid.querySelectorAll(".hex-card").forEach(card => {
        card.addEventListener("click", () => showHexagramDetail(parseInt(card.dataset.id)));
    });
}

async function showHexagramDetail(hid) {
    const resp = await fetch(`/api/hexagram/${hid}`);
    const h = await resp.json();
    if (h.error) return;

    const modal = $("#hexagram-modal");
    const body = $("#modal-body");

    body.innerHTML = `
        <div class="modal-sym">${h.unicode_symbol}</div>
        <div class="modal-name">${h.name}</div>
        <div class="modal-short">${h.short_name}</div>
        <div class="modal-core">${h.core_meaning}</div>
        <div class="tag-list" style="justify-content:center">${(h.keywords||[]).map(k => `<span class="tag">${esc(k)}</span>`).join("")}</div>

        <div class="section-title"><span class="section-icon">📜</span> 卦辞</div>
        <blockquote class="judgment-text">${esc(h.judgment)}</blockquote>
        <p class="judgment-interp">${esc(h.judgment_interpretation)}</p>

        <div class="section-title"><span class="section-icon">🌄</span> 象曰</div>
        <blockquote class="judgment-text">${esc(h.image)}</blockquote>
        <p class="judgment-interp">${esc(h.image_interpretation)}</p>

        <div class="section-title"><span class="section-icon">📊</span> 爻辞</div>
        <div class="yao-list">
        ${(h.yao_ci||[]).map(y => `
            <div class="yao-card">
                <div class="yao-header">${esc(y.position)}</div>
                <div class="yao-text">${esc(y.text)}</div>
                <div class="yao-interp">${esc(y.interpretation)}</div>
            </div>
        `).join("")}
        </div>
    `;

    modal.classList.remove("hidden");
}

// Modal events
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay") || e.target.classList.contains("modal-close")) {
        $("#hexagram-modal").classList.add("hidden");
    }
});
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") $("#hexagram-modal").classList.add("hidden");
});

// Search
$("#btn-search").addEventListener("click", () => loadHexagramGrid($("#search-input").value.trim()));
$("#search-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") loadHexagramGrid($("#search-input").value.trim());
});
// Load grid on first browse tab visit
let gridLoaded = false;
const browseTab = $('[data-tab="browse"]');
browseTab.addEventListener("click", () => {
    if (!gridLoaded) { gridLoaded = true; loadHexagramGrid(); }
});

// ====== Helpers ======
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function esc(s) { return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
