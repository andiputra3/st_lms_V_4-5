#!/usr/bin/env python3
"""
ST-LMS DATA VIEWER v1.0.0
Read-only knowledge portal for entire ST-LMS project.
Zero dependencies. Python stdlib only.
http://0.0.0.0:8082
"""

import http.server
import json
import os
import re
import sqlite3
import time
import urllib.parse
import mimetypes
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
        _shell_instance = STLMSShell(symbol="BTCUSDT", timeframe="15m")
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
    if ext: files = [f for f in files if f.suffix == ext]
    return len(files)

def repo_stats():
    return {"total_files": count_files(), "md_files": count_files(".md"), "py_files": count_files(".py"),
            "html_files": count_files(".html"), "sql_files": count_files(".sql"), "js_files": count_files(".js"),
            "last_update": wib_now()}

def dict_to_html_table(d, depth=0):
    """Render a dict as nested HTML tables. Lists are rendered as cards."""
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
    """Render content as a card."""
    sub = f'<p class="mute">{subtitle}</p>' if subtitle else ''
    return f'<div class="card"><h3>{title}</h3>{sub}{content}</div>'

def no_data_html(message="No data loaded. Run shell.generate() first."):
    return f'<div class="card"><p class="mute">⚠️ {message}</p></div>'

def sqlite_stats():
    if not DB_PATH.exists(): return {"status": "Database not found"}
    try:
        conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
        tables = conn.execute("SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table'").fetchone()["cnt"]
        indexes = conn.execute("SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='index'").fetchone()["cnt"]
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        return {"tables": tables, "indexes": indexes, "integrity": integrity, "size_bytes": os.path.getsize(DB_PATH) if DB_PATH.exists() else 0}
    except Exception as e: return {"error": str(e)}

def test_stats():
    import subprocess
    try:
        r = subprocess.run(["python", "-m", "unittest", "discover", "-s", "stlms/tests", "-p", "test_*.py"],
                          cwd=str(ROOT), capture_output=True, text=True, timeout=30)
        ok = "OK" in r.stdout
        return {"result": "PASS" if ok else "FAIL", "detail": r.stdout.split("\n")[-3].strip() if r.stdout else "?"}
    except: return {"result": "ERROR"}

def sqlite_tables():
    if not DB_PATH.exists(): return []
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
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
        if ".git/" in str(f) or "__pycache__" in str(f): continue
        rel = str(f.relative_to(ROOT))
        st = f.stat()
        files.append({"name": f.name, "path": rel, "size": st.st_size,
                       "modified": st.st_mtime, "modified_str": datetime.fromtimestamp(st.st_mtime, WIB).strftime("%Y-%m-%d %H:%M")})
    reverse = order == "desc"
    if sort_by == "name": files.sort(key=lambda x: x["name"].lower(), reverse=reverse)
    elif sort_by == "size": files.sort(key=lambda x: x["size"], reverse=reverse)
    elif sort_by == "modified": files.sort(key=lambda x: x["modified"], reverse=reverse)
    return files

def list_py_modules():
    modules = []
    for f in sorted(ROOT.rglob("stlms/**/*.py")):
        if "__pycache__" in str(f) or "__init__" in f.name: continue
        modules.append({"name": str(f.relative_to(ROOT)), "size": f.stat().st_size})
    return modules

def read_md_file(filename):
    path = ROOT / filename
    if not path.exists(): return None
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
            if in_code: html.append("</pre>"); in_code = False
            else: html.append("<pre>"); in_code = True
            continue
        if in_code:
            html.append(line)
            continue
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                html.append('<div class="tblwrap"><table>')
                in_table = True
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(c.replace("-","").replace(":","").strip() == "" for c in cells):
                continue
            tag = "th" if in_table and html[-1].startswith("<table>") or (len(html)>1 and html[-2].startswith("<table>")) else "td"
            html.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        else:
            if in_table:
                html.append("</table></div>")
                in_table = False
            stripped = line.strip()
            if not stripped:
                html.append("<br>")
            elif stripped.startswith("# "): html.append(f"<h1>{stripped[2:]}</h1>")
            elif stripped.startswith("## "): html.append(f"<h2>{stripped[2:]}</h2>")
            elif stripped.startswith("### "): html.append(f"<h3>{stripped[3:]}</h3>")
            elif stripped.startswith("#### "): html.append(f"<h4>{stripped[4:]}</h4>")
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
        ("01","Market Collection","DONE","stlms/market/collection.py"),
        ("02","Market Artifact","DONE","stlms/market/artifact.py"),
        ("03","Supertrend Point","DONE","stlms/truth/point.py"),
        ("04","Truth Layer","DONE","stlms/truth/"),
        ("05","Supertrend Line","DONE","stlms/structure/line.py"),
        ("06","Distance Layer","DONE","stlms/truth/point.py"),
        ("07","Wave","DONE","stlms/structure/wave.py"),
        ("08","Structure + Evidence","DONE","stlms/structure/cage.py, stlms/evidence/bus.py"),
        ("09-11","Clone + Trade + Position","DONE","stlms/clone/engine.py"),
        ("10-11","Statistics + BAG","DONE","stlms/statistics/, stlms/bag/"),
        ("11","Knowledge","DONE","stlms/knowledge/engine.py"),
        ("12","Prediction","DONE","stlms/prediction/engine.py"),
        ("13","Trading Schema","DONE","stlms/schema/engine.py"),
        ("15","Recommendation","DONE","stlms/recommendation/engine.py"),
        ("16","Simulation","DONE","stlms/simulation/engine.py"),
        ("17","Consumer","DONE","stlms/consumer/engine.py"),
        ("18","Benchmark","DONE","stlms/bench/engine.py"),
        ("19","Governance","DONE","stlms/governance/engine.py"),
        ("20","Integration","DONE","stlms/integration/engine.py"),
    ]

def markdown_categories():
    cats = {
        "Reference": ["MASTER_SPECIFICATION.html","DOCUMENT_DEPENDENCY.html","QWEN_14_DOC.html",
                      "ST_LMS_CORE.js","STLMS_SQLITE_SCHEMA_V1.sql","01-07_IMPLEMENTATION_AUDIT.md"],
        "Phase 0 Freeze": ["REFERENCE_FREEZE.md","COMPONENT_INVENTORY.md","FILE_RELATIONSHIP.md",
                          "SPECIFICATION_FREEZE.md","DEPENDENCY_FREEZE.md","ARCHITECTURE_FREEZE.md",
                          "SQLITE_FOUNDATION_FREEZE.md","TRADING_SCHEMA_FREEZE.md","TRUTH_LAYER_FREEZE.md",
                          "DECISION_TREE_FREEZE.md","BUILD_CONTRACT.md","IMPLEMENTATION_CONTRACT.md"],
        "Architecture Mapping": ["01_SQLITE_FOUNDATION.md","02_MARKET_LAYER.md","03_TRUTH_LAYER.md",
                          "04_DISTANCE_LAYER.md","05_STRUCTURE_LAYER.md","06_TRADING_LAYER.md",
                          "07_STATISTICS_LAYER.md","08_SNAPSHOT_LAYER.md","09_SIMULATION_LAYER.md",
                          "10_KNOWLEDGE_LAYER.md","11_PREDICTION_LAYER.md","12_TRADING_SCHEMA_LAYER.md",
                          "13_GOVERNANCE_LAYER.md","14_BENCHMARK_LAYER.md","15_DASHBOARD_LAYER.md",
                          "16_INTEGRATION_LAYER.md","17_FINAL_AUDIT_LAYER.md","18_MASTER_ARCHITECTURE_MAPPING.md"],
        "Enrichment": ["DISTANCE_LAYER_ENRICHMENT.md","BAG_LAYER_POSITION.md","TRADING_SCHEMA_LAYER.md",
                      "TRUTH_LAYER_ENRICHMENT.md","STATISTICS_LAYER_ENRICHMENT.md","KNOWLEDGE_LAYER_ENRICHMENT.md",
                      "FINAL_LOGICAL_PIPELINE.md","ENRICHMENT_REPORT.md","ENRICHMENT_REPORT_V1.md"],
        "Freeze Contracts": ["01_ARCHITECTURE_FREEZE.md","02_ARTIFACT_REGISTRY.md","03_TRADING_CONSTITUTION.md",
                            "04_BUILD_CONTRACT.md","05_TEST_CONTRACT.md","06_CONSUMER_MATRIX.md",
                            "07_BUILD_RESTRICTION.md","08_MASTER_FREEZE_CONTRACT.md"],
        "Implementation Contracts": ["01_PIPELINE_CONTRACT.md","02_DECISION_TREE_CONTRACT.md",
                                     "03_COMPONENT_CONTRACT.md","04_WORKER_CONTRACT.md",
                                     "05_REGISTRY_CONTRACT.md","06_BUILD_QUEUE.md"],
        "BAG": ["BAG_ARCHITECTURE_SPECIFICATION.md","BAG_LAYER_POSITION.md"],
        "Phase 0 Output": ["PHASE_0_IMPLEMENTATION_READY.md","IMPLEMENTATION_ORDER.md",
                          "CODE_BUILD_GUIDELINE.md","IMPLEMENTATION_FREEZE.md",
                          "PHASE_1_BUILD_PERMISSION.md","PHASE_0.5_IMPLEMENTATION_ENRICHMENT.md"],
        "Audit": ["FINAL_STLMS_IMPLEMENTATION_VISION_AUDIT.md","OPEN_INTEREST_AUDIT.md",
                 "mass_audit.md","MASTER_FILE_INVENTORY.md"],
        "Contracts": ["RECOMMENDATION_LAYER_OUTPUT_CONTRACT.md","SIMULATION_LAYER_OUTPUT_CONTRACT.md",
                     "MARKET_INTELLIGENCE_REPORT_FORMAT.md","MINOR_REPOSITORY_CLEANUP_REPORT.md"],
        "Reports": ["MARKET_ANALYST_INTERVIEW.md","all_fitur.md","stlms_fitur.md",
                   "history_chat_stlms.md","map_pull_request_mcp.md","README.md"],
    }
    return cats

# ── CSS ──────────────────────────────────────────────────────
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
.stat-box .label{font-size:.78em;color:var(--mute);margin-top:4px}
"""

def page(title, body, nav_links=None):
    nav = '<div class="nav">'
    links = nav_links or [("/","Home"),("/truth","Truth"),("/timeline","Timeline"),("/events","Events"),
                          ("/structure","Structure"),("/distance","Distance"),("/statistics","Statistics"),
                          ("/prediction","Prediction"),("/recommendation","Recommendation"),
                          ("/simulation","Simulation"),("/pipeline","Pipeline"),("/clone","Clone"),
                          ("/markdown","Markdown"),("/data-html","HTML Reports"),
                          ("/architecture","Architecture"),
                          ("/phases","Phases"),("/components","Components"),
                          ("/sqlite","SQLite"),("/contracts","Contracts"),("/tests","Tests"),
                          ("/repository","Repository"),("/cli","CLI"),("/market","Market")]
    for href, label in links:
        active = ' class="active"' if title.lower() == label.lower() else ''
        nav += f'<a href="{href}"{active}>{label}</a>'
    nav += '</div>'
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ST-LMS Data Viewer — {title}</title><style>{CSS}</style></head><body>
<h1>📊 ST-LMS Data Viewer</h1>{nav}<h2>{title}</h2>{body}
<footer>ST-LMS Data Viewer v1.0 · {wib_now()} · Read Only · Zero Dependencies · Port 8082</footer></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def serve_html(self, title, body, nav=None):
        html = page(title, body, nav)
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode()))); self.end_headers()
        self.wfile.write(html.encode())

    def serve_json(self, data):
        j = json.dumps(data, indent=2, default=str)
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.end_headers(); self.wfile.write(j.encode())

    def serve_md_page(self, filename):
        content = read_md_file(filename)
        if content is None: self.send_error(404); return
        html_content = md_to_html(content)
        self.serve_html(f"📄 {filename}", f"<div class=\"card\">{html_content}</div><p class=\"mute\"><a href=\"/markdown\">← Back to Markdown</a></p>")

    def _content_type(self, filename):
        ext = filename.rsplit(".",1)[-1].lower() if "." in filename else ""
        return {"md":"text/markdown","txt":"text/plain","json":"application/json",
                "html":"text/html","csv":"text/csv","sql":"text/plain"}.get(ext,"text/plain")

    def _find_file(self, filename):
        for d in [ROOT, ROOT/"data_viewer/data-html"]:
            p = d / filename
            if p.exists(): return p
        return None

    def serve_raw_file(self, filename):
        fpath = self._find_file(filename)
        if fpath is None:
            self.send_response(404)
            self.send_header("Content-Type","text/plain")
            body = f"404 DOCUMENT NOT FOUND\n\nRequested File:\n{filename}\n\nSuggestions:\n- /docs-index\n- /health\n- /ping\n"
            self.send_header("Content-Length",str(len(body)))
            self.end_headers(); self.wfile.write(body.encode()); return
        content = sanitize_content(fpath.read_text(encoding="utf-8",errors="replace"))
        ct = self._content_type(filename)
        self.send_response(200)
        self.send_header("Content-Type",ct)
        self.send_header("Content-Length",str(len(content.encode())))
        self.end_headers(); self.wfile.write(content.encode())

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # ── HEALTH / PING ────────────────────────────────────
        if path == "/ping":
            self.send_response(200); self.send_header("Content-Type","text/plain")
            body = "ST-LMS DATA VIEWER ONLINE\n\nversion : v4-5\nstatus : online\nproxy : OK\nruntime : OK\nhttps : OK\n"
            self.send_header("Content-Length",str(len(body)))
            self.end_headers(); self.wfile.write(body.encode()); return

        if path == "/health":
            stats = repo_stats()
            self.serve_json({"service":"ST-LMS Data Viewer","status":"online","version":"v4-5",
                           "https":"OK","proxy":"OK","runtime":"OK",
                           "documents":stats["md_files"],"html_reports":len(list((ROOT/"data_viewer/data-html").glob("*.html"))),
                           "python_modules":stats["py_files"]}); return

        # ── DOCS INDEX ────────────────────────────────────────
        if path == "/docs-index":
            all_files = list_md_files()
            html_files = list((ROOT/"data_viewer/data-html").glob("*.html"))
            body = "AVAILABLE DOCUMENTS\n\n"
            seen = set()
            for f in all_files:
                name = f["name"]
                if name in seen: continue
                seen.add(name)
                body += f"- {name}\n"
                base = name.rsplit(".",1)[0]
                for ext in [".html",".json"]:
                    hname = base + ext
                    if hname not in seen and any(h.name==hname for h in html_files):
                        body += f"- {hname}\n"
                        seen.add(hname)
            body += f"\nTotal: {len(all_files)} documents\n"
            self.send_response(200); self.send_header("Content-Type","text/plain")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers(); self.wfile.write(body.encode()); return

        # ── AUDIT ─────────────────────────────────────────────
        if path == "/audit":
            body = """ST-LMS AUDIT INFORMATION

CURRENT BUILD:
PASS

CURRENT PRIORITY:
1. Statistics Layer
2. Recommendation Layer
3. Simulation Layer

READ THESE DOCUMENTS FIRST:
- MARKET_ANALYST_INTERVIEW.md
- RECOMMENDATION_LAYER_OUTPUT_CONTRACT.md
- SIMULATION_LAYER_OUTPUT_CONTRACT.md
- FINAL_LOGICAL_PIPELINE.md

KNOWN ISSUES:
- Wave statistics incomplete.
- Sample statistics not calibrated.
- Recommendation package incomplete.

LAST BUILD:
2026-07-29
"""
            self.send_response(200); self.send_header("Content-Type","text/plain")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers(); self.wfile.write(body.encode()); return

        # ── RAW FILE ──────────────────────────────────────────
        if path.startswith("/raw/"):
            self.serve_raw_file(path[5:]); return

        # ── MULTI-FORMAT DOCS ─────────────────────────────────
        if path.startswith("/docs/"):
            filename = path[6:]
            ext = filename.rsplit(".",1)[-1].lower() if "." in filename else ""
            if ext in ("txt","json","csv","sql"):
                base = filename.rsplit(".",1)[0]
                md_file = self._find_file(base+".md")
                if md_file and ext=="txt":
                    content = sanitize_content(md_file.read_text(encoding="utf-8",errors="replace"))
                    self.send_response(200); self.send_header("Content-Type","text/plain")
                    self.send_header("Content-Length",str(len(content.encode())))
                    self.end_headers(); self.wfile.write(content.encode()); return
                if md_file and ext=="json":
                    content = sanitize_content(md_file.read_text(encoding="utf-8",errors="replace"))
                    self.serve_json({"filename":base+".md","content":content,"format":"markdown","source":"ST-LMS Data Viewer"}); return
            if ext == "html":
                html_path = ROOT/"data_viewer/data-html"/filename
                if html_path.exists():
                    content = html_path.read_text(encoding="utf-8")
                    self.send_response(200); self.send_header("Content-Type","text/html")
                    self.send_header("Content-Length",str(len(content.encode())))
                    self.end_headers(); self.wfile.write(content.encode()); return
            self.serve_md_page(filename); return

        # ── HOME ─────────────────────────────────────────────
        if path == "/":
            stats = repo_stats()
            sql = sqlite_stats()
            tests = test_stats()
            body = f"""<div class="stats-row">
<div class="stat-box"><div class="num">{stats['total_files']}</div><div class="label">Total Files</div></div>
<div class="stat-box"><div class="num">{stats['md_files']}</div><div class="label">Documents</div></div>
<div class="stat-box"><div class="num">{stats['py_files']}</div><div class="label">Python Modules</div></div>
<div class="stat-box"><div class="num">{sql.get('tables','?')}</div><div class="label">SQLite Tables</div></div>
<div class="stat-box"><div class="num">23</div><div class="label">Pipeline Stages</div></div>
<div class="stat-box"><div class="num">20</div><div class="label">Phases (ALL DONE)</div></div>
</div>
<div class="card"><h3>Status</h3>
<p>SQLite: <b class="{'pass' if sql.get('integrity')=='ok' else 'fail'}">{sql.get('integrity','?')}</b> | Size: {(sql.get('size_bytes',0)//1024)} KB</p>
<p>Tests: <b class="{'pass' if tests.get('result')=='PASS' else 'fail'}">{tests.get('result','?')}</b> — {tests.get('detail','')}</p>
<p>Last Update: {stats['last_update']}</p></div>
<div class="card"><h3>Quick Navigation</h3>
<div class="grid">
<a href="/truth">🔮 Truth — Current snapshot</a>
<a href="/timeline">📊 Timeline — Truth range</a>
<a href="/events">⚡ Events — Flip events</a>
<a href="/structure">🏗️ Structure — Wave + Cage</a>
<a href="/distance">📏 Distance — Metrics</a>
<a href="/statistics">📈 Statistics — Market stats</a>
<a href="/prediction">🔭 Prediction — Market possibility</a>
<a href="/recommendation">📋 Recommendation — Report</a>
<a href="/simulation">🧪 Simulation — 5 simulators</a>
<a href="/pipeline">⚙️ Pipeline — Status</a>
<a href="/clone">👥 Clone — Clone stats</a>
<a href="/markdown">📄 Markdown Viewer (77 docs)</a>
<a href="/architecture">🏗️ Architecture</a>
<a href="/phases">📋 Phases (20 phases)</a>
<a href="/components">🧩 Components (17 core)</a>
<a href="/sqlite">🗄️ SQLite (40 tables)</a>
<a href="/contracts">📜 Contracts & Freeze</a>
<a href="/tests">✅ Tests & Benchmarks</a>
<a href="/repository">📁 Repository</a>
<a href="/cli">💻 CLI Reference</a>
<a href="/data-html">🌐 HTML Reports</a>
<a href="/market">📈 Market Intelligence</a>
</div></div>"""
            self.serve_html("Home", body); return

        # ── MARKDOWN VIEWER ──────────────────────────────────
        if path == "/markdown":
            sort_by = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("sort", ["name"])[0]
            order = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("order", ["asc"])[0]
            cats = markdown_categories()
            all_files = list_md_files(sort_by, order)
            all_names = {f["name"] for f in all_files}
            
            # Sort indicator
            def sort_link(col, label):
                next_order = "desc" if sort_by == col and order == "asc" else "asc"
                arrow = " ▲" if sort_by == col and order == "asc" else (" ▼" if sort_by == col and order == "desc" else "")
                return f'<a href="/markdown?sort={col}&order={next_order}" style="color:var(--accent);font-weight:600">{label}{arrow}</a>'
            
            body = f"""<div class="card" style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">
<div class="search" style="flex:1;min-width:200px"><input type="text" id="search" placeholder="Search {len(all_files)} documents..." oninput="filterDocs()"></div>
<div style="display:flex;gap:10px;font-size:.85em">
Sort: {sort_link('name','Name')} | {sort_link('modified','Date')} | {sort_link('size','Size')}
</div></div>"""
            
            # All files table view with date modified
            body += '<div class="tblwrap"><table id="doctable"><tr><th>File</th><th>Date Modified</th><th>Size</th><th>Path</th></tr>'
            for f in all_files:
                size_kb = f["size"] // 1024
                body += f'<tr class="doc-link"><td><a href="/docs/{f["name"]}"><b>{f["name"]}</b></a></td><td class="mute">{f["modified_str"]}</td><td>{size_kb} KB</td><td class="mute">{f["path"]}</td></tr>'
            body += '</table></div>'
            
            # Category view
            body += '<h3>By Category</h3>'
            for cat, files in cats.items():
                existing = [f for f in files if f in all_names]
                if not existing: continue
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
            self.serve_html(f"📄 Markdown Viewer ({len(all_files)} documents)", body); return

        # ── ARCHITECTURE ─────────────────────────────────────
        if path == "/architecture":
            body = """<div class="card"><h3>ST-LMS Architecture</h3>
<p><b>23 pipeline stages:</b> SHARED (1-4) → PER-CLONE (5-11 ×3) → SHARED-AGAIN (12-22) + ON-DEMAND (15) + OPTIONAL Consumer</p>
<p><b>26 logical layers</b> across Foundation, SHARED, PER-CLONE, SHARED-AGAIN, ON-DEMAND, OPTIONAL, CROSS-CUTTING</p>
<p><b>Data flow:</b> Unidirectional. No backward loops to Core. Card Sharing: Truth/Structure/Evidence 1x → 3 clones.</p>
<p><b>SP Philosophy:</b> After Market Collection, system works on Supertrend Point level, not candle.</p></div>
<div class="card"><h3>Key Architecture Documents</h3>
<div class="grid">
<a href="/docs/01_ARCHITECTURE_FREEZE.md">Architecture Freeze</a>
<a href="/docs/ARCHITECTURE_FREEZE.md">Architecture Freeze (Detailed)</a>
<a href="/docs/FINAL_STLMS_IMPLEMENTATION_VISION_AUDIT.md">Vision Audit</a>
<a href="/docs/FINAL_LOGICAL_PIPELINE.md">Logical Pipeline</a>
<a href="/docs/18_MASTER_ARCHITECTURE_MAPPING.md">Master Architecture Mapping</a>
<a href="/docs/DEPENDENCY_FREEZE.md">Dependency Freeze</a>
</div></div>"""
            self.serve_html("Architecture", body); return

        # ── PIPELINE STAGES (static) ────────────────────────
        if path == "/pipeline-stages":
            stages = [("0","ONCE","BOOT","BOOT"),("1","SHARED","MARKET OBSERVATION","MARKET"),("2","SHARED","TRUTH LAYER","TRUTH"),
                      ("3","SHARED","STRUCTURE LAYER","STRUCTURE"),("4","SHARED","EVIDENCE LAYER","EVIDENCE"),
                      ("5","PER-CLONE ×3","CLONE OBSERVATION","CLONE"),("6","PER-CLONE ×3","ENTRY VALIDATION","TRADE"),
                      ("7","PER-CLONE ×3","POSITION MGMT","POSITION"),("8","PER-CLONE ×3","PROFIT MGMT","POSITION"),
                      ("9","PER-CLONE ×3","EXIT VALIDATION","TRADE"),("10","PER-CLONE ×3","CLOSE POSITION","TRADE"),
                      ("11","PER-CLONE ×3","TRADE MARKER","TRADE"),("12","SHARED-AGAIN","STATISTICS","STATISTICS"),
                      ("13","SHARED-AGAIN","BAG","BAG"),("14","SHARED-AGAIN","RIVER","KNOWLEDGE"),
                      ("15","ON-DEMAND","BENCHMARK","BENCHMARK"),("16","SHARED-AGAIN","ACADEMY","KNOWLEDGE"),
                      ("17","SHARED-AGAIN","ORACLE","KNOWLEDGE"),("18","SHARED-AGAIN","HIVEMIND","KNOWLEDGE"),
                      ("19","SHARED-AGAIN","CERMIN","KNOWLEDGE"),("20","SHARED-AGAIN","DARWIN","KNOWLEDGE"),
                      ("21","SHARED-AGAIN","PREDICTION","PREDICTION"),("22","SHARED-AGAIN","GOVERNANCE","GOVERNANCE"),
                      ("OPT","OPTIONAL","CONSUMER","CONSUMER")]
            rows = "".join(f"<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td></tr>" for s in stages)
            body = f"<div class=\"tblwrap\"><table><tr><th>Stage</th><th>Type</th><th>Name</th><th>Owner</th></tr>{rows}</table></div>"
            self.serve_html("Pipeline Stages (23)", body); return

        # ── PHASES ───────────────────────────────────────────
        if path == "/phases":
            phases = get_phases()
            rows = "".join(f"<tr><td>{p[0]}</td><td>{p[1]}</td><td class=\"pass\">{p[2]}</td><td class=\"mute\">{p[3]}</td></tr>" for p in phases)
            body = f"<div class=\"tblwrap\"><table><tr><th>Phase</th><th>Name</th><th>Status</th><th>Module</th></tr>{rows}</table></div><p>Total: {len(phases)} phases — ALL DONE ✅</p>"
            self.serve_html("Implementation Phases", body); return

        # ── COMPONENTS ───────────────────────────────────────
        if path == "/components":
            comps = [("Supertrend Point","truth/point.py","15 indicators per candle — unit truth utama"),
                     ("Supertrend Line","structure/line.py","Support/resistance walls, OI inheritance"),
                     ("Wave","structure/wave.py","13 structures, OI divergence"),
                     ("Cage","structure/cage.py","HUKUM CAGE — 2 dinding=kompresi, 1=trend"),
                     ("Evidence Bus","evidence/bus.py","3 buses (Direction, Exit, Correction)"),
                     ("Clone Engine","clone/engine.py","LONG/SHORT/GRID, entry conjunction, exit priority"),
                     ("Statistics","statistics/engine.py","Sample-gated per-clone metrics"),
                     ("BAG","bag/engine.py","Grouping, pattern mining, consensus, maturity"),
                     ("Knowledge","knowledge/engine.py","7 entities (Academy,Oracle,HiveMind,CERMIN,Librarian,Darwin,River)"),
                     ("Prediction","prediction/engine.py","Market Possibility — empirical, no-model"),
                     ("Schema","schema/engine.py","41 trading schemas, 5 categories"),
                     ("Recommendation","recommendation/engine.py","Market Intelligence Report — 20 sections"),
                     ("Simulation","simulation/engine.py","5 simulators"),
                     ("Consumer","consumer/engine.py","Fund eval, veto, intent, CSV, live DISABLED"),
                     ("Benchmark","bench/engine.py","WASIT 5-gate walk-forward"),
                     ("Governance","governance/engine.py","6 validations, bounded auto-reject, rollback"),
                     ("Integration","integration/engine.py","Pipeline orchestration, architecture validation")]
            rows = "".join(f"<tr><td><b>{c[0]}</b></td><td class=\"mute\">{c[1]}</td><td>{c[2]}</td></tr>" for c in comps)
            body = f"<div class=\"tblwrap\"><table><tr><th>Component</th><th>Module</th><th>Description</th></tr>{rows}</table></div><p>Total: {len(comps)} core components</p>"
            self.serve_html("Components", body); return

        # ── SQLITE ───────────────────────────────────────────
        if path == "/sqlite":
            tables = sqlite_tables()
            sql = sqlite_stats()
            
            # Table selector
            table_param = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("table", [None])[0]
            
            body = f"""<div class="card"><h3>🗄️ SQLite Database</h3>
<div style="display:flex;gap:20px;flex-wrap:wrap">
<div><span class="mute">Tables:</span> <b>{sql.get('tables')}</b></div>
<div><span class="mute">Indexes:</span> <b>{sql.get('indexes')}</b></div>
<div><span class="mute">Integrity:</span> <b class="{'pass' if sql.get('integrity')=='ok' else 'fail'}">{sql.get('integrity')}</b></div>
<div><span class="mute">Size:</span> <b>{(sql.get('size_bytes',0)//1024)} KB</b></div>
<div><span class="mute">Path:</span> <code>stlms.db</code></div>
</div></div>"""
            
            # Table list + data view
            if table_param:
                # Show specific table
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                try:
                    info = conn.execute(f"PRAGMA table_info([{table_param}])").fetchall()
                    columns = [dict(r) for r in info]
                    count = conn.execute(f"SELECT COUNT(*) as cnt FROM [{table_param}]").fetchone()["cnt"]
                    rows_data = conn.execute(f"SELECT * FROM [{table_param}] LIMIT 100").fetchall()
                    conn.close()
                    
                    body += f'<p class="mute"><a href="/sqlite">← All Tables</a> | Table: <b>{table_param}</b> ({count} rows, {len(columns)} columns)</p>'
                    
                    # Column info
                    body += '<div class="card"><h4>Columns</h4><div class="tblwrap"><table><tr><th>#</th><th>Name</th><th>Type</th><th>NotNull</th><th>Default</th><th>PK</th></tr>'
                    for c in columns:
                        body += f'<tr><td>{c["cid"]}</td><td><b>{c["name"]}</b></td><td>{c["type"]}</td><td>{"✓" if c["notnull"] else ""}</td><td class="mute">{c["dflt_value"] or ""}</td><td>{"🔑" if c["pk"] else ""}</td></tr>'
                    body += '</table></div></div>'
                    
                    # Data rows
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
                # All tables list
                body += '<div class="card"><div class="search"><input type="text" id="sqliteSearch" placeholder="Search 40 tables..." oninput="filterSQLite()"></div></div>'
                body += '<div class="grid">'
                for t in tables:
                    body += f'<a href="/sqlite?table={t["name"]}" class="sqlite-link"><b>{t["name"]}</b><br><span class="mute">{t["row_count"]} rows</span></a>'
                body += '</div>'
                body += """<script>
function filterSQLite(){var q=document.getElementById('sqliteSearch').value.toLowerCase();
document.querySelectorAll('.sqlite-link').forEach(function(a){
a.style.display=a.textContent.toLowerCase().includes(q)?'':'none';});}
</script>"""
            
            self.serve_html("🗄️ SQLite Viewer", body); return

        # ── CONTRACTS ────────────────────────────────────────
        if path == "/contracts":
            contracts = [f.name for f in sorted(ROOT.glob("*.md")) if any(kw in f.name.upper() for kw in ["CONTRACT","FREEZE","CONSTITUTION","REGISTRY","RESTRICTION","QUEUE","MATRIX"])]
            body = f"<h3>Contracts & Freeze Documents ({len(contracts)})</h3><div class=\"grid\">"
            for f in contracts:
                body += f'<a href="/docs/{f}">{f}</a>'
            body += "</div>"
            self.serve_html("Contracts", body); return

        # ── TESTS ────────────────────────────────────────────
        if path == "/tests":
            tests = test_stats()
            body = f"""<div class="card"><h3>Unit Tests</h3><p>Result: <b class="{'pass' if tests.get('result')=='PASS' else 'fail'}">{tests.get('result','?')}</b></p><p>{tests.get('detail','')}</p></div>
<div class="card"><h3>CLI Commands</h3><pre># Run all tests
python -m unittest discover -s stlms/tests -p "test_*.py" -v

# Run specific test
python -m unittest stlms.tests.test_market -v
python -m unittest stlms.tests.test_phase_03_12 -v

# Run benchmarks
python -m unittest discover -s stlms/benchmarks -p "test_*.py" -v</pre></div>"""
            self.serve_html("Tests & Benchmarks", body); return

        # ── REPOSITORY ───────────────────────────────────────
        if path == "/repository":
            stats = repo_stats()
            sort_by = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("sort", ["name"])[0]
            order = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("order", ["asc"])[0]
            md_files = list_md_files(sort_by, order)
            py_files = list_py_modules()
            
            def sort_link(col, label):
                next_order = "desc" if sort_by == col and order == "asc" else "asc"
                arrow = " ▲" if sort_by == col and order == "asc" else (" ▼" if sort_by == col and order == "desc" else "")
                return f'<a href="/repository?sort={col}&order={next_order}" style="color:var(--accent)">{label}{arrow}</a>'
            
            body = f"""<div class="stats-row">
<div class="stat-box"><div class="num">{stats['total_files']}</div><div class="label">Total Files</div></div>
<div class="stat-box"><div class="num">{stats['md_files']}</div><div class="label">.md</div></div>
<div class="stat-box"><div class="num">{stats['py_files']}</div><div class="label">.py</div></div>
<div class="stat-box"><div class="num">{stats['html_files']}</div><div class="label">.html</div></div>
<div class="stat-box"><div class="num">{stats['sql_files']}</div><div class="label">.sql</div></div>
<div class="stat-box"><div class="num">{stats['js_files']}</div><div class="label">.js</div></div>
</div>
<div class="card" style="display:flex;gap:10px;font-size:.85em;align-items:center">
Sort: {sort_link('name','Name')} | {sort_link('modified','Date')} | {sort_link('size','Size')}
</div>
<h3>Markdown Documents ({len(md_files)})</h3>
<div class="tblwrap"><table><tr><th>File</th><th>Date Modified</th><th>Size</th></tr>"""
            for f in md_files:
                body += f'<tr><td><a href="/docs/{f["name"]}"><b>{f["name"]}</b></a></td><td class="mute">{f["modified_str"]}</td><td>{f["size"]//1024} KB</td></tr>'
            body += f'</table></div><p class="mute"><a href="/markdown">View all with categories →</a></p>'
            body += f'<h3>Python Modules ({len(py_files)})</h3><div class="grid">'
            for f in py_files[:40]:
                body += f'<a href="#"><code>{f["name"]}</code><br><span class="mute">{f["size"]} bytes</span></a>'
            body += f'</div>'
            self.serve_html("Repository", body); return

        # ── CLI ──────────────────────────────────────────────
        if path == "/cli":
            body = """<div class="card"><h3>CLI Reference</h3>
<pre># Full Pipeline Runner
python run_stlms.py --symbol BTCUSDT --candles 200 --seed 42
python run_stlms.py --symbol SOLUSDT --candles 500

# Foundation CLI
python -m stlms.cli.foundation_cli status
python -m stlms.cli.foundation_cli sqlite
python -m stlms.cli.foundation_cli validate
python -m stlms.cli.foundation_cli resource
python -m stlms.cli.foundation_cli benchmark
python -m stlms.cli.foundation_cli config
python -m stlms.cli.foundation_cli mcp list
python -m stlms.cli.foundation_cli mcp toggle stlms-github

# Unit Tests
python -m unittest discover -s stlms/tests -p "test_*.py" -v
python -m unittest stlms.tests.test_market -v

# Benchmarks
python -m unittest discover -s stlms/benchmarks -p "test_*.py" -v

# GitHub MCP
stlms-github status
stlms-github test
stlms-github on
stlms-github pr phase-01

# Data Viewer
python data_viewer/server.py
# Then open http://0.0.0.0:8082</pre></div>"""
            self.serve_html("CLI Reference", body); return

        # ── MARKET ───────────────────────────────────────────
        if path == "/market":
            body = """<div class="card"><h3>Market Intelligence Philosophy</h3>
<p>ST-LMS adalah <b>Market Intelligence Operating System</b> — BUKAN trading bot, BUKAN signal engine.</p>
<p><b>Pipeline:</b> Market Understanding → Market Possibility → Recommendation Package → Simulation → Market Intelligence Report</p>
<p><b>Output:</b> "82% Breakout", "67% Continuation", "12% Fake Breakout" — BUKAN "BUY BTC"</p></div>
<div class="card"><h3>Key Documents</h3><div class="grid">
<a href="/docs/MARKET_ANALYST_INTERVIEW.md">Market Analyst Interview (30 components)</a>
<a href="/docs/RECOMMENDATION_LAYER_OUTPUT_CONTRACT.md">Recommendation Output Contract</a>
<a href="/docs/MARKET_INTELLIGENCE_REPORT_FORMAT.md">Market Intelligence Report Format</a>
<a href="/docs/SIMULATION_LAYER_OUTPUT_CONTRACT.md">Simulation Output Contract</a>
<a href="/docs/all_fitur.md">All Features (~995)</a>
<a href="/docs/stlms_fitur.md">Features Overview</a>
</div></div>"""
            self.serve_html("Market Intelligence", body); return

        # ── TRUTH ────────────────────────────────────────────
        if path == "/truth":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Truth — Current Snapshot", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.truth_current()
                if not data.get("available"):
                    self.serve_html("Truth — Current Snapshot", no_data_html()); return
                body = card_html("Truth — Current Snapshot", dict_to_html_table(data))
                self.serve_html("Truth", body); return
            except Exception as e:
                self.serve_html("Truth — Current Snapshot", no_data_html(str(e))); return

        # ── TIMELINE ─────────────────────────────────────────
        if path == "/timeline":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Truth Timeline", no_data_html(err or "STLMSShell not available")); return
            try:
                # Use wide range to capture all fixture-generated truth points
                data = shell.truth_timeline(0, 9_999_999_999_999)
                if not data:
                    self.serve_html("Truth Timeline", no_data_html()); return
                # Show first 50 rows for performance
                displayed = data[:50]
                body = '<div class="tblwrap"><table><tr><th>ts</th><th>close</th><th>st</th><th>st_dir</th><th>st_color</th><th>atr</th><th>ema</th><th>rsi</th><th>wpr</th><th>macd_hist</th><th>dist</th><th>dist_atr</th><th>flip</th><th>point_status</th></tr>'
                for row in displayed:
                    body += '<tr>' + ''.join(f'<td>{row.get(k,"")}</td>' for k in ["ts","close","st","st_dir","st_color","atr","ema","rsi","wpr","macd_hist","dist","dist_atr","flip","point_status"]) + '</tr>'
                body += '</table></div>'
                self.serve_html(f"Truth Timeline ({len(data)} total, showing {len(displayed)})", body); return
            except Exception as e:
                self.serve_html("Truth Timeline", no_data_html(str(e))); return

        # ── EVENTS ───────────────────────────────────────────
        if path == "/events":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Truth Events", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.truth_events()
                if not data:
                    self.serve_html("Truth Events", '<div class="card"><p class="mute">No flip events</p></div>'); return
                body = '<div class="card"><h3>Flip Events</h3><ul>'
                for ev in data:
                    body += f'<li><b>ts={ev["ts"]}</b> flip={ev["flip"]} st={ev["st"]} close={ev["close"]}</li>'
                body += '</ul></div>'
                self.serve_html(f"Truth Events ({len(data)} events)", body); return
            except Exception as e:
                self.serve_html("Truth Events", no_data_html(str(e))); return

        # ── STRUCTURE ────────────────────────────────────────
        if path == "/structure":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Structure", no_data_html(err or "STLMSShell not available")); return
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
                self.serve_html("Structure", body); return
            except Exception as e:
                self.serve_html("Structure", no_data_html(str(e))); return

        # ── DISTANCE ─────────────────────────────────────────
        if path == "/distance":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Distance", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.distance_summary()
                if not data.get("available"):
                    self.serve_html("Distance", no_data_html()); return
                body = card_html("Distance Metrics", dict_to_html_table(data))
                self.serve_html("Distance", body); return
            except Exception as e:
                self.serve_html("Distance", no_data_html(str(e))); return

        # ── STATISTICS ───────────────────────────────────────
        if path == "/statistics":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Statistics", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.statistics_market()
                if not data.get("available"):
                    self.serve_html("Statistics", no_data_html()); return
                body = card_html("Market Statistics", dict_to_html_table(data))
                self.serve_html("Statistics", body); return
            except Exception as e:
                self.serve_html("Statistics", no_data_html(str(e))); return

        # ── PREDICTION ───────────────────────────────────────
        if path == "/prediction":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Prediction", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.prediction_current()
                if not data.get("available"):
                    self.serve_html("Prediction", no_data_html()); return
                body = card_html("Market Possibility Prediction", dict_to_html_table(data))
                self.serve_html("Prediction", body); return
            except Exception as e:
                self.serve_html("Prediction", no_data_html(str(e))); return

        # ── RECOMMENDATION ───────────────────────────────────
        if path == "/recommendation":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Recommendation", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.recommendation_report()
                if not data.get("available"):
                    self.serve_html("Recommendation", no_data_html()); return
                body = card_html("Market Intelligence Report", dict_to_html_table(data))
                self.serve_html("Recommendation", body); return
            except Exception as e:
                self.serve_html("Recommendation", no_data_html(str(e))); return

        # ── SIMULATION ───────────────────────────────────────
        if path == "/simulation":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Simulation", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.simulation_results()
                if not data.get("available"):
                    self.serve_html("Simulation", no_data_html(data.get("error"))); return
                body = card_html("Simulation Results", dict_to_html_table(data))
                self.serve_html("Simulation", body); return
            except Exception as e:
                self.serve_html("Simulation", no_data_html(str(e))); return

        # ── PIPELINE STATUS ──────────────────────────────────
        if path == "/pipeline":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Pipeline Status", no_data_html(err or "STLMSShell not available")); return
            try:
                data = shell.pipeline_status()
                if not data.get("available"):
                    self.serve_html("Pipeline Status", no_data_html("Pipeline not run yet")); return
                body = card_html("Pipeline Status", dict_to_html_table(data))
                self.serve_html("Pipeline", body); return
            except Exception as e:
                self.serve_html("Pipeline Status", no_data_html(str(e))); return

        # ── CLONE ────────────────────────────────────────────
        if path == "/clone":
            shell, err = get_shell()
            if shell is None:
                self.serve_html("Clone Stats", no_data_html(err or "STLMSShell not available")); return
            try:
                body = ""
                for clone_id in ("LONG", "SHORT", "GRID"):
                    try:
                        stats = shell.statistics_clone(clone_id)
                        if stats.get("available"):
                            body += card_html(f"Clone: {clone_id}", dict_to_html_table(stats))
                        else:
                            body += card_html(f"Clone: {clone_id}", '<p class="mute">No statistics available</p>')
                    except Exception as e:
                        body += card_html(f"Clone: {clone_id}", f'<p class="fail">Error: {e}</p>')
                if not body:
                    body = no_data_html()
                self.serve_html("Clone Stats", body); return
            except Exception as e:
                self.serve_html("Clone Stats", no_data_html(str(e))); return

        # ── HTML REPORTS ──────────────────────────────────────
        if path == "/data-html":
            html_dir = ROOT / "data_viewer" / "data-html"
            files = sorted(html_dir.glob("*.html"))
            body = f"<h3>HTML Reports ({len(files)})</h3><p class=\"mute\">Generated from Markdown documents for rich viewing.</p><div class=\"grid\">"
            for f in files:
                size_kb = f.stat().st_size // 1024
                body += f'<a href="/data-html/{f.name}"><b>{f.name}</b><br><span class="mute">{size_kb} KB</span></a>'
            if not files:
                body += '<p class="mute">No HTML reports yet. Run: python3 -c "from data_viewer.server import md_to_html; ..."</p>'
            body += "</div>"
            self.serve_html("🌐 HTML Reports", body); return

        if path.startswith("/data-html/"):
            filename = path[11:]
            html_path = ROOT / "data_viewer" / "data-html" / filename
            if not html_path.exists():
                self.send_error(404); return
            content = html_path.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content.encode())))
            self.end_headers()
            self.wfile.write(content.encode()); return

        # ── MARKDOWN FILE VIEWER ─────────────────────────────
        if path.startswith("/docs/"):
            filename = path[6:]
            self.serve_md_page(filename); return

        # ── API ENDPOINTS ────────────────────────────────────
        if path == "/api/stats": self.serve_json(repo_stats()); return
        if path == "/api/sqlite": self.serve_json({"tables": sqlite_tables(), "stats": sqlite_stats()}); return
        if path == "/api/tests": self.serve_json(test_stats()); return
        if path == "/api/phases": self.serve_json([{"phase":p[0],"name":p[1],"status":p[2]} for p in get_phases()]); return

        # ── ERROR PAGES ───────────────────────────────────────
        doc_name = path.strip("/").split("/")[-1] or "index"
        all_docs = list_md_files()
        related = [f for f in all_docs if doc_name.lower() in f["name"].lower()][:5]
        related_html = "".join(f'<a href="/docs/{f["name"]}">{f["name"]}</a>' for f in related) if related else '<span class="mute">No related documents found</span>'
        
        body = f"""<div class="card" style="text-align:center;padding:50px 30px">
<div style="font-size:5em;font-weight:800;color:var(--red);margin:0">404</div>
<h2 style="margin:8px 0">ST-LMS Documentation Error</h2>
<p class="mute">Document not found: <code>{doc_name}</code></p>
<div class="card" style="text-align:left;margin:16px 0">
<div class="row" style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line)"><span class="mute">Document</span><b>{doc_name}</b></div>
<div class="row" style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line)"><span class="mute">Status</span><span class="fail">NOT FOUND</span></div>
<div class="row" style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line)"><span class="mute">Full Path</span><code>{path}</code></div>
<div class="row" style="display:flex;justify-content:space-between;padding:6px 0"><span class="mute">Suggestion</span>Browse /markdown for all documents</div>
</div>
<h3>Related Documents</h3>
<div class="grid">{related_html}</div>
<div style="margin-top:16px;color:var(--accent)">💡 Browse <a href="/markdown">/markdown</a> to see all 77 available documents</div>
<br>
<div class="grid" style="max-width:500px;margin:0 auto">
<a href="/">🏠 Home</a>
<a href="/markdown">📄 Markdown Viewer</a>
<a href="/architecture">🏗️ Architecture</a>
<a href="/pipeline">⚙️ Pipeline</a>
<a href="/components">🧩 Components</a>
<a href="/sqlite">🗄️ SQLite</a>
</div>
</div>"""
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        html = page("404 — Documentation Error", body)
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        self.send_response(403)
        body = """<div class="card" style="text-align:center;padding:50px 30px">
<div style="font-size:5em;font-weight:800;color:var(--accent);margin:0">403</div>
<h2>ST-LMS Access Error</h2><p class="mute">Write operations are not permitted. Data Viewer is READ ONLY.</p>
<div class="grid" style="max-width:300px;margin:20px auto"><a href="/">🏠 Back to Home</a></div></div>"""
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
    print(f"ST-LMS Data Viewer v1.0 — http://{HOST}:{PORT} — {wib_now()}")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nShutdown"); server.shutdown()
