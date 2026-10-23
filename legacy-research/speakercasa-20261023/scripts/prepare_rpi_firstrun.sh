#!/usr/bin/env bash
set -euo pipefail

NETWORK_CONFIG=${1:-/tmp/galileo-rpi-cloudinit/network-config}
SSH_PUB=${2:-/home/denny/.ssh/id_ed25519.pub}
OUT=${3:-/tmp/galileo-firstrun.sh}

if [[ ! -r "$NETWORK_CONFIG" ]]; then
  echo "Missing temporary network config: $NETWORK_CONFIG" >&2
  exit 1
fi

if [[ ! -r "$SSH_PUB" ]]; then
  echo "Missing SSH public key: $SSH_PUB" >&2
  exit 1
fi

python3 - "$NETWORK_CONFIG" "$SSH_PUB" "$OUT" <<'PY'
import pathlib
import re
import stat
import sys

network_config = pathlib.Path(sys.argv[1])
ssh_pub = pathlib.Path(sys.argv[2])
out = pathlib.Path(sys.argv[3])

text = network_config.read_text()
ssid_match = re.search(r'^\s{6}"(.+)":\s*$', text, re.MULTILINE)
password_match = re.search(r'^\s{8}password:\s*"(.+)"\s*$', text, re.MULTILINE)
if not ssid_match or not password_match:
    raise SystemExit("Could not extract SSID/password from temporary network config")

ssid = ssid_match.group(1)
password = password_match.group(1)
key = ssh_pub.read_text().strip()

def sh_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"

def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

script = f'''#!/bin/bash
set -euo pipefail

cat > /run/galileo-custom.toml <<'EOF_TOML'
config_version = 1

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
EOF_TOML

/usr/lib/raspberrypi-sys-mods/init_config /run/galileo-custom.toml
rm -f /run/galileo-custom.toml
systemctl enable ssh || true

FWLOC="/boot/firmware"
if [ ! -d "$FWLOC" ]; then
  FWLOC="/boot"
fi

if [ -f "$FWLOC/cmdline.txt" ]; then
  sed -i 's| systemd.run=[^ ]*||g; s| systemd.run_success_action=[^ ]*||g; s| systemd.unit=kernel-command-line.target||g' "$FWLOC/cmdline.txt"
fi

rm -f "$FWLOC/firstrun.sh" /boot/firstrun.sh
sync
'''

out.write_text(script)
out.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
print(out)
PY
