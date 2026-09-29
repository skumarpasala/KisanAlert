/* ==========================================================
   Kisan Alert – frontend logic (matched to the Flask backend)
   ========================================================== */
const API_BASE = "http://127.0.0.1:5001";
const ENDPOINTS = {
  diagnose: "/diagnose",              // POST JSON {symptoms, language}
  image:    "/diagnose-image",        // POST form image + language
  soil:     "/soil-card",             // POST form image
  advisory: "/farm-advisory"          // POST JSON {crop, location, language, soil_card}
};

/* languages from language_config.py: [code, native name, speech code] */
const LANGS = [
  ["en", "English", "en-IN"], ["te", "తెలుగు", "te-IN"], ["hi", "हिन्दी", "hi-IN"],
  ["ta", "தமிழ்", "ta-IN"], ["kn", "ಕನ್ನಡ", "kn-IN"], ["ml", "മലയാളം", "ml-IN"],
  ["mr", "मराठी", "mr-IN"], ["bn", "বাংলা", "bn-IN"], ["pa", "ਪੰਜਾਬੀ", "pa-IN"],
  ["gu", "ગુજરાતી", "gu-IN"], ["or", "ଓଡ଼ିଆ", "or-IN"]
];
const CROPS = ["Tomato", "Rice", "Cotton", "Chilli", "Maize", "Groundnut", "Redgram", "Greengram"];
const VOICE_CODES = ["te", "en", "hi", "ta", "kn"];   // buttons shown on the Voice tab

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const list = v => Array.isArray(v) ? v : (v ? [v] : []);
const ul = arr => list(arr).length ? `<ul>${list(arr).map(x => `<li>${esc(x)}</li>`).join("")}</ul>` : "";

/* ---------- fill the dropdowns from the lists above ---------- */
const langOptions = () => LANGS.map(([c, n]) => `<option value="${c}">${n}</option>`).join("");
$("#globalLang").innerHTML = langOptions();
$("#diagLang").innerHTML = langOptions();
$("#advLang").innerHTML = '<option value="">Auto (from location)</option>' + langOptions();
$("#advCrop").innerHTML = CROPS.map(c => `<option>${c}</option>`).join("");

/* ---------- navigation ---------- */
function showTab(id) {
  $$(".tab").forEach(t => t.classList.toggle("active", t.id === id));
  $$("#nav button").forEach(b => b.classList.toggle("active", b.dataset.tab === id));
  window.scrollTo({ top: 0 });
}
document.addEventListener("click", e => {
  const el = e.target.closest("[data-tab]");
  if (el) { e.preventDefault(); showTab(el.dataset.tab); }
});

/* ---------- helpers ---------- */
function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 3200);
}
const loading = box => box.innerHTML = '<div class="spinner" aria-label="Loading"></div>';
const fail = (box, msg) => box.innerHTML = `<div class="empty error">${esc(msg)}</div>`;

async function api(path, options = {}) {
  let res;
  try { res = await fetch(API_BASE + path, options); }
  catch { throw new Error("Cannot reach the backend. Is it running on " + API_BASE + "?"); }
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false) throw new Error(data.error || `Server error ${res.status}`);
  return data;
}
const postJSON = (path, body) => api(path, {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
});
function postFile(path, file, extra = {}) {
  const fd = new FormData();
  fd.append("image", file);
  Object.entries(extra).forEach(([k, v]) => fd.append(k, v));
  return api(path, { method: "POST", body: fd });
}

/* ---------- diagnosis card (text + image) ---------- */
function renderDiagnosis(box, d) {
  const name = d.disease || "Result";
  const conf = d.confidence ? `Confidence: ${d.confidence}` : "";
  box.innerHTML = `
    <span class="badge">Diagnosis Result</span>
    <h3 class="name">${esc(name)}
      ${d.crop ? `<small>(${esc(d.crop)})</small>` : ""}
      ${conf ? `<span class="badge ${/medium|low/i.test(conf) ? "medium" : ""}">${esc(conf)}</span>` : ""}
    </h3>
    ${d.cause ? `<h4>Cause</h4><p>${esc(d.cause)}</p>` : ""}
    ${list(d.treatment).length ? `<h4>Treatment</h4>${ul(d.treatment)}` : ""}
    ${list(d.prevention).length ? `<h4>Prevention</h4>${ul(d.prevention)}` : ""}`;
}

/* ---------- crop diagnosis (text) ---------- */
$("#diagBtn").addEventListener("click", async () => {
  const symptoms = $("#symptoms").value.trim();
  if (!symptoms) return toast("Describe your crop symptoms first");
  const box = $("#diagResult"); loading(box);
  try {
    renderDiagnosis(box, await postJSON(ENDPOINTS.diagnose, { symptoms, language: $("#diagLang").value }));
  } catch (err) { fail(box, err.message); }
});

/* ---------- reusable drag-and-drop uploader ---------- */
function setupUploader({ drop, choose, input, preview, button }) {
  let file = null;
  const take = f => {
    if (!f) return;
    if (!/^image\/(png|jpe?g)$/.test(f.type)) return toast("Use a JPG or PNG image");
    if (f.size > 5 * 1024 * 1024) return toast("Image must be under 5MB");
    file = f;
    $(preview).src = URL.createObjectURL(f); $(preview).hidden = false;
    $(button).disabled = false;
  };
  $(choose).addEventListener("click", () => $(input).click());
  $(input).addEventListener("change", e => take(e.target.files[0]));
  const dz = $(drop);
  ["dragenter", "dragover"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add("over"); }));
  ["dragleave", "drop"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove("over"); }));
  dz.addEventListener("drop", e => take(e.dataTransfer.files[0]));
  return () => file;
}

/* ---------- image diagnosis ---------- */
const getCropImg = setupUploader({ drop: "#imgDrop", choose: "#imgChoose", input: "#imgInput", preview: "#imgPreview", button: "#imgBtn" });
$("#imgBtn").addEventListener("click", async () => {
  const box = $("#imgResult"); loading(box);
  try {
    const d = await postFile(ENDPOINTS.image, getCropImg(), { language: $("#globalLang").value });
    renderDiagnosis(box, d.diagnosis || {});
  } catch (err) { fail(box, err.message); }
});

/* ---------- soil card ---------- */
let soilCard = null;   // saved here and sent to /farm-advisory
try { soilCard = JSON.parse(sessionStorage.getItem("soilCard")); } catch {}

const getSoilImg = setupUploader({ drop: "#soilDrop", choose: "#soilChoose", input: "#soilInput", preview: "#soilPreview", button: "#soilBtn" });
// [backend key, label, colour, rough max for the bar]
const SOIL_FIELDS = [
  ["ph", "pH", "#1b8a4f", 14],
  ["electrical_conductivity", "EC", "#00a3a3", 4],
  ["organic_carbon", "Organic Carbon", "#2ecc71", 1.5],
  ["nitrogen", "Nitrogen (N)", "#1d6fe0", 560],
  ["phosphorus", "Phosphorus (P)", "#f57c1f", 50],
  ["potassium", "Potassium (K)", "#7c4dff", 600],
  ["sulphur", "Sulphur (S)", "#c9a300", 40],
  ["zinc", "Zinc (Zn)", "#e5484d", 2],
  ["iron", "Iron (Fe)", "#b5651d", 20],
  ["manganese", "Manganese (Mn)", "#8e44ad", 10],
  ["copper", "Copper (Cu)", "#d35400", 3],
  ["boron", "Boron (B)", "#16a085", 2]
];
const SOIL_LABEL = Object.fromEntries(SOIL_FIELDS.map(f => [f[0], f[1]]));

$("#soilBtn").addEventListener("click", async () => {
  const box = $("#soilResult"); loading(box);
  try {
    const d = await postFile(ENDPOINTS.soil, getSoilImg());
    soilCard = d.soil_card;
    try { sessionStorage.setItem("soilCard", JSON.stringify(soilCard)); } catch {}
    const params = soilCard.soil_parameters || {};
    const cells = SOIL_FIELDS.map(([key, label, color, max]) => {
      const p = params[key];
      if (!p || p.value === null || p.value === undefined) return "";
      const pct = Math.min(100, (parseFloat(p.value) / max) * 100 || 0);
      return `<div><small>${label}</small><b>${esc(p.value)}</b><small>${esc(p.unit || "")}</small>
        <div class="bar"><i style="width:${pct}%;background:${color}"></i></div></div>`;
    }).join("");
    if (cells) box.innerHTML = `<span class="badge">Extracted Soil Parameters</span><div class="soil-grid">${cells}</div>
      <p class="sub" style="margin-top:14px">Saved. You can now generate a Farm Advisory.</p>`;
    else fail(box, "No soil values could be read from this image. Try a clearer photo.");
  } catch (err) { fail(box, err.message); }
});

/* ---------- farm advisory ---------- */
// Weather comes from farm_profile.weather (raw Open-Meteo), or from "weather" if you added it to main.py
function readWeather(d) {
  const raw = (d.farm_profile || {}).weather || {};
  const c = raw.current || {}, dl = raw.daily || {};
  const w = d.weather || {}, wc = w.current || {}, wf = w.forecast || {};
  return {
    temp: c.temperature_2m ?? wc.temperature,
    humidity: c.relative_humidity_2m ?? wc.humidity,
    wind: c.wind_speed_10m ?? wc.wind_speed,
    rain: (dl.precipitation_probability_max || wf.rain_probability || [])[0]
  };
}

$("#advBtn").addEventListener("click", async () => {
  const box = $("#advResult");
  if (!soilCard) {
    fail(box, "Upload your soil health card in the Soil tab first. The advisory needs it.");
    return toast("Soil card needed");
  }
  loading(box);
  try {
    const d = await postJSON(ENDPOINTS.advisory, {
      crop: $("#advCrop").value,
      location: $("#advLoc").value.trim(),
      language: $("#advLang").value,
      soil_card: soilCard
    });
    const a = d.advisory || {};
    const w = readWeather(d);
    const loc = (d.farm || {}).location || {};
    const place = [loc.name, loc.state].filter(Boolean).join(", ");
    const val = (v, unit) => (v === undefined || v === null) ? "–" : `${esc(v)}${unit}`;
    const para = (label, text) => text ? `<h4>${label}</h4><p>${esc(text)}</p>` : "";

    // soil status badges from soil_interpretation (skip unknown / measured)
    const soilChips = Object.entries(d.soil_interpretation || {})
      .filter(([, v]) => v && v.status && !["unknown", "measured"].includes(v.status))
      .map(([k, v]) => `<span class="badge">${esc(SOIL_LABEL[k] || k)}: ${esc(v.status.replace(/_/g, " "))}</span>`)
      .join(" ");

    // alternative crops: rule-based (crop_recommendations) + Gemini suggestions
    const rec = d.crop_recommendations || {};
    const cropCard = c => `<h4>${esc(c.crop)} <span class="badge">${esc(c.confidence || "")}</span></h4>
      <p>${esc(c.reason)}</p>${c.soil_role ? `<p>${esc(c.soil_role)}</p>` : ""}`;
    const soilBased = list(rec.recommendations).map(cropCard).join("");
    const aiBased = list(a.alternative_crops_to_consider).map(cropCard).join("");

    const sections = {
      "Overview": `
        ${a.overall_risk ? `<span class="badge ${a.overall_risk === "low" ? "" : "medium"}">Risk: ${esc(a.overall_risk)}</span>` : ""}
        ${soilChips}
        ${para("Crop assessment", a.crop_assessment)}
        ${para("Weather", a.weather_observation)}
        ${para("Soil", a.soil_observation)}
        ${para("Irrigation", a.irrigation_advice)}
        ${para("Satellite data", a.satellite_observation)}`,
      "Farm Actions": `
        ${list(a.farm_actions).length ? `<h4>Farm actions</h4>${ul(a.farm_actions)}` : ""}
        ${list(a.regenerative_practices).length ? `<h4>Regenerative practices</h4>${ul(a.regenerative_practices)}` : ""}
        ${list(a.crop_rotation).length ? `<h4>Crop rotation</h4>${ul(a.crop_rotation)}` : ""}`,
      "Alternative Crops": `
        ${soilBased ? `<h3>Based on your soil</h3>${soilBased}` : ""}
        ${aiBased ? `<h3>AI suggestions</h3>${aiBased}` : ""}
        ${rec.disclaimer ? `<p class="sub" style="margin-top:12px">${esc(rec.disclaimer)}</p>` : ""}`,
      "Warnings": ul(a.warnings)
    };
    const body = t => (sections[t] || "").trim() || '<p class="sub">Nothing to show.</p>';

    box.innerHTML = `
      <span class="badge">Weather Overview${place ? " – " + esc(place) : ""}</span>
      <div class="weather">
        <div><b>${val(w.temp, "°C")}</b><small>Temperature</small></div>
        <div><b>${val(w.humidity, "%")}</b><small>Humidity</small></div>
        <div><b>${val(w.wind, " km/h")}</b><small>Wind Speed</small></div>
        <div><b>${val(w.rain, "%")}</b><small>Rain Probability</small></div>
      </div>
      <h3>Advisory Results</h3>
      <div class="tabs">${Object.keys(sections).map((t, i) => `<button class="${i ? "" : "on"}" data-adv="${t}">${t}</button>`).join("")}</div>
      <div id="advBody" class="result">${body("Overview")}</div>`;
    $$("[data-adv]", box).forEach(b => b.addEventListener("click", () => {
      $$("[data-adv]", box).forEach(x => x.classList.toggle("on", x === b));
      $("#advBody").innerHTML = body(b.dataset.adv);
    }));
  } catch (err) { fail(box, err.message); }
});

/* ---------- voice: speech -> text -> /diagnose -> spoken reply ---------- */
const voiceLangs = LANGS.filter(l => VOICE_CODES.includes(l[0]))
  .sort((a, b) => VOICE_CODES.indexOf(a[0]) - VOICE_CODES.indexOf(b[0]));
let voice = voiceLangs[0];            // [code, name, speech code]
let rec = null, listening = false;

const chipBox = $("#voice .chips");
chipBox.innerHTML = voiceLangs.map(([c, n], i) =>
  `<button class="chip ${i ? "" : "active"}" data-vlang="${c}">${n}</button>`).join("");
chipBox.addEventListener("click", e => {
  const chip = e.target.closest("[data-vlang]");
  if (!chip) return;
  voice = voiceLangs.find(l => l[0] === chip.dataset.vlang);
  $$("[data-vlang]", chipBox).forEach(x => x.classList.toggle("active", x === chip));
});

$("#micBtn").addEventListener("click", () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return toast("Voice input needs Chrome or Edge");
  if (listening) return rec.stop();
  rec = new SR(); rec.lang = voice[2]; rec.interimResults = false;
  rec.onstart = () => { listening = true; $("#micBtn").classList.add("live"); $("#micLabel").textContent = "Listening… click to stop"; };
  rec.onend = () => { listening = false; $("#micBtn").classList.remove("live"); $("#micLabel").textContent = "Click to Start Listening"; };
  rec.onerror = e => toast(`Microphone error: ${e.error}`);
  rec.onresult = async e => {
    const text = e.results[0][0].transcript, out = $("#voiceOut");
    out.innerHTML = `<p><b>You:</b> ${esc(text)}</p><div class="spinner"></div>`;
    try {
      const d = await postJSON(ENDPOINTS.diagnose, { symptoms: text, language: voice[0] });
      const reply = [d.disease, d.cause, ...list(d.treatment)].filter(Boolean).join(". ");
      out.innerHTML = `<p><b>You:</b> ${esc(text)}</p><p><b>Kisan Alert:</b> ${esc(reply)}</p>`;
      const u = new SpeechSynthesisUtterance(reply); u.lang = voice[2]; speechSynthesis.speak(u);
    } catch (err) { out.innerHTML = `<p class="error">${esc(err.message)}</p>`; }
  };
  rec.start();
});

/* keep the language selectors in sync with the top bar */
$("#globalLang").addEventListener("change", e => {
  ["#diagLang", "#advLang"].forEach(s => $(s).value = e.target.value);
});