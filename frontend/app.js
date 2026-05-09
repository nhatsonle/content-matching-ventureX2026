/**
 * Frontend Logic
 * Owner: Duy (Frontend Developer)
 *
 * TODOs:
 *  1. Wire up runMatch() to POST /api/match
 *  2. Render candidate cards from response
 *  3. Add filter/sort controls (by score, by genre, by availability)
 *  4. Handle loading and error states nicely
 */

const API_BASE = "http://localhost:8000/api";

async function runMatch() {
  const briefText  = document.getElementById("brief-text").value.trim();
  const genresRaw  = document.getElementById("genres").value;
  const stylesRaw  = document.getElementById("styles").value;
  const topN       = parseInt(document.getElementById("top-n").value) || 5;

  if (!briefText) { showError("Vui lòng nhập mô tả dự án."); return; }

  const genres = genresRaw.split(",").map(s => s.trim()).filter(Boolean);
  const styles = stylesRaw.split(",").map(s => s.trim()).filter(Boolean);

  setLoading(true);
  clearError();
  hide("results");

  try {
    const res = await fetch(`${API_BASE}/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief_text: briefText, genres, style_tags: styles, top_n: topN }),
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    renderResults(data);

  } catch (err) {
    showError(`Lỗi kết nối tới server: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

function renderResults(data) {
  const container = document.getElementById("cards-container");
  container.innerHTML = "";

  document.getElementById("result-count").textContent =
    `(${data.shortlist.length} / ${data.total_candidates_considered} ứng viên)`;

  data.shortlist.forEach((c, idx) => {
    // TODO (Duy): enhance card with more fields once backend sends them
    const card = document.createElement("div");
    card.className = "candidate-card";
    card.innerHTML = `
      <div>
        <div class="candidate-name">#${idx + 1} — ${c.name}</div>
        <div class="candidate-meta">ID: ${c.id}</div>
        <div class="tags">
          ${Object.entries(c.feature_breakdown)
            .sort(([,a],[,b]) => b - a).slice(0, 3)
            .map(([k, v]) => `<span class="tag">${k}: ${(v * 100).toFixed(0)}%</span>`)
            .join("")}
        </div>
        <div class="explanation">${c.explanation}</div>
      </div>
      <div class="score-badge">${Math.round(c.score)}<span>/ 100</span></div>
    `;
    container.appendChild(card);
  });

  show("results");
}

// ── Helpers ──
function setLoading(on) { on ? show("loading") : hide("loading"); }
function showError(msg)  { const el = document.getElementById("error-msg"); el.textContent = msg; show("error-msg"); }
function clearError()    { hide("error-msg"); }
function show(id)        { document.getElementById(id).classList.remove("hidden"); }
function hide(id)        { document.getElementById(id).classList.add("hidden"); }
