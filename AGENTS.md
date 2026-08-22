# AGENTS.md

## Repository Rules & Overview: SimLinkServer

This project is **SimLinkServer**, a FastAPI-based server integrating Asterisk PBX with USB GSM dongles (`chan_dongle`) and Android/Web Push notifications.

### Quick Reference Files
- Comprehensive Overview: [`PROJECT_OVERVIEW.md`]
- Claude Code Guidance: [`CLAUDE.md`]
- Development Bootstrap: [`start.sh`]
### Key Rules & Guidelines
1. **Asterisk Configuration Templates**:
   - Updates to user configurations dynamically alter `/etc/asterisk/dongle.conf`, `/etc/asterisk/pjsip.conf`, and `/etc/asterisk/extensions.conf`.
   - Always verify changes in [`app/asterisk_confi_template.py`] and [`app/asterisk_config_generator.py`].
   - Dynamic lines are written below `;******** Auto generated lines below ********`. Preserve manual user configurations above this marker.

2. **Data Stores**:
   - JSON Database: [`app/data.json`] managed via [`app/database.py`]. Keep its structure backwards-compatible.
   - SQLite Database: `/var/log/asterisk/master.db` managed via [`app/database_sqlite.py`] for event logging (`sms_log`, `fastapi_call_log`, `fastapi_sms_log`).

3. **Push Notifications**:
   - Firebase Cloud Messaging API v1: Managed in [`app/services/firebase.py`] and [`app/oAuth2_generator.py`].
   - VAPID Web Push: Managed in [`app/services/webpush.py`].

4. **Testing Guidelines**:
   - Unit tests are in [`test/`].
   - Always run tests with `PYTHONPATH=. pytest` (mocking is used extensively to avoid requiring live Asterisk or Firebase hardware).
