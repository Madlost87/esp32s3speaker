#!/usr/bin/env bash
set -euo pipefail

BOOTFS=${1:-/run/media/denny/bootfs}
SSH_PUB=${2:-/home/denny/.ssh/id_ed25519.pub}
OUT_DIR=${3:-/tmp/galileo-rpi-cloudinit}

WPA="$BOOTFS/wpa_supplicant.conf"

if [[ ! -r "$WPA" ]]; then
  echo "Missing readable Wi-Fi config: $WPA" >&2
  exit 1
fi

if [[ ! -r "$SSH_PUB" ]]; then
  echo "Missing readable SSH public key: $SSH_PUB" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

ssid=$(awk -F= '/^[[:space:]]*ssid=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); gsub(/^"|"$/, "", $2); print $2; exit}' "$WPA")
psk=$(awk -F= '/^[[:space:]]*psk=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); gsub(/^"|"$/, "", $2); print $2; exit}' "$WPA")
country=$(awk -F= '/^[[:space:]]*country=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit}' "$WPA")
ssh_key=$(<"$SSH_PUB")

if [[ -z "$ssid" || -z "$psk" ]]; then
  echo "Could not extract SSID/PSK from $WPA" >&2
  exit 1
fi

if [[ -z "$country" ]]; then
  country=IT
fi

cat > "$OUT_DIR/user-data" <<EOF_USER
#cloud-config
hostname: galileo
manage_etc_hosts: true
ssh_pwauth: false
disable_root: true
users:
  - name: denny
    gecos: Galileo Operator
    groups: adm,audio,cdrom,dialout,gpio,i2c,input,netdev,plugdev,spi,sudo,users,video
    shell: /bin/bash
    lock_passwd: true
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - $ssh_key
timezone: Europe/Rome
package_update: false
runcmd:
  - [ systemctl, enable, ssh ]
  - [ systemctl, start, ssh ]
EOF_USER

cat > "$OUT_DIR/network-config" <<EOF_NET
version: 2
wifis:
  wlan0:
    optional: true
    dhcp4: true
    access-points:
      "$ssid":
        password: "$psk"
EOF_NET

cat > "$OUT_DIR/meta.txt" <<EOF_META
hostname=galileo
username=denny
ssid=$ssid
country=$country
ssh_key=$SSH_PUB
EOF_META

chmod 600 "$OUT_DIR/user-data" "$OUT_DIR/network-config" "$OUT_DIR/meta.txt"
echo "$OUT_DIR"
