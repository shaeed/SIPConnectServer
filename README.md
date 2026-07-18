[![Build Status](https://github.com/shaeed/SimLinkServer/actions/workflows/python-app.yml/badge.svg)](https://github.com/shaeed/SimLinkServer/actions/workflows/python-app.yml) [![CodeQL](https://github.com/shaeed/SimLinkServer/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/shaeed/SimLinkServer/actions/workflows/github-code-scanning/codeql)

# SimLinkServer

**SimLinkServer** is a management and notification layer on top of Asterisk PBX. It lets you run SIP-based voice/SMS communication through USB GSM dongles, and pushes call/SMS alerts to Android and browser clients in real time.
This project aims to provide a simple, self-hosted solution for SIP-based voice communication in a local environment (to be used with VPN).

---

## Features

✅ SIP registration handling via Asterisk, using USB GSM dongles as trunks
✅ Auto-generated Asterisk config (`pjsip.conf`, `dongle.conf`, `extensions.conf`) from a simple user list
✅ Incoming call/SMS alerts pushed to devices via Firebase Cloud Messaging (Android) and Web Push (Chrome/Firefox)
✅ Outgoing SMS routed back through the dongle or forwarded via Firebase
✅ Vue-based admin dashboard: manage SIP users, view/remove registered devices (FCM + Web Push), browse Call Logs and SMS Logs
✅ Single `./start.sh` script for first-time setup and upgrades

---

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Upgrading](#upgrading)
- [Local Development (without Docker)](#local-development-without-docker)
- [Using the Dashboard](#using-the-dashboard)
- [Testing & Linting](#testing--linting)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture

The stack runs as two containers behind `docker-compose`:

- **`simlink`** — Asterisk + FastAPI (`app/`), managed by `supervisord`. Generates Asterisk config from a JSON user database, handles SIP/SMS alerts, and serves the REST API.
- **`nginx`** — terminates TLS, serves the built Vue frontend (`frontend/dist`), and proxies `/sip`, `/api`, `/gsm`, `/upload_sa` to the FastAPI service.

Persistent state (`data.json`, `master.db`, `service-account.json`) is bind-mounted from a fixed host path (`/var/lib/simlink` by default) so it survives container rebuilds.

---

## Prerequisites

- **Docker** and **Docker Compose**
- **Node.js/npm** (only needed to build the frontend — `start.sh` runs this for you)
- A USB GSM dongle with a SIM card
- `sudo` access (the SIP container needs `privileged: true` for dongle access, and `/var/lib/simlink` is root-owned by default)

---

## Quick Start (Docker)

```bash
git clone https://github.com/shaeed/SimLinkServer.git
cd SimLinkServer
./start.sh
```

`start.sh` does everything needed for a first run:

1. Builds the Vue frontend (`cd frontend && npm install && npm run build`)
2. Generates a self-signed TLS certificate under `certs/` if one doesn't already exist
3. Seeds `data.json`, `master.db`, and `service-account.json` under the data directory (default `/var/lib/simlink`, override with `SIMLINK_DATA_DIR`) if they don't already exist — this avoids a Docker bind-mount pitfall where a missing source file gets silently created as a directory instead
4. Runs `docker-compose up -d --build`

Once it's up, open `https://<server-ip>/` (you'll need to accept the self-signed cert warning unless you swap in your own certificate) to reach the admin dashboard. From there:

- Upload your Firebase service account JSON (for push notifications) under the Config card
- Add a SIP user, picking the dongle's audio/data `ttyUSB` interfaces
- Point your SIP client (e.g. ZoiPer) at the server using that username/password

---

## Upgrading

```bash
git pull
./start.sh
```

Re-running `start.sh` rebuilds the frontend and restarts the containers (`docker-compose up -d --build`), picking up both backend and frontend changes. It's safe to re-run any time — it only seeds data files that don't already exist.

---

## Local Development (without Docker)

```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal, proxies API calls to :8000)
cd frontend
npm install
npm run dev
```

---

## Using the Dashboard

- **Users** — add, edit, or delete SIP users; Asterisk config is regenerated and Asterisk restarted automatically on any change.
- **Devices** — each user row has a devices icon that opens a dialog listing every device registered for FCM push, Web Push, or both, with a one-click remove.
- **Call Logs / SMS Logs** — separate pages under the nav bar, backed by the SQLite call/SMS log.
- **Notifications** — lets a browser subscribe to Web Push alerts for a given SIP username (no app install required for desktop notifications).

---

## Testing & Linting

```bash
# Run all backend tests
PYTHONPATH=. pytest

# Run a single test file / test
PYTHONPATH=. pytest test/test_main.py
PYTHONPATH=. pytest test/test_main.py::test_function_name

# Lint (blocking: syntax errors / undefined names)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Lint (full, non-blocking)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

CI runs these on every push to `dev` and on all pull requests.

---

## Configuration

| Setting | Where | Notes |
|---|---|---|
| Data directory | `SIMLINK_DATA_DIR` env var (used by `start.sh`) | Defaults to `/var/lib/simlink`; must be an absolute path so it resolves the same under `sudo` or any user |
| Firebase service account | Dashboard → Config card (`/upload_sa`) | Required for FCM/Web Push alerts to be sent |
| SIP port | `docker-compose.yml` (`network_mode: host`) | UDP 5060, standard SIP |
| Dashboard/API | `nginx` | HTTPS on 443 (redirects from 80), proxies to FastAPI on `127.0.0.1:8000` |

---

## Contributing

Contributions, issues, and feature requests are welcome!

    Fork the repository

    Create your feature branch (git checkout -b feature/awesome-feature)

    Commit your changes (git commit -m 'Add some feature')

    Push to the branch (git push origin feature/awesome-feature)

    Open a Pull Request

## License

This project is licensed under the MIT License — see LICENSE for details.

## Author

Maintained by Shaeed Khan.
