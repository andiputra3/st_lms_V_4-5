#!/usr/bin/env python3
"""
ST-LMS DATA VIEWER v2.0.0 — Market Evolution Operating System Dashboard
Read-only knowledge portal for entire ST-LMS project.
Zero dependencies. Python stdlib only.
http://0.0.0.0:8082

Pages:
  /                Dashboard — All key metrics overview
  /observation     Market Observation — Live TruthPoint, Structure, Evidence
  /statistics      Statistics — All 7 statistics domains in tables
  /evolution       Evolution — Lifecycle, mutation, versioning, reliability
  /timeline        Timeline — Observation range selector
  /knowledge       Knowledge — Academy, Oracle, HiveMind, CERMIN, Darwin
  /prediction      Prediction — Market possibilities with probabilities
  /simulation      Simulation — 5 simulators results
  /recommendation  Recommendation — Market Intelligence Report
  /snapshot        Snapshot — Snapshot viewer with type filter
  /dna             Market DNA — DNA profile viewer
  /lifecycle       Lifecycle — Entity lifecycle viewer
  /mutation        Mutation — Mutation tracker viewer
  /pipeline        Pipeline — Status, stage list, execution log
  /health-page     Health — Health check dashboard
  /sqlite          SQLite — SQLite browser
  /config          Config — Configuration viewer
"""

import http.server
import json
import os
import re
import sqlite3
import time
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone, timedelta

from stlms.core.shell import STLMSShell

WIB = timezone(timedelta(hours=7))
ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "stlms.db"
SCHEMA_PATH = ROOT / "STLMS_SQLITE_SCHEMA_V1.sql"
SECRET_PATTERNS = [r'ghp_[a-zA-Z0-9]{36}', r'sk-[a-zA-Z0-9\-]+', r'api[Kk]ey["\s:=]+[a-zA-Z0-9\-]+',
                   r'Bearer\s+[a-zA-Z0-9\-_\.]+', r'password["\s:=]+["\']?\S+', r'token["\s:=]+["\']?\S+']

_shell_instance = None
_shell_error = None


def get_shell():
    global _shell_instance, _shell_error
    if _shell_instance is not None:
        return _shell_instance, _shell_error
    try:
        _shell_instance = STLMSShell(symbol="BTCUSDT", timeframe="1m")
        _shell_instance.generate(candle_count=200)
        _shell_error = None
    except Exception as e:
        _shell_error = str(e)
        _shell_instance = None
    return _shell_instance, _shell_error


def wib_now():
    return datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")


def count_files(ext=None):
    files = [f for f in ROOT.rglob("*") if ".git/" not in str(f) and "__pycache__" not in str(f) and f.is_file()]
    if ext:
        files = [f for f in files if f.suffix == ext]
    return len(files)


def repo_stats():
    return {"total_files": count_files(), "md_files": count_files(".md"), "py_files": count_files(".py"),
            "html_files": count_files(".html"), "sql_files": count_files(".sql"), "js_files": count_files(".js"),
            "last_update": wib_now()}


def _safe(v, default="N/A"):
    """Return value or N/A if None."""
    if v is None:
        return default
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def dict_to_html_table(d, depth=0):
    """Render a dict as nested HTML tables. Lists rendered as cards."""
    if isinstance(d, list):
        if not d:
            return '<p class="mute">No items</p>'
        html = '<div class="grid">'
        for item in d:
            if isinstance(item, dict):
                html += f'<div class="card">{dict_to_html_table(item, depth+1)}</div>'
            else:
                html += f'<div class="card"><p>{str(item)}</p></div>'
        html += '</div>'
        return html
    if not isinstance(d, dict):
        return f'<p>{str(d)}</p>'
    if not d:
        return '<p class="mute">No data</p>'
    rows = []
    for k, v in d.items():
        if k in ("available",):
            continue
        if isinstance(v, dict):
            val_html = dict_to_html_table(v, depth + 1)
        elif isinstance(v, list):
            if not v:
                val_html = '<span class="mute">empty</span>'
            elif all(isinstance(i, dict) for i in v):
                val_html = dict_to_html_table(v, depth + 1)
            else:
                val_html = ', '.join(str(i) for i in v)
        elif isinstance(v, float):
            val_html = f'{v:.4f}'
        elif isinstance(v, bool):
            val_html = f'<b class="{"pass" if v else "fail"}">{v}</b>'
        else:
            val_html = str(v)
        rows.append(f'<tr><td style="width:30%"><b>{k}</b></td><td>{val_html}</td></tr>')
    return f'<div class="tblwrap"><table>{"".join(rows)}</table></div>'


def card_html(title, content, subtitle=None):
    sub = f'<p class="mute">{subtitle}</p>' if subtitle else ''
    return f'<div class="card"><h3>{title}</h3>{sub}{content}</div>'


def no_data_html(message="No data loaded. Run shell.generate() first."):
    return f'<div class="card"><p class="mute">N/A — {message}</p></div>'


def stat_box(num, label, klass=""):
    return f'<div class="stat-box"><div class="num {klass}">{num}</div><div class="label">{label}</div></div>'


def sqlite_stats():
    if not DB_PATH.exists():
        return {"status": "Database not found"}
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        tables = conn.execute("SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table'").fetchone()["cnt"]
        indexes = conn.execute("SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='index'").fetchone()["cnt"]
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        return {"tables": tables, "indexes": indexes, "integrity": integrity,
                "size_bytes": os.path.getsize(DB_PATH) if DB_PATH.exists() else 0}
    except Exception as e:
        return {"error": str(e)}


def sqlite_tables():
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    result = []
    for t in tables:
        name = t["name"]
        cnt = conn.execute(f"SELECT COUNT(*) as cnt FROM [{name}]").fetchone()["cnt"]
        result.append({"name": name, "row_count": cnt})
    conn.close()
    return result


def list_md_files(sort_by="name", order="asc"):
    files = []
    for f in ROOT.rglob("*.md"):
        if ".git/" in str(f) or "__pycache__" in str(f):
            continue
        rel = str(f.relative_to(ROOT))
        st = f.stat()
        files.append({"name": f.name, "path": rel, "size": st.st_size,
                       "modified": st.st_mtime,
                       "modified_str": datetime.fromtimestamp(st.st_mtime, WIB).strftime("%Y-%m-%d %H:%M")})
    reverse = order == "desc"
    if sort_by == "name":
        files.sort(key=lambda x: x["name"].lower(), reverse=reverse)
    elif sort_by == "size":
        files.sort(key=lambda x: x["size"], reverse=reverse)
    elif sort_by == "modified":
        files.sort(key=lambda x: x["modified"], reverse=reverse)
    return files


def read_md_file(filename):
    path = ROOT / filename
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def sanitize_content(content):
    for pattern in SECRET_PATTERNS:
        content = re.sub(pattern, "[REDACTED]", content)
    return content


def md_to_html(text):
    text = sanitize_content(text)
    lines = text.split("\n")
    html = []
    in_code = False
    in_table = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                html.append("</pre>")
                in_code = False
            else:
                html.append("<pre>")
                in_code = True
            continue
        if in_code:
            html.append(line)
            continue
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                html.append('<div class="tblwrap"><table>')
                in_table = True
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                continue
            tag = "th" if (html and html[-1].startswith("<div class=\"tblwrap\"><table>")) else "td"
            html.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        else:
            if in_table:
                html.append("</table></div>")
                in_table = False
            stripped = line.strip()
            if not stripped:
                html.append("<br>")
            elif stripped.startswith("# "): html.append(f"<h1>{stripped[2:]}</h1>")
            elif stripped.startswith("## "): html.append(f"<h2>{stripped[3:]}</h2>")
            elif stripped.startswith("### "): html.append(f"<h3>{stripped[4:]}</h3>")
            elif stripped.startswith("#### "): html.append(f"<h4>{stripped[5:]}</h4>")
            elif stripped.startswith("- "): html.append(f"<li>{stripped[2:]}</li>")
            elif re.match(r'^\d+\.\s', stripped): html.append(f"<li>{re.sub(r'^\d+\.\s', '', stripped)}</li>")
            elif stripped.startswith(">"): html.append(f"<blockquote>{stripped[1:].strip()}</blockquote>")
            elif stripped.startswith("---"): html.append("<hr>")
            else:
                line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
                line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', line)
                html.append(line)
    if in_table: html.append("</table></div>")
    if in_code: html.append("</pre>")
    return "\n".join(html)


def get_phases():
    return [
        ("01", "Market Collection", "DONE", "stlms/market/collection.py"),
        ("02", "Market Artifact", "DONE", "stlms/market/artifact.py"),
        ("03", "Supertrend Point", "DONE", "stlms/truth/point.py"),
        ("04", "Truth Layer", "DONE", "stlms/truth/"),
        ("05", "Supertrend Line", "DONE", "stlms/structure/line.py"),
        ("06", "Distance Layer", "DONE", "stlms/truth/point.py"),
        ("07", "Wave", "DONE", "stlms/structure/wave.py"),
        ("08", "Structure + Evidence", "DONE", "stlms/structure/cage.py, stlms/evidence/bus.py"),
        ("09-11", "Clone + Trade + Position", "DONE", "stlms/clone/engine.py"),
        ("10-11", "Statistics + BAG", "DONE", "stlms/statistics/, stlms/bag/"),
        ("11", "Knowledge", "DONE", "stlms/knowledge/engine.py"),
        ("12", "Prediction", "DONE", "stlms/prediction/engine.py"),
        ("13", "Trading Schema", "DONE", "stlms/schema/engine.py"),
        ("15", "Recommendation", "DONE", "stlms/recommendation/engine.py"),
        ("16", "Simulation", "DONE", "stlms/simulation/engine.py"),
        ("17", "Consumer", "DONE", "stlms/consumer/engine.py"),
        ("18", "Benchmark", "DONE", "stlms/bench/engine.py"),
        ("19", "Governance", "DONE", "stlms/governance/engine.py"),
        ("20", "Integration", "DONE", "stlms/integration/engine.py"),
    ]


def markdown_categories():
    return {
        "Reference": ["MASTER_SPECIFICATION.html", "DOCUMENT_DEPENDENCY.html", "QWEN_14_DOC.html",
                       "ST_LMS_CORE.js", "STLMS_SQLITE_SCHEMA_V1.sql", "01-07_IMPLEMENTATION_AUDIT.md"],
        "Phase 0 Freeze": ["REFERENCE_FREEZE.md", "COMPONENT_INVENTORY.md", "FILE_RELATIONSHIP.md",
                           "SPECIFICATION_FREEZE.md", "DEPENDENCY_FREEZE.md", "ARCHITECTURE_FREEZE.md",
                           "SQLITE_FOUNDATION_FREEZE.md", "TRADING_SCHEMA_FREEZE.md", "TRUTH_LAYER_FREEZE.md",
                           "DECISION_TREE_FREEZE.md", "BUILD_CONTRACT.md", "IMPLEMENTATION_CONTRACT.md"],
        "Architecture Mapping": ["01_SQLITE_FOUNDATION.md", "02_MARKET_LAYER.md", "03_TRUTH_LAYER.md",
                                  "04_DISTANCE_LAYER.md", "05_STRUCTURE_LAYER.md", "06_TRADING_LAYER.md",
                                  "07_STATISTICS_LAYER.md", "08_SNAPSHOT_LAYER.md", "09_SIMULATION_LAYER.md",
                                  "10_KNOWLEDGE_LAYER.md", "11_PREDICTION_LAYER.md", "12_TRADING_SCHEMA_LAYER.md",
                                  "13_GOVERNANCE_LAYER.md", "14_BENCHMARK_LAYER.md", "15_DASHBOARD_LAYER.md",
                                  "16_INTEGRATION_LAYER.md", "17_FINAL_AUDIT_LAYER.md", "18_MASTER_ARCHITECTURE_MAPPING.md"],
        "Freeze Contracts": ["01_ARCHITECTURE_FREEZE.md", "02_ARTIFACT_REGISTRY.md", "03_TRADING_CONSTITUTION.md",
                             "04_BUILD_CONTRACT.md", "05_TEST_CONTRACT.md", "06_CONSUMER_MATRIX.md",
                             "07_BUILD_RESTRICTION.md", "08_MASTER_FREEZE_CONTRACT.md"],
        "Audit": ["FINAL_STLMS_IMPLEMENTATION_VISION_AUDIT.md", "OPEN_INTEREST_AUDIT.md",
                  "mass_audit.md", "MASTER_FILE_INVENTORY.md"],
        "Contracts": ["RECOMMENDATION_LAYER_OUTPUT_CONTRACT.md", "SIMULATION_LAYER_OUTPUT_CONTRACT.md",
                      "MARKET_INTELLIGENCE_REPORT_FORMAT.md", "MINOR_REPOSITORY_CLEANUP_REPORT.md"],
        "Reports": ["MARKET_ANALYST_INTERVIEW.md", "all_fitur.md", "stlms_fitur.md",
                    "history_chat_stlms.md", "map_pull_request_mcp.md", "README.md"],
    }


# ── CSS ──────────────────────────────────────────────────────────
CSS = """
:root{--bg:#0a0e14;--bg2:#12171f;--fg:#bfc7d5;--mute:#5a6a7a;--accent:#ffb454;--green:#39bae6;--red:#fa6e83;--line:#1a2535;--hover:#1e2a3a}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--fg);line-height:1.65;padding:24px;max-width:1200px;margin:0 auto}
h1{color:var(--accent);font-size:1.5em;margin:24px 0 12px}
h2{color:var(--green);font-size:1.15em;margin:20px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{font-size:1em;margin:16px 0 6px;color:var(--fg)}
h4{font-size:.9em;margin:12px 0 4px;color:var(--mute)}
a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline;color:var(--accent)}
.nav{display:flex;flex-wrap:wrap;gap:5px;margin:16px 0}
.nav a{background:var(--bg2);padding:5px 12px;border-radius:4px;font-size:.82em;border:1px solid var(--line);white-space:nowrap}
.nav a:hover,.nav a.active{background:var(--hover);border-color:var(--green)}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:.88em}
th,td{border:1px solid var(--line);padding:7px 12px;text-align:left}
th{background:var(--bg2);color:var(--accent);font-weight:600}
tr:hover{background:var(--hover)}
.pass{color:var(--green)}.fail{color:var(--red)}.mute{color:var(--mute)}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:18px;margin:12px 0}
.card h3{margin-top:0}
pre{background:#05080c;color:var(--green);padding:14px;border-radius:6px;overflow-x:auto;font-size:.83em;line-height:1.5;border:1px solid var(--line)}
code{background:rgba(57,186,230,.12);color:var(--green);padding:1px 5px;border-radius:3px;font-size:.9em}
pre code{background:none;padding:0}
blockquote{border-left:3px solid var(--accent);padding:6px 14px;margin:8px 0;color:var(--mute);background:rgba(255,180,84,.04)}
li{margin:3px 0 3px 20px}
hr{border:none;border-top:1px solid var(--line);margin:16px 0}
footer{text-align:center;color:var(--mute);font-size:.78em;margin:40px 0 16px;border-top:1px solid var(--line);padding-top:16px}
.tblwrap{overflow-x:auto;margin:10px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.grid a{display:block;background:var(--bg2);padding:10px 14px;border-radius:6px;border:1px solid var(--line);font-size:.85em}
.grid a:hover{background:var(--hover);border-color:var(--green)}
.search{margin:12px 0}
.search input{width:100%;padding:10px 14px;background:var(--bg2);border:1px solid var(--line);border-radius:6px;color:var(--fg);font-size:.9em;outline:none}
.search input:focus{border-color:var(--accent)}
.cat-title{color:var(--accent);font-size:.9em;margin:16px 0 8px;text-transform:uppercase;letter-spacing:.05em}
.badge{display:inline-block;padding:2px 8px;border-radius:3px;font-size:.75em;margin-left:6px}
.badge-done{background:rgba(57,186,230,.15);color:var(--green)}
.badge-md{background:rgba(255,180,84,.1);color:var(--accent)}
.stats-row{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}
.stat-box{flex:1;min-width:140px;background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:14px;text-align:center}
.stat-box .num{font-size:1.8em;font-weight:700;color:var(--accent)}
.stat-box .num.green{color:var(--green)}
.stat-box .num.red{color:var(--red)}
.stat-box .label{font-size:.78em;color:var(--mute);margin-top:4px}
.refresh-bar{display:flex;align-items:center;gap:8px;font-size:.8em;color:var(--mute);margin:8px 0}
.refresh-bar input{width:60px;background:var(--bg2);border:1px solid var(--line);border-radius:4px;color:var(--fg);padding:4px 8px;text-align:center}
@media(max-width:768px){body{padding:12px}.nav{flex-direction:column}.stat-box{min-width:100px}}
"""

# ── Sidebar Navigation ────────────────────────────────────────────
NAV_LINKS = [
    ("/", "Dashboard"),
    ("/observation", "Observation"),
    ("/statistics", "Statistics"),
    ("/evolution", "Evolution"),
    ("/timeline", "Timeline"),
    ("/knowledge", "Knowledge"),
    ("/prediction", "Prediction"),
    ("/simulation", "Simulation"),
    ("/recommendation", "Recommendation"),
    ("/snapshot", "Snapshot"),
    ("/dna", "DNA"),
    ("/lifecycle", "Lifecycle"),
    ("/mutation", "Mutation"),
    ("/pipeline", "Pipeline"),
    ("/health-page", "Health"),
    ("/sqlite", "SQLite"),
    ("/config", "Config"),
    ("/markdown", "Docs"),
]


def nav_html(current_path):
    parts = []
    for href, label in NAV_LINKS:
        active = ' class="active"' if current_path == href else ''
        parts.append(f'<a href="{href}"{active}>{label}</a>')
    return '<div class="nav">' + ''.join(parts) + '</div>'


def refresh_bar_html(refresh_sec=0):
    if refresh_sec > 0:
        return f'<div class="refresh-bar">Auto-refresh: {refresh_sec}s <input type="number" id="refreshInput" value="{refresh_sec}" onchange="setRefresh(this.value)"> <button onclick="toggleRefresh()" id="refreshBtn">Pause</button><span id="countdown"></span></div>'
    return '<div class="refresh-bar">Auto-refresh: off <input type="number" id="refreshInput" value="30" onchange=""> <button onclick="toggleRefresh()" id="refreshBtn">Start</button></div>'


REFRESH_SCRIPT = """
<script>
var _t=null,_s=%d;
function setRefresh(v){_s=parseInt(v)||0;if(_t){clearInterval(_t);_t=null;}if(_s>0){startCountdown();_t=setInterval(function(){location.reload();},_s*1000);}}
function toggleRefresh(){if(_t){clearInterval(_t);_t=null;document.getElementById('refreshBtn').textContent='Start';document.getElementById('countdown').textContent='';}else{setRefresh(document.getElementById('refreshInput').value);document.getElementById('refreshBtn').textContent='Pause';}}
function startCountdown(){var c=_s;var el=document.getElementById('countdown');el.textContent='('+c+'s)';var ci=setInterval(function(){c--;if(c<=0||!_t){clearInterval(ci);return;}el.textContent='('+c+'s)';},1000);}
if(_s>0){setRefresh(_s);document.getElementById('refreshBtn').textContent='Pause';}
</script>
"""


def page(title, body, current_path="/", refresh_sec=0):
    nav = nav_html(current_path)
    rbar = refresh_bar_html(refresh_sec)
    rscript = REFRESH_SCRIPT % refresh_sec
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ST-LMS — {title}</title><style>{CSS}</style></head><body>
<h1>ST-LMS Market Evolution OS</h1>{nav}{rbar}<h2>{title}</h2>{body}{rscript}
<footer>ST-LMS Data Viewer v2.0 · {wib_now()} · Read Only · Zero Dependencies · Port 8082</footer></body></html>"""


# ═══════════════════════════════════════════════════════════════════
#  PAGE BUILDERS — each returns HTML body string
# ═══════════════════════════════════════════════════════════════════

def build_dashboard():
    shell, err = get_shell()
    stats = repo_stats()
    sql = sqlite_stats()

    body = '<div class="stats-row">'

    # Shell status
    if shell is not None:
        st = shell.status()
        body += stat_box(len(shell._truth_points), "Truth Points")
        body += stat_box(len(shell._lines), "Structure Lines")
        body += stat_box(len(shell._waves), "Waves")
        body += stat_box(len(shell._markers), "Trade Markers")
        body += stat_box(len(shell._bag_artifacts), "BAG Artifacts")
        body += stat_box(st.get("stages_executed", 0), "Pipeline Stages")
    else:
        body += stat_box("—", "Shell Error", "red")
        body += stat_box(err or "?", "Error Detail", "red")

    body += stat_box(stats['total_files'], "Total Files")
    body += stat_box(sql.get('tables', '?'), "SQLite Tables")
    body += stat_box(stats['py_files'], "Python Modules")
    body += stat_box(stats['md_files'], "Documents")
    body += stat_box("20", "Phases (ALL DONE)")
    body += '</div>'

    # Status card
    if shell is not None:
        st = shell.status()
        health = shell.health()
        body += '<div class="card"><h3>System Status</h3>'
        body += f'<p>Status: <b class="{"pass" if st.get("status")=="OK" else "fail"}">{st.get("status","?")}</b></p>'
        body += f'<p>Symbol: <b>{st.get("symbol","?")}</b> · Timeframe: <b>{st.get("timeframe","?")}</b></p>'
        body += f'<p>Memory: <b>{st.get("memory_observations",0)}</b> / {st.get("memory_max",0)} observations</p>'
        body += f'<p>Snapshots: <b>{st.get("snapshot_cards",0)}</b> cards ({st.get("snapshot_types",0)} types)</p>'
        body += f'<p>Market DNA: <b class="{"pass" if st.get("market_dna_available") else "mute"}">{st.get("market_dna_available","N/A")}</b></p>'
        body += f'<p>Healthy: <b class="{"pass" if health.get("healthy") else "fail"}">{health.get("healthy","?")}</b></p>'
        body += '</div>'

        # Quick stats from shell
        pred = shell.prediction_current()
        if pred.get("available"):
            body += card_html("Latest Prediction",
                              f'<p>Dominant Bias: <b>{pred.get("dominant_bias","N/A")}</b></p>'
                              f'<p>Intelligence Score: <b>{pred.get("intelligence_score","N/A")}</b></p>')

        dna = shell.market_dna()
        if dna.get("available"):
            char = dna.get("market_character", {})
            body += card_html("Market Character",
                              f'<p>Type: <b>{char.get("type", dna.get("character","N/A"))}</b></p>')

    # SQLite + files
    body += f'<div class="card"><h3>Infrastructure</h3>'
    body += f'<p>SQLite: <b class="{"pass" if sql.get("integrity")=="ok" else "fail"}">{sql.get("integrity","?")}</b> · Size: {(sql.get("size_bytes",0)//1024)} KB · Tables: {sql.get("tables","?")}</p>'
    body += f'<p>Repository: {stats["total_files"]} files · Last Update: {stats["last_update"]}</p>'
    body += '</div>'

    if err:
        body += f'<div class="card"><h3>Shell Error</h3><p class="fail">{err}</p></div>'

    return body


def build_observation():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""
    truth = shell.truth_current()
    if truth.get("available"):
        body += card_html("Current TruthPoint", dict_to_html_table(truth))

    structure = shell.structure_summary()
    if structure.get("available"):
        body += card_html("Structure Summary", dict_to_html_table(structure))

    wave = shell.wave_current()
    if wave.get("available"):
        body += card_html("Current Wave", dict_to_html_table(wave))

    cage = shell.cage_current()
    if cage.get("available"):
        body += card_html("Current Cage", dict_to_html_table(cage))

    distance = shell.distance_summary()
    if distance.get("available"):
        body += card_html("Distance Metrics", dict_to_html_table(distance))

    # Memory stats
    mem = shell._memory if hasattr(shell, '_memory') else None
    if mem:
        mem_stats = mem.stats() if hasattr(mem, 'stats') else {}
        body += card_html("Observation Memory",
                          f'<p>Size: <b>{mem_stats.get("current_size", mem.size)}</b> / {mem_stats.get("max_size", mem.max_size)}</p>'
                          f'<p>Total Observations: <b>{mem_stats.get("total_observations", mem.total_observations)}</b></p>'
                          f'<p>Full: <b class="{"pass" if not mem_stats.get("is_full") else "fail"}">{mem_stats.get("is_full", False)}</b></p>')

    # Events
    events = shell.truth_events()
    if events:
        rows = "".join(f'<tr><td>{e["ts"]}</td><td>{e["st"]}</td><td>{e["close"]}</td><td>{e["flip"]}</td></tr>' for e in events[:30])
        body += f'<div class="card"><h3>Flip Events ({len(events)})</h3><div class="tblwrap"><table><tr><th>ts</th><th>st</th><th>close</th><th>flip</th></tr>{rows}</table></div></div>'

    if not body:
        body = no_data_html()
    return body


def build_statistics():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""
    domains = [
        ("evolution", "Evolution Statistics", shell.evolution_statistics),
        ("indicator", "Indicator Statistics", shell.indicator_statistics),
        ("market", "Market Statistics", shell.market_statistics),
        ("clone_stats", "Clone Statistics", shell.clone_statistics),
        ("correlation", "Correlation Statistics", shell.correlation_statistics),
        ("distance", "Distance Statistics", shell.distance_statistics),
        ("oi", "OI Statistics", shell.oi_statistics),
    ]

    for key, title, method in domains:
        try:
            data = method()
            if data.get("available"):
                body += card_html(title, dict_to_html_table(data))
            else:
                body += card_html(title, '<p class="mute">N/A</p>')
        except Exception as e:
            body += card_html(title, f'<p class="fail">Error: {e}</p>')

    # Clone statistics
    for clone_id in ("LONG", "SHORT", "GRID"):
        try:
            stats = shell.statistics_clone(clone_id)
            if stats.get("available"):
                body += card_html(f"Clone: {clone_id}", dict_to_html_table(stats))
            else:
                body += card_html(f"Clone: {clone_id}", '<p class="mute">N/A</p>')
        except Exception as e:
            body += card_html(f"Clone: {clone_id}", f'<p class="fail">Error: {e}</p>')

    if not body:
        body = no_data_html()
    return body


def build_evolution():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""

    # Evolution statistics
    try:
        evo = shell.evolution_statistics()
        if evo.get("available"):
            body += card_html("Evolution Domain", dict_to_html_table(evo))
        else:
            body += no_data_html("No evolution data")
    except Exception as e:
        body += no_data_html(str(e))

    # Lifecycle info from truth points
    if shell._truth_points:
        last_tp = shell._truth_points[-1]
        lifecycle_info = {}
        if hasattr(last_tp, 'point_status'):
            lifecycle_info["point_status"] = str(last_tp.point_status)
        body += card_html("Latest TruthPoint Lifecycle", dict_to_html_table(lifecycle_info))

    # Version info
    if shell._waves:
        last_wave = shell._waves[-1]
        wave_info = {
            "structure": last_wave.structure if hasattr(last_wave, 'structure') else "N/A",
            "status": last_wave.status if hasattr(last_wave, 'status') else "N/A",
            "line_count": len(last_wave.lines) if hasattr(last_wave, 'lines') else 0,
        }
        body += card_html("Current Wave Version", dict_to_html_table(wave_info))

    # Mutation data from memory observations
    if hasattr(shell, '_memory') and hasattr(shell._memory, '_buffer'):
        mutations = []
        for obs in shell._memory._buffer[-20:]:
            md = obs.get("mutation_delta", {})
            ver = obs.get("version", 0)
            mc = obs.get("mutation_count", 0)
            if mc > 0:
                mutations.append({
                    "observation_id": obs.get("observation_id", "?"),
                    "version": ver,
                    "mutation_count": mc,
                    "mutation_delta": str(md)[:80],
                })
        if mutations:
            rows = "".join(f'<tr><td>{m["observation_id"]}</td><td>{m["version"]}</td><td>{m["mutation_count"]}</td><td class="mute">{m["mutation_delta"]}</td></tr>' for m in mutations)
            body += f'<div class="card"><h3>Recent Mutations ({len(mutations)})</h3><div class="tblwrap"><table><tr><th>Observation</th><th>Version</th><th>Mutations</th><th>Delta</th></tr>{rows}</table></div></div>'

    if not body:
        body = no_data_html()
    return body


def build_timeline():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    qs = {}
    try:
        from urllib.parse import parse_qs, urlparse
        qs = parse_qs(urlparse(f"http://x/?{''}").query)
    except:
        pass

    # Range selector
    total = len(shell._truth_points)
    start = 0
    end = min(50, total)

    body = f'<div class="card"><h3>Timeline Range Selector</h3>'
    body += f'<p>Total Observations: <b>{total}</b></p>'
    body += f'<p>Showing: candle {start} to {end}</p>'
    body += f'<p class="mute">Use /api/timeline?start=0&end=200 for programmatic access</p>'
    body += '</div>'

    if total == 0:
        body += no_data_html("No truth points available")
        return body

    # Show first 50 observations
    timeline = shell.get_timeline(start, end)
    if not timeline:
        body += no_data_html("No observations in range")
        return body

    rows = ""
    for obs in timeline:
        t = obs.get("truth", {})
        rows += f'<tr><td>{obs.get("candle_index","?")}</td><td>{obs.get("timestamp","?")}</td><td>{_safe(t.get("close"))}</td><td>{_safe(t.get("st"))}</td><td>{_safe(t.get("st_dir"))}</td><td>{_safe(t.get("st_color"))}</td><td>{_safe(t.get("rsi"))}</td><td>{_safe(t.get("wpr"))}</td><td>{_safe(t.get("dist_atr"))}</td><td>{_safe(t.get("point_status"))}</td></tr>'

    body += f'<div class="tblwrap"><table><tr><th>#</th><th>ts</th><th>close</th><th>st</th><th>st_dir</th><th>st_color</th><th>rsi</th><th>wpr</th><th>dist_atr</th><th>status</th></tr>{rows}</table></div>'

    # Also show truth points table for compatibility
    try:
        tp_data = shell.truth_timeline(0, 9_999_999_999_999)
        if tp_data:
            displayed = tp_data[:50]
            trows = ""
            for row in displayed:
                trows += '<tr>' + ''.join(f'<td>{_safe(row.get(k))}</td>' for k in ["ts","close","st","st_dir","st_color","atr","ema","rsi","wpr","macd_hist","dist","dist_atr","flip","point_status"]) + '</tr>'
            body += f'<h3>Truth Timeline Raw ({len(tp_data)} total, showing {len(displayed)})</h3><div class="tblwrap"><table><tr><th>ts</th><th>close</th><th>st</th><th>st_dir</th><th>st_color</th><th>atr</th><th>ema</th><th>rsi</th><th>wpr</th><th>macd_hist</th><th>dist</th><th>dist_atr</th><th>flip</th><th>status</th></tr>{trows}</table></div>'
    except Exception as e:
        body += f'<p class="mute">Truth timeline raw: {e}</p>'

    return body


def build_knowledge():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""

    # Academy
    try:
        academy = shell.knowledge_academy()
        if academy:
            body += card_html("Academy — Empirical Learning", dict_to_html_table(academy))
        else:
            body += card_html("Academy", '<p class="mute">N/A — No learning data</p>')
    except Exception as e:
        body += card_html("Academy", f'<p class="fail">Error: {e}</p>')

    # Oracle
    try:
        oracle = shell.knowledge_oracle()
        if oracle:
            body += card_html("Oracle — Similarity Match", dict_to_html_table(oracle))
        else:
            body += card_html("Oracle", '<p class="mute">N/A</p>')
    except Exception as e:
        body += card_html("Oracle", f'<p class="fail">Error: {e}</p>')

    # HiveMind
    try:
        hivemind = shell.knowledge_hivemind()
        if hivemind:
            body += card_html("HiveMind — Synthesis", dict_to_html_table(hivemind))
        else:
            body += card_html("HiveMind", '<p class="mute">N/A</p>')
    except Exception as e:
        body += card_html("HiveMind", f'<p class="fail">Error: {e}</p>')

    # CERMIN + Darwin from knowledge dict
    if hasattr(shell, '_knowledge') and shell._knowledge:
        for ktype in ["cermin", "darwin", "river", "librarian"]:
            if ktype in shell._knowledge:
                body += card_html(f"{ktype.title()}", dict_to_html_table(shell._knowledge[ktype]))

    # BAG artifacts summary
    if shell._bag_artifacts:
        bag_summary = []
        for ba in shell._bag_artifacts[:20]:
            bag_summary.append({
                "bag_id": getattr(ba, 'bag_id', '?'),
                "kind": str(getattr(ba, 'bag_kind', '?')),
                "consensus": getattr(ba, 'consensus', 'N/A'),
                "win_rate": getattr(ba, 'win_rate', 0),
                "confidence": getattr(ba, 'confidence', 0),
                "maturity": getattr(ba, 'maturity_score', 0),
            })
        body += card_html(f"BAG Artifacts ({len(shell._bag_artifacts)})", dict_to_html_table(bag_summary))

    if not body:
        body = no_data_html()
    return body


def build_prediction():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    try:
        data = shell.prediction_current()
        if not data.get("available"):
            return no_data_html()

        body = ""
        body += card_html("Market Possibility Prediction", dict_to_html_table(data))

        # Possibilities table
        possibilities = data.get("possibilities", [])
        if possibilities:
            prows = "".join(
                f'<tr><td>{p.get("type","?")}</td><td>{p.get("probability",0)}</td><td>{p.get("confidence","N/A")}</td></tr>'
                for p in possibilities)
            body += f'<div class="card"><h3>Possibilities</h3><div class="tblwrap"><table><tr><th>Type</th><th>Probability</th><th>Confidence</th></tr>{prows}</table></div></div>'

        # Evolution context in prediction
        evo_ctx = data.get("evolution_context", {})
        if evo_ctx:
            body += card_html("Evolution Context", dict_to_html_table(evo_ctx))

        # Market DNA in prediction
        dna = data.get("market_dna", {})
        if dna:
            body += card_html("Market DNA Context", dict_to_html_table(dna))

        return body
    except Exception as e:
        return no_data_html(str(e))


def build_simulation():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    try:
        data = shell.simulation_results()
        if not data.get("available"):
            return no_data_html(data.get("error"))

        body = ""
        simulators = [
            ("architecture", "Architecture Simulator"),
            ("market_possibility", "Market Possibility Simulator"),
            ("market_push", "Market Push Simulator"),
            ("knowledge", "Knowledge Simulator"),
            ("balance", "Balance Simulator"),
        ]
        for key, title in simulators:
            if key in data:
                body += card_html(title, dict_to_html_table(data[key]))
            else:
                body += card_html(title, '<p class="mute">N/A</p>')

        return body
    except Exception as e:
        return no_data_html(str(e))


def build_recommendation():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    try:
        data = shell.recommendation_report()
        if not data.get("available"):
            return no_data_html()

        body = card_html("Market Intelligence Report", dict_to_html_table(data))

        # Key sections extracted
        sections = ["market_character", "decision_tree", "recommended_action",
                     "evolution_stats", "structure_stats", "wave_stats",
                     "observation_memory", "market_dna"]
        for sec in sections:
            if sec in data and data[sec]:
                body += card_html(sec.replace("_", " ").title(), dict_to_html_table(data[sec]))

        return body
    except Exception as e:
        return no_data_html(str(e))


def build_snapshot():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    qs = {}
    try:
        parsed = urllib.parse.urlparse(f"http://x/")
        qs = {}
    except:
        pass

    body = ""
    try:
        snaps = shell.snapshots()
        body += card_html("Snapshot Registry", dict_to_html_table(snaps))
    except Exception as e:
        body += no_data_html(str(e))

    # Query SQLite snapshots table
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            total_snaps = conn.execute("SELECT COUNT(*) as cnt FROM snapshots").fetchone()["cnt"]
            by_type = conn.execute(
                "SELECT entity_type, COUNT(*) as cnt FROM snapshots GROUP BY entity_type ORDER BY cnt DESC"
            ).fetchall()
            recent = conn.execute(
                "SELECT entity_id, entity_type, entity_state, timestamp_ms FROM snapshots ORDER BY timestamp_ms DESC LIMIT 20"
            ).fetchall()
            conn.close()

            body += f'<div class="card"><h3>Persisted Snapshots ({total_snaps} total)</h3>'
            body += '<h4>By Type</h4><div class="tblwrap"><table><tr><th>Type</th><th>Count</th></tr>'
            for bt in by_type:
                body += f'<tr><td>{bt["entity_type"]}</td><td>{bt["cnt"]}</td></tr>'
            body += '</table></div>'

            if recent:
                body += '<h4>Recent Snapshots</h4><div class="tblwrap"><table><tr><th>ID</th><th>Type</th><th>State</th><th>Timestamp</th></tr>'
                for r in recent:
                    body += f'<tr><td class="mute">{r["entity_id"][:20]}...</td><td>{r["entity_type"]}</td><td>{r["entity_state"]}</td><td>{r["timestamp_ms"]}</td></tr>'
                body += '</table></div>'
            body += '</div>'
        except Exception as e:
            body += f'<p class="mute">SQLite snapshots: {e}</p>'

    return body


def build_dna():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""
    try:
        dna = shell.market_dna()
        if dna.get("available"):
            body += card_html("Market DNA Profile", dict_to_html_table(dna))

            # Wave distribution
            wave_dist = dna.get("wave_distribution", {})
            if wave_dist:
                wrows = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in wave_dist.items())
                body += f'<div class="card"><h3>Wave Distribution</h3><div class="tblwrap"><table><tr><th>Structure</th><th>Count</th></tr>{wrows}</table></div></div>'

            # Cage distribution
            cage_dist = dna.get("cage_distribution", {})
            if cage_dist:
                crows = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in cage_dist.items())
                body += f'<div class="card"><h3>Cage Distribution</h3><div class="tblwrap"><table><tr><th>Status</th><th>Count</th></tr>{crows}</table></div></div>'

            # Market character
            char = dna.get("market_character", {})
            if char:
                body += card_html("Market Character", dict_to_html_table(char))
        else:
            body += no_data_html("No DNA data available")
    except Exception as e:
        body += no_data_html(str(e))

    return body


def build_lifecycle():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""
    try:
        evo = shell.evolution_statistics()
        if evo.get("available"):
            truth = evo.get("truth", {})
            line = evo.get("line", {})
            wave = evo.get("wave", {})
            cage = evo.get("cage", {})

            body += card_html("Truth Lifecycle", dict_to_html_table(truth))
            body += card_html("Line Lifecycle", dict_to_html_table(line))
            body += card_html("Wave Lifecycle", dict_to_html_table(wave))
            body += card_html("Cage Lifecycle", dict_to_html_table(cage))
        else:
            body += no_data_html("No lifecycle data")
    except Exception as e:
        body += no_data_html(str(e))

    return body


def build_mutation():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""
    try:
        evo = shell.evolution_statistics()
        if evo.get("available"):
            truth = evo.get("truth", {})
            body += card_html("Mutation Statistics", dict_to_html_table({
                "flip_rate": truth.get("flip_rate", "N/A"),
                "mutation_rate": truth.get("mutation_rate", "N/A"),
                "survival_rate": truth.get("survival_rate", "N/A"),
            }))
        else:
            body += no_data_html("No mutation data")
    except Exception as e:
        body += no_data_html(str(e))

    # Per-observation mutation from memory
    if hasattr(shell, '_memory') and hasattr(shell._memory, '_buffer'):
        mut_rows = ""
        for obs in shell._memory._buffer[-30:]:
            mc = obs.get("mutation_count", 0)
            ver = obs.get("version", 0)
            rel = obs.get("reliability", {})
            mut_rows += f'<tr><td>{obs.get("observation_id","?")}</td><td>{ver}</td><td>{mc}</td><td>{_safe(rel.get("score") if isinstance(rel, dict) else rel)}</td><td class="mute">{str(obs.get("mutation_delta",{}))[:60]}</td></tr>'
        if mut_rows:
            body += f'<div class="card"><h3>Observation Mutation Log</h3><div class="tblwrap"><table><tr><th>Observation</th><th>Version</th><th>Mutations</th><th>Reliability</th><th>Delta</th></tr>{mut_rows}</table></div></div>'

    return body


def build_pipeline():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""

    # Pipeline status from shell
    try:
        data = shell.pipeline_status()
        if data.get("available"):
            body += card_html("Pipeline Execution", dict_to_html_table(data))
        else:
            body += card_html("Pipeline Status",
                              f'<p>Stages Executed: <b>{data.get("stages_executed",0)}</b> / {data.get("stages_total",0)}</p>'
                              f'<p>Verdict: <b>{data.get("verdict","NOT_RUN")}</b></p>')
    except Exception as e:
        body += card_html("Pipeline Status", f'<p class="fail">Error: {e}</p>')

    # Stage list (static reference)
    stages = [("0", "ONCE", "BOOT", "BOOT"),
              ("1", "SHARED", "MARKET OBSERVATION", "MARKET"),
              ("2", "SHARED", "TRUTH LAYER", "TRUTH"),
              ("3", "SHARED", "STRUCTURE LAYER", "STRUCTURE"),
              ("4", "SHARED", "EVIDENCE LAYER", "EVIDENCE"),
              ("5", "PER-CLONE x3", "CLONE OBSERVATION", "CLONE"),
              ("6", "PER-CLONE x3", "ENTRY VALIDATION", "TRADE"),
              ("7", "PER-CLONE x3", "POSITION MGMT", "POSITION"),
              ("8", "PER-CLONE x3", "PROFIT MGMT", "POSITION"),
              ("9", "PER-CLONE x3", "EXIT VALIDATION", "TRADE"),
              ("10", "PER-CLONE x3", "CLOSE POSITION", "TRADE"),
              ("11", "PER-CLONE x3", "TRADE MARKER", "TRADE"),
              ("12", "SHARED-AGAIN", "STATISTICS", "STATISTICS"),
              ("13", "SHARED-AGAIN", "BAG", "BAG"),
              ("14", "SHARED-AGAIN", "RIVER", "KNOWLEDGE"),
              ("15", "ON-DEMAND", "BENCHMARK", "BENCHMARK"),
              ("16", "SHARED-AGAIN", "ACADEMY", "KNOWLEDGE"),
              ("17", "SHARED-AGAIN", "ORACLE", "KNOWLEDGE"),
              ("18", "SHARED-AGAIN", "HIVEMIND", "KNOWLEDGE"),
              ("19", "SHARED-AGAIN", "CERMIN", "KNOWLEDGE"),
              ("20", "SHARED-AGAIN", "DARWIN", "KNOWLEDGE"),
              ("21", "SHARED-AGAIN", "PREDICTION", "PREDICTION"),
              ("22", "SHARED-AGAIN", "GOVERNANCE", "GOVERNANCE"),
              ("OPT", "OPTIONAL", "CONSUMER", "CONSUMER")]
    srows = "".join(f'<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td></tr>' for s in stages)
    body += f'<div class="card"><h3>Pipeline Stages (23 + OPT)</h3><div class="tblwrap"><table><tr><th>Stage</th><th>Type</th><th>Name</th><th>Owner</th></tr>{srows}</table></div></div>'

    return body


def build_health_page():
    shell, err = get_shell()
    body = ""

    # System checks
    stats = repo_stats()
    sql = sqlite_stats()
    body += '<div class="card"><h3>Infrastructure Health</h3>'
    body += f'<p>SQLite: <b class="{"pass" if sql.get("integrity")=="ok" else "fail"}">{sql.get("integrity","?")}</b> · Size: {(sql.get("size_bytes",0)//1024)} KB</p>'
    body += f'<p>DB Path: <code>stlms.db</code> (exists: <b class="{"pass" if DB_PATH.exists() else "fail"}">{DB_PATH.exists()}</b>)</p>'
    body += f'<p>Repository: {stats["total_files"]} files, {stats["py_files"]} python modules</p>'
    body += f'<p>Server Time: {wib_now()}</p>'
    body += '</div>'

    if shell is not None:
        health = shell.health()
        body += card_html("Shell Health", dict_to_html_table(health))

        st = shell.status()
        body += card_html("Shell Status", dict_to_html_table(st))
    else:
        body += f'<div class="card"><h3>Shell</h3><p class="fail">Shell not available: {err or "Unknown error"}</p></div>'

    # Phases status
    phases = get_phases()
    prows = "".join(f'<tr><td>{p[0]}</td><td>{p[1]}</td><td class="pass">{p[2]}</td><td class="mute">{p[3]}</td></tr>' for p in phases)
    body += f'<div class="card"><h3>Implementation Phases</h3><div class="tblwrap"><table><tr><th>#</th><th>Name</th><th>Status</th><th>Module</th></tr>{prows}</table></div></div>'

    return body


def build_config():
    shell, err = get_shell()
    if shell is None:
        return no_data_html(err or "STLMSShell not available")

    body = ""
    try:
        config = shell.config
        params = config.all_params()
        body += card_html(f"Bounded Parameters ({len(params)})", dict_to_html_table(params))

        snapshot = config.snapshot()
        body += card_html("Configuration Snapshot", dict_to_html_table(snapshot))
    except Exception as e:
        body += no_data_html(str(e))

    return body


# ═══════════════════════════════════════════════════════════════════
#  HTTP HANDLER
# ═══════════════════════════════════════════════════════════════════

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def serve_html(self, title, body, path="/", refresh=0):
        html = page(title, body, path, refresh)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_json(self, data):
        j = json.dumps(data, indent=2, default=str)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(j.encode())

    def serve_md_page(self, filename):
        content = read_md_file(filename)
        if content is None:
            self.send_error(404)
            return
        html_content = md_to_html(content)
        self.serve_html(f"{filename}", f"<div class=\"card\">{html_content}</div><p class=\"mute\"><a href=\"/markdown\">← Back to Markdown</a></p>",
                        "/markdown")

    def _content_type(self, filename):
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return {"md": "text/markdown", "txt": "text/plain", "json": "application/json",
                "html": "text/html", "csv": "text/csv", "sql": "text/plain"}.get(ext, "text/plain")

    def _find_file(self, filename):
        for d in [ROOT, ROOT / "data_viewer/data-html"]:
            p = d / filename
            if p.exists():
                return p
        return None

    def serve_raw_file(self, filename):
        fpath = self._find_file(filename)
        if fpath is None:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            body = f"404 DOCUMENT NOT FOUND\n\nRequested File:\n{filename}\n\nSuggestions:\n- /docs-index\n- /health\n- /ping\n"
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())
            return
        content = sanitize_content(fpath.read_text(encoding="utf-8", errors="replace"))
        ct = self._content_type(filename)
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(content.encode())))
        self.end_headers()
        self.wfile.write(content.encode())

    def _get_refresh(self):
        try:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            return int(qs.get("refresh", [0])[0])
        except:
            return 0

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        refresh = self._get_refresh()

        # ── PING / HEALTH ────────────────────────────────────────
        if path == "/ping":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            body = "ST-LMS DATA VIEWER ONLINE\n\nversion : v4-5\nstatus : online\nproxy : OK\nruntime : OK\nhttps : OK\n"
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())
            return

        if path == "/health":
            stats = repo_stats()
            self.serve_json({"service": "ST-LMS Data Viewer", "status": "online", "version": "v4-5",
                             "https": "OK", "proxy": "OK", "runtime": "OK",
                             "documents": stats["md_files"],
                             "html_reports": len(list((ROOT / "data_viewer/data-html").glob("*.html"))),
                             "python_modules": stats["py_files"]})
            return

        # ── DOCS INDEX ────────────────────────────────────────────
        if path == "/docs-index":
            all_files = list_md_files()
            html_files = list((ROOT / "data_viewer/data-html").glob("*.html"))
            body = "AVAILABLE DOCUMENTS\n\n"
            seen = set()
            for f in all_files:
                name = f["name"]
                if name in seen:
                    continue
                seen.add(name)
                body += f"- {name}\n"
                base = name.rsplit(".", 1)[0]
                for ext in [".html", ".json"]:
                    hname = base + ext
                    if hname not in seen and any(h.name == hname for h in html_files):
                        body += f"- {hname}\n"
                        seen.add(hname)
            body += f"\nTotal: {len(all_files)} documents\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())
            return

        # ── RAW FILE ──────────────────────────────────────────────
        if path.startswith("/raw/"):
            self.serve_raw_file(path[5:])
            return

        # ── MULTI-FORMAT DOCS ─────────────────────────────────────
        if path.startswith("/docs/"):
            filename = path[6:]
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext in ("txt", "json", "csv", "sql"):
                base = filename.rsplit(".", 1)[0]
                md_file = self._find_file(base + ".md")
                if md_file and ext == "txt":
                    content = sanitize_content(md_file.read_text(encoding="utf-8", errors="replace"))
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(content.encode())))
                    self.end_headers()
                    self.wfile.write(content.encode())
                    return
                if md_file and ext == "json":
                    content = sanitize_content(md_file.read_text(encoding="utf-8", errors="replace"))
                    self.serve_json({"filename": base + ".md", "content": content, "format": "markdown",
                                     "source": "ST-LMS Data Viewer"})
                    return
            if ext == "html":
                html_path = ROOT / "data_viewer/data-html" / filename
                if html_path.exists():
                    content = html_path.read_text(encoding="utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(content.encode())))
                    self.end_headers()
                    self.wfile.write(content.encode())
                    return
            self.serve_md_page(filename)
            return

        # ── MARKDOWN VIEWER ───────────────────────────────────────
        if path == "/markdown":
            sort_by = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("sort", ["name"])[0]
            order = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("order", ["asc"])[0]
            cats = markdown_categories()
            all_files = list_md_files(sort_by, order)
            all_names = {f["name"] for f in all_files}

            def sort_link(col, label):
                next_order = "desc" if sort_by == col and order == "asc" else "asc"
                arrow = " ▲" if sort_by == col and order == "asc" else (" ▼" if sort_by == col and order == "desc" else "")
                return f'<a href="/markdown?sort={col}&order={next_order}" style="color:var(--accent);font-weight:600">{label}{arrow}</a>'

            body = f"""<div class="card" style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">
<div class="search" style="flex:1;min-width:200px"><input type="text" id="search" placeholder="Search {len(all_files)} documents..." oninput="filterDocs()"></div>
<div style="display:flex;gap:10px;font-size:.85em">
Sort: {sort_link('name','Name')} | {sort_link('modified','Date')} | {sort_link('size','Size')}
</div></div>"""

            body += '<div class="tblwrap"><table id="doctable"><tr><th>File</th><th>Date Modified</th><th>Size</th><th>Path</th></tr>'
            for f in all_files:
                size_kb = f["size"] // 1024
                body += f'<tr class="doc-link"><td><a href="/docs/{f["name"]}"><b>{f["name"]}</b></a></td><td class="mute">{f["modified_str"]}</td><td>{size_kb} KB</td><td class="mute">{f["path"]}</td></tr>'
            body += '</table></div>'

            body += '<h3>By Category</h3>'
            for cat, files in cats.items():
                existing = [f for f in files if f in all_names]
                if not existing:
                    continue
                body += f'<div class="cat-title">{cat} ({len(existing)})</div><div class="grid cat-group">'
                for f in existing:
                    info = next((x for x in all_files if x["name"] == f), None)
                    size_kb = info["size"] // 1024 if info else 0
                    mod = info["modified_str"] if info else ""
                    body += f'<a href="/docs/{f}" class="doc-link"><b>{f}</b><br><span class="mute">{mod} · {size_kb} KB</span></a>'
                body += '</div>'
            body += """<script>
function filterDocs(){var q=document.getElementById('search').value.toLowerCase();
document.querySelectorAll('.doc-link').forEach(function(a){
a.style.display=a.textContent.toLowerCase().includes(q)?'':'none';});
document.querySelectorAll('.cat-group').forEach(function(g){
var visible=g.querySelectorAll('.doc-link[style*="display: none"]').length!=g.querySelectorAll('.doc-link').length;
g.previousElementSibling.style.display=visible?'':'none';g.style.display=visible?'':'none';});}
</script>"""
            self.serve_html(f"Markdown Viewer ({len(all_files)} documents)", body, "/markdown")
            return

        # ── DATA-HTML ────────────────────────────────────────────
        if path == "/data-html":
            html_dir = ROOT / "data_viewer" / "data-html"
            files = sorted(html_dir.glob("*.html"))
            body = f"<h3>HTML Reports ({len(files)})</h3><p class=\"mute\">Generated from Markdown documents for rich viewing.</p><div class=\"grid\">"
            for f in files:
                size_kb = f.stat().st_size // 1024
                body += f'<a href="/data-html/{f.name}"><b>{f.name}</b><br><span class="mute">{size_kb} KB</span></a>'
            if not files:
                body += '<p class="mute">No HTML reports yet.</p>'
            body += "</div>"
            self.serve_html("HTML Reports", body, "/data-html")
            return

        if path.startswith("/data-html/"):
            filename = path[11:]
            html_path = ROOT / "data_viewer" / "data-html" / filename
            if not html_path.exists():
                self.send_error(404)
                return
            content = html_path.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content.encode())))
            self.end_headers()
            self.wfile.write(content.encode())
            return

        # ═══════════════════════════════════════════════════════════
        #  MAIN PAGES
        # ═══════════════════════════════════════════════════════════

        if path == "/":
            self.serve_html("Dashboard", build_dashboard(), "/", refresh)
            return

        if path == "/observation":
            self.serve_html("Market Observation", build_observation(), "/observation", refresh)
            return

        if path == "/statistics":
            self.serve_html("Statistics", build_statistics(), "/statistics", refresh)
            return

        if path == "/evolution":
            self.serve_html("Evolution", build_evolution(), "/evolution", refresh)
            return

        if path == "/timeline":
            self.serve_html("Timeline", build_timeline(), "/timeline", refresh)
            return

        if path == "/knowledge":
            self.serve_html("Knowledge", build_knowledge(), "/knowledge", refresh)
            return

        if path == "/prediction":
            self.serve_html("Prediction", build_prediction(), "/prediction", refresh)
            return

        if path == "/simulation":
            self.serve_html("Simulation", build_simulation(), "/simulation", refresh)
            return

        if path == "/recommendation":
            self.serve_html("Recommendation", build_recommendation(), "/recommendation", refresh)
            return

        if path == "/snapshot":
            self.serve_html("Snapshot", build_snapshot(), "/snapshot", refresh)
            return

        if path == "/dna":
            self.serve_html("Market DNA", build_dna(), "/dna", refresh)
            return

        if path == "/lifecycle":
            self.serve_html("Lifecycle", build_lifecycle(), "/lifecycle", refresh)
            return

        if path == "/mutation":
            self.serve_html("Mutation", build_mutation(), "/mutation", refresh)
            return

        if path == "/pipeline":
            self.serve_html("Pipeline", build_pipeline(), "/pipeline", refresh)
            return

        if path == "/health-page":
            self.serve_html("Health", build_health_page(), "/health-page", refresh)
            return

        if path == "/config":
            self.serve_html("Configuration", build_config(), "/config", refresh)
            return

        # ── SQLITE (keep existing) ────────────────────────────────
        if path == "/sqlite":
            tables = sqlite_tables()
            sql = sqlite_stats()
            table_param = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("table", [None])[0]

            body = f"""<div class="card"><h3>SQLite Database</h3>
<div style="display:flex;gap:20px;flex-wrap:wrap">
<div><span class="mute">Tables:</span> <b>{sql.get('tables')}</b></div>
<div><span class="mute">Indexes:</span> <b>{sql.get('indexes')}</b></div>
<div><span class="mute">Integrity:</span> <b class="{'pass' if sql.get('integrity')=='ok' else 'fail'}">{sql.get('integrity')}</b></div>
<div><span class="mute">Size:</span> <b>{(sql.get('size_bytes',0)//1024)} KB</b></div>
<div><span class="mute">Path:</span> <code>stlms.db</code></div>
</div></div>"""

            if table_param:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                try:
                    info = conn.execute(f"PRAGMA table_info([{table_param}])").fetchall()
                    columns = [dict(r) for r in info]
                    count = conn.execute(f"SELECT COUNT(*) as cnt FROM [{table_param}]").fetchone()["cnt"]
                    rows_data = conn.execute(f"SELECT * FROM [{table_param}] LIMIT 100").fetchall()
                    conn.close()

                    body += f'<p class="mute"><a href="/sqlite">← All Tables</a> | Table: <b>{table_param}</b> ({count} rows, {len(columns)} columns)</p>'
                    body += '<div class="card"><h4>Columns</h4><div class="tblwrap"><table><tr><th>#</th><th>Name</th><th>Type</th><th>NotNull</th><th>Default</th><th>PK</th></tr>'
                    for c in columns:
                        body += f'<tr><td>{c["cid"]}</td><td><b>{c["name"]}</b></td><td>{c["type"]}</td><td>{"✓" if c["notnull"] else ""}</td><td class="mute">{c["dflt_value"] or ""}</td><td>{"🔑" if c["pk"] else ""}</td></tr>'
                    body += '</table></div></div>'

                    if rows_data:
                        col_names = [c["name"] for c in columns]
                        body += f'<div class="card"><h4>Data ({min(count,100)} of {count} rows)</h4><div class="tblwrap"><table><tr>'
                        body += ''.join(f'<th>{cn}</th>' for cn in col_names) + '</tr>'
                        for row in rows_data:
                            body += '<tr>' + ''.join(f'<td>{str(row[cn])[:100]}</td>' for cn in col_names) + '</tr>'
                        body += '</table></div></div>'
                    else:
                        body += '<div class="card"><p class="mute">Table is empty</p></div>'
                except Exception as e:
                    conn.close()
                    body += f'<div class="card"><p class="fail">Error: {e}</p></div>'
            else:
                body += '<div class="card"><div class="search"><input type="text" id="sqliteSearch" placeholder="Search tables..." oninput="filterSQLite()"></div></div>'
                body += '<div class="grid">'
                for t in tables:
                    body += f'<a href="/sqlite?table={t["name"]}" class="sqlite-link"><b>{t["name"]}</b><br><span class="mute">{t["row_count"]} rows</span></a>'
                body += '</div>'
                body += """<script>
function filterSQLite(){var q=document.getElementById('sqliteSearch').value.toLowerCase();
document.querySelectorAll('.sqlite-link').forEach(function(a){
a.style.display=a.textContent.toLowerCase().includes(q)?'':'none';});}
</script>"""
            self.serve_html("SQLite Viewer", body, "/sqlite")
            return

        # ═══════════════════════════════════════════════════════════
        #  LEGACY ROUTES (keep working)
        # ═══════════════════════════════════════════════════════════

        if path == "/truth":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Truth", no_data_html(err or "STLMSShell not available"))
                return
            try:
                data = shell.truth_current()
                if not data.get("available"):
                    self.serve_html("Truth", no_data_html())
                    return
                self.serve_html("Truth", card_html("Truth — Current Snapshot", dict_to_html_table(data)))
            except Exception as e:
                self.serve_html("Truth", no_data_html(str(e)))
            return

        if path == "/structure":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Structure", no_data_html(err or "STLMSShell not available"))
                return
            try:
                summary = shell.structure_summary()
                wave = shell.wave_current()
                cage = shell.cage_current()
                body = ""
                if summary.get("available"):
                    body += card_html("Structure Summary", dict_to_html_table(summary))
                else:
                    body += no_data_html("No structure data")
                if wave.get("available"):
                    body += card_html("Current Wave", dict_to_html_table(wave))
                if cage.get("available"):
                    body += card_html("Current Cage", dict_to_html_table(cage))
                if not body:
                    body = no_data_html()
                self.serve_html("Structure", body)
            except Exception as e:
                self.serve_html("Structure", no_data_html(str(e)))
            return

        if path == "/distance":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Distance", no_data_html(err or "STLMSShell not available"))
                return
            try:
                data = shell.distance_summary()
                if not data.get("available"):
                    self.serve_html("Distance", no_data_html())
                    return
                self.serve_html("Distance", card_html("Distance Metrics", dict_to_html_table(data)))
            except Exception as e:
                self.serve_html("Distance", no_data_html(str(e)))
            return

        if path == "/events":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Events", no_data_html(err or "STLMSShell not available"))
                return
            try:
                data = shell.truth_events()
                if not data:
                    self.serve_html("Events", '<div class="card"><p class="mute">No flip events</p></div>')
                    return
                body = '<div class="card"><h3>Flip Events</h3><ul>'
                for ev in data:
                    body += f'<li><b>ts={ev["ts"]}</b> flip={ev["flip"]} st={ev["st"]} close={ev["close"]}</li>'
                body += '</ul></div>'
                self.serve_html(f"Events ({len(data)} events)", body)
            except Exception as e:
                self.serve_html("Events", no_data_html(str(e)))
            return

        if path == "/clone":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Clone Stats", no_data_html(err or "STLMSShell not available"))
                return
            try:
                body = ""
                for clone_id in ("LONG", "SHORT", "GRID"):
                    try:
                        stats = shell.statistics_clone(clone_id)
                        if stats.get("available"):
                            body += card_html(f"Clone: {clone_id}", dict_to_html_table(stats))
                        else:
                            body += card_html(f"Clone: {clone_id}", '<p class="mute">N/A</p>')
                    except Exception as e:
                        body += card_html(f"Clone: {clone_id}", f'<p class="fail">Error: {e}</p>')
                if not body:
                    body = no_data_html()
                self.serve_html("Clone Stats", body)
            except Exception as e:
                self.serve_html("Clone Stats", no_data_html(str(e)))
            return

        if path == "/architecture":
            body = """<div class="card"><h3>ST-LMS Architecture</h3>
<p><b>23 pipeline stages:</b> SHARED (1-4) → PER-CLONE (5-11 x3) → SHARED-AGAIN (12-22) + ON-DEMAND (15) + OPTIONAL Consumer</p>
<p><b>26 logical layers</b> across Foundation, SHARED, PER-CLONE, SHARED-AGAIN, ON-DEMAND, OPTIONAL, CROSS-CUTTING</p>
<p><b>Data flow:</b> Unidirectional. No backward loops to Core. Card Sharing: Truth/Structure/Evidence 1x → 3 clones.</p></div>
<div class="card"><h3>Key Documents</h3><div class="grid">
<a href="/docs/01_ARCHITECTURE_FREEZE.md">Architecture Freeze</a>
<a href="/docs/ARCHITECTURE_FREEZE.md">Architecture Freeze (Detailed)</a>
<a href="/docs/FINAL_STLMS_IMPLEMENTATION_VISION_AUDIT.md">Vision Audit</a>
<a href="/docs/FINAL_LOGICAL_PIPELINE.md">Logical Pipeline</a>
<a href="/docs/18_MASTER_ARCHITECTURE_MAPPING.md">Master Architecture Mapping</a>
</div></div>"""
            self.serve_html("Architecture", body)
            return

        if path == "/phases":
            phases = get_phases()
            rows = "".join(
                f"<tr><td>{p[0]}</td><td>{p[1]}</td><td class=\"pass\">{p[2]}</td><td class=\"mute\">{p[3]}</td></tr>"
                for p in phases)
            body = f"<div class=\"tblwrap\"><table><tr><th>Phase</th><th>Name</th><th>Status</th><th>Module</th></tr>{rows}</table></div><p>Total: {len(phases)} phases — ALL DONE</p>"
            self.serve_html("Implementation Phases", body)
            return

        if path == "/components":
            comps = [
                ("Supertrend Point", "truth/point.py", "15 indicators per candle"),
                ("Supertrend Line", "structure/line.py", "Support/resistance walls"),
                ("Wave", "structure/wave.py", "13 structures, OI divergence"),
                ("Cage", "structure/cage.py", "HUKUM CAGE — 2 dinding=kompresi"),
                ("Evidence Bus", "evidence/bus.py", "3 buses (Direction, Exit, Correction)"),
                ("Clone Engine", "clone/engine.py", "LONG/SHORT/GRID, entry conjunction"),
                ("Statistics", "statistics/engine.py", "Sample-gated per-clone metrics"),
                ("BAG", "bag/engine.py", "Grouping, pattern mining, consensus"),
                ("Knowledge", "knowledge/engine.py", "7 entities"),
                ("Prediction", "prediction/engine.py", "Market Possibility — empirical"),
                ("Schema", "schema/engine.py", "41 trading schemas, 5 categories"),
                ("Recommendation", "recommendation/engine.py", "Market Intelligence Report"),
                ("Simulation", "simulation/engine.py", "5 simulators"),
                ("Consumer", "consumer/engine.py", "Fund eval, veto, intent"),
                ("Benchmark", "bench/engine.py", "WASIT 5-gate walk-forward"),
                ("Governance", "governance/engine.py", "6 validations, bounded auto-reject"),
                ("Integration", "integration/engine.py", "Pipeline orchestration"),
            ]
            rows = "".join(
                f"<tr><td><b>{c[0]}</b></td><td class=\"mute\">{c[1]}</td><td>{c[2]}</td></tr>" for c in comps)
            body = f"<div class=\"tblwrap\"><table><tr><th>Component</th><th>Module</th><th>Description</th></tr>{rows}</table></div><p>Total: {len(comps)} core components</p>"
            self.serve_html("Components", body)
            return

        if path == "/contracts":
            contracts = [f.name for f in sorted(ROOT.glob("*.md")) if
                         any(kw in f.name.upper() for kw in
                             ["CONTRACT", "FREEZE", "CONSTITUTION", "REGISTRY", "RESTRICTION", "QUEUE", "MATRIX"])]
            body = f"<h3>Contracts & Freeze Documents ({len(contracts)})</h3><div class=\"grid\">"
            for f in contracts:
                body += f'<a href="/docs/{f}">{f}</a>'
            body += "</div>"
            self.serve_html("Contracts", body)
            return

        if path == "/tests":
            import subprocess
            try:
                r = subprocess.run(
                    ["python", "-m", "unittest", "discover", "-s", "stlms/tests", "-p", "test_*.py"],
                    cwd=str(ROOT), capture_output=True, text=True, timeout=30)
                ok = "OK" in r.stdout
                result = "PASS" if ok else "FAIL"
                detail = r.stdout.split("\n")[-3].strip() if r.stdout else "?"
            except:
                result = "ERROR"
                detail = "?"
            body = f"""<div class="card"><h3>Unit Tests</h3>
<p>Result: <b class="{'pass' if result=='PASS' else 'fail'}">{result}</b></p><p>{detail}</p></div>
<div class="card"><h3>CLI Commands</h3><pre># Run all tests
python -m unittest discover -s stlms/tests -p "test_*.py" -v

# Run specific test
python -m unittest stlms.tests.test_market -v

# Run benchmarks
python -m unittest discover -s stlms/benchmarks -p "test_*.py" -v</pre></div>"""
            self.serve_html("Tests & Benchmarks", body)
            return

        if path == "/repository":
            stats = repo_stats()
            md_files = list_md_files()
            body = f"""<div class="stats-row">
<div class="stat-box"><div class="num">{stats['total_files']}</div><div class="label">Total Files</div></div>
<div class="stat-box"><div class="num">{stats['md_files']}</div><div class="label">.md</div></div>
<div class="stat-box"><div class="num">{stats['py_files']}</div><div class="label">.py</div></div>
<div class="stat-box"><div class="num">{stats['html_files']}</div><div class="label">.html</div></div>
<div class="stat-box"><div class="num">{stats['sql_files']}</div><div class="label">.sql</div></div>
<div class="stat-box"><div class="num">{stats['js_files']}</div><div class="label">.js</div></div>
</div>
<h3>Markdown Documents ({len(md_files)})</h3>
<div class="tblwrap"><table><tr><th>File</th><th>Date Modified</th><th>Size</th></tr>"""
            for f in md_files:
                body += f'<tr><td><a href="/docs/{f["name"]}"><b>{f["name"]}</b></a></td><td class="mute">{f["modified_str"]}</td><td>{f["size"]//1024} KB</td></tr>'
            body += '</table></div>'
            self.serve_html("Repository", body)
            return

        if path == "/cli":
            body = """<div class="card"><h3>CLI Reference</h3>
<pre># Full Pipeline Runner
python run_stlms.py --symbol BTCUSDT --candles 200 --seed 42

# Foundation CLI
python -m stlms.cli.foundation_cli status
python -m stlms.cli.foundation_cli sqlite
python -m stlms.cli.foundation_cli validate

# Unit Tests
python -m unittest discover -s stlms/tests -p "test_*.py" -v

# Data Viewer
python data_viewer/server.py
# Then open http://0.0.0.0:8082</pre></div>"""
            self.serve_html("CLI Reference", body)
            return

        if path == "/market":
            body = """<div class="card"><h3>Market Intelligence Philosophy</h3>
<p>ST-LMS is a <b>Market Intelligence Operating System</b> — NOT a trading bot, NOT a signal engine.</p>
<p><b>Pipeline:</b> Market Understanding → Market Possibility → Recommendation Package → Simulation → Market Intelligence Report</p></div>
<div class="card"><h3>Key Documents</h3><div class="grid">
<a href="/docs/MARKET_ANALYST_INTERVIEW.md">Market Analyst Interview</a>
<a href="/docs/RECOMMENDATION_LAYER_OUTPUT_CONTRACT.md">Recommendation Output Contract</a>
<a href="/docs/MARKET_INTELLIGENCE_REPORT_FORMAT.md">Market Intelligence Report Format</a>
<a href="/docs/SIMULATION_LAYER_OUTPUT_CONTRACT.md">Simulation Output Contract</a>
</div></div>"""
            self.serve_html("Market Intelligence", body)
            return

        if path == "/pipeline-stages":
            stages = [("0", "ONCE", "BOOT", "BOOT"),
                      ("1", "SHARED", "MARKET OBSERVATION", "MARKET"),
                      ("2", "SHARED", "TRUTH LAYER", "TRUTH"),
                      ("3", "SHARED", "STRUCTURE LAYER", "STRUCTURE"),
                      ("4", "SHARED", "EVIDENCE LAYER", "EVIDENCE"),
                      ("5", "PER-CLONE x3", "CLONE OBSERVATION", "CLONE"),
                      ("6", "PER-CLONE x3", "ENTRY VALIDATION", "TRADE"),
                      ("7", "PER-CLONE x3", "POSITION MGMT", "POSITION"),
                      ("8", "PER-CLONE x3", "PROFIT MGMT", "POSITION"),
                      ("9", "PER-CLONE x3", "EXIT VALIDATION", "TRADE"),
                      ("10", "PER-CLONE x3", "CLOSE POSITION", "TRADE"),
                      ("11", "PER-CLONE x3", "TRADE MARKER", "TRADE"),
                      ("12", "SHARED-AGAIN", "STATISTICS", "STATISTICS"),
                      ("13", "SHARED-AGAIN", "BAG", "BAG"),
                      ("14", "SHARED-AGAIN", "RIVER", "KNOWLEDGE"),
                      ("15", "ON-DEMAND", "BENCHMARK", "BENCHMARK"),
                      ("16", "SHARED-AGAIN", "ACADEMY", "KNOWLEDGE"),
                      ("17", "SHARED-AGAIN", "ORACLE", "KNOWLEDGE"),
                      ("18", "SHARED-AGAIN", "HIVEMIND", "KNOWLEDGE"),
                      ("19", "SHARED-AGAIN", "CERMIN", "KNOWLEDGE"),
                      ("20", "SHARED-AGAIN", "DARWIN", "KNOWLEDGE"),
                      ("21", "SHARED-AGAIN", "PREDICTION", "PREDICTION"),
                      ("22", "SHARED-AGAIN", "GOVERNANCE", "GOVERNANCE"),
                      ("OPT", "OPTIONAL", "CONSUMER", "CONSUMER")]
            rows = "".join(f"<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td></tr>" for s in stages)
            body = f"<div class=\"tblwrap\"><table><tr><th>Stage</th><th>Type</th><th>Name</th><th>Owner</th></tr>{rows}</table></div>"
            self.serve_html("Pipeline Stages (23)", body)
            return

        # ═══════════════════════════════════════════════════════════
        #  API ENDPOINTS
        # ═══════════════════════════════════════════════════════════

        if path == "/api/status":
            shell, err = get_shell()
            if shell is not None:
                self.serve_json(shell.status())
            else:
                self.serve_json({"status": "ERROR", "error": err})
            return

        if path == "/api/health":
            shell, err = get_shell()
            if shell is not None:
                self.serve_json(shell.health())
            else:
                self.serve_json({"healthy": False, "error": err})
            return

        if path == "/api/observation":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            idx = int(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("index", [-1])[0])
            if idx >= 0:
                self.serve_json(shell.get_observation(idx))
            else:
                self.serve_json(shell.truth_current())
            return

        if path == "/api/timeline":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            start = int(qs.get("start", [0])[0])
            end = int(qs.get("end", [min(50, len(shell._truth_points))])[0])
            self.serve_json(shell.get_timeline(start, end))
            return

        if path == "/api/statistics":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            domain = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("domain", ["all"])[0]
            if domain == "evolution":
                self.serve_json(shell.evolution_statistics())
            elif domain == "indicator":
                self.serve_json(shell.indicator_statistics())
            elif domain == "market":
                self.serve_json(shell.market_statistics())
            elif domain == "clone":
                self.serve_json(shell.clone_statistics())
            elif domain == "correlation":
                self.serve_json(shell.correlation_statistics())
            elif domain == "distance":
                self.serve_json(shell.distance_statistics())
            elif domain == "oi":
                self.serve_json(shell.oi_statistics())
            else:
                self.serve_json(shell.statistics_market())
            return

        if path == "/api/knowledge":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json({
                "academy": shell.knowledge_academy(),
                "oracle": shell.knowledge_oracle(),
                "hivemind": shell.knowledge_hivemind(),
            })
            return

        if path == "/api/prediction":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.prediction_current())
            return

        if path == "/api/simulation":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.simulation_results())
            return

        if path == "/api/recommendation":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.recommendation_report())
            return

        if path == "/api/snapshot":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.snapshots())
            return

        if path == "/api/dna":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.market_dna())
            return

        if path == "/api/pipeline":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.pipeline_status())
            return

        if path == "/api/config":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.config.snapshot())
            return

        if path == "/api/sqlite":
            self.serve_json({"tables": sqlite_tables(), "stats": sqlite_stats()})
            return

        if path == "/api/stats":
            self.serve_json(repo_stats())
            return

        if path == "/api/tests":
            import subprocess
            try:
                r = subprocess.run(
                    ["python", "-m", "unittest", "discover", "-s", "stlms/tests", "-p", "test_*.py"],
                    cwd=str(ROOT), capture_output=True, text=True, timeout=30)
                ok = "OK" in r.stdout
                result = {"result": "PASS" if ok else "FAIL",
                          "detail": r.stdout.split("\n")[-3].strip() if r.stdout else "?"}
            except:
                result = {"result": "ERROR"}
            self.serve_json(result)
            return

        if path == "/api/phases":
            self.serve_json([{"phase": p[0], "name": p[1], "status": p[2]} for p in get_phases()])
            return

        if path == "/api/events":
            shell, err = get_shell()
            if shell is None:
                self.serve_json({"error": err})
                return
            self.serve_json(shell.truth_events())
            return

        # ── 404 ──────────────────────────────────────────────────
        doc_name = path.strip("/").split("/")[-1] or "index"
        body = f"""<div class="card" style="text-align:center;padding:50px 30px">
<div style="font-size:5em;font-weight:800;color:var(--red);margin:0">404</div>
<h2 style="margin:8px 0">Page Not Found</h2>
<p class="mute">Route not found: <code>{doc_name}</code></p>
<div class="grid" style="max-width:500px;margin:20px auto">
<a href="/">Dashboard</a>
<a href="/observation">Observation</a>
<a href="/statistics">Statistics</a>
<a href="/knowledge">Knowledge</a>
<a href="/prediction">Prediction</a>
<a href="/pipeline">Pipeline</a>
<a href="/sqlite">SQLite</a>
</div></div>"""
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        html = page("404 — Not Found", body)
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        self.send_response(403)
        body = """<div class="card" style="text-align:center;padding:50px 30px">
<div style="font-size:5em;font-weight:800;color:var(--accent);margin:0">403</div>
<h2>Access Denied</h2><p class="mute">Write operations are not permitted. Data Viewer is READ ONLY.</p>
<div class="grid" style="max-width:300px;margin:20px auto"><a href="/">Back to Dashboard</a></div></div>"""
        html = page("403 — Access Denied", body)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())


if __name__ == "__main__":
    PORT = 8082
    HOST = "0.0.0.0"
    import socketserver
    http.server.HTTPServer.allow_reuse_address = True
    server = http.server.HTTPServer((HOST, PORT), Handler)
    print(f"ST-LMS Data Viewer v2.0 — http://{HOST}:{PORT} — {wib_now()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown")
        server.shutdown()
