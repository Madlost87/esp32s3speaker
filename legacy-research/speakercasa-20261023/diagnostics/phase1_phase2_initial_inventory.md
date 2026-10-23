# Galileo Voice Satellite - Phase 1/2 Initial Inventory

Date: 2026-10-01

## Discovery Result

Raspberry reachable:
- Hostname: `galileo`
- mDNS hostname: `galileo.local`
- IPv4: `<raspberry-ip>`
- MAC: `<raspberry-mac>`
- SSH: reachable with key authentication as user `denny`
- Password login: not used

## Raspberry Identity

- Model: `Raspberry Pi Zero 2 W Rev 1.0`
- CPU architecture: `aarch64`
- Kernel: `Linux galileo 6.12.25+rpt-rpi-v8`
- OS: Debian GNU/Linux 12 bookworm
- RAM: 416 MiB total, 284 MiB available at inspection
- Swap: 511 MiB
- microSD:
  - `/dev/mmcblk0`, 7.4 GiB
  - `/dev/mmcblk0p1`, 512 MiB, `/boot/firmware`
  - `/dev/mmcblk0p2`, 6.9 GiB, `/`
- Root filesystem usage: 2.1 GiB used, 4.4 GiB available
- Temperature: 42.932 C
- Throttling/undervoltage: `throttled=0x0`
- Failed systemd units: none

## Network

- Interface: `wlan0`
- IPv4: `<raspberry-ip>/24`
- Default gateway: `<gateway-ip>`
- NetworkManager connection: `preconfigured`
- PC discovered the Raspberry through mDNS `_workstation._tcp`.

## USB / Local Connection

- Raspberry was not exposed as USB serial, USB Ethernet, RNDIS, CDC, or gadget device to the PC.
- Current working access path is Wi-Fi + SSH.
- This is acceptable for the Galileo project; USB gadget mode is not needed right now.

## GPIO / Buses

Observed on Raspberry:
- GPIO devices:
  - `/dev/gpiochip0`
  - `/dev/gpiochip4`
- I2C device nodes: none visible
- SPI device nodes: none visible

Kernel modules:
- `i2c_bcm2835` loaded
- ALSA/sound modules loaded for HDMI/Broadcom audio only

Boot config relevant lines:
- `dtparam=audio=on`
- `#dtparam=i2c_arm=on`
- `#dtparam=i2s=on`
- `#dtparam=spi=on`
- `dtoverlay=vc4-kms-v3d`

## Audio / ReSpeaker Status

ALSA playback devices:
- `card 0: vc4hdmi [vc4-hdmi]`

ALSA capture devices:
- none

`/proc/asound`:
- only `card0` / `vc4hdmi`

ReSpeaker / codec evidence:
- No `wm8960`, `ac108`, `seeed`, `respeaker`, or Keyestudio-specific audio driver active in `dmesg`.
- No HAT/device-tree node automatically detected for the ReSpeaker.
- Available overlay includes `wm8960-soundcard.dtbo`.

Initial conclusion:
- The Raspberry is healthy and reachable.
- The KEYESTUDIO ReSpeaker 2-Mic Pi HAT is not currently configured as an ALSA audio capture/playback device.
- The likely next minimal software step is to enable the required hardware buses and the matching sound-card overlay, most likely:
  - `dtparam=i2c_arm=on`
  - `dtparam=i2s=on`
  - `dtoverlay=wm8960-soundcard`
- This should be done as a controlled config change with a backup of `/boot/firmware/config.txt`, followed by reboot and repeat ALSA/I2C diagnostics.

No permanent audio calibration, recording, playback, or driver installation has been performed yet.

## WM8960 Enablement 2026-10-01T16:12:57+02:00

Config change performed:
- Backup created on Raspberry: `/boot/firmware/config.txt.galileo-pre-wm8960-20261001-160941.bak`
- Updated `/boot/firmware/config.txt`:
  - `dtparam=i2c_arm=on`
  - `dtparam=i2s=on`
  - `#dtparam=spi=on` remains disabled
  - `dtoverlay=wm8960-soundcard`
- Raspberry rebooted successfully.

Post-reboot ALSA result:
- Playback:
  - `card 0: wm8960soundcard [wm8960-soundcard]`
  - `card 1: vc4hdmi [vc4-hdmi]`
- Capture:
  - `card 0: wm8960soundcard [wm8960-soundcard]`
- Default ALSA device is now `wm8960soundcard`.

Kernel/module evidence:
- `snd_soc_wm8960` loaded
- `snd_soc_bcm2835_i2s` loaded
- `snd_soc_simple_card` loaded
- `wm8960 1-001a` appears in `dmesg`

Format probe:
- Device: `hw:0,0`
- Supported formats: `S16_LE`, `S24_LE`, `S32_LE`
- Supported channels: `2`
- Supported sample rate range: `8000..48000`
- Project target format `S16_LE`, 16 kHz, stereo is supported.

First microphone recording:
- Path on Raspberry: `/home/denny/galileo/recordings/mic_test.wav`
- Duration: 10.0 seconds
- Format: WAV, 16 kHz, 16-bit, stereo
- Size: 640044 bytes
- ALSA errors/xruns: none reported
- Stats path on Raspberry: `/home/denny/galileo/diagnostics/mic_test_stats.json`

Channel statistics:
- Channel 0:
  - RMS: `15.85`
  - RMS dBFS: `-66.31`
  - Peak: `303`
  - Peak dBFS: `-40.68`
  - DC offset: `0.0079%` full scale
  - Clipped samples: `0`
- Channel 1:
  - RMS: `13.08`
  - RMS dBFS: `-67.98`
  - Peak: `249`
  - Peak dBFS: `-42.39`
  - DC offset: `0.0067%` full scale
  - Clipped samples: `0`

Interpretation:
- ReSpeaker/WM8960 audio is now recognized by ALSA.
- Both capture channels are present.
- No clipping or xruns were observed.
- Recorded level is low, likely due to quiet room and/or conservative default capture gain; no permanent gain calibration has been applied yet.
