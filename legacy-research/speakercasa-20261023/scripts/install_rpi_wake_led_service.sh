#!/usr/bin/env bash
set -euo pipefail

SERVICE_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${SERVICE_DIR}/galileo-wake-led.service"

mkdir -p "${SERVICE_DIR}"

cat > "${SERVICE_FILE}" <<'EOF'
[Unit]
Description=Galileo continuous wake-word purple LED test
After=default.target

[Service]
Type=simple
WorkingDirectory=/home/denny/galileo
ExecStart=/home/denny/galileo/venv-oww-infer/bin/python /home/denny/galileo/bin/rpi_continuous_openwakeword_led.py /home/denny/galileo/models/openwakeword/galileo_v3.onnx --threshold 0.95
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable galileo-wake-led.service
systemctl --user restart galileo-wake-led.service

if command -v sudo >/dev/null 2>&1; then
  sudo loginctl enable-linger "${USER}"
fi

systemctl --user --no-pager status galileo-wake-led.service
