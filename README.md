# ISP Health Integration for Home Assistant

A comprehensive ISP health monitoring integration for Home Assistant that tracks network performance, connectivity, and reliability metrics.

## 🆓 **NO API KEYS REQUIRED**

This integration works **completely without any external API keys or paid services** for basic functionality. All core features use free services and system commands.

## Features

### Default Sensors (Always Active)
- **Public IP Information**: IP address, hostname, city, region, country, location coordinates, organization, postal code, timezone
- **DNS Configuration**: Current DNS servers and resolution status

### Optional Sensors (User Configurable)
- **Latency**: Ping times to various targets (Google, Cloudflare, ISP gateway)
- **Packet Loss**: Packet loss percentage over time
- **Jitter**: Network jitter measurement
- **Throughput**: Download/upload speed testing (min interval 1h, max 24h)
- **DNS Reliability**: DNS resolution success rate and response times
- **Route Stability**: Traceroute analysis for route changes

### IP Information Sources (All Free, No API Keys Required)
- **ip-api.com** (default) - 45 requests/minute free, no API key required
- **ipinfo.io** - 50,000 requests/month free, unlimited with token
- **ipgeolocation.io** - Premium service, API key required

## 🏠 Home Assistant Integration

### Installation

#### HACS (Recommended)
1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Open HACS in Home Assistant
3. Go to **Integrations** > **Custom repositories**
4. Click the three dots (⋮) in the top right
5. Add this repository URL: `https://github.com/dotelpenguin/ha-integration-isphealth`
6. Select **Integration** as the category
7. Click **Add**
8. Search for **ISP Health Monitor** and install it
9. Restart Home Assistant
10. Go to **Settings** > **Devices & Services** > **Add Integration** > Search for **ISP Health Monitor**

#### Manual Installation
1. Copy `custom_components/isp_health/` to your HA config directory
2. Restart Home Assistant
3. Add integration via **Settings** > **Devices & Services**

### Configuration
1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration** > **ISP Health Monitor**
3. Configure update interval and IP source
4. Select which sensors to enable
5. Complete setup

### Sensors Created
- `sensor.isp_health_ip_information` - Public IP details
- `sensor.isp_health_dns_configuration` - DNS server info
- `sensor.isp_health_network_latency` - Ping times
- `sensor.isp_health_packet_loss` - Packet loss %
- `sensor.isp_health_network_jitter` - Jitter measurement
- `sensor.isp_health_network_throughput` - Speed test results
- `sensor.isp_health_dns_reliability` - DNS success rate
- `sensor.isp_health_route_stability` - Route analysis

### Services
- `isp_health.test_isp_health` - Manual test trigger
- `isp_health.get_isp_report` - Get comprehensive report

## 🐍 Standalone Testing Framework

This project includes a standalone Python framework for testing and development without Home Assistant.

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   Edit `config.json` to enable/disable sensors and configure settings:
   ```json
   {
     "update_interval": 60,
     "ip_info_source": "ipinfo",
     "sensors": {
       "latency": {
         "enabled": true,
         "targets": ["8.8.8.8", "1.1.1.1"]
       },
       "throughput": {
         "enabled": false,
         "interval": 3600
       }
     }
   }
   ```

3. **Run Tests**
   ```bash
   # Basic functionality test
   python test_framework.py
   
   # Full sensor test with detailed output
   python test_framework.py --all
   
   # Single test run
   python standalone_test.py --single
   
   # Continuous monitoring for 5 minutes
   python standalone_test.py --continuous 5
   
   # Show summary of latest results
   python standalone_test.py --summary
   ```

### Configuration Options

#### Update Intervals
- **General**: 30 seconds to 10 minutes
- **Throughput**: 1 hour to 24 hours (due to bandwidth usage)

#### IP Information Sources
- **ip-api.com**: Free alternative, no API key needed
- **ipinfo.io**: High-quality data, token optional for higher limits
- **ipgeolocation.io**: Premium service, API key required

#### Sensor Configuration
Each sensor can be individually enabled/disabled and configured:

```json
{
  "sensors": {
    "latency": {
      "enabled": true,
      "targets": ["8.8.8.8", "1.1.1.1", "208.67.222.222"],
      "interval": 60
    },
    "packet_loss": {
      "enabled": true,
      "interval": 120
    },
    "jitter": {
      "enabled": true,
      "interval": 120
    },
    "throughput": {
      "enabled": false,
      "interval": 3600
    },
    "dns_reliability": {
      "enabled": true,
      "servers": ["8.8.8.8", "1.1.1.1"],
      "interval": 180
    },
    "route_stability": {
      "enabled": false,
      "targets": ["google.com", "cloudflare.com"],
      "interval": 1800
    }
  }
}
```

### API Keys and Tokens

For IP information sources that require authentication, add them to `config.json`:

```json
{
  "ip_info_config": {
    "ipinfo": {
      "token": "your_ipinfo_token_here"
    },
    "ipgeolocation": {
      "api_key": "your_api_key_here"
    }
  }
}
```

### Output Format

The framework outputs structured JSON data with the following format:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "sensors": {
    "ip_info": {
      "ip": "192.168.1.1",
      "city": "Example City",
      "country": "US",
      "source": "ipinfo.io"
    },
    "latency": {
      "average": 15.5,
      "minimum": 12.1,
      "maximum": 18.9,
      "status": "online"
    }
  }
}
```

## Development

### Project Structure
```
ha-integration-isphealth/
├── src/                           # Core framework code
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── ip_info.py                 # IP information providers
│   ├── sensors.py                 # Sensor implementations
│   └── isp_health.py              # Main monitor class
├── custom_components/             # Home Assistant integration
│   └── isp_health/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── const.py
│       ├── services.yaml
│       ├── strings.json
│       └── README.md
├── config.json                    # Configuration file
├── standalone_test.py             # Standalone testing script
├── test_framework.py              # Basic functionality tests
├── test_ha_structure.py           # HA integration structure test
├── requirements.txt               # Python dependencies
├── INSTALLATION.md                # Installation guide
└── README.md                     # This file
```

### Adding New Sensors

1. Create a new sensor class in `src/sensors.py` inheriting from `BaseSensor`
2. Implement the `get_data()` method
3. Add configuration options in `src/config.py`
4. Register the sensor in `src/isp_health.py`

### Adding New IP Sources

1. Create a new provider class in `src/ip_info.py` inheriting from `IPInfoProvider`
2. Implement `get_ip_info()` and `normalize_data()` methods
3. Add configuration options in `src/config.py`
4. Register the provider in `IPInfoManager`

## System Requirements

- Python 3.8+
- Internet connectivity
- `ping` command (for ICMP tests)
- `traceroute` command (for route analysis)
- `speedtest-cli` (for throughput testing)

## Troubleshooting

### Common Issues

1. **Permission denied for ping/traceroute**
   - On Linux: `sudo setcap cap_net_raw+ep /usr/bin/ping`
   - On macOS: May need to run with sudo

2. **DNS resolution failures**
   - Check your DNS configuration
   - Verify internet connectivity

3. **API rate limiting**
   - Add API keys/tokens to configuration
   - Consider using different IP information sources

4. **Throughput test failures**
   - Ensure `speedtest-cli` is installed
   - Check internet connection stability

### Logging

Enable debug logging by modifying the logging level in the test scripts:

```python
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Roadmap

- [x] **Home Assistant integration** - Complete custom component
- [x] **Standalone testing framework** - Full Python framework
- [x] **All core sensors** - IP info, DNS, latency, packet loss, jitter, throughput, DNS reliability, route stability
- [x] **No API keys required** - Works with free services
- [ ] **HACS publication** - Ready for HACS submission
- [ ] **Historical data storage** - SQLite database for trends
- [ ] **Alerting system** - Threshold-based notifications
- [ ] **Multiple ISP monitoring** - Track multiple connections
- [ ] **Custom target configuration** - User-defined test targets
- [ ] **Web UI** - Configuration interface
- [ ] **Mobile app** - Companion app
