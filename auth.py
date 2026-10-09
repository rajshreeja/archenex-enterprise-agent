"""
Access control: named users with roles, PBKDF2 password hashes (no plain-text passwords in secrets).

Roles:  viewer  = read dashboards and reports
        reviewer = viewer + approve / reject / defer actions, dispatch to owners
        admin   = reviewer + manage connections and assumptions

Secrets format (Streamlit -> Settings -> Secrets):
  [users.priya]
  password_hash = "pbkdf2_sha256$200000$<salt>$<hash>"     # from scripts/make_user_hash.py
  role = "reviewer"

Legacy: a single APP_PASSWORD still works and signs the person in as admin.
If neither is configured the app runs in OPEN DEMO MODE and says so on screen.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os

ROLES = ("viewer", "reviewer", "admin")
ITER = 200_000


def hash_password(password: str, salt: bytes | None = None, iterations: int = ITER) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, it, salt_b64, dk_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt, want = base64.b64decode(salt_b64), base64.b64decode(dk_b64)
        got = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(it))
        return hmac.compare_digest(got, want)
    except Exception:
        return False


def authenticate(username: str, password: str, users: dict | None, legacy_password: str | None):
    """Return (role, display_name) or None."""
    if users:
        u = users.get(username.strip())
        if u and verify_password(password, str(u.get("password_hash", ""))):
            role = u.get("role", "viewer")
            return (role if role in ROLES else "viewer"), username.strip()
    if legacy_password and hmac.compare_digest(str(password), str(legacy_password)):
        return "admin", username.strip() or "admin"
    return None


def can(role: str, need: str) -> bool:
    return ROLES.index(role) >= ROLES.index(need)
