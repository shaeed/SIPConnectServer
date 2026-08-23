# SimLinkServer Repository & Architecture Overview

## Project Summary
**SimLinkServer** is a FastAPI-based management, routing, and push notification layer built on top of Asterisk PBX. It bridges PSTN voice calls and SMS functionality (via USB GSM Huawei dongles running `chan_dongle` or Android devices operating in server mode) to mobile clients (Android via Firebase Cloud Messaging) and web applications (via Web Push VAPID).

---

## Technical Stack
- **Backend**: Python 3.9+ with FastAPI, Uvicorn, Jinja2 templates, Pydantic v2, `aiofiles`, `aiohttp`, `pywebpush`, `py_vapid`, `google-auth`.
- **PBX & Telephony**: Asterisk PBX with `asterisk-chan-dongle` module, PJSIP stack, AGI scripts (`agi_sms_sender.py`).
- **Data Stores**:
  - `app/data.json`: Primary JSON document database storing users, SIP credentials, FCM tokens, Web Push subscriptions, OAuth2 cache, and VAPID key pairs.
  - `/var/log/asterisk/master.db` (or `/var/lib/simlink/master.db`): SQLite database logging call events (`fastapi_call_log`) and SMS message history (`fastapi_sms_log` and `sms_log`).
- **Frontend**:
  - Legacy/Admin views: FastAPI Jinja2 HTML templates (`app/templates/dashboard.html`, `logs.html`).
  - SPA: Vue 3 + Vite single-page app in `frontend/` (components for User management, Device dialogs, System config, and Call/SMS log viewers).
- **Web Server & Reverse Proxy**: Nginx (serving static frontend assets and reverse proxying API requests with SSL/TLS support).
- **Process Supervision & Containerization**: Docker Compose (`privileged: true`, `network_mode: host`), Dockerfile (Debian Bullseye), Supervisord (managing Asterisk & Uvicorn in container).

---

## Directory & File Structure Map

```
SimLinkServer/
├── app/                              # Core FastAPI Application
│   ├── Constants.py                  # Modem device type constants (Huawei, Android, Dummy)
│   ├── asterisk_confi_template.py    # Raw templates for dongle.conf, pjsip.conf, extensions.conf
│   ├── asterisk_config_generator.py  # Dynamic generation of Asterisk config files
│   ├── data.json                     # JSON database file (User & system config state)
│   ├── database.py                   # Data access layer for JSON database (users, FCM, VAPID, OAuth2)
│   ├── database_sqlite.py            # SQLite data access layer for Call & SMS logs
│   ├── devices.py                    # Routing target resolution (huawei dongle vs android vs dummy)
│   ├── main.py                       # FastAPI entry point & API route definitions
│   ├── models.py                     # Pydantic v2 schemas / data transfer objects
│   ├── oAuth2_generator.py           # Google Service Account OAuth2 token manager for FCM v1
│   ├── services/                     # Application service modules
│   │   ├── asterisk.py               # Asterisk CLI execution & server configuration runner
│   │   ├── firebase.py               # Asynchronous FCM push notification dispatcher
│   │   ├── gsm.py                    # SMS routing service (Asterisk CLI or Firebase)
│   │   └── webpush.py                # VAPID Web Push notification service
│   ├── templates/                    # Jinja2 templates (dashboard.html, logs.html, home.html)
│   ├── tty_devices.py                # Serial interface detection (/dev/ttyUSB*)
│   └── users.py                      # User registration logic & voicemail ID allocation
├── frontend/                         # Vue 3 + Vite SPA Frontend
│   ├── dist/                         # Compiled static production assets
│   ├── src/
│   │   ├── api/index.js              # Centralized API fetch client for FastAPI routes
│   │   ├── components/               # UI components (UserTable, UserFormDialog, DeviceListDialog, ConfigCard)
│   │   ├── views/                    # Pages (Dashboard, CallLogs, SmsLogs, Notifications)
│   │   ├── App.vue                   # SPA Root layout component
│   │   └── main.js                   # Vue app initialization
│   ├── package.json                  # Frontend dependencies
│   └── vite.config.js                # Vite build config with API proxy rule
├── scripts/                          # Auxiliary & AGI Scripts
│   ├── agi_sms_sender.py             # Asterisk AGI script triggered on incoming dongle SMS
│   └── check_tty.sh                  # Shell script for inspecting TTY devices
├── nginx/                            # Reverse Proxy Config
│   └── nginx.conf                    # Nginx SSL & reverse proxy configuration
├── test/                             # Automated Test Suite (Pytest)
│   ├── test_main.py                  # API endpoint tests
│   ├── test_database.py              # JSON database unit tests
│   ├── test_database_sqlite.py       # SQLite database unit tests
│   ├── test_asterisk_config_generator.py # Asterisk generator unit tests
│   ├── test_oAuth2_generator.py      # OAuth2 token manager tests
│   ├── test_users.py                 # User creation unit tests
│   └── services/                     # Unit tests for asterisk, firebase, gsm, and webpush services
├── CLAUDE.md                         # Command & architecture guidelines for Claude Code
├── Dockerfile                        # Production Dockerfile (Debian Bullseye, Asterisk, chan_dongle build)
├── Dockerfile.dev                    # Development Dockerfile
├── docker-compose.yml                # Multi-service compose configuration (FastAPI + Nginx)
├── requirements.txt                  # Python dependencies
├── start.sh                          # Automated deployment/bootstrap script
└── supervisord.conf                  # Supervisord config running Asterisk and Uvicorn
```

---

## Core System Workflows

### 1. User Creation & Dynamic Asterisk Config Generation
- **API**: `POST /sip/users` or `PUT /sip/users/{username}`
- **Flow**:
  1. `app/users.py` validates request, assigns a voicemail number (100, 101, ...), and saves details to `data.json`.
  2. `app/asterisk_config_generator.py` reads user database and formats templates in `asterisk_confi_template.py`.
  3. Writes auto-generated blocks into `/etc/asterisk/dongle.conf`, `/etc/asterisk/pjsip.conf`, and `/etc/asterisk/extensions.conf` (preserving manual edits above the marker identifier).
  4. Triggers `asterisk -rx "core restart now"` via `app/services/asterisk.py`.

### 2. Mobile & Web Push Device Registration
- **FCM Registration**: `POST /sip/client/register` stores device FCM tokens under `users -> <username> -> devices -> <device_id>`.
- **Web Push Registration**: `POST /sip/client/register/web-push` stores VAPID push subscriptions under the device entry.
- **Unregistration**: `DELETE /sip/client/{username}/{device_id}` removes the specified device entry.

### 3. Incoming Call & SMS Alerts
- **Call Alert (`POST /sip/alert/call`)**:
  - Asterisk dialplan routes incoming GSM dongle calls to execute a curl/HTTP call to FastAPI `/sip/alert/call`.
  - Logged into SQLite `fastapi_call_log`.
  - Dispatches FCM push notifications via `app/services/firebase.py` and Web Push notifications via `app/services/webpush.py`.
- **SMS Alert (`POST /sip/alert/sms`)**:
  - Dongle receives SMS → Asterisk executes AGI script `scripts/agi_sms_sender.py`.
  - AGI script posts payload to FastAPI `/sip/alert/sms` and inserts log into `sms_log`.
  - FastAPI logs entry into SQLite `fastapi_sms_log`.
  - Broadcasts push notifications to registered FCM and Web Push clients (filtering out sender device if applicable).

### 4. Outgoing SMS Dispatch
- **API**: `POST /gsm/sms`
- **Flow**:
  - Logged in SQLite `fastapi_sms_log`.
  - `app/services/gsm.py` evaluates outgoing device type (`determine_outgoing_system`):
    - **Huawei Dongle**: Invokes `asterisk -rx "dongle sms <dongle_id> <phone_number> <message>"`.
    - **Android Mode / Remote**: Sends FCM notification with `forward_to_gsm=True` to instruct the Android device to send the SMS via its cellular network.

---

## Primary API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/sip/users` | `GET`, `POST` | List all SIP users / Create new user |
| `/sip/users/{username}` | `GET`, `PUT`, `DELETE` | View, update, or delete a SIP user |
| `/sip/users/{username}/devices` | `GET` | Get registered devices for a user |
| `/sip/client/register` | `POST` | Register/update FCM token for a device |
| `/sip/client/register/web-push` | `POST` | Register Web Push subscription |
| `/sip/client/{username}/{device_id}` | `DELETE` | Remove registered device |
| `/sip/alert/call` | `POST` | Webhook triggered on incoming call alert |
| `/sip/alert/sms` | `POST` | Webhook triggered on incoming SMS alert |
| `/gsm/sms` | `POST` | Send outgoing SMS via Dongle or Android |
| `/api/config` | `GET` | Retrieve Firebase service account & project status |
| `/api/tty-devices` | `GET` | List available USB serial TTY devices |
| `/api/vapid-public-key` | `GET` | Get server VAPID public key for Web Push |
| `/api/logs/call` | `GET` | Fetch call history from SQLite |
| `/api/logs/sms` | `GET` | Fetch SMS history from SQLite |
| `/upload_sa` | `POST` | Upload Google Firebase service account JSON |
| `/sip/restart` | `POST` | Restart Asterisk SIP server |

---

## Deployment & Running Instructions

### Local Development
1. **Backend**:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Production Setup via Docker
- Run `./start.sh` which performs:
  1. Frontend compilation (`cd frontend && npm run build`).
  2. Generation of self-signed TLS certificates in `certs/` if missing.
  3. Initialization of host persistence data directory `/var/lib/simlink` (`data.json`, `master.db`, `service-account.json`).
  4. Spawning Docker containers via `docker-compose up -d --build`.
