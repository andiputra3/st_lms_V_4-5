"""
ST-LMS HTTPS Proxy — Layer 1 Error Pages
Forward :443 -> :8082 with informative error pages.
"""
from flask import Flask, request, Response
import urllib.request
import urllib.error

app = Flask(__name__)
BACKEND = "http://0.0.0.0:8082"

ERROR_CSS = """
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#0a0e14;color:#bfc7d5;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}
.card{background:#12171f;border:1px solid #1a2535;border-radius:12px;padding:40px;max-width:600px;width:100%;text-align:center}
h1{font-size:5em;margin:0;color:#ffb454}
h2{font-size:1.3em;margin:8px 0 20px;color:#bfc7d5}
.code{font-size:5em;font-weight:800;margin:0}
.code.e502{color:#fa6e83}.code.e503{color:#ffb454}.code.e504{color:#39bae6}.code.e403{color:#ffb454}.code.e500{color:#fa6e83}
.info{background:#0a0e14;border:1px solid #1a2535;border-radius:8px;padding:16px;margin:16px 0;text-align:left;font-size:.9em}
.info .row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1a2535}
.info .row:last-child{border:none}
.info .label{color:#5a6a7a}.info .value{color:#bfc7d5;font-weight:600}
.info .offline{color:#fa6e83}.info .online{color:#39bae6}
.suggestion{background:rgba(255,180,84,.06);border:1px solid rgba(255,180,84,.2);border-radius:8px;padding:14px;margin:16px 0;font-size:.85em;color:#ffb454}
.links{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:16px}
.links a{background:#12171f;border:1px solid #1a2535;color:#39bae6;text-decoration:none;padding:8px 16px;border-radius:6px;font-size:.85em}
.links a:hover{background:#1a2535}
</style>"""

def error_page(code, title, subtitle, info_rows, suggestion, links):
    css_class = f"e{code}" if code in (502,503,504,403,500) else ""
    rows_html = "".join(f'<div class="row"><span class="label">{k}</span><span class="value {v.get("cls","")}">{v["val"]}</span></div>' for k,v in info_rows)
    links_html = "".join(f'<a href="{l["url"]}">{l["label"]}</a>' for l in links)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>ST-LMS — {title}</title>{ERROR_CSS}</head><body>
<div class="card">
<div class="code {css_class}">{code}</div>
<h1>{title}</h1>
<h2>{subtitle}</h2>
<div class="info">{rows_html}</div>
<div class="suggestion">💡 {suggestion}</div>
<div class="links">{links_html}</div>
</div></body></html>"""

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    url = f"{BACKEND}/{path}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            return Response(content, status=resp.status,
                          content_type=resp.headers.get("Content-Type", "text/html"))
    except urllib.error.HTTPError as e:
        # Backend returned error — forward it
        return Response(f"Backend error: {e.code}", status=e.code)
    except urllib.error.URLError as e:
        # Connection refused — backend OFFLINE
        return Response(error_page(502, "ST-LMS Gateway Error",
            "Data Viewer is not reachable",
            [("Component","Data Viewer",{"val":"Data Viewer"}),
             ("Status","OFFLINE",{"val":"OFFLINE","cls":"offline"}),
             ("Port","8082",{"val":"8082"}),
             ("Host","0.0.0.0",{"val":"0.0.0.0"}),
             ("Error",str(e.reason),{"val":str(e.reason)})],
            "Restart Data Viewer: python3 data_viewer/server.py",
            [{"url":"/","label":"🏠 Retry Home"},
             {"url":"javascript:location.reload()","label":"🔄 Reload"}]),
            status=502)
    except Exception as e:
        return Response(error_page(504, "ST-LMS Gateway Timeout",
            "Data Viewer did not respond in time",
            [("Component","Data Viewer",{"val":"Data Viewer"}),
             ("Status","TIMEOUT",{"val":"TIMEOUT","cls":"offline"}),
             ("Port","8082",{"val":"8082"}),
             ("Error",str(e),{"val":str(e)})],
            "Check server load and restart if needed: python3 data_viewer/server.py",
            [{"url":"/","label":"🏠 Retry Home"},
             {"url":"javascript:location.reload()","label":"🔄 Reload"}]),
            status=504)

@app.errorhandler(404)
def not_found(e):
    path = request.path
    doc_name = path.split("/")[-1] or "index"
    return Response(error_page(404, "ST-LMS Documentation Error",
        f"Document not found: {doc_name}",
        [("Document",doc_name,{"val":doc_name}),
         ("Status","NOT FOUND",{"val":"NOT FOUND","cls":"offline"}),
         ("Full Path",path,{"val":path}),
         ("Suggestion","Check /markdown for all documents",{"val":"Browse all docs"})],
        "Browse /markdown to see all 77 available documents",
        [{"url":"/","label":"🏠 Home"},
         {"url":"/markdown","label":"📄 All Documents"},
         {"url":"/architecture","label":"🏗️ Architecture"},
         {"url":"/pipeline","label":"⚙️ Pipeline"}]),
        status=404)

@app.errorhandler(500)
def server_error(e):
    return Response(error_page(500, "ST-LMS Internal Error",
        "An unexpected error occurred",
        [("Component","Data Viewer",{"val":"Data Viewer"}),
         ("Status","ERROR",{"val":"ERROR","cls":"offline"}),
         ("Error",str(e),{"val":str(e)})],
        "Check server logs: cat /tmp/stlms_viewer.log",
        [{"url":"/","label":"🏠 Home"},
         {"url":"javascript:location.reload()","label":"🔄 Reload"}]),
        status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443,
            ssl_context=("/etc/letsencrypt/live/ryquest.fun/fullchain.pem",
                         "/etc/letsencrypt/live/ryquest.fun/privkey.pem"))
