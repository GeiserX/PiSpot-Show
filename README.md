<p align="center">
  <img src="docs/images/banner.svg" alt="PiSpot-Show Banner" width="900">
</p>

<p align="center">
  <strong>Turn any HDMI display into a self-service WiFi voucher kiosk using a Raspberry Pi.</strong>
</p>

<p align="center">
  <a href="https://github.com/GeiserX/PiSpot-Show/blob/main/LICENSE"><img src="https://img.shields.io/github/license/GeiserX/PiSpot-Show?color=43A047" alt="License: MIT"></a>
  <a href="https://www.raspberrypi.org/"><img src="https://img.shields.io/badge/platform-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white" alt="Platform: Raspberry Pi"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.x-3776AB?logo=python&logoColor=white" alt="Python 3"></a>
  <a href="https://www.ansible.com/"><img src="https://img.shields.io/badge/deploy-Ansible-EE0000?logo=ansible&logoColor=white" alt="Ansible"></a>
  <a href="https://github.com/PiSupply/PiJuice"><img src="https://img.shields.io/badge/power-PiJuice%20HAT-1B5E20" alt="PiJuice HAT"></a>
</p>

---

## Overview

PiSpot-Show is a headless Raspberry Pi appliance that drives an HDMI-connected TV or monitor to display WiFi voucher codes for hotel guests and public venues. Each hour it requests a fresh time-limited voucher from the [Spotipo](https://www.spotipo.com/) captive-portal API, pulls the current weather forecast, composites everything into a branded 1920x1080 image with [Pillow](https://python-pillow.org/), and pushes it to the framebuffer.

A [PiJuice HAT](https://github.com/PiSupply/PiJuice) provides battery-backed power management with scheduled wake/sleep, watchdog recovery, and graceful shutdown on low voltage -- making the device suitable for unattended 24/7 operation.

The project was originally developed and deployed in 2018 for the company GPConnect.

---

## Features

- **Automatic voucher rotation** -- generates a new Spotipo WiFi voucher every hour with configurable duration, speed limits, and device caps.
- **Live weather overlay** -- fetches temperature, conditions, and daily forecast from the Dark Sky API and renders weather icons on the display.
- **Full-HD output** -- produces a 1920x1080 branded image rendered with custom Raleway typography and composited logos.
- **Battery-backed power management** -- PiJuice HAT enables scheduled wake-up alarms, watchdog reboot, low-voltage shutdown, and wake-on-charge.
- **Systemd integration** -- runs as two systemd units: a boot splash screen and the main voucher service, both starting automatically.
- **Ansible deployment** -- single-playbook provisioning handles package installation, SSH key generation, service registration, timezone, GPU memory, and USB power-saving.
- **3D-printable enclosure** -- FreeCAD source files and ready-to-print STLs for a custom case with a button panel and lid.
- **Error resilience** -- on API failure, displays an error screen and retries after 60 seconds.

---

## Hardware Requirements

| Component | Purpose |
|---|---|
| Raspberry Pi 3 (or later) | Main compute board |
| PiJuice HAT | Battery UPS, RTC wake-up alarms, watchdog |
| HDMI display (TV or monitor) | Guest-facing voucher screen |
| MicroSD card (8 GB+) | Raspbian OS + application |
| Power supply (5 V / 2.5 A) | Board + HAT power |

---

## Software Requirements

- **Raspbian** (Stretch or later)
- **Python 3** with `pip3`
- **System packages** -- `fbi`, `git`, `imagemagick`, `pijuice-base`, `python3-smbus`
- **Python packages** -- `requests`, `Pillow`
- **Ansible** (on the deployment host)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/GeiserX/PiSpot-Show.git
cd PiSpot-Show
```

### 2. Configure API keys

Edit `main.py` and replace the placeholder values:

```python
Spotipo_Key = "TOKEN-SPOTIPO"      # Your Spotipo API token
Darksky_Key = "DARSKY-KEY"         # Your Dark Sky API key
```

Also update the Spotipo endpoint URL, SSID name, and weather coordinates to match your deployment:

```python
urlVoucher = 'https://wifi.YOUR-NET.us/s/1/api/voucher/create/'
ssid = "SSID-NAME"
urlWeather = 'https://api.darksky.net/forecast/.../<LAT>,<LON>?lang=fr&...'
```

### 3. Deploy with Ansible

From your deployment host (not the Pi), run the playbook against your target inventory:

```bash
ansible-playbook -i inventory deployment-files/main.yml
```

The playbook will:

1. Update and upgrade system packages.
2. Set the timezone and GPU memory allocation.
3. Install all runtime dependencies (`fbi`, `python3-pip`, `pijuice-base`, etc.).
4. Create a dedicated system user with scoped `sudoers` permissions.
5. Generate an ECDSA SSH key and register it for Git access.
6. Clone the application to `/opt/PiSpot_HDMI`.
7. Install and enable the `splashscreen` and `pispot_hdmi` systemd services.
8. Deploy the PiJuice configuration and WPA supplicant settings.

### 4. Configure PiJuice wake/sleep schedule

Use the PiJuice CLI to set the RTC wake-up alarm (e.g., 09:00 on weekdays), and add a cron entry for the shutdown script:

```bash
crontab -e
# Add: 0 17 * * * /usr/bin/python3 /opt/PiSpot_HDMI/piJuice_stop.py
```

This powers off the Pi at 17:00 daily; the PiJuice RTC alarm powers it back on at the configured time.

---

## Configuration

### Voucher parameters

Voucher settings are passed in the API request body inside `main.py`:

| Parameter | Default | Description |
|---|---|---|
| `duration_val` | `4` | Voucher validity period |
| `duration_type` | `2` | Duration unit (2 = hours) |
| `num_devices` | `10` | Max concurrent devices per voucher |
| `speed_dl` | `1024` | Download speed limit (Kbps) |
| `speed_ul` | `256` | Upload speed limit (Kbps) |
| `bytes_t` | `0` | Data cap (0 = unlimited) |

### PiJuice system events

The file `pijuice_config.JSON` defines hardware event handlers:

- **Low battery voltage** -- halt and power off.
- **Watchdog reset** -- automatic reboot.
- **Wake-on-charge** -- boot when battery reaches 20%.
- **Button power off / forced power off** -- graceful halt.

### Display refresh

The main loop sleeps for **1 hour** between voucher generations. On error, it retries after **60 seconds**.

---

## 3D-Printable Enclosure

The `Case/` directory contains a complete enclosure designed in FreeCAD:

| File | Description |
|---|---|
| `Caja.stl` | Main housing body |
| `Tapa.stl` | Top lid / cover |
| `Botonera.stl` | Button panel insert |
| `*.fcstd` | FreeCAD parametric source files |
| `*.gx` | Pre-sliced GCode files |

Print all three STL parts to assemble the full enclosure. The FreeCAD files are provided for customization.

---

## Architecture

```
                         +------------------+
                         |   HDMI Display   |
                         |   (1920x1080)    |
                         +--------+---------+
                                  |
                         +--------+---------+
                         |   Raspberry Pi   |
                         |   + PiJuice HAT  |
                         +--+-----+------+--+
                            |     |      |
                  +---------+  +--+--+  ++----------+
                  |            |     |  |            |
          +-------v---+ +-----v-+ +-v--v------+ +---v--------+
          | Spotipo   | | Dark  | | Pillow    | | fbi        |
          | WiFi API  | | Sky   | | (image    | | (framebuf  |
          | (voucher) | | (wx)  | |  render)  | |  display)  |
          +-----------+ +-------+ +-----------+ +------------+
```

1. **main.py** runs in an infinite loop as a systemd service.
2. Each cycle, it POSTs to the Spotipo API to create a time-limited voucher.
3. It GETs the current weather from Dark Sky.
4. Pillow composites the voucher code, SSID, weather data, date, and branding onto a 1920x1080 PNG.
5. `fbi` pushes the image directly to the Linux framebuffer (`/dev/fb0`), bypassing any desktop environment.
6. **piJuice_stop.py** is called via cron to trigger a timed shutdown; the PiJuice RTC alarm handles the next wake-up.

---

## Project Structure

```
PiSpot-Show/
  main.py                  # Main application loop
  piJuice_stop.py          # PiJuice scheduled shutdown script
  pijuice_config.JSON      # PiJuice HAT event configuration
  fonts/                   # Raleway typeface (Light + Black)
  images/                  # Background, logos, weather icons
  servicefiles/
    pispot_hdmi.service    # Main application systemd unit
    splashscreen.service   # Boot splash systemd unit
  deployment-files/
    main.yml               # Ansible deployment playbook
    wpa_supplicant.conf    # WiFi network configuration
    GitLabANDHostname.py   # SSH key upload and hostname setup
  Case/                    # 3D enclosure (FreeCAD + STL + GCode)
  docs/images/             # Documentation assets
  LICENSE                  # MIT License
```

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Maintainers

- [@GeiserX](https://github.com/GeiserX)

## Contributing

Contributions are welcome. [Open an issue](https://github.com/GeiserX/PiSpot-Show/issues/new) or submit a pull request.

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) Code of Conduct.
