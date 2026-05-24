import streamlit as st
import cv2
import numpy as np
from PIL import Image
import datetime
import os
import ai_logic
import parking_lot
import sqlite3
import time
from database import get_db_connection

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartPark — Intelligent Parking",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🅿️"
)
# ─── SIDEBAR STATE CONTROL ───────────────────────────────────
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

# Handle toggle from URL
query = st.query_params
if "toggle" in query:
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.query_params.clear()

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if 'live_plate' not in st.session_state:
    st.session_state['live_plate'] = "Waiting..."

# ══════════════════════════════════════════════════════════════
# THEME + CSS + LIVE CLOCK + HAMBURGER FIX
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── ROOT VARS ── */
:root {
    --bg:       #0a0c0f;
    --surface:  #111418;
    --surface2: #181c22;
    --border:   #1e2530;
    --accent:   #00e5ff;
    --accent2:  #ff6b35;
    --green:    #00ff9d;
    --red:      #ff3860;
    --yellow:   #ffd166;
    --text:     #e8edf5;
    --muted:    #5a6780;
}

/* ── GLOBAL ── */
html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

/* GRID BACKGROUND */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--border) 1px, transparent 1px),
        linear-gradient(90deg, var(--border) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.25;
    pointer-events: none;
    z-index: 0;
}



/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #080a0d !important;
    border-right: 1px solid var(--border) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 6px 0 !important;
    transition: color 0.2s;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--accent) !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h2 {
    color: var(--accent) !important;
    font-size: 1rem !important;
    letter-spacing: 1px;
}

/* ── OUR CUSTOM HAMBURGER BUTTON ── */
#sp-hamburger {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 99999;
    width: 42px;
    height: 42px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
#sp-hamburger:hover {
    border-color: var(--accent);
    box-shadow: 0 0 12px rgba(0,229,255,0.25);
}
#sp-hamburger .bar {
    width: 20px;
    height: 2px;
    background: var(--accent);
    border-radius: 2px;
    transition: all 0.25s ease;
}
/* Animate to X when sidebar is closed */
#sp-hamburger.is-closed .bar:nth-child(1) {
    transform: translateY(7px) rotate(45deg);
}
#sp-hamburger.is-closed .bar:nth-child(2) {
    opacity: 0;
    transform: scaleX(0);
}
#sp-hamburger.is-closed .bar:nth-child(3) {
    transform: translateY(-7px) rotate(-45deg);
}

/* ── TOP BAR WITH CLOCK ── */
#sp-topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 58px;
    background: rgba(10,12,15,0.97);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 0 24px 0 70px;
    z-index: 9999;
    gap: 16px;
    backdrop-filter: blur(6px);
}
#sp-topbar-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    color: var(--muted);
    margin-right: auto;
    margin-left: 10px;
}
#sp-status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse-dot 2s infinite;
    flex-shrink: 0;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1;   box-shadow: 0 0 6px var(--green); }
    50%       { opacity: 0.5; box-shadow: 0 0 14px var(--green); }
}
#sp-clock-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}
#sp-clock-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 1px;
}
#sp-live-clock {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 3px;
    line-height: 1;
}
#sp-live-date {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── PUSH CONTENT DOWN BELOW FIXED TOPBAR ── */
.main .block-container {
    padding-top: 76px !important;
}

/* ── ALL TEXT ── */
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}
p, span, label, div, li {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
.stMarkdown p { color: var(--muted) !important; font-size: 0.88rem !important; }

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent);
}
[data-testid="stMetricLabel"] > div {
    color: var(--muted) !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-family: 'Space Mono', monospace !important;
}
[data-testid="stMetricValue"] > div {
    color: var(--accent) !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── INPUTS ── */
input, textarea, [data-baseweb="input"] input {
    background-color: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
[data-baseweb="select"] > div {
    background-color: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] span { color: var(--text) !important; }
[data-baseweb="popover"] { background: var(--surface) !important; border: 1px solid var(--border) !important; }
[data-baseweb="menu"] li { background: var(--surface) !important; color: var(--text) !important; }
[data-baseweb="menu"] li:hover { background: var(--surface2) !important; }

/* ── BUTTONS ── */
.stButton > button {
    background-color: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background-color: #33ecff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,229,255,0.3) !important;
}
.btn-danger .stButton > button {
    background-color: var(--red) !important; color: #fff !important;
}
.btn-danger .stButton > button:hover {
    background-color: #ff5577 !important;
    box-shadow: 0 4px 16px rgba(255,56,96,0.3) !important;
}
.btn-secondary .stButton > button {
    background-color: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.btn-secondary .stButton > button:hover {
    border-color: var(--accent) !important; color: var(--accent) !important;
}

/* ── CAMERA INPUT ── */
[data-testid="stCameraInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stCameraInputButton"] {
    background-color: var(--accent) !important; color: #000 !important;
    border: none !important; border-radius: 8px !important; font-weight: 700 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--surface) !important;
    border-radius: 10px !important; border: 1px solid var(--border) !important;
    padding: 4px !important; gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important; color: var(--muted) !important;
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 0.82rem !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important;
    border: none !important; padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] { background-color: var(--surface2) !important; color: var(--text) !important; }
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── TABLES ── */
.stDataFrame, [data-testid="stTable"] {
    background-color: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; overflow: hidden !important;
}
thead tr th {
    background-color: var(--surface2) !important; color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.68rem !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
    border-bottom: 1px solid var(--border) !important;
}
tbody tr td {
    color: var(--text) !important; font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important; border-bottom: 1px solid var(--border) !important;
    background-color: transparent !important;
}
tbody tr:hover td { background-color: var(--surface2) !important; }

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 10px !important; border-left: 3px solid !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important;
}
.stSuccess { background: rgba(0,255,157,0.08) !important;  border-color: var(--green)  !important; color: var(--green)  !important; }
.stError   { background: rgba(255,56,96,0.08) !important;  border-color: var(--red)    !important; color: var(--red)    !important; }
.stWarning { background: rgba(255,209,102,0.08) !important;border-color: var(--yellow) !important; color: var(--yellow) !important; }
.stInfo    { background: rgba(0,229,255,0.08) !important;  border-color: var(--accent) !important; color: var(--accent) !important; }
[data-testid="stAlert"] p { color: inherit !important; }

/* ── CODE ── */
[data-testid="stExpander"] {
    background-color: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important;
}
code, pre {
    background: var(--surface2) !important; color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important; border-radius: 6px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── CUSTOM CARDS ── */
.sp-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
    position: relative; overflow: hidden; margin-bottom: 16px;
}
.sp-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; background: var(--accent);
}
.sp-card-red::before    { background: var(--red); }
.sp-card-green::before  { background: var(--green); }
.sp-card-yellow::before { background: var(--yellow); }
.sp-card-orange::before { background: var(--accent2); }

.sp-card-label {
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--muted); font-family: 'Space Mono', monospace; margin-bottom: 8px;
}
.sp-card-value        { font-size: 2.2rem; font-weight: 800; color: var(--accent);   line-height: 1; font-family: 'Syne', sans-serif; }
.sp-card-value-red    { color: var(--red)    !important; }
.sp-card-value-green  { color: var(--green)  !important; }
.sp-card-value-yellow { color: var(--yellow) !important; }
.sp-card-value-orange { color: var(--accent2)!important; }

.sp-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 20px;
    font-family: 'Space Mono', monospace; font-size: 0.7rem; font-weight: 700;
}
.sp-badge-cyan   { background:rgba(0,229,255,0.12);  border:1px solid rgba(0,229,255,0.3);  color:var(--accent); }
.sp-badge-red    { background:rgba(255,56,96,0.12);   border:1px solid rgba(255,56,96,0.35); color:var(--red); }
.sp-badge-green  { background:rgba(0,255,157,0.08);   border:1px solid rgba(0,255,157,0.25); color:var(--green); }
.sp-badge-yellow { background:rgba(255,209,102,0.1);  border:1px solid rgba(255,209,102,0.3);color:var(--yellow); }

.sp-section-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid var(--border);
}
.sp-section-accent { width: 3px; height: 22px; background: var(--accent); border-radius: 2px; display: inline-block; }
.sp-section-title {
    font-size: 0.82rem !important; text-transform: uppercase !important;
    letter-spacing: 2px !important; color: var(--text) !important;
    font-weight: 700 !important; font-family: 'Syne', sans-serif !important;
}

.sp-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 4px 0 16px; border-bottom: 1px solid var(--border); margin-bottom: 16px;
}
.sp-logo-icon {
    width: 34px; height: 34px; background: var(--accent); border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #000; font-size: 16px; font-weight: 900;
}
.sp-logo-text { font-size: 1.2rem; font-weight: 800; color: var(--text) !important; }
.sp-logo-text span { color: var(--accent) !important; }

.made-by {
    font-family: 'Space Mono', monospace !important; color: var(--muted) !important;
    font-size: 0.7rem !important; text-align: center; letter-spacing: 1px;
    padding: 12px 0 4px; text-transform: uppercase;
}
.made-by strong { color: var(--accent) !important; }

[data-testid="stCheckbox"] label span { color: var(--text) !important; font-size:0.85rem !important; }

/* ── HIDE STREAMLIT BRANDING ONLY ── */
#MainMenu { visibility: hidden !important; }
footer    { visibility: hidden !important; }
</style>

<!-- ═══ FIXED TOP BAR ═══ -->
<div id="sp-topbar">
    <span id="sp-topbar-title">🅿 SmartPark System</span>
    <div id="sp-clock-box">
        <div id="sp-status-dot"></div>
        <div id="sp-clock-wrap">
            <div id="sp-live-clock">--:--:--</div>
            <div id="sp-live-date">Loading...</div>
        </div>
    </div>
</div>

<!-- ═══ CUSTOM HAMBURGER ═══ -->
<div id="sp-hamburger" title="Toggle Sidebar">
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
</div>

<script>
// ── LIVE CLOCK ──
(function startClock() {
    function tick() {
        var now  = new Date();
        var hh   = String(now.getHours()).padStart(2,'0');
        var mm   = String(now.getMinutes()).padStart(2,'0');
        var ss   = String(now.getSeconds()).padStart(2,'0');
        var days = ['SUN','MON','TUE','WED','THU','FRI','SAT'];
        var mos  = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
        var ds   = days[now.getDay()] + ' ' +
                   String(now.getDate()).padStart(2,'0') + ' ' +
                   mos[now.getMonth()] + ' ' +
                   now.getFullYear();
        var c = document.getElementById('sp-live-clock');
        var d = document.getElementById('sp-live-date');
        if (c) c.textContent = hh + ':' + mm + ':' + ss;
        if (d) d.textContent = ds;
    }
    tick();
    setInterval(tick, 1000);
})();

// ── HAMBURGER / SIDEBAR TOGGLE ──
(function initHamburger() {
    var btn = document.getElementById('sp-hamburger');
    if (!btn) return;

    btn.addEventListener('click', function() {
        // Try every known selector for Streamlit's sidebar button
        var selectors = [
            '[data-testid="collapsedControl"] button',
            '[data-testid="stSidebarCollapsedControl"] button',
            'button[aria-label="open sidebar"]',
            'button[aria-label="close sidebar"]',
            'button[aria-label="Open sidebar"]',
            'button[aria-label="Close sidebar"]',
            'button[aria-label="Hide sidebar"]',
            'button[aria-label="Show sidebar"]'
        ];

        var clicked = false;
        for (var i = 0; i < selectors.length; i++) {
            var el = document.querySelector(selectors[i]);
            if (el) { el.click(); clicked = true; break; }
        }

        if (!clicked) {
            // Pure CSS fallback — toggle sidebar visibility directly
            var sb = document.querySelector('[data-testid="stSidebar"]');
            if (sb) {
                if (sb.getAttribute('aria-expanded') === 'false' ||
                    sb.style.marginLeft === '-300px') {
                    sb.style.marginLeft = '0';
                    sb.style.visibility = 'visible';
                    sb.setAttribute('aria-expanded', 'true');
                } else {
                    sb.style.marginLeft = '-300px';
                    sb.setAttribute('aria-expanded', 'false');
                }
            }
        }

        // Animate hamburger ↔ X
        btn.classList.toggle('is-closed');
    });

    // Sync hamburger icon with real sidebar state on load & re-render
    function syncIcon() {
        var sb = document.querySelector('[data-testid="stSidebar"]');
        if (!sb || !btn) return;
        var expanded = sb.getAttribute('aria-expanded');
        if (expanded === 'false') {
            btn.classList.add('is-closed');
        } else {
            btn.classList.remove('is-closed');
        }
    }

    // Watch for sidebar attribute mutations
    var sb = document.querySelector('[data-testid="stSidebar"]');
    if (sb) {
        new MutationObserver(syncIcon).observe(sb, { attributes: true });
    }

    // Also sync after Streamlit re-renders
    [300, 800, 1500, 3000].forEach(function(t) {
        setTimeout(syncIcon, t);
    });
})();
</script>

""", unsafe_allow_html=True)

# ─── INIT DB ───────────────────────────────────────────────────────────────────
if not os.path.exists('parking_system.db'):
    import init_db
    init_db.init_db()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sp-logo">
    <div class="sp-logo-icon">P</div>
    <div class="sp-logo-text">Smart<span>Park</span></div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "NAVIGATION",
    ["Live Monitoring", "Parking Operations", "AI Analytics", "Security", "Logs"],
    label_visibility="visible"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div class="sp-section-title" style="color:var(--muted);font-size:0.68rem;'
    'letter-spacing:2px;margin-bottom:8px">🎥 IPCAM SETUP</div>',
    unsafe_allow_html=True
)
ip_link = st.sidebar.text_input(
    "Stream Link (IP/RTSP)",
    placeholder="e.g. 192.168.1.50",
    label_visibility="visible"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="made-by">Made by <strong>Rafay</strong></div>
""", unsafe_allow_html=True)

# ─── PAGE TITLE ────────────────────────────────────────────────────────────────
page_icons = {
    "Live Monitoring":    "📡",
    "Parking Operations": "🚗",
    "AI Analytics":       "🧠",
    "Security":           "🔒",
    "Logs":               "📜",
}
st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;
            padding-bottom:14px;border-bottom:1px solid var(--border)">
    <div style="width:3px;height:28px;background:var(--accent);border-radius:2px"></div>
    <div style="font-size:1.1rem;font-weight:800;text-transform:uppercase;
                letter-spacing:2px;color:var(--text)">
        {page_icons.get(page,'')} &nbsp;{page}
    </div>
    <div style="margin-left:auto;font-family:'Space Mono',monospace;
                font-size:0.68rem;color:var(--muted);letter-spacing:1px">
        SYSTEM ONLINE
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: LIVE MONITORING
# ══════════════════════════════════════════════════════════════
if page == "Live Monitoring":

    st.markdown("""
    <div class="sp-section-header">
        <span class="sp-section-accent"></span>
        <span class="sp-section-title">Two-Stage Deep Learning Scanner</span>
        <span class="sp-badge sp-badge-cyan" style="margin-left:auto">CRAFT + CRNN</span>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)

        if ip_link:
            st.markdown(f'<div class="sp-card-label">📡 LIVE STREAM — {ip_link}</div>', unsafe_allow_html=True)
            run = st.checkbox("▶  Enable Live Feed", value=True)
            FRAME_WIN = st.image([])
            source = ip_link if ip_link else 0
            cap = cv2.VideoCapture(source)
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Stream failed — switching to primary camera...")
                    cap = cv2.VideoCapture(0)
                    ret, frame = cap.read()
                    if not ret:
                        break

                if int(time.time() * 5) % 5 == 0:
                    cv2.imwrite("dl_frame.jpg", frame)
                    plate, box = ai_logic.perform_ocr("dl_frame.jpg", return_box=True)
                    if plate:
                        st.session_state['live_plate'] = plate
                        st.session_state['entry_plate'] = plate
                    if box:
                        st.session_state['last_box'] = box

                h, w, _ = frame.shape
                if 'last_box' in st.session_state and st.session_state['last_box']:
                    xmin, xmax, ymin, ymax = st.session_state['last_box']
                    cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 229, 255), 3)
                else:
                    cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 229, 255), 2)

                if st.session_state.get('live_plate') and st.session_state['live_plate'] != "Waiting...":
                    msg = f"DETECTED: {st.session_state['live_plate']}"
                    cv2.putText(frame, msg, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 229, 255), 3)

                FRAME_WIN.image(frame, channels="BGR")
            cap.release()
        else:
            st.markdown('<div class="sp-card-label">📷 LOCAL CAMERA — SCAN LICENSE PLATE</div>', unsafe_allow_html=True)
            img = st.camera_input("", label_visibility="hidden")
            if img:
                b    = img.getvalue()
                cimg = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                cv2.imwrite("dl_snap.jpg", cimg)
                plate = ai_logic.perform_ocr("dl_snap.jpg")
                st.session_state['live_plate'] = plate if plate else "No text detected"
                st.image(cimg, channels="BGR")

        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        curr_plate = st.session_state['live_plate']

        st.markdown(f"""
        <div class="sp-card">
            <div class="sp-card-label">🔍 AI DETECTION RESULT</div>
            <div style="font-family:'Space Mono',monospace;font-size:1.5rem;font-weight:700;
                        letter-spacing:4px;color:var(--accent);margin:10px 0 6px">
                {curr_plate if curr_plate != "Waiting..." else "— — —"}
            </div>
        </div>
        """, unsafe_allow_html=True)

        curr_plate = st.text_input("Edit Plate If Wrong", value=st.session_state['live_plate'])

        if curr_plate == "Waiting...":
            st.info("Awaiting camera input...")
        else:
            sec_msg = ai_logic.is_suspicious(curr_plate)
            if sec_msg:
                st.error(f"🚨 SECURITY ALERT: {sec_msg}")
            elif curr_plate != "No text detected":
                st.success("✅ Security Check: CLEAR")

            st.markdown("---")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("➡ Move to Gate", use_container_width=True):
                    st.session_state['entry_plate'] = curr_plate
                    st.success("Transferred to Gate!")
            with col_b2:
                st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
                if st.button("↺ Clear / Retry", use_container_width=True):
                    st.session_state['live_plate'] = "Waiting..."
                    if 'entry_plate' in st.session_state:
                        del st.session_state['entry_plate']
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            if curr_plate != "No text detected":
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("🚨 Blacklist This Vehicle", use_container_width=True):
                    ai_logic.add_to_blacklist(curr_plate, "Intelligence Alert")
                    st.warning(f"{curr_plate} has been blacklisted!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="sp-card" style="margin-top:16px">
            <div class="sp-card-label">SYSTEM STATUS</div>
        """, unsafe_allow_html=True)
        try:
            conn = get_db_connection()
            active_count = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
            total_slots  = conn.execute("SELECT COUNT(*) FROM parking_slots").fetchone()[0]
            conn.close()
            avail = total_slots - active_count
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">
                <div>
                    <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
                                color:var(--muted);text-transform:uppercase;letter-spacing:1px">Available</div>
                    <div style="font-size:1.4rem;font-weight:800;color:var(--green)">{avail}</div>
                </div>
                <div>
                    <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
                                color:var(--muted);text-transform:uppercase;letter-spacing:1px">Occupied</div>
                    <div style="font-size:1.4rem;font-weight:800;color:var(--red)">{active_count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: PARKING OPERATIONS
# ══════════════════════════════════════════════════════════════
elif page == "Parking Operations":

    t_in, t_out = st.tabs(["🚀  Vehicle Entry", "🏁  Vehicle Exit"])

    with t_in:
        st.markdown("""
        <div class="sp-section-header">
            <span class="sp-section-accent"></span>
            <span class="sp-section-title">Gate Entry — Log Incoming Vehicle</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="sp-card">', unsafe_allow_html=True)
            st.markdown('<div class="sp-card-label">VEHICLE DETAILS</div>', unsafe_allow_html=True)
            plat  = st.text_input("License Plate Number", value=st.session_state.get('entry_plate', ""))
            vtype = st.selectbox("Vehicle Class", ["Normal", "Disabled", "VIP", "Bike"])
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="sp-card">', unsafe_allow_html=True)
            st.markdown('<div class="sp-card-label">SLOT ASSIGNMENT</div>', unsafe_allow_html=True)
            if st.button("🤖 AI Recommend Slot", use_container_width=True):
                rec = ai_logic.recommend_parking_slot(vtype)
                st.session_state['rec_slot'] = rec
            slat = st.text_input("Assigned Slot Number", value=str(st.session_state.get('rec_slot', "")))
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✅ PROCESS ENTRY", use_container_width=True):
            if plat and slat:
                if ai_logic.is_suspicious(plat):
                    st.error(f"🛑 ENTRY DENIED — Vehicle {plat} is blacklisted!")
                else:
                    if parking_lot.park_vehicle(plat, vtype, slat):
                        st.success(f"✅ Vehicle {plat} parked in Slot {slat}")
                        st.balloons()
                    else:
                        st.error("Slot unavailable or already occupied.")
            else:
                st.error("Please fill Plate Number and Slot.")

    with t_out:
        st.markdown("""
        <div class="sp-section-header">
            <span class="sp-section-accent" style="background:var(--red)"></span>
            <span class="sp-section-title">Gate Exit — Checkout & Billing</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sp-card sp-card-red">', unsafe_allow_html=True)
        st.markdown('<div class="sp-card-label">EXIT PLATE NUMBER</div>', unsafe_allow_html=True)
        out_plat = st.text_input("Enter Exit Plate", placeholder="e.g. ABC-1234", label_visibility="hidden")

        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("💳 CHECKOUT & GENERATE BILL", use_container_width=True):
            if ai_logic.is_suspicious(out_plat):
                st.error(f"🛑 EXIT LOCKED — Security issues pending for {out_plat}")
            else:
                conn   = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, entry_time FROM vehicles WHERE plate_number=?", (out_plat,))
                res = cursor.fetchone()
                if res:
                    v_id, e_time = res
                    hrs = max(1, (
                        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None) -
                        datetime.datetime.strptime(e_time, '%Y-%m-%d %H:%M:%S')
                    ).total_seconds() / 3600)
                    fee = parking_lot.calculate_fee(hrs)
                    parking_lot.remove_parked_vehicle(v_id, hrs)
                    st.markdown(f"""
                    <div class="sp-card sp-card-green" style="margin-top:16px">
                        <div class="sp-card-label">✅ CHECKOUT RECEIPT</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:10px">
                            <div>
                                <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
                                            color:var(--muted);text-transform:uppercase">Plate</div>
                                <div style="font-family:'Space Mono',monospace;font-weight:700;
                                            font-size:0.9rem;letter-spacing:2px">{out_plat}</div>
                            </div>
                            <div>
                                <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
                                            color:var(--muted);text-transform:uppercase">Duration</div>
                                <div style="font-family:'Space Mono',monospace;font-weight:700;
                                            font-size:0.9rem;color:var(--yellow)">{round(hrs,1)} hrs</div>
                            </div>
                            <div>
                                <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
                                            color:var(--muted);text-transform:uppercase">Total Fee</div>
                                <div style="font-family:'Space Mono',monospace;font-weight:700;
                                            font-size:1.2rem;color:var(--green)">PKR {round(fee,2)}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"No active parking record found for {out_plat}")
                conn.close()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: AI ANALYTICS
# ══════════════════════════════════════════════════════════════
elif page == "AI Analytics":

    st.markdown("""
    <div class="sp-section-header">
        <span class="sp-section-accent" style="background:var(--yellow)"></span>
        <span class="sp-section-title">Smart AI Insights & Predictions</span>
        <span class="sp-badge sp-badge-yellow" style="margin-left:auto">7 ACTIVE MODELS</span>
    </div>
    """, unsafe_allow_html=True)

    try:
        conn    = get_db_connection()
        active  = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
        total_s = conn.execute("SELECT COUNT(*) FROM parking_slots").fetchone()[0]
        hist_c  = conn.execute("SELECT COUNT(*) FROM parking_history").fetchone()[0]
        rev     = conn.execute("SELECT COALESCE(SUM(amount),0) FROM receipts").fetchone()[0]
        conn.close()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="sp-card"><div class="sp-card-label">Currently Parked</div>
            <div class="sp-card-value">{active}</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="sp-card sp-card-green"><div class="sp-card-label">Total Slots</div>
            <div class="sp-card-value sp-card-value-green">{total_s}</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="sp-card sp-card-yellow"><div class="sp-card-label">History Records</div>
            <div class="sp-card-value sp-card-value-yellow">{hist_c}</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="sp-card sp-card-orange"><div class="sp-card-label">Total Revenue (PKR)</div>
            <div class="sp-card-value sp-card-value-orange" style="font-size:1.5rem">{round(rev,0):.0f}</div></div>""",
            unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("---")
    l, r = st.columns(2)
    with l:
        st.markdown("""
        <div class="sp-card">
            <div class="sp-card-label">📈 PEAK DEMAND FORECASTING</div>
            <div style="font-size:0.78rem;color:var(--muted);margin:6px 0 14px">
                Statistical frequency model on historical data</div>
        """, unsafe_allow_html=True)
        if st.button("▶  Run Peak Hour Model", use_container_width=True):
            result = ai_logic.predict_peak_hours()
            st.success(f"🕐 Predicted Peak: **{result}**")
        st.markdown('</div>', unsafe_allow_html=True)

    with r:
        st.markdown("""
        <div class="sp-card">
            <div class="sp-card-label">🎥 VIOLATION DETECTION</div>
            <div style="font-size:0.78rem;color:var(--muted);margin:6px 0 14px">
                Camera-based fraud & wrong parking scan</div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Scan All Cameras", use_container_width=True):
            v = ai_logic.detect_wrong_parking()
            if v:
                st.warning(f"⚠️ AI Alert: {v}")
            else:
                st.success("✅ All zones clear — no violations")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="sp-section-header">
        <span class="sp-section-accent" style="background:var(--red)"></span>
        <span class="sp-section-title">Overstay Detection</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Overstay Report", use_container_width=True):
        overstays = ai_logic.detect_overstays(0.01)
        if overstays:
            st.markdown(f'<span class="sp-badge sp-badge-red">{len(overstays)} OVERSTAYS DETECTED</span>',
                        unsafe_allow_html=True)
            st.table(overstays)
        else:
            st.success("✅ No overstays detected")

# ══════════════════════════════════════════════════════════════
# PAGE: SECURITY
# ══════════════════════════════════════════════════════════════
elif page == "Security":

    st.markdown("""
    <div class="sp-section-header">
        <span class="sp-section-accent" style="background:var(--red)"></span>
        <span class="sp-section-title">Security Watchlist & Blacklist Management</span>
        <span class="sp-badge sp-badge-red" style="margin-left:auto">🔒 RESTRICTED</span>
    </div>
    """, unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("""
        <div class="sp-card sp-card-red">
            <div class="sp-card-label">➕ ADD TO WATCHLIST</div>
        """, unsafe_allow_html=True)
        bp = st.text_input("Plate Number",     placeholder="e.g. LEB7570")
        br = st.text_input("Violation Reason", placeholder="e.g. Stolen Vehicle")
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🚫 ADD TO BLACKLIST", use_container_width=True):
            if bp and br:
                ai_logic.add_to_blacklist(bp, br)
                st.success(f"✅ {bp} added to watchlist")
                st.rerun()
            else:
                st.error("Fill both fields")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_list:
        st.markdown("""
        <div class="sp-card">
            <div class="sp-card-label">📋 CURRENT WATCHLIST</div>
        """, unsafe_allow_html=True)
        conn      = get_db_connection()
        blacklist = conn.execute("SELECT plate_number, reason FROM blacklist").fetchall()
        conn.close()

        if blacklist:
            for row in blacklist:
                plate_bl, reason_bl = row
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:10px 14px;
                            border-radius:8px;background:var(--surface2);
                            border:1px solid var(--border);margin-bottom:8px;">
                    <span style="font-family:'Space Mono',monospace;font-weight:700;
                                 letter-spacing:2px;font-size:0.88rem">{plate_bl}</span>
                    <span style="flex:1;font-size:0.75rem;color:var(--muted)">{reason_bl}</span>
                    <span class="sp-badge sp-badge-red">🚫 BLOCKED</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Watchlist is empty")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: LOGS
# ══════════════════════════════════════════════════════════════
elif page == "Logs":

    st.markdown("""
    <div class="sp-section-header">
        <span class="sp-section-accent" style="background:var(--muted)"></span>
        <span class="sp-section-title">System Event Records</span>
    </div>
    """, unsafe_allow_html=True)

    conn = get_db_connection()
    t_a, t_h = st.tabs(["🟢  Active Vehicles", "📁  Archive History"])

    with t_a:
        st.markdown("""
        <div class="sp-section-header" style="margin-top:16px">
            <span class="sp-section-accent" style="background:var(--green)"></span>
            <span class="sp-section-title" style="color:var(--green)">Currently Parked</span>
        </div>
        """, unsafe_allow_html=True)
        active_data = conn.execute(
            "SELECT plate_number, vehicle_type, slot_id, entry_time FROM vehicles"
        ).fetchall()
        if active_data:
            st.table(active_data)
        else:
            st.info("No vehicles currently parked")

    with t_h:
        st.markdown("""
        <div class="sp-section-header" style="margin-top:16px">
            <span class="sp-section-accent" style="background:var(--muted)"></span>
            <span class="sp-section-title">Last 20 Sessions</span>
        </div>
        """, unsafe_allow_html=True)
        history_data = conn.execute(
            "SELECT * FROM parking_history ORDER BY id DESC LIMIT 20"
        ).fetchall()
        if history_data:
            st.table(history_data)
        else:
            st.info("No history records yet")

    conn.close()