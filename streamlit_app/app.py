import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API = os.getenv("AURA_API_URL", "http://127.0.0.1:8010")

st.set_page_config(
    page_title="AURA | AI Customer Operations",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# AURA — Enterprise Executive UI
# Presentation layer only. Existing FastAPI/agents/RAG/governance are preserved.
# =============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{
  --navy:#061a35; --navy2:#0b2b52; --navy3:#123f70;
  --blue:#1476e8; --blue2:#2e9bff; --cyan:#59d9ff;
  --ink:#142746; --muted:#70819a; --line:#dce6f1;
  --bg:#f4f8fc; --surface:#ffffff; --green:#16b978;
  --red:#ff4e54; --amber:#e9a522; --violet:#8354ed;
}

html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{
  background:
    radial-gradient(circle at 86% 8%,rgba(42,132,239,.075),transparent 23%),
    linear-gradient(180deg,#f3f7fb 0%,#f8fafc 50%,#eef3f8 100%);
  color:var(--ink);
}
.block-container{max-width:1600px;padding:1.05rem 1.75rem 2.5rem}
[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}

/* -------------------------------------------------------------------------- */
/* Sidebar                                                                    */
/* -------------------------------------------------------------------------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#06172e 0%,#071b34 58%,#092441 100%);
  border-right:1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"]>div{padding:1rem .8rem}
.aura-brand{padding:8px 10px 20px;border-bottom:1px solid rgba(255,255,255,.10);margin-bottom:15px}
.aura-brand-row{display:flex;align-items:center;gap:10px;color:#fff;font-weight:800;font-size:1.12rem}
.aura-mark{
  width:38px;height:38px;border-radius:12px;
  background:linear-gradient(135deg,#1476e8,#59d9ff);
  display:grid;place-items:center;color:#06172e;font-weight:900;font-size:1.25rem;
  box-shadow:0 8px 25px rgba(20,118,232,.30)
}
.aura-caption{color:#8295af;font-size:.60rem;letter-spacing:.11em;text-transform:uppercase;margin-top:7px}
.side-status{
  margin:15px 2px 18px;padding:12px;border-radius:12px;
  background:linear-gradient(145deg,rgba(255,255,255,.07),rgba(255,255,255,.025));
  border:1px solid rgba(255,255,255,.10);color:#dce8f6;font-size:.70rem
}
.side-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#19c58a;margin-right:7px;box-shadow:0 0 0 4px rgba(25,197,138,.10)}
.side-nav-title{margin:16px 8px 7px;color:#607795;font-size:.56rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
section[data-testid="stSidebar"] .stButton{margin:0!important}
section[data-testid="stSidebar"] .stButton>button{
  display:flex;align-items:center;justify-content:flex-start;width:100%;
  min-height:39px;height:39px;margin:3px 0;padding:0 10px;
  border:1px solid transparent!important;border-radius:10px!important;
  background:transparent!important;color:#a9b8cb!important;box-shadow:none!important;
  font-size:.68rem!important;font-weight:650!important;text-align:left!important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(53,140,241,.10)!important;color:#fff!important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
  background:linear-gradient(90deg,rgba(45,129,233,.25),rgba(45,129,233,.10))!important;
  border-color:rgba(85,163,255,.23)!important;color:#fff!important;
}
/* Workspace selector: blue enterprise treatment instead of Streamlit default accent. */
.workspace-tabs div[data-testid="stButton"] button[kind^="primary"],
.workspace-tabs div[data-testid="stButton"] button[kind*="Primary"],
.workspace-tabs button[kind="primary"]{
  background:#1476e8!important;color:#fff!important;border:1px solid #1476e8!important;
  border-radius:9px!important;box-shadow:0 6px 16px rgba(20,118,232,.18)!important;
}
.workspace-tabs div[data-testid="stButton"] button[kind^="secondary"]{
  background:#fff!important;border:1px solid #dbe5ef!important;color:#53677f!important;
  border-radius:9px!important;
}
.workspace-tabs div[data-testid="stButton"] button[kind^="secondary"]:hover{
  background:#f3f8fe!important;color:#1476e8!important;border-color:#bcd8f5!important;
}
.side-glyph{
  display:inline-grid;place-items:center;width:23px;height:23px;margin-right:8px;
  border-radius:7px;background:rgba(255,255,255,.06);color:#77baff;font-size:.72rem
}
.side-note{
  margin:22px 4px 0;padding:14px 10px;border:1px solid rgba(91,169,255,.16);
  border-radius:12px;background:rgba(45,129,233,.07);color:#9fb2ca;font-size:.64rem;line-height:1.55
}
.side-note b{color:#d9e9fb}
.side-foot{position:fixed;bottom:14px;color:#58708e;font-size:.57rem}

/* -------------------------------------------------------------------------- */
/* Hero                                                                      */
/* -------------------------------------------------------------------------- */
.hero{
  position:relative;overflow:hidden;min-height:205px;border-radius:21px;
  margin:0 0 15px;padding:28px 38px;color:#fff;
  background:
    radial-gradient(circle at 88% 52%,rgba(69,176,255,.28),transparent 25%),
    linear-gradient(105deg,#06182f 0%,#0b2b52 58%,#174c82 100%);
  box-shadow:0 18px 50px rgba(9,36,69,.20);
}
.hero-copy{position:relative;z-index:4;max-width:990px}
.hero-eyebrow{font-size:.59rem;letter-spacing:.19em;text-transform:uppercase;color:#9bb4d0;font-weight:800}
.hero-kicker{font-size:.92rem;font-weight:600;color:#eef7ff;margin:8px 0 5px}
.hero h1{
  font-family:'Space Grotesk',sans-serif;font-size:2.12rem;line-height:1.08;
  margin:0 0 10px;letter-spacing:-.045em;color:#fff
}
.hero p{margin:0;max-width:930px;font-size:.72rem;line-height:1.55;color:#c9d8e8}
.hero-pills{display:flex;gap:7px;flex-wrap:wrap;margin-top:15px}
.pill{
  padding:6px 10px;border:1px solid rgba(255,255,255,.15);border-radius:999px;
  background:rgba(255,255,255,.055);color:#e1edf9;font-size:.57rem
}
.live-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#19c58a;margin-right:6px;box-shadow:0 0 0 4px rgba(25,197,138,.10)}
.hero-meta{
  position:absolute;right:25px;top:17px;z-index:4;text-align:right;color:#cfe0f1;
  font-size:.59rem;line-height:1.7
}
.hero-meta .online{font-size:.76rem;font-weight:800;color:#fff}
.hero-meta .online span{color:#16c27f;font-size:1.0rem;vertical-align:-1px}
.hero-meta .rule{width:35px;height:2px;background:#1985ee;margin:5px 0 3px auto}

/* Lighthouse illustration */
.lighthouse-wrap{position:absolute;right:80px;bottom:-3px;width:190px;height:195px;z-index:2;opacity:.96}
.lh-glow{
  position:absolute;left:45px;top:25px;width:125px;height:75px;
  background:linear-gradient(90deg,rgba(255,255,255,0),rgba(222,244,255,.26),rgba(255,255,255,0));
  transform:skewY(-15deg);filter:blur(1px)
}
.lh-beam{
  position:absolute;left:66px;top:23px;width:175px;height:3px;
  background:linear-gradient(90deg,rgba(255,255,255,.95),rgba(101,207,255,.25),transparent);
  transform:rotate(-17deg);transform-origin:left center;box-shadow:0 0 16px rgba(151,226,255,.45)
}
.lh-tower{
  position:absolute;left:78px;bottom:18px;width:32px;height:118px;
  background:linear-gradient(90deg,#dbe5ed 0%,#fff 35%,#9eafc0 100%);
  clip-path:polygon(17% 0,83% 0,100% 100%,0 100%);box-shadow:0 0 12px rgba(0,0,0,.18)
}
.lh-stripe{position:absolute;left:76px;bottom:58px;width:37px;height:15px;background:#0a315b;transform:skewY(-7deg)}
.lh-balcony{position:absolute;left:69px;bottom:132px;width:50px;height:7px;border-radius:4px;background:#102f51;box-shadow:0 -4px 0 -2px #102f51}
.lh-top{position:absolute;left:74px;bottom:138px;width:41px;height:32px;background:linear-gradient(180deg,#173c63,#092441);border-radius:9px 9px 3px 3px}
.lh-light{position:absolute;left:89px;bottom:151px;width:11px;height:11px;border-radius:50%;background:#fff6bd;box-shadow:0 0 20px 7px rgba(255,241,165,.35)}
.lh-roof{position:absolute;left:70px;bottom:168px;width:49px;height:10px;background:#071b33;clip-path:polygon(50% 0,100% 100%,0 100%)}
.lh-ground{position:absolute;left:32px;bottom:0;width:135px;height:25px;background:linear-gradient(180deg,#163b62,#06172d);border-radius:50% 50% 0 0}

/* -------------------------------------------------------------------------- */
/* KPI cards                                                                  */
/* -------------------------------------------------------------------------- */
.kpi{
  position:relative;background:#fff;border:1px solid #dfe8f1;border-radius:13px;
  padding:12px 13px 11px;min-height:103px;overflow:hidden;
  box-shadow:0 8px 24px rgba(20,50,85,.055)
}
.kpi:after{content:"";position:absolute;left:0;bottom:0;width:40px;height:2px;background:#2c9bff}
.kpi-top{display:flex;justify-content:space-between;align-items:center}
.kpi-label{color:#73849b;font-size:.58rem;font-weight:700}
.kpi-icon{
  width:31px;height:31px;border-radius:9px;background:#edf6ff;color:#1476e8;
  display:grid;place-items:center;font-size:.95rem
}
.kpi-value{font-family:'Space Grotesk',sans-serif;color:#112846;font-size:1.42rem;line-height:1;margin-top:8px;font-weight:700;letter-spacing:-.04em}
.kpi-note{font-size:.59rem;color:#8999ad;margin-top:6px}
.kpi-impact{font-size:.60rem;color:#159d6d;font-weight:700;margin-top:6px}

/* -------------------------------------------------------------------------- */
/* Tabs / sections                                                            */
/* -------------------------------------------------------------------------- */
.workspace-tabs{display:flex;gap:0;border-bottom:1px solid #d7e1eb;margin:13px 0 16px}
.workspace-tabs .stButton{flex:1}
.workspace-tabs .stButton>button{
  border:none!important;border-radius:0!important;background:transparent!important;
  color:#566a84!important;box-shadow:none!important;min-height:42px;height:42px;
  font-size:.67rem!important;font-weight:650!important
}
.workspace-tabs .stButton>button:hover{color:#1476e8!important;background:#f7fbff!important}
.workspace-tabs .stButton>button[kind="primary"]{
  color:#1476e8!important;border-bottom:3px solid #1476e8!important;background:#fff!important
}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;letter-spacing:-.025em;color:#142746;margin:2px 0 3px}
.section-subtitle{font-size:.62rem;color:#8797ab;margin-bottom:11px}
.micro{font-size:.55rem;color:#8293a8;text-transform:uppercase;letter-spacing:.10em;font-weight:800}
.panel{
  background:#fff;border:1px solid #dfe8f1;border-radius:13px;padding:16px;
  box-shadow:0 8px 25px rgba(20,50,85,.045)
}
.assumption{color:#73849a;font-size:.58rem;line-height:1.45;padding:8px 10px;background:#f8fbfe;border-radius:8px;border:1px solid #e3ebf3}

/* -------------------------------------------------------------------------- */
/* Root causes                                                                */
/* -------------------------------------------------------------------------- */
.chart-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:11px}
.filter-pill{padding:6px 9px;border:1px solid #d9e5f0;border-radius:8px;color:#647891;background:#fbfdff;font-size:.58rem}
.root-row{margin:11px 0 14px}
.root-head{display:flex;justify-content:space-between;font-size:.63rem;font-weight:700;color:#43566f;margin-bottom:5px}
.root-track{height:9px;background:#edf2f7;border-radius:99px;overflow:hidden}
.root-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#1476e8,#4cc8ff)}
.insight{
  display:flex;gap:10px;align-items:flex-start;margin-top:14px;padding:11px 12px;
  border-radius:9px;background:#edf7ff;border:1px solid #d2e9ff;color:#315f91;font-size:.61rem;line-height:1.45
}
.insight-icon{font-size:1rem;color:#1476e8}

/* -------------------------------------------------------------------------- */
/* Value case                                                                 */
/* -------------------------------------------------------------------------- */
.value-title{display:flex;gap:9px;align-items:center}
.value-icon{width:34px;height:34px;border-radius:9px;background:#eef7ff;color:#1476e8;display:grid;place-items:center;font-size:1.0rem}
.value-hero{
  margin-top:10px;padding:13px;border-radius:10px;background:linear-gradient(135deg,#eaf5ff,#f7fbff);
  border:1px solid #d3e8fb
}
.big-number{font-family:'Space Grotesk',sans-serif;font-size:1.65rem;font-weight:700;letter-spacing:-.04em;color:#12315b}
.value-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:9px}
.value-stat{border:1px solid #dfe7ef;border-radius:9px;padding:11px;background:#fff}
.value-stat .v{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:#132a48}
.value-stat .l{font-size:.55rem;color:#8292a6;margin-top:3px}

/* Feature strip */
.feature-strip{margin-top:13px;padding:12px 7px;background:#fff;border:1px solid #dfe8f1;border-radius:12px}
.feature{padding:3px 13px;border-right:1px solid #e1e8ef;min-height:48px}
.feature:last-child{border-right:none}
.feature-icon{color:#1476e8;font-size:1.0rem}
.feature-title{font-size:.62rem;font-weight:750;color:#27415f;margin-top:2px}
.feature-text{font-size:.54rem;color:#8191a5;margin-top:2px}

/* Case / governance */
.case-banner{padding:13px 15px;border-radius:11px;background:linear-gradient(135deg,#081a31,#10375f);color:#e4f0fb;margin-bottom:11px}
.case-banner .id{font-size:.55rem;color:#9cb3cc;letter-spacing:.08em;text-transform:uppercase}
.case-banner .title{font-family:'Space Grotesk',sans-serif;font-size:.95rem;font-weight:700;margin-top:3px}
.trace{padding:10px 12px;border:1px solid #e0e8f0;border-left:3px solid #1476e8;background:#fff;border-radius:9px;margin-bottom:6px}
.trace b{font-size:.64rem}.trace .detail{font-size:.61rem;color:#52657e;line-height:1.4}.trace .small{font-size:.53rem;color:#9aa8b8}
.evidence{padding:8px 10px;background:#f7faff;border:1px solid #e0e9f2;border-radius:8px;margin:5px 0;color:#344b67;font-size:.61rem}
.successbox,.warnbox{padding:11px 12px;border-radius:9px;line-height:1.45;font-size:.61rem}
.successbox{background:#ebfaf4;border:1px solid #bcebd7;color:#08734e}
.warnbox{background:#fff7e8;border:1px solid #f1d291;color:#8e5b0a}

/* Evaluation */
.eval-score{padding:14px;border-radius:11px;background:linear-gradient(135deg,#071a31,#103b66);color:#fff}
.eval-score .n{font-family:'Space Grotesk',sans-serif;font-size:1.65rem;font-weight:700}
.eval-score .l{font-size:.53rem;color:#b5c8dd;text-transform:uppercase;letter-spacing:.08em;margin-top:3px}
.eval-item{padding:9px 10px;border:1px solid #e1e8f0;border-radius:8px;background:#fff;margin:5px 0;font-size:.61rem;color:#41546b}
.eval-check{color:#16a970;font-weight:800;margin-right:6px}

/* Streamlit controls */
.stButton>button{border-radius:8px;font-weight:750;min-height:38px}
.stTextInput input,.stTextArea textarea,.stNumberInput input{border-radius:8px}
div[data-testid="stMetric"]{background:#fff;border:1px solid #dfe7ef;border-radius:10px;padding:9px 10px}
.footer{
  color:#93a1b3;font-size:.53rem;text-align:center;margin-top:20px;padding-top:11px;
  border-top:1px solid #dfe6ee
}
/* Final executive navigation polish */
.workspace-tabs > div[data-testid="column"]{min-width:0}
.workspace-tabs div[data-testid="stButton"] button{
  transition:all .18s ease!important;
  letter-spacing:-.01em!important;
}
.workspace-tabs div[data-testid="stButton"] button[kind="secondary"]{
  box-shadow:0 1px 2px rgba(20,45,75,.03)!important;
}
.workspace-tabs div[data-testid="stButton"] button[kind="secondary"]:hover{
  transform:translateY(-1px);
}
@media(max-width:1050px){
  .block-container{padding-left:1rem;padding-right:1rem}
  .hero h1{font-size:1.65rem}.hero-meta,.lighthouse-wrap{display:none}
  .value-grid{grid-template-columns:1fr}
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# API helpers
# =============================================================================
def get(path, **kwargs):
    return requests.get(f"{API}{path}", timeout=15, **kwargs)


def post(path, **kwargs):
    return requests.post(f"{API}{path}", timeout=60, **kwargs)


def safe_json(path, fallback=None):
    try:
        r = get(path)
        return r.json() if r.ok else (fallback if fallback is not None else {})
    except Exception:
        return fallback if fallback is not None else {}


def fmt_cr(value):
    try:
        return f"₹{float(value) / 1e7:.2f} Cr"
    except Exception:
        return "₹0.00 Cr"


def fmt_lakh(value):
    try:
        return f"₹{float(value) / 1e5:.0f} lakh"
    except Exception:
        return "₹0 lakh"


def api_ready():
    try:
        r = get("/ready")
        return r.ok and r.json().get("status") == "ready"
    except Exception:
        return False


# =============================================================================
# Connectivity + navigation
# =============================================================================
PAGES = [
    ("Executive Control Tower", "▣"),
    ("AI Resolution Center", "♙"),
    ("Governance & Audit", "◈"),
    ("Operational Intelligence", "◌"),
    ("AI Evaluation", "✓"),
]

if "aura_page" not in st.session_state:
    st.session_state.aura_page = PAGES[0][0]

# Sidebar
st.sidebar.markdown(
    """
<div class="aura-brand">
  <div class="aura-brand-row"><span class="aura-mark">A</span><span>AURA</span></div>
  <div class="aura-caption">AI Customer Operations</div>
</div>
<div class="side-status">
  <span class="side-dot"></span><b>Control Tower Online</b><br>
  <span style="color:#7186a1">Governed AI · Demo Environment</span>
</div>
<div class="side-nav-title">Workspace</div>
""",
    unsafe_allow_html=True,
)

for label, glyph in PAGES:
    active = st.session_state.aura_page == label
    if st.sidebar.button(
        f"{glyph}   {label}",
        key=f"side_{label}",
        type="primary" if active else "secondary",
        width="stretch",
    ):
        st.session_state.aura_page = label
        st.rerun()

st.sidebar.markdown(
    """
<div class="side-note">
<b>Built for what's next.</b><br>
Human-centered.<br>
AI-powered.<br>
Business-driven.
</div>
""",
    unsafe_allow_html=True,
)

ready = api_ready()
api_badge = (
    '<span style="color:#16b978">● API READY</span>'
    if ready
    else '<span style="color:#ff747a">● API OFFLINE</span>'
)
st.sidebar.markdown(
    f'<div style="margin-top:14px">{api_badge}</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown('<div class="side-foot">NexaCommerce · AURA v2.0 · Synthetic data</div>', unsafe_allow_html=True)

# Hero
now_label = datetime.now().strftime("%d %b %Y · %H:%M")
st.markdown(
    f"""
<div class="hero">
  <div class="hero-copy">
    <div class="hero-eyebrow">NexaCommerce · AI Operations Intelligence</div>
    <div class="hero-kicker">From Issues to Insights. From Support to Strategic Impact.</div>
    <h1>AURA — AI Customer Operations Control Tower</h1>
    <p>Agentic resolution · policy-grounded decisions · human-in-the-loop governance · operational intelligence — designed for measurable customer-operations transformation.</p>
    <div class="hero-pills">
      <span class="pill"><span class="live-dot"></span>Control Tower Online</span>
      <span class="pill">Governed AI</span>
      <span class="pill">Measurable Impact</span>
      <span class="pill">Better Customer Outcomes</span>
    </div>
  </div>
  <div class="hero-meta">
    <div class="online">CONTROL TOWER <span>●</span> ONLINE</div>
    <div>Governed AI &nbsp;|&nbsp; Measurable Impact</div>
    <div>Better Customer Outcomes</div>
    <div class="rule"></div>
    <div>{now_label} IST</div>
  </div>
  <div class="lighthouse-wrap">
    <div class="lh-glow"></div><div class="lh-beam"></div>
    <div class="lh-tower"></div><div class="lh-stripe"></div>
    <div class="lh-balcony"></div><div class="lh-top"></div>
    <div class="lh-light"></div><div class="lh-roof"></div><div class="lh-ground"></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if not ready:
    st.error(f"AURA API is unavailable at {API}. Start FastAPI on port 8010 and refresh.")
    st.stop()

# KPI strip
kpi = safe_json("/api/v1/analytics/kpis", {})
metrics = [
    ("Annual customer cases", f"{kpi.get('enterprise_annual_interactions', 0):,}", "Enterprise scale", "♧"),
    ("AI opportunity", f"{kpi.get('ai_automation_hypothesis_pct', 0)}%", "Automatable cases", "◎"),
    ("AHT target", f"↓ {kpi.get('target_aht_reduction_pct', 0)}%", "Faster resolution", "◷"),
    ("Annual cost pool", fmt_cr(kpi.get("enterprise_annual_cost_pool_inr", 0)), "Significant savings potential", "₹"),
    ("Demo cases", str(kpi.get("demo_ticket_volume", 0)), "For live demonstration", "⚗"),
]
cols = st.columns(5, gap="small")
for col, (label, value, note, icon) in zip(cols, metrics):
    with col:
        st.markdown(
            f"""
<div class="kpi">
  <div class="kpi-top"><div class="kpi-label">{label}</div><div class="kpi-icon">{icon}</div></div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-note">{note}</div>
  <div class="kpi-impact">↗ Business impact</div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div class="assumption" style="margin:9px 0 12px">{kpi.get("modeling_note", "Enterprise figures are scenario assumptions; demo counts are synthetic.")}</div>',
    unsafe_allow_html=True,
)

# Horizontal workspace tabs — executive workspace switcher.
st.markdown('<div class="workspace-tabs">', unsafe_allow_html=True)
tab_cols = st.columns(5, gap="small")
for col, (label, glyph) in zip(tab_cols, PAGES):
    with col:
        # Keep all buttons neutral; the active state is rendered explicitly below
        # so Streamlit's default red primary accent never leaks into the product UI.
        if st.button(
            label,
            key=f"top_{label}",
            type="secondary",
            width="stretch",
        ):
            st.session_state.aura_page = label
            st.rerun()

# Product-style active indicator.
indicator_cols = st.columns(5, gap="small")
for col, (label, _glyph) in zip(indicator_cols, PAGES):
    with col:
        if st.session_state.aura_page == label:
            st.markdown('<div style="height:3px;background:#1476e8;border-radius:3px;margin:-5px 10px 0"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="height:3px;background:transparent;margin:-5px 10px 0"></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

page = st.session_state.aura_page

st.markdown(
    f'<div style="display:flex;justify-content:space-between;align-items:center;margin:-4px 0 10px;color:#8292a6;font-size:.56rem;letter-spacing:.02em"><span>Workspace · {page}</span><span>Governed AI · Synthetic demonstration environment</span></div>',
    unsafe_allow_html=True,
)

# =============================================================================
# Executive Control Tower
# =============================================================================
if page == "Executive Control Tower":
    st.markdown('<div class="section-title">Executive Control Tower</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">A single operating view across customer impact, root causes, AI decisioning and value realization.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.22, .78], gap="medium")

    with left:
        roots = safe_json("/api/v1/analytics/root-causes", [])
        df = pd.DataFrame(roots if isinstance(roots, list) else [])

        st.markdown(
            """
<div class="panel">
  <div class="chart-head">
    <div>
      <div class="value-title">
        <div class="value-icon">▥</div>
        <div><div class="section-title" style="margin:0">Operational root causes</div>
        <div class="section-subtitle" style="margin:3px 0 0">Top drivers of customer issues · demonstration dataset</div></div>
      </div>
    </div>
    <div class="filter-pill">Last 30 days⌄</div>
  </div>
""",
            unsafe_allow_html=True,
        )

        if not df.empty and "root_cause" in df.columns:
            value_col = "cases" if "cases" in df.columns else ("count" if "count" in df.columns else None)
            if value_col:
                numeric = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
                max_count = max(int(numeric.max()), 1)
                sorted_df = df.assign(_v=numeric).sort_values("_v", ascending=False)
                for _, row in sorted_df.iterrows():
                    label = str(row["root_cause"]).replace("_", " ").title()
                    count = int(pd.to_numeric(pd.Series([row[value_col]]), errors="coerce").fillna(0).iloc[0])
                    pct = max(4, int(count / max_count * 100))
                    st.markdown(
                        f"""
<div class="root-row">
  <div class="root-head"><span>{label}</span><span>{count}</span></div>
  <div class="root-track"><div class="root-fill" style="width:{pct}%"></div></div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                # Executive insight based only on the returned dataset.
                top_labels = sorted_df.head(2)["root_cause"].astype(str).str.replace("_", " ").str.title().tolist()
                if len(top_labels) >= 2:
                    insight_text = f"{top_labels[0]} and {top_labels[1]} are the leading concentration signals in the current synthetic operating dataset."
                elif top_labels:
                    insight_text = f"{top_labels[0]} is the leading concentration signal in the current synthetic operating dataset."
                else:
                    insight_text = "No concentration signal is available."
                st.markdown(
                    f'<div class="insight"><div class="insight-icon">◉</div><div><b>Executive insight</b><br>{insight_text} Use these signals to prioritize targeted intervention rather than case-by-case firefighting.</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("Root-cause response did not contain a recognized volume field.")
        else:
            st.info("No root-cause data returned.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
<div class="panel">
  <div class="value-title">
    <div class="value-icon">▥</div>
    <div><div class="section-title" style="margin:0">Value case</div>
    <div class="section-subtitle" style="margin:3px 0 0">Business impact based on scenario economics</div></div>
  </div>
""",
            unsafe_allow_html=True,
        )

        efficiency = st.slider("Efficiency improvement", 5, 50, 20, key="target_efficiency")
        investment_lakh = st.slider(
            "Program investment (₹ lakh)", 10, 200, 60, 5, key="target_investment"
        )
        investment = investment_lakh * 100000

        try:
            roi = post(
                "/api/v1/analytics/roi",
                json={
                    "annual_interactions": 600000,
                    "cost_per_interaction_inr": 180,
                    "efficiency_improvement_pct": efficiency,
                    "annual_investment_inr": investment,
                },
            ).json()
        except Exception:
            roi = {}

        st.markdown(
            f"""
<div class="value-hero">
  <div class="micro">Program investment</div>
  <div class="big-number">{fmt_lakh(investment)}</div>
  <div class="muted">Adjustable scenario input · {investment_lakh:.0f} lakh</div>
</div>
<div class="value-hero" style="margin-top:8px">
  <div class="micro">Annual benefit</div>
  <div class="big-number">{fmt_cr(roi.get("annual_benefit_inr", 0))}</div>
  <div class="muted">Cost savings per year at {efficiency}% modeled efficiency improvement</div>
</div>
<div class="value-grid">
  <div class="value-stat"><div class="v">{roi.get("simple_roi_pct", 0):.0f}%</div><div class="l">Simple ROI</div></div>
  <div class="value-stat"><div class="v">{roi.get("payback_months", 0):.1f} mo</div><div class="l">Payback</div></div>
  <div class="value-stat"><div class="v">{investment_lakh:.0f}L</div><div class="l">Investment</div></div>
</div>
<div class="assumption" style="margin-top:9px"><b>Scenario economics:</b> illustrative only; replace with validated finance inputs before investment decisions.</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="feature-strip">
""",
        unsafe_allow_html=True,
    )
    feature_cols = st.columns(4, gap="small")
    features = [
        ("♢", "Policy-grounded AI", "Evidence-based, compliant and auditable"),
        ("♙", "Human-in-the-loop", "Higher-risk decisions under human control"),
        ("⚙", "Operational intelligence", "From individual cases to systemic improvement"),
        ("⌁", "Measurable business impact", "Efficiency, cost savings and better CX"),
    ]
    for c, (icon, title, desc) in zip(feature_cols, features):
        with c:
            st.markdown(
                f'<div class="feature"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-text">{desc}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# Resolution Center
# =============================================================================
elif page == "AI Resolution Center":
    st.markdown('<div class="section-title">AI Resolution Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Investigate → ground → reason → govern → act. Every decision remains explainable.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([.78, 1.22], gap="medium")
    with left:
        st.markdown('<div class="panel"><div class="micro">Case intake</div><div class="section-title" style="margin-top:4px">Customer issue</div>', unsafe_allow_html=True)
        customer_id = st.text_input("Customer ID", "C10001")
        message = st.text_area(
            "Customer message",
            "My ₹85,000 order was supposed to arrive last week. I've contacted support twice and nobody has helped me.",
            height=125,
        )
        if st.button("Run AURA Investigation", type="primary", width="stretch"):
            try:
                r = post("/api/v1/cases/resolve", json={"customer_id": customer_id, "message": message})
                if r.ok:
                    st.session_state["case"] = r.json()
                else:
                    st.error(r.text)
            except Exception as exc:
                st.error(str(exc))
        st.markdown(
            '<div class="muted" style="margin-top:9px">Demo path: C10001 → delayed ₹85,000 order → ₹750 goodwill. Then test ₹5,000 refund to demonstrate human approval.</div></div>',
            unsafe_allow_html=True,
        )

    with right:
        case = st.session_state.get("case")
        if not case:
            st.markdown(
                """
<div class="panel">
  <div class="micro">Decision workspace</div>
  <div class="section-title" style="margin-top:4px">Awaiting AI investigation</div>
  <div class="muted">Submit a customer case to activate the governed resolution workspace.</div>
  <div class="flow" style="display:flex;align-items:center;gap:7px;margin-top:18px">
    <div class="flow-node" style="flex:1;text-align:center;padding:11px 5px;border:1px solid #dfe7ef;border-radius:9px"><div>◌</div><b style="font-size:.57rem">Intake</b></div>
    <div>→</div>
    <div class="flow-node" style="flex:1;text-align:center;padding:11px 5px;border:1px solid #dfe7ef;border-radius:9px"><div>⌁</div><b style="font-size:.57rem">Investigate</b></div>
    <div>→</div>
    <div class="flow-node" style="flex:1;text-align:center;padding:11px 5px;border:1px solid #dfe7ef;border-radius:9px"><div>◈</div><b style="font-size:.57rem">Govern</b></div>
    <div>→</div>
    <div class="flow-node" style="flex:1;text-align:center;padding:11px 5px;border:1px solid #dfe7ef;border-radius:9px"><div>✓</div><b style="font-size:.57rem">Act</b></div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="case-banner"><div class="id">AURA case · {case.get("case_id", "—")}</div><div class="title">Governed decision workspace</div></div>',
                unsafe_allow_html=True,
            )
            a, b, c, d = st.columns(4)
            a.metric("Priority", str(case.get("priority", "unknown")).upper())
            try:
                conf = float(case.get("confidence", 0)) * 100
            except Exception:
                conf = 0
            b.metric("Confidence", f"{conf:.0f}%")
            c.metric("Compensation", f'₹{float(case.get("recommended_compensation_inr", 0)):,.0f}')
            d.metric("Action", str(case.get("action_status", "unknown")).replace("_", " ").title())

            if case.get("approval_required"):
                st.markdown(
                    '<div class="warnbox"><b>HUMAN APPROVAL REQUIRED</b><br>Governance has blocked autonomous execution for this decision.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="successbox"><b>AUTONOMOUS EXECUTION ALLOWED</b><br>Decision is within configured policy and execution thresholds.</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div class="panel" style="margin-top:8px"><div class="micro">Decision rationale</div><div style="font-size:.68rem;font-weight:750;margin-top:5px">Root cause: {case.get("root_cause","Not identified")}</div><div class="muted" style="margin-top:7px">{case.get("resolution","—")}</div></div>',
                unsafe_allow_html=True,
            )

    case = st.session_state.get("case")
    if case:
        st.markdown(
            '<div class="panel" style="margin-top:12px"><div class="micro">Explainability</div><div class="section-title" style="margin-top:4px">Agent investigation trace</div><div class="section-subtitle">Transparent agent-by-agent execution path.</div>',
            unsafe_allow_html=True,
        )
        for item in case.get("trace", []):
            status = str(item.get("status", "")).lower()
            icon = "✓" if status in {"complete", "passed", "executed"} else "•"
            st.markdown(
                f'<div class="trace"><b><span style="color:#16b978">{icon}</span> {item.get("step","—")}. {item.get("agent","Agent")}</b><div class="detail">{item.get("detail","")}</div><span class="small">{item.get("timestamp","")}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="micro" style="margin-top:15px">Grounding evidence</div>', unsafe_allow_html=True)
        for evidence in case.get("evidence", []):
            st.markdown(f'<div class="evidence">✓ {evidence}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# Governance & Audit
# =============================================================================
elif page == "Governance & Audit":
    case = st.session_state.get("case")
    st.markdown('<div class="section-title">Governance & Audit</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Deterministic controls remain authoritative over autonomous execution.</div>',
        unsafe_allow_html=True,
    )
    if not case:
        st.markdown(
            '<div class="panel"><div class="micro">Governance workspace</div><div class="section-title" style="margin-top:4px">No active case</div><div class="muted">Run a case in AI Resolution Center to inspect governance and audit history.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        gov = case.get("governance", {})
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Risk", str(gov.get("risk_level", "unknown")).upper())
        g2.metric("Autonomous limit", f'₹{float(gov.get("autonomous_limit_inr", 0)):,.0f}')
        g3.metric("Policy grounded", "YES" if gov.get("policy_grounded") else "NO")
        g4.metric("Decision", str(gov.get("decision", "unknown")).replace("_", " ").title())

        st.markdown('<div class="panel" style="margin-top:11px">', unsafe_allow_html=True)
        if case.get("approval_required"):
            st.markdown(
                '<div class="warnbox"><b>HUMAN REVIEW REQUIRED</b><br>Compensation exceeds the autonomous threshold or confidence is below the configured execution threshold.</div>',
                unsafe_allow_html=True,
            )
            approver = st.text_input("Approver", "Operations Manager")
            comment = st.text_input("Approval comment", "Validated against policy and evidence.")
            a, b = st.columns(2)
            if a.button("Approve & execute", type="primary", width="stretch"):
                r = post(
                    f'/api/v1/cases/{case["case_id"]}/approve',
                    json={"approver": approver, "comment": comment},
                )
                if r.ok:
                    st.session_state["case"] = r.json()
                    st.rerun()
                else:
                    st.error(r.text)
            if b.button("Reject & escalate", width="stretch"):
                r = post(
                    f'/api/v1/cases/{case["case_id"]}/reject',
                    json={"approver": approver, "comment": comment},
                )
                if r.ok:
                    st.session_state["case"] = r.json()
                    st.rerun()
                else:
                    st.error(r.text)
        else:
            st.markdown(
                '<div class="successbox"><b>AUTONOMOUS EXECUTION ALLOWED</b><br>The decision is within policy and configured confidence/compensation thresholds.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="micro" style="margin-top:16px">Immutable decision history</div>', unsafe_allow_html=True)
        try:
            audit = get(f'/api/v1/cases/{case["case_id"]}/audit').json().get("events", [])
            st.dataframe(pd.DataFrame(audit), width="stretch", hide_index=True)
        except Exception as exc:
            st.error(str(exc))
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# Operational Intelligence
# =============================================================================
elif page == "Operational Intelligence":
    st.markdown('<div class="section-title">Operational Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Move from individual case resolution to systemic operational improvement.</div>',
        unsafe_allow_html=True,
    )
    insight = safe_json("/api/v1/analytics/insights", {})
    a, b, c = st.columns(3)
    a.metric("Delayed shipments", insight.get("delayed_shipments", 0))
    b.metric("Top carrier share", f'{insight.get("top_carrier_share_pct", 0)}%')
    c.metric("Top hub share", f'{insight.get("top_hub_share_pct", 0)}%')

    st.markdown('<div class="panel" style="margin-top:11px">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="micro">Concentration signal</div><div class="section-title" style="margin-top:4px">{insight.get("top_carrier","Unknown")} · {insight.get("top_hub","Unknown")}</div><div class="muted">{insight.get("top_carrier","Unknown")} is the leading delayed-shipment carrier; {insight.get("top_hub","Unknown")} is the highest-concentration hub in the synthetic dataset.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="insight" style="margin-top:11px"><div class="insight-icon">↗</div><div><b>AI recommendation</b><br>{insight.get("recommendation","No recommendation returned.")}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="micro" style="margin-top:17px">Ask AURA</div><div class="muted" style="margin-bottom:7px">Translate operational data into an executive-ready answer.</div>',
        unsafe_allow_html=True,
    )
    question = st.text_input(
        "Operational question",
        "Why are delivery escalations happening?",
        label_visibility="collapsed",
    )
    if st.button("Generate business insight", width="content"):
        try:
            r = post("/api/v1/analytics/ask", json={"question": question})
            if r.ok:
                answer = r.json()
                st.markdown(
                    f'<div class="value-hero" style="margin-top:9px"><div class="micro">AURA answer</div><div style="font-size:.67rem;line-height:1.55;margin-top:5px">{answer.get("answer","")}</div><div class="muted" style="margin-top:7px">Grounding mode: {answer.get("mode")} · Confidence: {float(answer.get("confidence",0))*100:.0f}%</div></div>',
                    unsafe_allow_html=True,
                )
                if answer.get("recommendation"):
                    st.success(answer.get("recommendation"))
            else:
                st.error(r.text)
        except Exception as exc:
            st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# AI Evaluation
# =============================================================================
elif page == "AI Evaluation":
    st.markdown('<div class="section-title">AI Evaluation Command Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Controlled synthetic benchmark for portfolio demonstration — not a production accuracy claim.</div>',
        unsafe_allow_html=True,
    )

    if "eval_result" not in st.session_state:
        st.session_state.eval_result = None

    if st.button("Run 30-case benchmark", type="primary", width="content"):
        try:
            r = get("/api/v1/evaluation/run")
            if r.ok:
                st.session_state.eval_result = r.json()
            else:
                st.error(r.text)
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.eval_result
    if result:
        a, b, c, d = st.columns(4)
        for col, value, label in [
            (a, result.get("benchmark_cases", 0), "Benchmark cases"),
            (b, f'{result.get("classification_accuracy_pct", 0)}%', "Classification accuracy"),
            (c, "PASS" if result.get("governance_gate_pass") else "REVIEW", "Governance gate"),
            (d, "READY" if result.get("governance_gate_pass") else "REVIEW", "Evaluation status"),
        ]:
            with col:
                st.markdown(
                    f'<div class="eval-score"><div class="n">{value}</div><div class="l">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        left, right = st.columns(2, gap="medium")
        with left:
            st.markdown('<div class="panel" style="margin-top:10px"><div class="micro">Evaluation controls</div><div class="section-title" style="margin-top:4px">Quality gates</div>', unsafe_allow_html=True)
            for item in [
                "Intent classification",
                "Sentiment classification",
                "Priority classification",
                "Governance threshold",
                "Policy grounding",
            ]:
                st.markdown(f'<div class="eval-item"><span class="eval-check">✓</span>{item}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel" style="margin-top:10px"><div class="micro">Evaluation sample</div><div class="section-title" style="margin-top:4px">Representative benchmark rows</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(result.get("sample_rows", [])), width="stretch", hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
<div class="panel">
  <div style="padding:24px 15px;text-align:center;border:1px dashed #d7e1eb;border-radius:10px;background:#fbfdff">
    <div style="font-size:1.5rem;color:#1476e8">✓</div>
    <div style="font-size:.75rem;font-weight:750;margin-top:5px">Evaluation harness ready</div>
    <div class="muted" style="margin-top:4px">Run the benchmark to validate classification and governance controls.</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="footer">AURA v2.0 · AI Unified Resolution & Analytics · Portfolio demonstration · Synthetic operational data · Governed AI · Not for production use</div>',
    unsafe_allow_html=True,
)
