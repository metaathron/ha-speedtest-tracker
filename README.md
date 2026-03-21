
# Speedtest Tracker – Home Assistant Integration

Custom integration for Home Assistant that connects to the Speedtest Tracker API and exposes speed test results, statistics, and controls as sensors, binary sensors, and a button.

## Source project
https://github.com/alexjustesen/speedtest-tracker  
https://docs.speedtest-tracker.dev

---

## Installation

### Installation via HACS

1. Add this repository as a custom repository to HACS:

[![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=metaathron&repository=ha-speedtest-tracker&category=Integration)

2. Use HACS to install the integration.  
3. Restart Home Assistant.  
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=speedtest_tracker)

---

### Manual Installation

1. Download the integration files from the GitHub repository.  
2. Place the integration folder in the `custom_components` directory of Home Assistant.  
3. Restart Home Assistant.  
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=speedtest_tracker)

---

## Setup

1. Go to Settings → Devices & Services  
2. Click "Add Integration"  
3. Select **Speedtest Tracker**  
4. Enter:
   - Base URL (e.g. `https://your-instance`)
   - Bearer Token
   - Scan interval
   - Timeout
   - SSL verification (optional)

---

## Features

- Latest speed test monitoring (download, upload, ping)
- Detailed latency and jitter metrics
- Packet loss tracking
- Server information (name, location, country, ISP)
- Historical statistics (avg/min/max)
- Manual test execution (button)
- Smart polling with retry logic
- Webhook support for instant updates
- Separation of current test and statistics into two devices

---

## Sensors

### Current / Last Test

- Download speed [Mbps]
- Upload speed [Mbps]
- Ping [ms]
- Packet loss [%]
- Ping jitter [ms]
- Download jitter [ms]
- Upload jitter [ms]
- Download latency (low / IQM / high) [ms]
- Upload latency (low / IQM / high) [ms]
- Download elapsed [ms]
- Upload elapsed [ms]
- Status (string)
- Last test time (as local time)
- Result URL
- Server (with attributes)

### Statistics

- Ping avg / min / max [ms]
- Download avg / min / max [Mbps]
- Upload avg / min / max [Mbps]
- Total results

---

## Binary Sensors

- Healthy
- Scheduled

---

## Button

- Run speed test

---

## Polling & Webhook Behavior

Integration combines polling and webhook updates:

### Polling
- Runs at configured scan interval  
- If test status is `running`:
  - values are **not overwritten**
  - retry is scheduled after **10 seconds**
  - retries continue until test completes  

### Manual test (button)
- After triggering a test:
  - refresh is scheduled after **10 seconds**
  - if still running → retry continues  

### Webhook
- When webhook is triggered:
  - integration performs immediate refresh  
- If webhook is missed (e.g. HA offline):
  - next polling cycle updates data  

This ensures:
- no data loss  
- no “N/A” states during running test  
- near real-time updates  

---

## Webhook Setup

After adding the integration:

1. Open the **Speedtest Tracker integration** in Home Assistant  
2. Find the **status sensor**
3. In attributes, locate:
   - `webhook_id`
   - `webhook_url`

Webhook endpoint format:
```
/api/webhook/<webhook_id>
```

Full example:
```
https://homeassistant.local:8123/api/webhook/xxxxxxxxxxxxxxxx
```

Configure your Speedtest Tracker (or external automation) to call this URL when a test finishes.

---

## Notes

- `updated_at` is treated as local server time and aligned with Home Assistant timezone  
- During running tests, last valid values are preserved  
- Statistics are separated into a dedicated device for clarity  

---

## Support

If you find this integration useful, you can support the development:

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/metaathron)

---

## License

This project is free to use, modify, and distribute.

Author: metaathron  
Please retain attribution and link to the original repository:  
https://github.com/metaathron/ha-speedtest-tracker
