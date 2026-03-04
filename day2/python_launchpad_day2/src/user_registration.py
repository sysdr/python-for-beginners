# project/src/user_registration.py

"""
ASSIGNMENT: User Registration Module

This script simulates a basic user registration process.
It defines variables for a new user's profile, applies meaningful naming,
adds comments, and prints a formatted registration confirmation.

This serves as a foundational component for a larger user management system.
"""

import datetime # Needed for timestamp formatting
import json
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_METRICS_FILE = os.path.join(_SCRIPT_DIR, "metrics.json")

def _load_metrics():
    try:
        with open(_METRICS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"main_runs": 0, "registration_runs": 0, "last_main_status": "never", "last_registration_status": "never", "total_demo_runs": 0}

def _save_metrics(m):
    with open(_METRICS_FILE, "w") as f:
        json.dump(m, f, indent=2)

# --- Define Variables for a New User ---
# TODO: Implement the assignment here.
#       1. Define new_user_id (int)
#       2. Define new_user_email (str)
#       3. Define initial_login_count (int)
#       4. Define has_premium_access (bool)
#       5. Define registration_timestamp (float - use 1678886400.0)

# Example placeholder (replace with your actual assignment implementation):
new_user_id: int = 1001
new_user_email: str = "john.doe@example.com"
initial_login_count: int = 0
has_premium_access: bool = False
registration_timestamp: float = 1678886400.0 # Placeholder Unix timestamp

# --- Processing and Output ---
print("\n" + "=" * 60)
print("       ✨ User Registration Module - Assignment Output ✨")
print("=" * 60)
print(f"User Registration Successful for ID: {new_user_id}!")
print(f"Email: {new_user_email}")
print(f"Initial Login Count: {initial_login_count}")
print(f"Premium Access: {'Yes' if has_premium_access else 'No'}")

# Format timestamp for better readability
timestamp_dt = datetime.datetime.fromtimestamp(registration_timestamp)
print(f"Registration Time: {timestamp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("=" * 60 + "\n")

# Update dashboard metrics
m = _load_metrics()
m["registration_runs"] = m.get("registration_runs", 0) + 1
m["last_registration_status"] = "success"
m["total_demo_runs"] = m.get("total_demo_runs", 0) + 1
_save_metrics(m)
