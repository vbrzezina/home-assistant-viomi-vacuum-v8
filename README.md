# Home Assistant support for Viomi Vacuum V8 (STYTJ02YM) / Xiaomi Mi Robot Vacuum-Mop P

Home Assistant custom integration for the **Viomi Vacuum V8 (STYTJ02YM)**, also sold as the **Xiaomi Mi Robot Vacuum-Mop P**.

Requires Home Assistant **2026.8.0 or newer**.

Tested with firmware **3.5.3_0017**.

> ⚠️ Other firmware versions and hardware variants may work, but are not currently verified.

This integration communicates with the vacuum locally over the network.

## Requirements

- Home Assistant **2026.8.0 or newer**
- Viomi Vacuum V8 (STYTJ02YM)
- Xiaomi Miio device token
- Firmware **3.5.3_0017** (tested)

## Installation

### HACS

1. Open **HACS → Integrations**.
2. Open the **⋮** menu and select **Custom repositories**.
3. Add:
   `https://github.com/vbrzezina/home-assistant-viomi-vacuum-v8`
4. Select **Integration** as the repository type and add it.
5. Install **Viomi Vacuum V8**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add Integration**.
8. Search for **Viomi Vacuum V8**.
9. Enter the vacuum's IP address and token.

No `configuration.yaml` entry is required.

## Getting your token

This integration requires the **32-character Xiaomi Miio device token**.

You can retrieve the token using [xiaomi-cloud-tokens-extractor](https://github.com/piotrmachowski/xiaomi-cloud-tokens-extractor) by [@piotrmachowski](https://github.com/PiotrMachowski).

You'll need the Xiaomi account credentials associated with the vacuum.

> 🔐 Treat the device token as a secret. Do not share it publicly or include it in screenshots, configuration files committed to Git, or issue reports.

## Supported entities

### Controls

- Vacuum
- Cleaning mode
- Water level
- Suction power

### Sensors

- Battery level
- Cleaning time
- Cleaned area
- Installed box
- Error code
- Firmware version
- Hardware version

### Binary sensors

- Charging status
- Working status
- Map availability
- New map status
- Mop installation status
- Remember-map status
- Repeat-cleaning status
- Problem status

## Notes

The integration supports multiple Viomi V8 vacuums in the same Home Assistant installation.

The vacuum, controls, sensors, and binary sensors are grouped under the same Home Assistant device.

Support for additional firmware versions, features, and hardware variants is not guaranteed.

## Credits

Original integration by [@tykarol](https://github.com/tykarol/home-assistant-viomi-vacuum-v8) and contributors.

Token extraction is provided by [xiaomi-cloud-tokens-extractor](https://github.com/piotrmachowski/xiaomi-cloud-tokens-extractor) by [@piotrmachowski](https://github.com/PiotrMachowski).
