"""Root conftest.py — sets environment variables before importing app modules."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
