#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Fixed absolute path (not ~) so it resolves the same regardless of which
# user or sudo runs this script or docker-compose directly.
DATA_DIR="${SIPCONNECT_DATA_DIR:-/var/lib/sipconnect}"

echo "==> Building frontend"
(cd frontend && npm install && npm run build)

echo "==> Checking TLS certificate"
if [ ! -f certs/cert.pem ] || [ ! -f certs/key.pem ]; then
  echo "    No certs found in certs/, generating a self-signed one"
  mkdir -p certs
  openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout certs/key.pem -out certs/cert.pem -days 365 -subj "/CN=sipconnect"
else
  echo "    Existing certs found, skipping"
fi

OLD_DATA_DIR="$HOME/SIPConnectServerData"
if [ -f "$OLD_DATA_DIR/data.json" ] && [ ! -f "$DATA_DIR/data.json" ]; then
  echo "==> Found existing data at $OLD_DATA_DIR (old default location)"
  echo "    Move it to $DATA_DIR before continuing, e.g.:"
  echo "      sudo mkdir -p $DATA_DIR && sudo mv $OLD_DATA_DIR/* $DATA_DIR/"
  exit 1
fi

echo "==> Checking data directory ($DATA_DIR)"
if ! mkdir -p "$DATA_DIR" 2>/dev/null; then
  echo "    $DATA_DIR needs elevated privileges to create, retrying with sudo"
  sudo mkdir -p "$DATA_DIR"
  sudo chown "$(id -u):$(id -g)" "$DATA_DIR"
fi

if [ ! -f "$DATA_DIR/data.json" ]; then
  echo "    Seeding data.json"
  cat > "$DATA_DIR/data.json" <<'EOF'
{
  "db_version": "0.01",
  "app-config": {
    "service_account_file": "uploads/dummy-service-account.json",
    "firebase_project_id": "dummy-project-id"
  },
  "users": []
}
EOF
else
  echo "    Existing data.json found, skipping"
fi

if [ ! -f "$DATA_DIR/master.db" ]; then
  echo "    Creating empty master.db"
  touch "$DATA_DIR/master.db"
else
  echo "    Existing master.db found, skipping"
fi

if [ ! -f "$DATA_DIR/service-account.json" ]; then
  echo "    Creating placeholder service-account.json"
  touch "$DATA_DIR/service-account.json"
else
  echo "    Existing service-account.json found, skipping"
fi

echo "==> Starting Docker Compose"
docker-compose up -d --build
