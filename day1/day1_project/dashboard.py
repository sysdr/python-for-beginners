"""Simple dashboard that displays metrics updated by the demo."""
import json
import os
import subprocess
import sys
from flask import Flask, send_from_directory

app = Flask(__name__)
METRICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json")
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(APP_DIR, "main.py")

def get_metrics():
    try:
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"posts_fetched": 0, "last_run_status": "never", "last_post_id": 0, "total_runs": 0}

def get_runtime_info():
    """Runtime info for Day 1 lesson: isolation, reproducibility, execution control."""
    venv_path = os.environ.get("VIRTUAL_ENV", "")
    venv_active = bool(venv_path)
    venv_name = os.path.basename(venv_path) if venv_path else ""
    venv_label = f"ACTIVE ({venv_name})" if venv_active else "NOT ACTIVE"
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    pyenv_ver = os.environ.get("PYENV_VERSION", "")
    python_source = " (pyenv)" if pyenv_ver else ""
    python_version_display = f"Python Version: {py_ver}{python_source}"
    req_loaded = "requirements.txt loaded"
    req_path = os.path.join(APP_DIR, "requirements.txt")
    if os.path.isfile(req_path):
        try:
            with open(req_path, "r") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            if lines:
                req_loaded = f"requirements.txt loaded ({', '.join(lines)})"
        except Exception:
            pass
    return {
        "venv_label": venv_label,
        "venv_active": venv_active,
        "python_version_display": python_version_display,
        "requirements_loaded": req_loaded,
    }

@app.route("/")
def index():
    m = get_metrics()
    ri = get_runtime_info()
    return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Day1 Dashboard</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; max-width: 720px; margin: 0 auto; padding: 2rem; min-height: 100vh; background: linear-gradient(160deg, #dbeafe 0%, #bfdbfe 50%, #93c5fd 100%); color: #1e3a5f; }}
  .header {{ text-align: center; margin-bottom: 2rem; padding: 1.5rem; background: rgba(224, 242, 254, 0.9); border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  .header h1 {{ margin: 0; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; color: #1e40af; }}
  .card {{ background: #eff6ff; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid rgba(59, 130, 246, 0.2); }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }}
  .metric {{ margin: 0; padding: 1rem; background: #dbeafe; border-radius: 10px; border-left: 4px solid #3b82f6; }}
  .metric .value {{ font-size: 1.5rem; font-weight: 700; display: block; margin-top: 0.25rem; }}
  .zero {{ color: #64748b; }}
  .updated {{ color: #1d4ed8; }}
  .card > p {{ margin: 0.75rem 0 0; font-size: 0.9rem; color: #1e40af; }}
  .section {{ margin-top: 2rem; }}
  .section h2 {{ margin: 0 0 1rem; font-size: 1.1rem; font-weight: 600; color: #1e40af; text-transform: uppercase; letter-spacing: 0.04em; }}
  .btn-row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
  .btn {{ margin: 0; padding: 0.6rem 1.2rem; font-size: 0.95rem; cursor: pointer; border-radius: 8px; border: none; font-weight: 500; transition: transform 0.15s, box-shadow 0.15s; }}
  .btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
  .btn:active {{ transform: translateY(0); }}
  .btn-run {{ background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%); color: #fff; }}
  .btn-restart {{ background: #bfdbfe; color: #1e40af; }}
  .btn-reset {{ background: #e0e7ff; color: #3730a3; }}
</style></head><body>
<div class="header"><h1>Day 1 Demo Dashboard</h1></div>

<div class="card">
  <div class="metrics-grid">
    <div class="metric">Posts fetched <span class="value {'updated' if m.get('posts_fetched') else 'zero'}">{m.get('posts_fetched', 0)}</span></div>
    <div class="metric">Total runs <span class="value {'updated' if m.get('total_runs') else 'zero'}">{m.get('total_runs', 0)}</span></div>
    <div class="metric">Last run status <span class="value">{m.get('last_run_status', 'never')}</span></div>
    <div class="metric">Last post ID <span class="value {'updated' if m.get('last_post_id') else 'zero'}">{m.get('last_post_id', 0)}</span></div>
  </div>
  <p><small>Run the demo (main.py) to update these metrics.</small></p>
</div>

<div class="section">
  <h2>Execution control</h2>
  <div class="card">
    <div class="btn-row">
      <button class="btn btn-run" type="button" onclick="runMain()">▶ Run main.py</button>
      <button class="btn btn-restart" type="button" onclick="restartApp()">🔄 Restart App</button>
      <button class="btn btn-reset" type="button" onclick="resetMetrics()">🧹 Reset Metrics</button>
    </div>
  </div>
</div>

<div class="section">
  <h2>Environment (isolation & reproducibility)</h2>
  <div class="card">
    <div class="metric">Virtual Env: <span class="value">{ri['venv_label']}</span></div>
    <div class="metric">{ri['python_version_display']}</div>
    <div class="metric">{ri['requirements_loaded']}</div>
  </div>
</div>

<script>
function runMain() {{
  fetch('/api/run-main', {{ method: 'POST' }}).then(r => r.json()).then(() => location.reload()).catch(() => location.reload());
}}
function restartApp() {{
  if (confirm('Restart the application? The page will reload.')) {{
    fetch('/api/restart', {{ method: 'POST' }}).then(() => setTimeout(() => location.reload(), 2000)).catch(() => location.reload());
  }}
}}
function resetMetrics() {{
  if (confirm('Reset all metrics to zero?')) {{
    fetch('/api/reset-metrics', {{ method: 'POST' }}).then(r => r.json()).then(() => location.reload()).catch(() => location.reload());
  }}
}}
</script>
</body></html>
"""

@app.route("/api/metrics")
def api_metrics():
    return get_metrics()

@app.route("/api/run-main", methods=["POST"])
def api_run_main():
    """Run main.py and return updated metrics."""
    try:
        subprocess.run(
            [sys.executable, MAIN_PY],
            cwd=APP_DIR,
            capture_output=True,
            env=os.environ.copy(),
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass
    return get_metrics()

@app.route("/api/restart", methods=["POST"])
def api_restart():
    """Restart the backend application (clear in-memory state)."""
    def do_restart():
        import time
        time.sleep(1)
        os.chdir(APP_DIR)
        subprocess.Popen([sys.executable, os.path.abspath(__file__)], cwd=APP_DIR, env=os.environ)
        os._exit(0)
    try:
        import threading
        t = threading.Thread(target=do_restart)
        t.daemon = True
        t.start()
        return {"status": "restarting"}
    except Exception:
        return {"status": "error"}, 500

@app.route("/api/reset-metrics", methods=["POST"])
def api_reset_metrics():
    """Reset metrics to initial state. Does not restart app."""
    initial = {"posts_fetched": 0, "last_run_status": "never", "last_post_id": 0, "total_runs": 0}
    try:
        with open(METRICS_FILE, "w") as f:
            json.dump(initial, f, indent=2)
    except Exception:
        pass
    return get_metrics()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
