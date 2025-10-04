# ISP Health Monitor for Home Assistant

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
- **ip-api.com** (default) - 1,000 requests/month free, no API key required
- **ipinfo.io** - 50,000 requests/month free, no API key required
- **ipapi.co** - 1,000 requests/month free, no API key required
- **ipapi.com** - 1,000 requests/month free, no API key required
- **ipgeolocation.io** - Optional premium service (requires API key)

## Installation

### HACS (Recommended)
1. Open HACS
2. Go to Integrations
3. Click the three dots menu
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as category
7. Click "Add"
8. Search for "ISP Health Monitor" and install

### Manual Installation
1. Download the latest release
2. Extract the `isp_health` folder
3. Copy it to `custom_components/` in your Home Assistant config directory
4. Restart Home Assistant
5. Add the integration via the UI

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **ISP Health Monitor**
4. Follow the setup wizard:
   - Configure update interval (30-600 seconds)
   - Select IP information source
   - Optionally add API token for higher rate limits
   - Choose which sensors to enable

## Sensors

The integration creates the following sensors:

### IP Information Sensor
- **State**: Current public IP address
- **Attributes**: Hostname, city, region, country, coordinates, organization, timezone, source

### DNS Configuration Sensor  
- **State**: Primary DNS server
- **Attributes**: Secondary DNS, all DNS servers, resolution test results

### Network Latency Sensor
- **State**: Average latency in milliseconds
- **Attributes**: Minimum, maximum, individual target results

### Packet Loss Sensor
- **State**: Average packet loss percentage
- **Attributes**: Minimum, maximum, individual target results

### Network Jitter Sensor
- **State**: Average jitter in milliseconds
- **Attributes**: Minimum, maximum, individual target results

### Network Throughput Sensor
- **State**: Download speed in Mbps
- **Attributes**: Upload speed, server info, test type

### DNS Reliability Sensor
- **State**: Overall success rate percentage
- **Attributes**: Average response time, individual server results

### Route Stability Sensor
- **State**: Overall stability score (0-1)
- **Attributes**: Route changes, hop count, detailed hop analysis

## Services

### `isp_health.test_isp_health`
Manually trigger an ISP health test.

**Service Data:**
- `sensor_type` (optional): Type of sensor to test, or "all" for all sensors

**Example:**
```yaml
service: isp_health.test_isp_health
data:
  sensor_type: latency
```

### `isp_health.get_isp_report`
Get a comprehensive ISP health report.

**Example:**
```yaml
service: isp_health.get_isp_report
```

## Automation Examples

### Alert on High Latency
```yaml
automation:
  - alias: "High Latency Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.isp_health_network_latency
      above: 100
    action:
      service: notify.persistent_notification
      data:
        message: "High network latency detected: {{ states('sensor.isp_health_network_latency') }}ms"
```

### Alert on Packet Loss
```yaml
automation:
  - alias: "Packet Loss Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.isp_health_packet_loss
      above: 5
    action:
      service: notify.persistent_notification
      data:
        message: "Packet loss detected: {{ states('sensor.isp_health_packet_loss') }}%"
```

### Alert on Slow Internet
```yaml
automation:
  - alias: "Slow Internet Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.isp_health_network_throughput
      below: 50
    action:
      service: notify.persistent_notification
      data:
        message: "Slow internet detected: {{ states('sensor.isp_health_network_throughput') }}Mbps"
```

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

### Logs

Enable debug logging by adding to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.isp_health: debug
```

## System Requirements

- Home Assistant 2023.1.0 or later
- Python 3.8+
- Internet connectivity
- `ping` command (for ICMP tests)
- `traceroute` command (for route analysis)
- `speedtest-cli` (for throughput testing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

- [GitHub Issues](https://github.com/dotelpenguin/ha-integration-isphealth/issues)
- [Home Assistant Community](https://community.home-assistant.io/)
