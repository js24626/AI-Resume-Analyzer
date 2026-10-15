"""Resume Analyzer & Job Matcher.

Marketing-style layout: navy hero with a swap-ready image slot, white detail
sections, an FAQ that opens and closes smoothly, and a navy footer.

Swap the hero image by setting HERO_IMAGE below.
"""

import html
import json

import streamlit as st

from parser import extract_text_from_pdf
from analyzer import extract_resume_data, extract_job_requirements, calculate_match


HERO_IMAGE = "assests/hero.avif"  # or None to leave the slot empty

AUTHOR = "Hassan Mehmood"
BRAND = "Resume Analyzer & Job Matcher"

st.set_page_config(page_title="Resume Analyzer & Job Matcher", layout="wide")

# --------------------------------------------------------------------------- #
# Theme
# --------------------------------------------------------------------------- #
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=Inter:wght@400;500;600;700&display=swap');

/* =====================================================================
   1. BASE PALETTE
   ===================================================================== */
:root, .stApp, [data-testid="stAppViewContainer"] {
    --background-color: #ffffff !important;
    --secondary-background-color: #f7f9fb !important;
    --text-color: #0a2540 !important;
    --primary-color: #00828a !important;
    color-scheme: light;
    interpolate-size: allow-keywords;
    scroll-behavior: smooth;

    --navy: #0a2540;
    --navy-deep: #06192b;
    --teal: #00828a;
    --teal-dark: #00676e;
    --gold: #f3be4d;
    --cream: #fbf8f2;
    --mint: #e1f2f0;
    --ink: #0a2540;
    --muted: #4a5d6e;
    --line: #e6e9ee;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background-color: #ffffff !important;
}
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

/* Hide chrome. The header itself stays rendered: it holds the sidebar toggle. */
#MainMenu, [data-testid="stMainMenu"],
[data-testid="stAppDeployButton"], [data-testid="stDeployButton"],
[data-testid="stStatusWidget"], [data-testid="stConnectionStatus"],
footer, [data-testid="stAppFooter"] { display: none !important; }
[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: none !important;
    pointer-events: none !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    visibility: visible !important; opacity: 1 !important;
    pointer-events: auto !important; color: #ececec !important;
}

.block-container {
    padding: 0 1.5rem !important;
    max-width: 1180px !important;
}

/* =====================================================================
   2. FULL-BLEED BANDS
   Streamlit container keys become .st-key-<key> classes. Each band paints
   its own edge-to-edge background behind the centred column via ::before,
   so widgets stay inside the 1180px grid while colour runs full width.
   ===================================================================== */
.st-key-hero, .st-key-how, .st-key-faq, .st-key-footer { position: relative; }
.st-key-hero::before,
.st-key-how::before,
.st-key-footer::before {
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    left: 50%;
    width: 100vw;
    transform: translateX(-50%);
    z-index: 0;
}
.st-key-hero::before { background: var(--navy); }
.st-key-how::before { background: var(--cream); }
.st-key-footer::before { background: var(--navy); }
.st-key-hero > *, .st-key-how > *, .st-key-faq > *, .st-key-footer > * {
    position: relative;
    z-index: 1;
}

.st-key-hero {
    padding-top: 3.2rem;
    background-color: var(--navy) !important;   /* belt and braces behind ::before */
}
.st-key-how { background-color: var(--cream) !important; }
.st-key-hero [data-testid="stMarkdownContainer"] { color: #ffffff; }
.st-key-how { padding-top: 0.5rem; }
.st-key-faq { padding-top: 0.5rem; }
.st-key-footer { padding-top: 0.5rem; }

/* =====================================================================
   3. HERO
   ===================================================================== */
.crumb {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #9fb3c8 !important;
    margin-bottom: 1.1rem;
}
.crumb span { color: #ffffff !important; }
.hero-h1 {
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif !important;
    font-size: clamp(2.2rem, 4.4vw, 3.15rem) !important;
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.015em;
    color: #ffffff !important;
    margin: 0 0 1.2rem 0;
}
.hero-p {
    font-size: 1.02rem;
    line-height: 1.65;
    color: #d0d7de !important;
    margin: 0 0 1.9rem 0;
    max-width: 34rem;
}
.hero-p strong { color: #ffffff !important; font-weight: 600; }

/* Dashed dropzone card */
.st-key-dropzone {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1.5px dashed rgba(255, 255, 255, 0.34) !important;
    border-radius: 14px !important;
    padding: 1.5rem 1.6rem 1.35rem 1.6rem !important;
}
.st-key-dropzone [data-testid="stWidgetLabel"] p,
.st-key-dropzone [data-testid="stWidgetLabel"] label,
.st-key-dropzone [data-testid="stFileUploader"] label,
.st-key-dropzone [data-testid="stTextArea"] label {
    color: #e8eff7 !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px dashed rgba(255, 255, 255, 0.32) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"] *,
.st-key-dropzone [data-testid="stFileUploaderDropzone"] small {
    color: #cfdcea !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"] button {
    background: var(--teal) !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
}
.st-key-dropzone [data-testid="stFileUploader"] * {
    background: transparent !important;
    color: #e8eff7 !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"] {
    background: rgba(255, 255, 255, 0.05) !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"] button {
    background: var(--teal) !important;
    color: #ffffff !important;
}
.st-key-dropzone [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    background: #12314e !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 10px !important;
}
.st-key-dropzone [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
    color: #f3f7fb !important;
    font-weight: 600 !important;
}
.st-key-dropzone [data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"] {
    color: #b8c8d8 !important;
}
.st-key-dropzone [data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 1px solid #cbd5df !important;
    border-radius: 12px !important;
    color: var(--navy) !important;
    caret-color: var(--navy) !important;
    font-size: 0.92rem !important;
}
.st-key-dropzone [data-testid="stTextArea"] textarea::placeholder { color: #718096 !important; }
.st-key-dropzone [data-testid="stTextArea"] textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(0, 130, 138, 0.2) !important;
}
.st-key-dropzone .stButton > button[kind="primary"] {
    background: var(--teal) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-radius: 999px !important;
    padding: 0.72rem 1.9rem !important;
    width: 100%;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22) !important;
}
.st-key-dropzone .stButton > button[kind="primary"]:hover {
    background: var(--teal-dark) !important;
}
.hero-note {
    font-size: 0.82rem;
    color: #9fb3c8 !important;
    margin-top: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}
.hero-note b { color: #ffffff !important; font-weight: 600; }

/* Hero image slot */
.hero-img {
    width: 100%;
    border-radius: 16px;
    display: block;
    box-shadow: 0 22px 48px rgba(0, 0, 0, 0.32);
}
.hero-img-empty {
    border: 1.5px dashed rgba(255, 255, 255, 0.34);
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
    padding: 3.4rem 1.5rem;
    text-align: center;
    color: #9fb3c8 !important;
}
.hero-img-empty b { display: block; color: #ffffff !important; font-size: 0.98rem; margin-bottom: 0.35rem; }
.hero-img-empty code {
    background: rgba(255,255,255,0.1); color:#fff; border-radius:4px;
    padding: 0.1rem 0.35rem; font-size: 0.8rem;
}

/* Trust strip */
.trust-strip {
    position: relative;
    margin-top: 2.6rem;
    padding: 1.1rem 0;
    background: var(--navy-deep);
}
.trust-strip::before {
    content: "";
    position: absolute; top: 0; bottom: 0; left: 50%;
    width: 100vw; transform: translateX(-50%);
    background: var(--navy-deep); z-index: 0;
}
.trust-inner {
    position: relative; z-index: 1;
    display: flex; flex-wrap: wrap; align-items: center;
    gap: 2.4rem; font-size: 0.88rem; color: #d0d7de;
}
.trust-item { display: flex; align-items: center; gap: 0.5rem; }
.tick { color: #00d394; font-weight: 700; }
.star { color: #00b67a; }
.trust-badge {
    font-weight: 700; color: #ffffff;
    letter-spacing: 0.02em;
}

/* =====================================================================
   4. SECTION HEADERS
   ===================================================================== */
.section-pad { padding: 4.2rem 0 0.5rem 0; }
.sec-head { text-align: center; max-width: 46rem; margin: 0 auto 2.6rem auto; }
.sec-title {
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif !important;
    font-size: clamp(1.6rem, 2.6vw, 2.25rem) !important;
    font-weight: 700;
    line-height: 1.2;
    color: var(--ink) !important;
    margin: 0 0 0.75rem 0;
}
.sec-sub {
    font-size: 0.98rem;
    line-height: 1.6;
    color: var(--muted) !important;
    margin: 0;
}
.sec-head-left { text-align: left; max-width: none; margin: 0 0 1.4rem 0; }

/* =====================================================================
   5. HOW IT WORKS
   ===================================================================== */
.steps { display: flex; flex-direction: column; gap: 0.9rem; }
.step {
    background: var(--cream);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.step-num {
    flex: 0 0 auto;
    width: 28px; height: 28px;
    border-radius: 50%;
    background: var(--gold);
    color: var(--navy) !important;
    font-size: 0.82rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    margin-top: 0.1rem;
}
.step-title {
    font-size: 1.05rem; font-weight: 700;
    color: var(--ink) !important;
    margin: 0 0 0.35rem 0;
}
.step-text {
    font-size: 0.9rem; line-height: 1.55;
    color: var(--muted) !important;
    margin: 0;
}

/* Illustration panel */
.illus {
    position: relative;
    min-height: 360px;
    border-radius: 16px;
    overflow: hidden;
    background-color: var(--mint);
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.75) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.75) 1px, transparent 1px);
    background-size: 34px 34px;
}
.illus-card {
    position: absolute; left: 27%; top: 32%;
    width: 44%;
    background: #ffffff;
    border: 1.5px dashed #c3d4d2;
    border-radius: 14px;
    padding: 1.9rem 1rem;
    text-align: center;
    box-shadow: 0 14px 30px rgba(10, 37, 64, 0.1);
}
.illus-cloud { font-size: 1.7rem; color: #f06a55; line-height: 1; }
.illus-text {
    margin-top: 0.5rem;
    font-size: 0.95rem; font-weight: 700; color: var(--ink) !important;
}
.illus-badges {
    position: absolute; left: 11%; top: 33%;
    display: flex; flex-direction: column; gap: 6px;
}
.fb {
    color: #ffffff !important;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.04em;
    padding: 0.32rem 0.5rem;
    border-radius: 4px;
    text-align: center;
    min-width: 60px;
}
.fb-pdf { background: #c94a38; }
.fb-word { background: #2c496e; }
.fb-txt { background: #3ea3b8; }
.fb-more { background: #8d9ba8; }
.illus-sheet {
    position: absolute; right: 9%; top: 34%;
    width: 25%; height: 48%;
    background: #ffffff;
    border: 1px solid #e2e8ea;
    border-radius: 6px;
    transform: rotate(-4deg);
    box-shadow: 0 10px 22px rgba(10, 37, 64, 0.14);
    padding: 0.7rem 0.6rem;
}
.sheet-line {
    height: 5px; border-radius: 3px;
    background: #e6ecf1; margin-bottom: 7px;
}
.sheet-line.w70 { width: 70%; }
.sheet-line.w90 { width: 90%; }
.sheet-line.w55 { width: 55%; background: #f6d9d2; }
.sheet-line.w80 { width: 80%; }

/* =====================================================================
   6. RESULTS
   ===================================================================== */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin-bottom: 1.1rem;
}
@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.kpi {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.05rem 1.15rem;
}
.kpi-label {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: #6b7c93 !important; margin-bottom: 0.45rem;
}
.kpi-value { font-size: 1.5rem; font-weight: 700; line-height: 1.15; color: var(--ink) !important; }
.kpi-value.ok { color: var(--teal) !important; }
.kpi-value.warn { color: #d99a2b !important; }
.kpi-sub { font-size: 0.78rem; color: #8494a6 !important; margin-top: 0.3rem; }

.score-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.5rem 1.6rem 0.5rem 1.6rem;
    margin-bottom: 1.1rem;
}
.score-top { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.score-value {
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif !important;
    font-size: 3rem; font-weight: 700; line-height: 1;
    color: var(--teal) !important;
}
.score-value.is-low { color: #d99a2b !important; }
.score-value.is-bad { color: #d9533f !important; }
.score-verdict {
    font-size: 0.8rem; font-weight: 700;
    color: var(--ink) !important;
    background: var(--mint);
    border: 1px solid #bfe3df;
    border-radius: 999px;
    padding: 0.32rem 0.8rem;
    white-space: nowrap;
}
.score-caption { font-size: 0.88rem; color: var(--muted) !important; margin: 0.6rem 0 0 0; }

.ra-label {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: #6b7c93 !important; margin: 0 0 0.7rem 0;
}
.ra-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.2rem 1.35rem;
    margin-bottom: 1rem;
}
.card-head { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; }
.count-pill {
    font-size: 0.75rem; font-weight: 700; color: var(--ink) !important;
    background: #f1f4f8; border: 1px solid var(--line);
    border-radius: 999px; padding: 0.15rem 0.6rem;
}

.chip-row { display: flex; flex-wrap: wrap; gap: 0.45rem; }
.chip {
    display: inline-block;
    font-size: 0.82rem; font-weight: 600; line-height: 1.35;
    border-radius: 999px; padding: 0.32rem 0.75rem;
    border: 1px solid transparent; white-space: nowrap;
}
.chip-ok { background: #e6f7f4; border-color: #9fdcd2; color: #046b57 !important; }
.chip-miss { background: #fdecea; border-color: #f3c0bd; color: #a4302a !important; }
.chip-bonus { background: #fdf3e0; border-color: #f0d9a8; color: #8a6300 !important; }
.chip-none { display: inline-block; font-size: 0.85rem; color: #8494a6 !important; font-style: italic; }

.stat-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; padding: 0.62rem 0;
    border-bottom: 1px solid var(--line); font-size: 0.92rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-key { color: #6b7c93 !important; }
.stat-value { color: var(--ink) !important; font-weight: 700; }

.badge {
    display: inline-block; font-size: 0.76rem; font-weight: 700;
    border-radius: 999px; padding: 0.22rem 0.65rem; border: 1px solid transparent;
}
.badge-ok { background: #e6f7f4; border-color: #9fdcd2; color: #046b57 !important; }
.badge-warn { background: #fdf3e0; border-color: #f0d9a8; color: #8a6300 !important; }

.skill-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.skill-table th {
    text-align: left; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: #6b7c93 !important;
    padding: 0.6rem; border-bottom: 1px solid var(--line);
}
.skill-table td {
    padding: 0.65rem 0.6rem;
    border-bottom: 1px solid var(--line);
    color: #22384f !important;
}
.skill-table tr:last-child td { border-bottom: none; }
.cell-status { font-weight: 700; }
.cell-status.ok { color: #046b57 !important; }
.cell-status.miss { color: #a4302a !important; }
.cell-status.bonus { color: #8a6300 !important; }

.json-block {
    background: #f7f9fb;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin: 0 0 0.8rem 0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.8rem; line-height: 1.55;
    color: #22384f !important;
    overflow-x: auto; white-space: pre;
}

/* Streamlit widgets on the light page */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span { color: #22384f !important; font-size: 0.88rem !important; }
[data-testid="stAlert"] {
    background: #fff8e6 !important;
    border: 1px solid #f0d9a8 !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] div, [data-testid="stAlert"] span { color: #7a5b00 !important; }
[data-testid="stSpinner"] span, [data-testid="stSpinner"] p { color: var(--muted) !important; }
[data-testid="stProgress"] { margin-bottom: 1.2rem; }
[data-testid="stProgress"] > div > div { background-color: #eef2f6 !important; border-radius: 999px !important; }
[data-testid="stProgress"] > div > div > div { background-color: var(--teal) !important; border-radius: 999px !important; }
[data-testid="stProgress"] [role="progressbar"] { background-color: #eef2f6 !important; }
[data-testid="stCaptionContainer"] p { color: #8494a6 !important; }

/* =====================================================================
   7. FAQ - smooth open / close, no JavaScript
   ===================================================================== */
.faq { display: flex; flex-direction: column; gap: 0.75rem; }
.faq-item {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}
.faq-item[open] { border-color: #bfe3df; box-shadow: 0 6px 18px rgba(10, 37, 64, 0.05); }
.faq-q {
    list-style: none;
    cursor: pointer;
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem;
    padding: 1.1rem 1.35rem;
    font-size: 1rem; font-weight: 600; color: var(--ink);
    user-select: none;
}
.faq-q::-webkit-details-marker { display: none; }
.faq-q:hover { color: var(--teal); }
.faq-icon {
    flex: 0 0 auto;
    width: 22px; height: 22px;
    border-radius: 50%;
    background: var(--mint);
    color: var(--teal-dark);
    font-size: 0.85rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.3s ease, background 0.3s ease;
}
.faq-item[open] .faq-icon { transform: rotate(45deg); background: var(--teal); color: #ffffff; }
.faq-a {
    padding: 0 1.35rem 1.2rem 1.35rem;
    font-size: 0.93rem; line-height: 1.65; color: var(--muted);
}
.faq-a p { margin: 0 0 0.6rem 0; color: var(--muted) !important; }
.faq-a p:last-child { margin-bottom: 0; }
/* Height transition where supported; a soft fade covers older engines. */
.faq-item::details-content {
    block-size: 0;
    overflow: hidden;
    transition: block-size 0.34s cubic-bezier(0.4, 0, 0.2, 1),
                content-visibility 0.34s cubic-bezier(0.4, 0, 0.2, 1) allow-discrete;
}
.faq-item[open]::details-content { block-size: auto; }
@supports not (interpolate-size: allow-keywords) {
    .faq-a { animation: faqIn 0.28s ease both; }
    @keyframes faqIn {
        from { opacity: 0; transform: translateY(-6px); }
        to { opacity: 1; transform: none; }
    }
}

/* =====================================================================
   8. FOOTER
   ===================================================================== */
.st-key-footer {
    background: var(--navy) !important;
    margin-top: 4.5rem !important;
    padding: 3.4rem 0 0 0 !important;
}
.foot-grid {
    display: grid;
    grid-template-columns: 1.6fr 1fr 1fr;
    gap: 2.5rem;
    padding-bottom: 2.6rem;
}
@media (max-width: 820px) { .foot-grid { grid-template-columns: 1fr; gap: 1.8rem; } }
.foot-brand {
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif !important;
    font-size: 1.25rem; font-weight: 700; color: #ffffff !important;
    margin-bottom: 0.7rem;
}
.foot-text { font-size: 0.9rem; line-height: 1.6; color: #9fb3c8 !important; margin: 0; max-width: 24rem; }
.foot-h {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em;
    text-transform: uppercase; color: #7e94ab !important; margin-bottom: 0.9rem;
}
.foot-links { display: flex; flex-direction: column; gap: 0.55rem; }
.foot-links a {
    font-size: 0.9rem; color: #d0d7de !important;
    text-decoration: none; transition: color 0.2s ease;
}
.foot-links a:hover { color: #ffffff !important; }
.foot-bottom {
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    padding: 1.2rem 0 2rem 0;
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; flex-wrap: wrap;
    font-size: 0.83rem; color: #7e94ab !important;
}
.foot-bottom b { color: #ffffff !important; font-weight: 600; }
.foot-pill {
    display: inline-flex; align-items: center; gap: 0.45rem;
    font-size: 0.78rem; color: #cfdcea !important;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 999px; padding: 0.28rem 0.75rem;
}
.dot { width: 7px; height: 7px; border-radius: 50%; background: #00d394; display: inline-block; }

/* Scrollbars */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-thumb { background: #c9d3dd; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: #a9b7c6; }
::-webkit-scrollbar-track { background: transparent; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Presentation helpers (formatting only - no analysis logic)
# --------------------------------------------------------------------------- #
def chips(items, variant, empty_text):
    """Render skills as coloured pills, or a muted note when the list is empty."""
    if not items:
        return f'<span class="chip-none">{empty_text}</span>'
    pills = "".join(
        f'<span class="chip {variant}">{html.escape(str(item))}</span>' for item in items
    )
    return f'<div class="chip-row">{pills}</div>'


def verdict_for(score):
    """Return (label, css class) describing how strong the match is."""
    if score >= 80:
        return "Strong match", ""
    if score >= 60:
        return "Good match", ""
    if score >= 40:
        return "Partial match", " is-low"
    return "Weak match", " is-bad"


def fmt_years(value):
    """Render a year count without a trailing .0."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return str(int(number)) if number.is_integer() else f"{number:g}"


def head(title, sub="", align="center"):
    """Section header block."""
    cls = "sec-head" if align == "center" else "sec-head sec-head-left"
    sub_html = f'<p class="sec-sub">{sub}</p>' if sub else ""
    st.markdown(
        f'<div class="{cls}"><h2 class="sec-title">{title}</h2>{sub_html}</div>',
        unsafe_allow_html=True,
    )


# =========================================================================== #
# HERO
# =========================================================================== #
with st.container(key="hero"):
    left, right = st.columns([0.85, 1.15], gap="large")

    with left:
        st.markdown(
            '<div class="crumb">AI Resume Analyzer <span>&bull;</span> '
            "ATS Match Checker</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h1 class="hero-h1">Free Resume Analyzer &amp; Job Matcher</h1>'
            '<p class="hero-p">Upload a resume and paste a job description to see how '
            "well the two align. The analyzer extracts skills, experience and education "
            "from both documents, then reports <strong>matched skills, gaps to close, "
            "and whether the experience bar is met</strong>.</p>",
            unsafe_allow_html=True,
        )

        with st.container(key="dropzone"):
            resume_file = st.file_uploader(
                "Upload your resume (PDF)",
                type=["pdf"],
                help="Text-based PDFs work best. Scanned images need OCR.",
            )
            job_description = st.text_area(
                "Paste the job description",
                height=150,
                placeholder="Include the required skills and the minimum years "
                "of experience.",
            )
            submit = st.button("Analyze Match", type="primary")

        st.markdown(
            '<div class="hero-note"><span class="tick">&check;</span>'
            '<span><b>Two LLM passes</b> per analysis - one for the resume, '
            "one for the posting.</span></div>",
            unsafe_allow_html=True,
        )

    with right:
        if HERO_IMAGE.startswith("http"):
            st.markdown(
                f'<img class="hero-img" src="{HERO_IMAGE}" alt="Resume analysis preview">',
                unsafe_allow_html=True,
            )
        elif HERO_IMAGE:
            st.image(HERO_IMAGE, use_container_width=True)
        else:
            st.markdown(
                '<div class="hero-img-empty">'
                "<b>Your image goes here</b>"
                "Set <code>HERO_IMAGE</code> at the top of <code>app.py</code> to a "
                "URL or a local path such as <code>assets/hero.avif</code>."
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="trust-strip"><div class="trust-inner">'
        '<div class="trust-item"><span class="tick">&check;</span>'
        "Required, nice-to-have and experience fit in a single pass</div>"
        '<div class="trust-item"><span class="tick">&check;</span>'
        "PDF resumes up to 200MB</div>"
        '<div class="trust-item"><span class="star">&#9733;</span>'
        '<span class="trust-badge">Powered by Groq</span></div>'
        "</div></div>",
        unsafe_allow_html=True,
    )


# =========================================================================== #
# RESULTS
# =========================================================================== #
if submit:
    if not resume_file or not job_description.strip():
        st.warning("Upload a resume and paste a job description to run the analysis.")
    else:
        try:
            with st.spinner("Reading the resume..."):
                resume_text = extract_text_from_pdf(resume_file)

            with st.spinner("Extracting structured data..."):
                resume_data = extract_resume_data(resume_text)
                job_data = extract_job_requirements(job_description)

            with st.spinner("Scoring the match..."):
                result = calculate_match(resume_data, job_data)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
        else:
            score = result["match_percentage"]
            verdict, score_class = verdict_for(score)

            matched = result["matched_required_skills"]
            missing = result["missing_required_skills"]
            bonus = result["matched_nice_to_have"]
            total_required = len(matched) + len(missing)

            your_years = resume_data.get("years_experience", 0)
            required_years = job_data.get("min_years_experience", 0)
            meets = result["meets_experience"]

            with st.container(key="results"):
                st.markdown('<div class="section-pad"></div>', unsafe_allow_html=True)
                head("Your match report", "Every required skill checked against the posting.")

                exp_class = "ok" if meets else "warn"
                exp_sub = (
                    f"Required {fmt_years(required_years)} yrs"
                    if meets
                    else f"Short of {fmt_years(required_years)} yrs required"
                )
                coverage_class = "warn" if missing else "ok"

                # Summary tiles
                st.markdown(
                    '<div class="kpi-grid">'
                    '<div class="kpi"><div class="kpi-label">Match score</div>'
                    f'<div class="kpi-value ok">{score}%</div>'
                    f'<div class="kpi-sub">{verdict}</div></div>'
                    '<div class="kpi"><div class="kpi-label">Required skills</div>'
                    f'<div class="kpi-value {coverage_class}">{len(matched)}/{total_required}</div>'
                    f'<div class="kpi-sub">{len(missing)} still missing</div></div>'
                    '<div class="kpi"><div class="kpi-label">Bonus skills</div>'
                    f'<div class="kpi-value">{len(bonus)}</div>'
                    '<div class="kpi-sub">Matched nice-to-haves</div></div>'
                    '<div class="kpi"><div class="kpi-label">Experience</div>'
                    f'<div class="kpi-value {exp_class}">{fmt_years(your_years)} yrs</div>'
                    f'<div class="kpi-sub">{exp_sub}</div></div>'
                    "</div>",
                    unsafe_allow_html=True,
                )

                # Score card
                st.markdown(
                    '<div class="score-card">'
                    '<div class="score-top">'
                    '<div class="ra-label" style="margin:0;">Match score</div>'
                    f'<div class="score-verdict">{verdict}</div>'
                    "</div>"
                    f'<div class="score-value{score_class}" style="margin-top:0.4rem;">'
                    f"{score}%</div>"
                    '<p class="score-caption">Percentage of the posting\'s required '
                    f"skills found in the resume ({len(matched)} of {total_required}).</p>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.progress(min(max(score / 100, 0.0), 1.0))

                # Skill breakdown
                col_matched, col_missing = st.columns(2, gap="medium")
                with col_matched:
                    st.markdown(
                        '<div class="ra-card">'
                        '<div class="card-head">'
                        '<span class="ra-label" style="margin:0;">Matched required</span>'
                        f'<span class="count-pill">{len(matched)}</span></div>'
                        + chips(matched, "chip-ok", "No required skills matched.")
                        + "</div>",
                        unsafe_allow_html=True,
                    )
                with col_missing:
                    st.markdown(
                        '<div class="ra-card">'
                        '<div class="card-head">'
                        '<span class="ra-label" style="margin:0;">Missing required</span>'
                        f'<span class="count-pill">{len(missing)}</span></div>'
                        + chips(missing, "chip-miss", "Nothing missing - full coverage.")
                        + "</div>",
                        unsafe_allow_html=True,
                    )

                if bonus:
                    st.markdown(
                        '<div class="ra-card">'
                        '<div class="card-head">'
                        '<span class="ra-label" style="margin:0;">Bonus skills</span>'
                        f'<span class="count-pill">{len(bonus)}</span></div>'
                        + chips(bonus, "chip-bonus", "")
                        + "</div>",
                        unsafe_allow_html=True,
                    )

                # Experience + candidate
                badge = (
                    '<span class="badge badge-ok">Requirement met</span>'
                    if meets
                    else '<span class="badge badge-warn">Below requirement</span>'
                )
                st.markdown(
                    '<div class="ra-card">'
                    '<div class="card-head" style="margin-bottom:0.35rem;">'
                    '<span class="ra-label" style="margin:0;">Experience requirement</span>'
                    f"{badge}</div>"
                    '<div class="stat-row"><span class="stat-key">Your experience</span>'
                    f'<span class="stat-value">{fmt_years(your_years)} years</span></div>'
                    '<div class="stat-row"><span class="stat-key">Posting requires</span>'
                    f'<span class="stat-value">{fmt_years(required_years)} years</span></div>'
                    '<div class="stat-row"><span class="stat-key">Candidate</span>'
                    f'<span class="stat-value">'
                    f'{html.escape(str(resume_data.get("name") or "Not stated"))}</span></div>'
                    "</div>",
                    unsafe_allow_html=True,
                )

                # Skill matrix
                rows = []
                for skill in matched:
                    rows.append((skill, "Required", "Matched", "ok"))
                for skill in missing:
                    rows.append((skill, "Required", "Missing", "miss"))
                for skill in bonus:
                    rows.append((skill, "Nice to have", "Bonus", "bonus"))

                if rows:
                    body = "".join(
                        "<tr>"
                        f"<td>{html.escape(str(skill))}</td>"
                        f"<td>{kind}</td>"
                        f'<td class="cell-status {cls}">{status}</td>'
                        "</tr>"
                        for skill, kind, status, cls in rows
                    )
                    st.markdown(
                        '<div class="ra-card">'
                        '<div class="ra-label">Skill matrix</div>'
                        '<table class="skill-table"><thead><tr>'
                        "<th>Skill</th><th>Type</th><th>Status</th>"
                        f"</tr></thead><tbody>{body}</tbody></table></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div class="ra-card"><span class="chip-none">No skills were '
                        "extracted from either document.</span></div>",
                        unsafe_allow_html=True,
                    )

                # Raw data
                with st.expander("Extracted data (raw JSON)"):
                    st.markdown(
                        '<pre class="json-block">'
                        f"{html.escape(json.dumps(resume_data, indent=2, ensure_ascii=False))}"
                        "</pre>"
                        '<pre class="json-block">'
                        f"{html.escape(json.dumps(job_data, indent=2, ensure_ascii=False))}"
                        "</pre>",
                        unsafe_allow_html=True,
                    )


# =========================================================================== #
# HOW IT WORKS
# =========================================================================== #
with st.container(key="how"):
    st.markdown('<div class="section-pad" id="how-it-works"></div>', unsafe_allow_html=True)
    head(
        "How the Resume Analyzer Works",
        "The analyzer reads both documents, extracts structure, and checks the resume "
        "against the posting to give you actionable steps for improvement.",
    )

    steps_col, illus_col = st.columns([0.92, 1.08], gap="large")

    with steps_col:
        st.markdown(
            '<div class="steps">'
            '<div class="step"><div class="step-num">1</div><div>'
            '<div class="step-title">Upload Your Resume</div>'
            '<p class="step-text">Upload a PDF and the text is extracted page by page, '
            "ready for analysis.</p></div></div>"

            '<div class="step"><div class="step-num">2</div><div>'
            '<div class="step-title">Paste the Job Description</div>'
            '<p class="step-text">Required skills, nice-to-haves and the minimum years '
            "of experience are pulled from the posting.</p></div></div>"

            '<div class="step"><div class="step-num">3</div><div>'
            '<div class="step-title">Review Your Match Report</div>'
            '<p class="step-text">See a match score, matched and missing skills, bonus '
            "skills, and whether the experience bar is met.</p></div></div>"

            '<div class="step"><div class="step-num">4</div><div>'
            '<div class="step-title">Optimize &amp; Apply</div>'
            '<p class="step-text">Close the gaps the report surfaces, then tailor your '
            "resume before you send it.</p></div></div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with illus_col:
        st.markdown(
            '<div class="illus">'
            '<div class="illus-badges">'
            '<span class="fb fb-pdf">PDF</span>'
            '<span class="fb fb-word">DOCX</span>'
            '<span class="fb fb-txt">TXT</span>'
            '<span class="fb fb-more">and more</span>'
            "</div>"
            '<div class="illus-card">'
            '<div class="illus-cloud">&#8682;</div>'
            '<div class="illus-text">Upload your resume</div>'
            "</div>"
            '<div class="illus-sheet">'
            '<div class="sheet-line w70"></div>'
            '<div class="sheet-line w90"></div>'
            '<div class="sheet-line w55"></div>'
            '<div class="sheet-line w80"></div>'
            '<div class="sheet-line w70"></div>'
            '<div class="sheet-line w90"></div>'
            '<div class="sheet-line w55"></div>'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )


# =========================================================================== #
# FAQ
# =========================================================================== #
FAQS = [
    (
        "How is the match score calculated?",
        "The score is the share of the posting's <em>required</em> skills that were "
        "found in your resume - matched required skills divided by total required "
        "skills, as a percentage. Nice-to-have skills are reported separately as bonus "
        "skills and do not change the score.",
    ),
    (
        "How are skills compared?",
        "Skills are normalised (lower-cased and trimmed) and then matched exactly. That "
        "means \"Python\" matches \"python\", but synonyms such as \"JS\" and "
        "\"JavaScript\" are treated as different skills, so mirror the wording used in "
        "the posting where you can.",
    ),
    (
        "Which file types can I upload?",
        "PDF resumes only, up to 200MB. Text-based PDFs work best - a resume exported "
        "directly from a word processor or design tool extracts cleanly.",
    ),
    (
        "What if my resume is a scanned image?",
        "A scanned PDF contains no selectable text, so the analyzer stops and tells you "
        "rather than scoring an empty document. Run the file through OCR first, or "
        "upload a text-based version.",
    ),
    (
        "Does it send my documents to an AI model?",
        "Yes - two calls are made per analysis, one to structure the resume and one to "
        "structure the posting, using Groq's <code>openai/gpt-oss-120b</code> model at "
        "temperature 0. No documents are stored on disk by the app.",
    ),
    (
        "Why did the score come back lower than expected?",
        "Usually one of three things: the posting lists skills your resume phrases "
        "differently, a skill is buried in a project description the extractor did not "
        "count, or the posting genuinely requires technologies you have not used. The "
        "missing-skills list tells you which.",
    ),
]

with st.container(key="faq"):
    st.markdown('<div class="section-pad" id="faq"></div>', unsafe_allow_html=True)
    head(
        "Frequently Asked Questions",
        "How the score is produced, what the analyzer reads, and how to raise your match.",
    )

    faq_html = "".join(
        '<details class="faq-item">'
        f'<summary class="faq-q">{q}<span class="faq-icon">+</span></summary>'
        f'<div class="faq-a"><p>{a}</p></div>'
        "</details>"
        for q, a in FAQS
    )
    st.markdown(f'<div class="faq">{faq_html}</div>', unsafe_allow_html=True)


# =========================================================================== #
# FOOTER
# =========================================================================== #
with st.container(key="footer"):
    st.markdown(
        '<div class="foot-grid">'
        "<div>"
        f'<div class="foot-brand">{BRAND}</div>'
        '<p class="foot-text">An ATS-style resume checker: extract the structure of a '
        "resume and a job posting, compare the required skills, and surface the gaps "
        "worth closing before you apply.</p>"
        "</div>"
        "<div>"
        '<div class="foot-h">Product</div>'
        '<div class="foot-links">'
        '<a href="#how-it-works">How it works</a>'
        '<a href="#faq">FAQ</a>'
        "</div>"
        "</div>"
        "<div>"
        '<div class="foot-h">Built with</div>'
        '<div class="foot-links">'
        '<a href="https://streamlit.io" target="_blank" rel="noopener">Streamlit</a>'
        '<a href="https://groq.com" target="_blank" rel="noopener">Groq API</a>'
        '<a href="https://pypi.org/project/pypdf/" target="_blank" rel="noopener">pypdf</a>'
        "</div>"
        "</div>"
        "</div>"
        '<div class="foot-bottom">'
        f"<span>&copy; 2026 <b>{BRAND}</b>. All rights reserved.</span>"
        f'<span class="foot-pill"><span class="dot"></span>'
        f"Built by <b>&nbsp;{AUTHOR}</b></span>"
        "</div>",
        unsafe_allow_html=True,
    )