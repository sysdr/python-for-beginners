import requests
import sys
import json
import os

METRICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json")

def load_metrics():
    try:
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"posts_fetched": 0, "last_run_status": "never", "last_post_id": 0, "total_runs": 0}

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

def fetch_post(post_id):
    """Fetches a single post from JSONPlaceholder API."""
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    print(f"  [App] Fetching data from: {url}", file=sys.stderr)
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"  [App] HTTP Error: {e}", file=sys.stderr)
    except requests.exceptions.ConnectionError as e:
        print(f"  [App] Connection Error: {e}", file=sys.stderr)
    except requests.exceptions.Timeout as e:
        print(f"  [App] Timeout Error: {e}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"  [App] An unexpected error occurred: {e}", file=sys.stderr)
    return None

if __name__ == "__main__":
    print("===========================================", file=sys.stderr)
    print("  [App] Starting Python application...", file=sys.stderr)
    metrics = load_metrics()
    metrics["total_runs"] = metrics.get("total_runs", 0) + 1
    post_data = fetch_post(1)
    if post_data:
        metrics["posts_fetched"] = metrics.get("posts_fetched", 0) + 1
        metrics["last_run_status"] = "success"
        metrics["last_post_id"] = post_data.get("id", 1)
        print("  [App] Fetched Post Data:", file=sys.stderr)
        print(f"    Title: {post_data.get('title')}", file=sys.stderr)
        print(f"    Body: {post_data.get('body')[:50]}...", file=sys.stderr) # Truncate body for display
    else:
        metrics["last_run_status"] = "failure"
        print("  [App] Failed to fetch post data.", file=sys.stderr)
    save_metrics(metrics)
    print("  [App] Application finished.", file=sys.stderr)
    print("===========================================", file=sys.stderr)
