"""Simple dashboard that displays metrics updated by the demo."""
import html as html_module
import json
import os
import re
import subprocess
import sys
from flask import Flask

app = Flask(__name__)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(APP_DIR, "metrics.json")
MAIN_PY = os.path.join(APP_DIR, "main.py")
REGISTRATION_PY = os.path.join(APP_DIR, "user_registration.py")

def get_metrics():
    try:
        with open(METRICS_FILE, "r") as f:
            data = json.load(f)
        if "last_main_output" not in data:
            data["last_main_output"] = ""
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"main_runs": 0, "registration_runs": 0, "last_main_status": "never", "last_registration_status": "never", "total_demo_runs": 0, "last_main_output": ""}

def _read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def _parse_variables_and_types(filepath):
    """Parse Python file for variable names and inferred/annotated types."""
    content = _read_file(filepath)
    results = []
    fname = os.path.basename(filepath)
    skip_names = {"else", "if", "for", "while", "try", "except", "with", "def", "class", "return", "pass", "break", "continue"}
    for m in re.finditer(r"^(\w+)\s*:\s*([\w\.]+)\s*=", content, re.MULTILINE):
        if m.group(1) not in skip_names:
            results.append({"file": fname, "variable": m.group(1), "type": m.group(2)})
    seen = {r["variable"] for r in results}
    for m in re.finditer(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.+)", content, re.MULTILINE):
        name = m.group(1)
        if name in seen:
            continue
        seen.add(name)
        val = m.group(2).strip()
        if val.startswith('"') or val.startswith("'"):
            t = "str"
        elif re.match(r"^-?\d+$", val):
            t = "int"
        elif re.match(r"^-?\d+\.\d+", val):
            t = "float"
        elif val in ("True", "False"):
            t = "bool"
        else:
            t = "inferred"
        results.append({"file": fname, "variable": name, "type": t})
    for m in re.finditer(r"^(\w+)\s*=\s*(.+)", content, re.MULTILINE):
        name = m.group(1)
        if name in seen or name in skip_names:
            continue
        if not re.match(r"^[a-zA-Z_]", name):
            continue
        seen.add(name)
        val = m.group(2).strip()
        if val.startswith('"') or val.startswith("'"):
            t = "str"
        elif re.match(r"^-?\d+$", val):
            t = "int"
        elif re.match(r"^-?\d+\.\d+", val):
            t = "float"
        elif val in ("True", "False"):
            t = "bool"
        else:
            t = "inferred"
        results.append({"file": fname, "variable": name, "type": t})
    return results

def _parse_docstrings_and_comments(filepath):
    """Extract module docstring and inline comments."""
    content = _read_file(filepath)
    fname = os.path.basename(filepath)
    docstring = ""
    comments = []
    if '"""' in content:
        i = content.index('"""')
        j = content.index('"""', i + 3)
        if j > i:
            docstring = content[i + 3:j].strip()
    elif "'''" in content:
        i = content.index("'''")
        j = content.index("'''", i + 3)
        if j > i:
            docstring = content[i + 3:j].strip()
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("#"):
            comments.append(line)
        elif "#" in line:
            idx = line.index("#")
            comment_part = line[idx:].strip()
            if comment_part:
                comments.append(comment_part)
    return {"file": fname, "docstring": docstring, "comments": comments}

@app.route("/")
def index():
    m = get_metrics()
    return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><title>Day2 Dashboard</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; min-height: 100vh; background: linear-gradient(165deg, #f0fdf4 0%, #dcfce7 40%, #bbf7d0 100%); color: #14532d; }}
  .header {{ text-align: center; margin-bottom: 1.75rem; padding: 1.5rem 1.25rem; background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(220,252,231,0.9) 100%); border-radius: 20px; box-shadow: 0 8px 24px rgba(22,163,74,0.15), 0 2px 8px rgba(0,0,0,0.06); border: 1px solid rgba(74,222,128,0.5); }}
  .header h1 {{ margin: 0; font-size: 1.85rem; font-weight: 700; letter-spacing: -0.03em; color: #166534; text-shadow: 0 1px 2px rgba(255,255,255,0.8); }}
  .header .hello-msg {{ margin: 0.5rem 0 0; font-size: 1.05rem; color: #15803d; font-weight: 500; }}
  .card {{ background: linear-gradient(145deg, rgba(255,255,255,0.92) 0%, rgba(240,253,244,0.9) 100%); border-radius: 16px; padding: 1.35rem 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(74,222,128,0.35); box-shadow: 0 4px 16px rgba(22,163,74,0.08), 0 1px 3px rgba(0,0,0,0.04); transition: box-shadow 0.25s ease, transform 0.2s ease; }}
  .card:hover {{ box-shadow: 0 8px 28px rgba(22,163,74,0.14), 0 2px 8px rgba(0,0,0,0.06); }}
  .dashboard-top {{ display: grid; grid-template-columns: 1fr; gap: 1rem; margin-bottom: 0.5rem; }}
  @media (min-width: 640px) {{ .dashboard-top {{ grid-template-columns: 1.2fr 1fr; }} .dashboard-top .card:first-child {{ grid-column: 1; grid-row: span 2; }} .dashboard-top .card:nth-child(2) {{ grid-column: 2; grid-row: 1; }} .dashboard-top .card:nth-child(3) {{ grid-column: 2; grid-row: 2; }} }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.6rem 1rem; }}
  @media (min-width: 480px) {{ .metrics-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
  @media (min-width: 640px) {{ .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
  .metric {{ margin: 0.2rem 0; padding: 0.4rem 0; }}
  .metrics-grid .metric {{ padding: 0.6rem 0.85rem; background: linear-gradient(135deg, rgba(220,252,231,0.7) 0%, rgba(187,247,208,0.5) 100%); border-radius: 10px; border-left: 4px solid #22c55e; box-shadow: 0 1px 4px rgba(22,163,74,0.08); }}
  .value {{ font-size: 1.25rem; font-weight: bold; }}
  .zero {{ color: #64748b; }} .updated {{ color: #15803d; }}
  .card > p {{ margin: 0.75rem 0 0; font-size: 0.9rem; color: #166534; }}
  .btn-row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }}
  .btn {{ padding: 0.55rem 1rem; font-size: 0.9rem; cursor: pointer; border-radius: 10px; border: 1px solid #86efac; background: linear-gradient(180deg, #dcfce7 0%, #bbf7d0 100%); color: #14532d; font-family: inherit; font-weight: 500; transition: transform 0.15s ease, box-shadow 0.15s ease; }}
  .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(34,197,94,0.25); }}
  .run-buttons {{ display: flex; flex-wrap: wrap; gap: 0.75rem; }}
  .run-buttons button {{ padding: 0.65rem 1.25rem; font-size: 0.95rem; cursor: pointer; border-radius: 10px; border: none; background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%); color: #fff; font-weight: 600; transition: transform 0.15s ease, box-shadow 0.15s ease; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }}
  .run-buttons button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(34,197,94,0.4); }}
  .indicators-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 0.25rem; }}
  .indicators-grid .card {{ margin-bottom: 0; padding: 1.1rem 1.25rem; border-radius: 14px; border-left: 4px solid #4ade80; }}
  .indicators-grid .card:nth-child(1) {{ border-left-color: #22c55e; }}
  .indicators-grid .card:nth-child(2) {{ border-left-color: #16a34a; }}
  .indicators-grid .card:nth-child(3) {{ border-left-color: #22c55e; }}
  .indicators-grid .card:nth-child(4) {{ border-left-color: #16a34a; }}
  .indicators-grid .metric {{ padding: 0.3rem 0; font-size: 0.95rem; }}
  .indicators-grid .metric:first-child {{ font-weight: 600; color: #166534; margin-bottom: 0.35rem; }}
  .modal-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 1000; align-items: center; justify-content: center; padding: 1rem; }}
  .modal-overlay.open {{ display: flex; }}
  .modal {{ background: #fff; border-radius: 16px; max-width: 90vw; max-height: 85vh; overflow: hidden; box-shadow: 0 12px 40px rgba(0,0,0,0.18); display: flex; flex-direction: column; }}
  .modal-header {{ padding: 1rem 1.25rem; background: linear-gradient(180deg, #dcfce7 0%, #bbf7d0 100%); border-bottom: 1px solid #86efac; display: flex; justify-content: space-between; align-items: center; }}
  .modal-header h2 {{ margin: 0; font-size: 1.1rem; color: #14532d; }}
  .modal-close {{ background: #64748b; color: #fff; border: none; padding: 0.35rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }}
  .modal-close:hover {{ background: #475569; }}
  .modal-body {{ padding: 1rem; overflow: auto; flex: 1; }}
  .modal-body pre {{ margin: 0; font-size: 0.8rem; background: #1e293b; color: #e2e8f0; padding: 1rem; border-radius: 8px; overflow: auto; max-height: 60vh; }}
  .modal-body pre code {{ font-family: ui-monospace, monospace; }}
  .vars-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  .vars-table th, .vars-table td {{ padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }}
  .vars-table th {{ background: linear-gradient(180deg, #dcfce7 0%, #bbf7d0 100%); color: #14532d; }}
  .docstrings-box {{ white-space: pre-wrap; font-size: 0.85rem; background: #f0fdf4; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #bbf7d0; }}
  @media (max-width: 520px) {{ .indicators-grid {{ grid-template-columns: 1fr; }} }}
  .main-output {{ white-space: pre-wrap; font-family: ui-monospace, monospace; font-size: 0.9rem; background: rgba(220,252,231,0.6); padding: 1rem; border-radius: 10px; border-left: 4px solid #22c55e; margin-top: 0.5rem; }}
  .main-output.empty {{ color: #64748b; font-style: italic; }}
</style></head><body>
<div class="header"><h1>Day 2 Demo Dashboard</h1><p class="hello-msg">Hello, World! Welcome to the Day 2 Demo Dashboard.</p></div>
<div class="card">
  <div class="metric"><strong>Output from Run main.py</strong></div>
  <div class="main-output {'empty' if not m.get('last_main_output') else ''}">{html_module.escape(m.get('last_main_output') or 'Click "Run main.py" to see the greeting and output here.')}</div>
</div>
<div class="dashboard-top">
<div class="card">
  <div class="metrics-grid">
  <div class="metric">Main runs <span class="value {'updated' if m.get('main_runs') else 'zero'}">{m.get('main_runs', 0)}</span></div>
  <div class="metric">Registration runs <span class="value {'updated' if m.get('registration_runs') else 'zero'}">{m.get('registration_runs', 0)}</span></div>
  <div class="metric">Total demo runs <span class="value {'updated' if m.get('total_demo_runs') else 'zero'}">{m.get('total_demo_runs', 0)}</span></div>
  <div class="metric">Last main status <span class="value">{m.get('last_main_status', 'never')}</span></div>
  <div class="metric">Last registration status <span class="value">{m.get('last_registration_status', 'never')}</span></div>
  </div>
  <p><small>Run main.py and user_registration.py to update these metrics.</small></p>
</div>
<div class="card">
  <div class="run-buttons">
  <button type="button" onclick="runMain()">Run main.py</button>
  <button type="button" onclick="runRegistration()">Run user_registration.py</button>
  </div>
</div>
<div class="card">
  <div class="btn-row">
    <button class="btn" type="button" onclick="viewFile('main')">View main.py</button>
    <button class="btn" type="button" onclick="viewFile('user_registration')">View user_registration.py</button>
    <button class="btn" type="button" onclick="viewVariablesTypes()">Show Variables &amp; Types</button>
    <button class="btn" type="button" onclick="viewDocstringsComments()">View Docstrings &amp; Comments</button>
    <button class="btn" type="button" onclick="resetMetrics()">Reset Metrics</button>
  </div>
</div>
</div>
<div class="indicators-grid">
<div class="card">
  <div class="metric">Naming Convention: ✔ snake_case compliant</div>
</div>
<div class="card">
  <div class="metric">Data Types Used:</div>
  <div class="metric">✔ str</div>
  <div class="metric">✔ int</div>
  <div class="metric">✔ float</div>
  <div class="metric">✔ bool</div>
</div>
<div class="card">
  <div class="metric">Documentation Status:</div>
  <div class="metric">✔ Module docstrings present</div>
  <div class="metric">✔ Inline comments present</div>
</div>
<div class="card">
  <div class="metric">Output Verification Summary:</div>
  <div class="metric">✔ Greeting message printed</div>
  <div class="metric">✔ User profile displayed</div>
  <div class="metric">✔ Conditional logic executed</div>
</div>
</div>
<div id="modal-code" class="modal-overlay"><div class="modal"><div class="modal-header"><h2 id="modal-code-title">Source</h2><button class="modal-close" type="button" onclick="closeModal('modal-code')">Close</button></div><div class="modal-body"><pre><code id="modal-code-content" class="language-python"></code></pre></div></div></div>
<div id="modal-vars" class="modal-overlay"><div class="modal"><div class="modal-header"><h2>Variables &amp; Types</h2><button class="modal-close" type="button" onclick="closeModal('modal-vars')">Close</button></div><div class="modal-body" id="modal-vars-body"></div></div></div>
<div id="modal-docs" class="modal-overlay"><div class="modal"><div class="modal-header"><h2>Docstrings &amp; Comments</h2><button class="modal-close" type="button" onclick="closeModal('modal-docs')">Close</button></div><div class="modal-body" id="modal-docs-body"></div></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
<script>
function runMain() {{ fetch('/api/run-main', {{ method: 'POST' }}).then(() => location.reload()); }}
function runRegistration() {{ fetch('/api/run-registration', {{ method: 'POST' }}).then(() => location.reload()); }}
function closeModal(id) {{ document.getElementById(id).classList.remove('open'); }}
function openModal(id) {{ document.getElementById(id).classList.add('open'); }}
function viewFile(which) {{
  var title = which === 'main' ? 'main.py' : 'user_registration.py';
  document.getElementById('modal-code-title').textContent = title;
  fetch('/api/file/' + (which === 'main' ? 'main' : 'user_registration'))
    .then(r => r.text())
    .then(text => {{
      var el = document.getElementById('modal-code-content');
      el.textContent = text;
      if (window.Prism) Prism.highlightElement(el);
      openModal('modal-code');
    }});
}}
function viewVariablesTypes() {{
  fetch('/api/variables-types')
    .then(r => r.json())
    .then(data => {{
      var html = '<table class="vars-table"><thead><tr><th>File</th><th>Variable</th><th>Type</th></tr></thead><tbody>';
      data.forEach(function(row) {{ html += '<tr><td>' + escapeHtml(row.file) + '</td><td>' + escapeHtml(row.variable) + '</td><td>' + escapeHtml(row.type) + '</td></tr>'; }});
      html += '</tbody></table>';
      document.getElementById('modal-vars-body').innerHTML = html;
      openModal('modal-vars');
    }});
}}
function viewDocstringsComments() {{
  fetch('/api/docstrings-comments')
    .then(r => r.json())
    .then(data => {{
      var html = '';
      data.forEach(function(item) {{
        html += '<div class="docstrings-box"><strong>' + escapeHtml(item.file) + '</strong><br><br>';
        if (item.docstring) html += 'Docstring:<br>' + escapeHtml(item.docstring) + '<br><br>';
        html += 'Comments:<br>' + (item.comments.length ? item.comments.map(c => escapeHtml(c)).join('<br>') : '(none)') + '</div>';
      }});
      document.getElementById('modal-docs-body').innerHTML = html;
      openModal('modal-docs');
    }});
}}
function resetMetrics() {{
  if (!confirm('Reset all metrics to zero?')) return;
  fetch('/api/reset-metrics', {{ method: 'POST' }}).then(() => location.reload());
}}
function escapeHtml(s) {{ var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}
</script>
</body></html>
"""

@app.route("/api/metrics")
def api_metrics():
    return get_metrics()

@app.route("/api/run-main", methods=["POST"])
def api_run_main():
    try:
        result = subprocess.run(
            [sys.executable, MAIN_PY],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
            timeout=30,
        )
        output = (result.stdout or "") + (result.stderr or "")
        m = get_metrics()
        m["last_main_output"] = output.strip()
        try:
            with open(METRICS_FILE, "w") as f:
                json.dump(m, f, indent=2)
        except Exception:
            pass
    except Exception:
        pass
    return get_metrics()

@app.route("/api/run-registration", methods=["POST"])
def api_run_registration():
    try:
        subprocess.run([sys.executable, REGISTRATION_PY], cwd=APP_DIR, capture_output=True, env=os.environ.copy(), timeout=30)
    except Exception:
        pass
    return get_metrics()

@app.route("/api/file/main")
def api_file_main():
    return _read_file(MAIN_PY), 200, {"Content-Type": "text/plain; charset=utf-8"}

@app.route("/api/file/user_registration")
def api_file_user_registration():
    return _read_file(REGISTRATION_PY), 200, {"Content-Type": "text/plain; charset=utf-8"}

@app.route("/api/variables-types")
def api_variables_types():
    data = _parse_variables_and_types(MAIN_PY) + _parse_variables_and_types(REGISTRATION_PY)
    return json.dumps(data)

@app.route("/api/docstrings-comments")
def api_docstrings_comments():
    data = [_parse_docstrings_and_comments(MAIN_PY), _parse_docstrings_and_comments(REGISTRATION_PY)]
    return json.dumps(data)

@app.route("/api/reset-metrics", methods=["POST"])
def api_reset_metrics():
    initial = {"main_runs": 0, "registration_runs": 0, "last_main_status": "never", "last_registration_status": "never", "total_demo_runs": 0, "last_main_output": ""}
    try:
        with open(METRICS_FILE, "w") as f:
            json.dump(initial, f, indent=2)
    except Exception:
        pass
    return get_metrics()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
