# Galileo Voice Satellite - Phase 0 USB Discovery

Date: 2026-10-01

## USB CONNECTION STATUS

PC OS:
- EndeavourOS, `ID_LIKE=arch`
- Kernel: `Linux pc-denny 6.18.46-1-lts x86_64`

USB connection detected:
- No Raspberry Pi USB gadget, serial, or USB network device detected.
- USB tree shows only existing/non-Raspberry devices:
  - `04f3:0c82` ELAN `ELAN:ARM-M4`, vendor-specific, 12 Mbps
  - `30c9:00d3` Luxvisions Innotech Limited `HP FHD Camera`
  - `8087:0033` Intel Corp. `AX211 Bluetooth`
  - Linux USB root hubs

USB device:
- No USB device identifiable as Raspberry Pi Zero 2 W.
- The visible vendor-specific USB device is `ELAN:ARM-M4`, not Raspberry Pi.

VID/PID:
- Raspberry: not detected.
- Non-Raspberry observed: `04f3:0c82` ELAN `ELAN:ARM-M4`.

USB serial:
- No `/dev/ttyUSB*`
- No `/dev/ttyACM*`
- No `/dev/serial/`

USB network interface:
- No USB Ethernet/RNDIS/CDC interface detected.
- Network interfaces observed:
  - `lo`
  - `enp3s0` PCI Ethernet, down/no carrier
  - `wlan0` Wi-Fi, up, `<pc-lan-ip>/24`
  - `docker0`, down
- `enp3s0` sysfs device path is PCI: `/sys/devices/pci0000:00/0000:00:1c.4/0000:03:00.0`
- `wlan0` sysfs device path is PCI/internal: `/sys/devices/pci0000:00/0000:00:14.3`

Possible power-only connection:
- Yes. Based on current PC-side evidence, the cable may be providing only power to the Raspberry, or it may be connected to the Raspberry's power-only port.
- This does not imply the Raspberry is faulty.

Raspberry boot evidence:
- None verified from the PC.
- Power alone is not boot evidence.
- No USB enumeration, no serial, no USB network, no mDNS SSH service, and no `raspberrypi.local` resolution were observed.

Wi-Fi/LAN presence:
- PC is on Wi-Fi network `<lan-subnet>/24` via gateway `<gateway-ip>`.
- Neighbor table only showed the gateway: `<gateway-ip>`.
- No Raspberry candidate was visible in the neighbor table.
- mDNS `_ssh._tcp` query returned no services.

Hostname:
- `raspberrypi` not resolved.
- `raspberrypi.local` not resolved.

IP:
- No Raspberry IP identified.

SSH:
- No SSH target identified.
- No login attempts were made.

microSD/OS status:
- Unknown. The PC-side checks cannot confirm whether the microSD has a bootable OS.

Conclusion:
- The PC currently does not see the Raspberry Pi Zero 2 W as a USB data device.
- There is no evidence yet that the Raspberry has completed boot.
- The most likely immediate explanation is a power-only USB connection or a Raspberry OS not configured to expose USB gadget/serial/network.
- The next manual step should verify the physical USB port/cable before changing software.

## Retry 2026-10-01T14:47:43+02:00

The discovery was repeated after the user requested `riprova`.

Result:
- USB device list is unchanged.
- No Raspberry Pi USB VID/PID detected.
- No `/dev/ttyUSB*`, `/dev/ttyACM*`, or `/dev/serial/` detected.
- Network interfaces are unchanged: `lo`, `enp3s0`, `wlan0`, `docker0`.
- No USB Ethernet/RNDIS/CDC interface detected.
- Neighbor table still only shows the gateway `<gateway-ip>`.
- mDNS `_ssh._tcp` query returned no services.

Updated conclusion:
- The PC still does not see the Raspberry as a USB data device.
- Current evidence still points to a power-only connection, wrong USB port for data, or a Raspberry OS that is not exposing USB gadget/serial/network.

## Retry 2026-10-01T14:51:38+02:00

The user reported no visible change after the manual USB-port attempt.

Result:
- USB device list is still unchanged.
- No Raspberry Pi USB VID/PID detected.
- No `/dev/ttyUSB*`, `/dev/ttyACM*`, or `/dev/serial/` detected.
- No USB Ethernet/RNDIS/CDC interface detected.
- `ip addr` still shows only `lo`, `enp3s0`, `wlan0`, and `docker0`.
- `ip neigh` still shows only the gateway `<gateway-ip>`.

Updated conclusion:
- The PC still has no evidence of a USB data connection to the Raspberry.
- The next most useful manual discriminator is whether the Raspberry shows power/activity LEDs when connected.

## Manual Observation 2026-10-01T14:52:11+02:00

User observation:
- Raspberry board LED: green fixed.

Interpretation:
- The board appears to receive power.
- A fixed green LED alone is not enough evidence that Raspberry Pi OS has booted.
- Combined with no USB enumeration, no serial, no USB network, no mDNS, and no LAN neighbor entry, the next suspect is boot media/OS state or a non-data USB setup.

## microSD Reflash 2026-10-01T16:02:54+02:00

microSD identification:
- Device: `/dev/sda`
- Size: 7.4 GiB
- Transport: USB
- Model: `STORAGE DEVICE`
- Internal PC disk was separately identified as `/dev/nvme0n1` and was not touched.

Source image:
- `/home/denny/Scaricati/2025-05-13-raspios-bookworm-arm64-lite.img.xz`
- Image integrity check: `xz -t` passed.
- Clean write with `rpi-imager --cli` completed and verified successfully.

Final customization:
- A final `rpi-imager --cli --disable-verify --first-run-script` pass completed successfully.
- `rpi-imager` reported:
  - `Customising OS...`
  - `Verifying OS customisation...`
  - `Write successful.`

Configured first boot behavior:
- Hostname: `galileo`
- User: `denny`
- Password login: disabled/locked
- SSH: enabled, key-only, using local public key `/home/denny/.ssh/id_ed25519.pub`
- Wi-Fi: configured from the previously present Raspberry boot configuration
- Country/timezone/keymap: `IT`, `Europe/Rome`, `it`

Security cleanup:
- Temporary files in `/tmp` containing Wi-Fi data were removed.

Final device handling:
- `/dev/sda` was safely powered off with `udisksctl power-off`.

## First Boot Success 2026-10-01

After reinserting the reflashed microSD into the Raspberry:
- User observed green LED blinking.
- The Raspberry appeared on mDNS as `galileo.local`.
- IPv4 address: `<raspberry-ip>`
- MAC address: `<raspberry-mac>`
- SSH succeeded with key authentication as user `denny`.

Conclusion:
- The Raspberry Pi Zero 2 W boots successfully from the reflashed microSD.
- Wi-Fi configuration works.
- SSH key access works.
- USB gadget mode is not required for the current project path.

## Commands/Evidence Collected

- `uname -a`
- `/etc/os-release`
- `lsusb`
- `lsusb -t`
- `/sys/bus/usb/devices/3-4/*` for the only vendor-specific USB device
- `/dev/ttyUSB*`, `/dev/ttyACM*`, `/dev/serial/`
- `ip addr`
- `ip route`
- `ip neigh`
- `avahi-browse -rt _ssh._tcp`
- `getent hosts raspberrypi`
- `getent hosts raspberrypi.local`
- `journalctl --dmesg` USB-related grep

Some commands required execution outside the sandbox because the sandbox blocked netlink/libusb/system bus access.
