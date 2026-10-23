#!/usr/bin/env bash
set -u

section() {
  printf '\n===== %s =====\n' "$1"
}

run() {
  printf '\n$ %s\n' "$*"
  "$@" 2>&1 || printf '[exit %s]\n' "$?"
}

section "System"
run hostname
run uname -a
run cat /etc/os-release
run uptime

section "Raspberry Identity"
run grep -E '^(Hardware|Revision|Model|Serial|processor|model name)' /proc/cpuinfo
if [ -r /sys/class/thermal/thermal_zone0/temp ]; then
  temp_milli=$(cat /sys/class/thermal/thermal_zone0/temp)
  printf 'temperature_c=%.3f\n' "$(awk "BEGIN { print $temp_milli / 1000 }")"
fi
if command -v vcgencmd >/dev/null 2>&1; then
  run vcgencmd get_throttled
fi

section "Memory And Disk"
run free -h
run df -h
run lsblk

section "Network"
run ip addr
run ip route
if command -v nmcli >/dev/null 2>&1; then
  run nmcli -t -f DEVICE,TYPE,STATE,CONNECTION dev
fi
if command -v iw >/dev/null 2>&1; then
  run iw dev wlan0 link
fi

section "Systemd"
run systemctl --failed --no-pager

section "Boot Config Audio Lines"
if [ -r /boot/firmware/config.txt ]; then
  run grep -nE '^(#)?dtparam=(audio|i2c_arm|i2s|spi)|^dtoverlay=|Galileo|wm8960|respeaker|seeed|keyestudio' /boot/firmware/config.txt
fi

section "ALSA Devices"
run aplay -l
run arecord -l
run aplay -L
run arecord -L

section "ALSA Cards"
if [ -r /proc/asound/cards ]; then
  run cat /proc/asound/cards
fi
run find /proc/asound -maxdepth 3 -type f -name info -print -exec cat '{}' ';'

section "WM8960 Mixer Summary"
if command -v amixer >/dev/null 2>&1; then
  run amixer -c 0 scontents
fi

section "Kernel Modules"
run sh -c "lsmod | grep -Ei 'wm8960|snd|i2c|i2s|spi|regmap|gpio' || true"

section "Device Nodes"
run sh -c "ls -l /dev/i2c* /dev/spidev* /dev/gpiochip* 2>/dev/null || true"

section "Relevant Kernel Log"
run sh -c "dmesg | grep -Ei 'wm8960|asoc|sound|snd|alsa|i2c|i2s|codec|respeaker|seeed|keyestudio|failed|error|undervoltage|voltage|thrott' | tail -240 || true"
