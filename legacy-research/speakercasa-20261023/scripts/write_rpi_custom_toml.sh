#!/usr/bin/env bash
set -euo pipefail

BOOTFS=${1:-/run/media/denny/bootfs}
NETWORK_CONFIG=${2:-/tmp/galileo-rpi-cloudinit/network-config}
SSH_PUB=${3:-/home/denny/.ssh/id_ed25519.pub}

if [[ ! -d "$BOOTFS" ]]; then
  echo "Missing bootfs mount: $BOOTFS" >&2
  exit 1
fi

if [[ ! -r "$NETWORK_CONFIG" ]]; then
  echo "Missing temporary network config: $NETWORK_CONFIG" >&2
  exit 1
fi

if [[ ! -r "$SSH_PUB" ]]; then
  echo "Missing SSH public key: $SSH_PUB" >&2
  exit 1
fi

python3 - "$BOOTFS" "$NETWORK_CONFIG" "$SSH_PUB" <<'PY'
import pathlib
import re
import sys

bootfs = pathlib.Path(sys.argv[1])
network_config = pathlib.Path(sys.argv[2])
ssh_pub = pathlib.Path(sys.argv[3])

text = network_config.read_text()
ssid_match = re.search(r'^\s{6}"(.+)":\s*$', text, re.MULTILINE)
password_match = re.search(r'^\s{8}password:\s*"(.+)"\s*$', text, re.MULTILINE)
if not ssid_match or not password_match:
    raise SystemExit("Could not extract SSID/password from temporary network config")

ssid = ssid_match.group(1)
password = password_match.group(1)
key = ssh_pub.read_text().strip()

def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

custom = f'''config_version = 1

[system]
hostname = "galileo"

[user]
name = "denny"
password = "!"
password_encrypted = true

[ssh]
enabled = true
password_authentication = false
authorized_keys = ["{toml_escape(key)}"]

[wlan]
ssid = "{toml_escape(ssid)}"
password = "{toml_escape(password)}"
password_encrypted = false
country = "IT"

[locale]
timezone = "Europe/Rome"
keymap = "it"
'''

target = bootfs / "custom.toml"
target.write_text(custom)
target.chmod(0o600)
print(target)
PY
