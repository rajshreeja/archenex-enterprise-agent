"""Create a password hash for Streamlit Secrets.   python scripts/make_user_hash.py"""
import getpass
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from archenex.auth import hash_password  # noqa: E402

pw = getpass.getpass("Password: ")
if pw != getpass.getpass("Repeat: "):
    sys.exit("Passwords differ.")
print("\nPaste this into Streamlit Secrets:\n")
print('[users.YOUR_NAME]')
print(f'password_hash = "{hash_password(pw)}"')
print('role = "reviewer"   # viewer | reviewer | admin')
