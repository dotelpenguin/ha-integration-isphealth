# ISP Health Monitor - Installation Guide

## 🏠 Home Assistant Integration

### Prerequisites
- Home Assistant 2023.1.0 or later
- Internet connectivity
- System commands: `ping`, `traceroute` (Linux/macOS), `tracert` (Windows)

### Installation Methods

#### Method 1: HACS (Recommended)
1. **Install HACS** (if not already installed):
   - Go to [HACS GitHub](https://github.com/hacs/integration)
   - Follow the installation instructions

2. **Add Custom Repository**:
   - Open HACS in Home Assistant
   - Go to **Integrations**
   - Click the three dots menu (⋮)
   - Select **Custom repositories**
   - Add this repository URL: `https://github.com/dotelpenguin/ha-integration-isphealth`
   - Select **Integration** as category
   - Click **Add**

3. **Install Integration**:
   - Search for **ISP Health Monitor**
   - Click **Install**
   - Restart Home Assistant

#### Method 2: Manual Installation
1. **Download the Integration**:
   ```bash
   git clone https://github.com/dotelpenguin/ha-integration-isphealth.git
   ```

2. **Copy to Home Assistant**:
   ```bash
   # Copy the custom component
   cp -r ha-integration-isphealth/custom_components/isp_health /path/to/homeassistant/config/custom_components/
   ```

3. **Restart Home Assistant**

### Configuration

1. **Add Integration**:
   - Go to **Settings** > **Devices & Services**
   - Click **Add Integration**
   - Search for **ISP Health Monitor**
   - Click **Configure**

2. **Setup Wizard**:
   - **Step 1 - Basic Settings**:
     - Update Interval: 30-600 seconds (default: 60)
     - IP Information Source: Choose from free options
     - API Token: Optional (for higher rate limits)
   
   - **Step 2 - Select Sensors**:
     - Choose which sensors to enable
     - All sensors work without API keys

3. **Complete Setup**:
   - Review your configuration
   - Click **Submit**
   - The integration will start monitoring

### System Requirements

#### Linux
```bash
# Install required system packages
sudo apt update
sudo apt install traceroute

# Optional: Set ping capabilities (if needed)
sudo setcap cap_net_raw+ep /usr/bin/ping
```

#### macOS
```bash
# Install required system packages
brew install traceroute

# Note: May need to run with sudo for ping
```

#### Windows
- `tracert` command is built-in
- `ping` command is built-in
- No additional installation required

### Verification

After installation, verify the integration is working:

1. **Check Entities**:
   - Go to **Settings** > **Devices & Services**
   - Find **ISP Health Monitor**
   - Check that sensors are created and updating

2. **Test Sensors**:
   - Go to **Developer Tools** > **States**
   - Look for `sensor.isp_health_*` entities
   - Verify they have data and are updating

3. **Check Logs**:
   - Go to **Settings** > **System** > **Logs**
   - Look for any errors related to `isp_health`

### Troubleshooting

#### Common Issues

**1. Permission Denied for Ping**
```bash
# Linux
sudo setcap cap_net_raw+ep /usr/bin/ping

# Or run Home Assistant with appropriate permissions
```

**2. Traceroute Command Not Found**
```bash
# Linux
sudo apt install traceroute

# macOS
brew install traceroute
```

**3. Integration Not Appearing**
- Check that files are in correct location: `custom_components/isp_health/`
- Restart Home Assistant
- Check logs for errors

**4. Sensors Not Updating**
- Check internet connectivity
- Verify system commands work: `ping google.com`
- Check Home Assistant logs

**5. API Rate Limiting**
- Add API tokens to configuration
- Switch to different IP information source
- Increase update intervals

#### Debug Logging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.isp_health: debug
```

#### Manual Testing

Test the integration manually:

```bash
# Test ping
ping -c 4 google.com

# Test traceroute
traceroute google.com

# Test speedtest
speedtest-cli --simple
```

### Uninstallation

1. **Remove Integration**:
   - Go to **Settings** > **Devices & Services**
   - Find **ISP Health Monitor**
   - Click **Delete**

2. **Remove Files** (if manual installation):
   ```bash
   rm -rf /path/to/homeassistant/config/custom_components/isp_health
   ```

3. **Restart Home Assistant**

## 🐍 Standalone Python Usage

### Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/dotelpenguin/ha-integration-isphealth.git
   cd ha-integration-isphealth
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**:
   ```bash
   cp config.json.example config.json
   # Edit config.json with your preferences
   ```

4. **Run**:
   ```bash
   python3 standalone_test.py
   ```

### Configuration

Edit `config.json` to customize:

```json
{
  "update_interval": 60,
  "ip_info_source": "ipapi",
  "ip_info_config": {
    "ipinfo": {"token": ""},
    "ipapi": {"token": ""},
    "ipgeolocation": {"api_key": ""}
  },
  "sensors": {
    "ip_info": {"enabled": true, "interval": 60},
    "dns_config": {"enabled": true, "interval": 60},
    "latency": {"enabled": true, "interval": 60},
    "packet_loss": {"enabled": true, "interval": 120},
    "jitter": {"enabled": true, "interval": 120},
    "throughput": {"enabled": true, "interval": 3600},
    "dns_reliability": {"enabled": true, "interval": 180},
    "route_stability": {"enabled": true, "interval": 1800}
  }
}
```

## 🚀 Quick Start

### Home Assistant (Recommended)
1. Install via HACS or manually
2. Add integration through UI
3. Configure sensors
4. Start monitoring!

### Standalone Python
1. `git clone` the repository
2. `pip install -r requirements.txt`
3. `python3 standalone_test.py`
4. Monitor your ISP health!

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/dotelpenguin/ha-integration-isphealth/issues)
- **Home Assistant Community**: [Get help from the community](https://community.home-assistant.io/)
- **Documentation**: Check the README.md for detailed information

## 🆓 No API Keys Required

This integration works completely without external API keys or paid services. All core functionality uses free services and system commands.
