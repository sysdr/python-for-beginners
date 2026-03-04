# project/src/main.py

"""
This script demonstrates basic Python concepts:
- Variables for storing user profile data.
- Basic data types: string, integer, float, boolean.
- Meaningful naming conventions (snake_case).
- Proper use of comments and docstrings for clarity.

In a real-world high-scale system, this foundational clarity
is paramount for maintainability, debugging, and collaboration
across large engineering teams.
"""

# --- Configuration & Global Constants (often loaded from external sources in real systems) ---
# This section would typically load sensitive data or dynamic configurations
# from environment variables, configuration files (e.g., YAML, TOML), or a
# distributed configuration service like Consul or etcd.
# For Day 2, we'll hardcode them for simplicity, but always keep the "real world" in mind.

# Application name constant - often used in logs or monitoring dashboards.
APP_NAME = "UserProfileService" # Use SCREAMING_SNAKE_CASE for constants

# --- Core Logic: User Profile Data ---

# Metrics for dashboard (same directory as script)
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
# Meaningful name: 'user_name' clearly indicates its purpose.
# In a distributed system, this might come from an authentication service.
user_name: str = "Alice Johnson" # Type hints (str) improve readability and static analysis

# 2. Integer variable for the user's age
# 'user_age' indicates an integer value representing age.
# Integer types are efficient for whole numbers and IDs.
user_age: int = 30 # Type hints (int) for whole numbers

# 3. Float variable for a user's account balance
# 'account_balance' uses a float for decimal precision, crucial for financial data.
# Note: For mission-critical financial systems, decimal.Decimal is often preferred
# to avoid floating-point inaccuracies, but float is fine for general understanding here.
account_balance: float = 12345.67 # Type hints (float) for decimal numbers

# 4. Boolean variable for user's active status
# 'is_active_user' is self-explanatory. Booleans are fundamental for feature flags,
# access controls, and state management in distributed systems.
is_active_user: bool = True # Type hints (bool) for true/false states

# --- Processing and Output ---

# Construct a personalized greeting message using f-strings (formatted string literals).
# f-strings are efficient and readable for embedding variables into strings.
greeting_message: str = f"Hello, {user_name}! Welcome to the {APP_NAME}."

# Conditional message based on active status.
# Simple control flow using a boolean variable.
status_message: str
if is_active_user:
    status_message = "Your account is currently active."
else:
    status_message = "Your account is inactive. Please reactivate."

# Print out the user's profile information.
# In a high-scale environment, these print statements would be replaced by structured logging
# (e.g., using `logging` module, pushing to ELK stack or Splunk) for observability.
print("-" * 50)
print(greeting_message)
print(f"Age: {user_age} years old")
print(f"Account Balance: ${account_balance:.2f}") # Format float to two decimal places
print(status_message)
print("-" * 50)

# Example of another comment explaining a specific part of the code
# This line below demonstrates a simple calculation, common in data processing.
future_age = user_age + 5
print(f"{user_name} will be {future_age} in five years.")

# Update dashboard metrics (so dashboard shows non-zero after demo)
m = _load_metrics()
m["main_runs"] = m.get("main_runs", 0) + 1
m["last_main_status"] = "success"
m["total_demo_runs"] = m.get("total_demo_runs", 0) + 1
_save_metrics(m)
