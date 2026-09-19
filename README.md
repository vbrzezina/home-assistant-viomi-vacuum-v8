# Home Assistant support for Viomi Vacuum V8 (STYTJ02YM) / Xiaomi Mi Robot Vacuum-Mop P

Home Assistant custom integration for the **Viomi Vacuum V8 (STYTJ02YM)**, also sold as the **Xiaomi Mi Robot Vacuum-Mop P**.

Tested with firmware **3.5.3_0017**. Requires Home Assistant **2026.8.0** or newer

⚠️ This integration is currently in beta. Other firmware versions and hardware variants may work, but are not currently verified.

_Original code by [@tykarol](https://github.com/tykarol/home-assistant-viomi-vacuum-v8) and other contributors._

## Requirements

- Home Assistant **2026.8.0 or newer**
- Viomi Vacuum V8 (STYTJ02YM)
- Firmware **3.5.3_0017** (tested)

## Installation

### HACS

1. Open **HACS → Integrations**.
2. Add this repository in custom repositories
3. Install the integration.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add Integration**.
6. Search for **Viomi Vacuum V8**.
7. Enter the vacuum's IP address and token.

## Getting your token

This integration requires the 32-character Xiaomi Miio device token.
You can retrieve it using [xiaomi-cloud-tokens-extractor](https://github.com/piotrmachowski/xiaomi-cloud-tokens-extractor) by @piotrmachowski.
You'll need the Xiaomi account credentials associated with the vacuum.

## Supported entities

The integration currently provides:

- Vacuum
- Battery level
- Cleaning time
- Cleaned area
- Suction power
- Water level
- Cleaning mode
- Installed box type
- Error code
- Firmware version
- Hardware version
- Charging status
- Working status
- Map availability
- New map status
- Mop installation status
- Remember-map status
- Repeat-cleaning status
- Problem status

## Notes

This integration communicates with the vacuum locally over the network.

Support for additional firmware versions, features, and hardware variants is not guaranteed.

## Credits

Original integration by [@tykarol](https://github.com/tykarol/home-assistant-viomi-vacuum-v8) and other contributors.
