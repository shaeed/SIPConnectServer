# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server locally (with auto-reload)
uvicorn app.main:app --reload

# Run with Docker Compose (full stack: Asterisk + FastAPI)
docker-compose up -d --build
```

### Testing
```bash
# Run all tests (must set PYTHONPATH to repo root)
PYTHONPATH=. pytest

# Run a single test file
PYTHONPATH=. pytest test/test_main.py

# Run a single test by name
PYTHONPATH=. pytest test/test_main.py::test_function_name
```

### Linting
```bash
# Check for syntax errors and undefined names (blocking)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full lint (non-blocking, max line length 127)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

CI runs on push to `dev` and all pull requests via `.github/workflows/python-app.yml`.

## Architecture

**SIPConnectServer** is a FastAPI server that acts as the management and notification layer on top of Asterisk PBX. It enables SIP-based voice communication via USB GSM dongles and pushes call/SMS alerts to Android clients via Firebase.

### Core Data Flow

1. **User Creation**: Admin POSTs to `/sip/users` → JSON database updated → Asterisk config files regenerated → Asterisk restarted
2. **Device Registration**: Mobile app POSTs FCM token to `/sip/client/register` → stored per user/device in JSON
3. **Incoming Call/SMS**: Asterisk receives signal from dongle → calls FastAPI `/sip/alert/call` or `/sip/alert/sms` → logged to SQLite → Firebase push notification sent to registered devices
4. **Outgoing SMS**: Client POSTs to `/gsm/sms` → routed to dongle modem via Asterisk CLI or Firebase

### Key Layers

**API Layer** (`app/main.py`)  
All HTTP endpoints. Handles user management, device registration, call/SMS alerts, log retrieval, and config upload. Uses Jinja2 templates for the admin dashboard (`/`) and logs page (`/logs`).

**Data Persistence**
- `app/data.json` — Primary user database (JSON file). Stores SIP users, FCM tokens, OAuth2 tokens, and metadata. Read/written via `app/database.py`.
- SQLite at `/var/log/asterisk/master.db` — Append-only log of call and SMS events. Accessed via `app/database_sqlite.py`.

**Asterisk Config Generation** (`app/asterisk_config_generator.py` + `app/asterisk_confi_template.py`)  
Configs for `dongle.conf`, `pjsip.conf`, and `extensions.conf` are generated dynamically from the JSON user database using Jinja2-style templates. The generator writes only the auto-generated section (delimited by a marker), preserving any manually added config above it. Config is regenerated on every user create/update/delete.

**Services** (`app/services/`)
- `asterisk.py` — Runs Asterisk CLI commands (`asterisk -rx "..."`) for dongle SMS sending and service restart
- `firebase.py` — Sends push notifications via Firebase Cloud Messaging using OAuth2 service account tokens
- `gsm.py` — Routes outgoing SMS to either Asterisk dongle or Firebase depending on device type

**Models** (`app/models.py`)  
Pydantic v2 schemas for all request/response bodies. `Constants.py` defines device type values (Android client, Huawei dongle, dummy).

### Important Constraints

- Asterisk config generation rewrites sections in `dongle.conf`, `pjsip.conf`, and `extensions.conf` — changes to templates in `app/asterisk_confi_template.py` affect all users on next restart.
- The JSON database (`app/data.json`) is both config and runtime state — it is tracked in git (with real data stripped); keep its schema consistent.
- Firebase push notifications require a valid service account JSON uploaded via the dashboard (`/upload_sa`). The OAuth2 token is refreshed and cached in the JSON database.
- The server runs inside Docker alongside Asterisk under `supervisord`. FastAPI runs on port 8000; SIP uses UDP port 5060.
- Tests in `test/` use mocking extensively to avoid requiring a live Asterisk or Firebase — maintain this pattern when adding tests.
