# ISP Health Monitor v2.0.0-beta.1

## 🎯 **Simplified ISP Health Monitoring**

A clean, simple ISP health monitoring integration for Home Assistant that focuses on the essentials.

## ✨ **What's New in v2.0.0-beta.1**

### **🎨 Simplified Design**
- **Single-step configuration** - No more overwhelming multi-step setup
- **Essential sensors only** - Focus on what matters most
- **Fixed intervals** - No complex timing configuration
- **Clean UI** - Simple, intuitive interface

### **📊 Core Features**
- **Public IP Information** - Your IP address, location, and ISP
- **DNS Configuration** - Current DNS servers and status
- **Network Latency** - Ping times to reliable servers
- **Speed Testing** - Optional internet speed tests

### **⚙️ Simple Configuration**
Just 5 options to configure:
1. **Update Interval** - How often to check (30-300 seconds)
2. **IP Information Provider** - Choose from free services
3. **API Token** - Optional for higher rate limits
4. **Enable Latency Monitoring** - Track ping times
5. **Enable Speed Testing** - Optional bandwidth testing

## 🚀 **Installation**

### **HACS (Recommended)**
1. Open HACS in Home Assistant
2. Go to **Integrations** > **Custom repositories**
3. Add: `https://github.com/dotelpenguin/ha-integration-isphealth`
4. Search for **ISP Health Monitor** and install
5. Restart Home Assistant
6. Add integration via **Settings** > **Devices & Services**

### **Manual Installation**
1. Download the latest release
2. Extract to `custom_components/isp_health/`
3. Restart Home Assistant
4. Add integration via UI

## 📱 **Configuration**

### **Initial Setup**
1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **ISP Health Monitor**
4. Configure the 5 simple options
5. Complete setup

### **Configuration Options**
- **Update Interval**: 30-300 seconds (default: 60)
- **IP Information Provider**: ip-api.com (free) or ipinfo.io (free with token)
- **API Token**: Optional for higher rate limits
- **Enable Latency Monitoring**: Track ping times (default: enabled)
- **Enable Speed Testing**: Optional bandwidth testing (default: disabled)

## 📊 **Sensors Created**

### **Always Enabled**
- `sensor.isp_health_public_wan_ip` - Your public IP address
- `sensor.isp_health_wan_dns_server` - Current DNS servers

### **Optional**
- `sensor.isp_health_wan_latency` - Network latency (ping times)
- `sensor.isp_health_network_throughput` - Internet speed test results

## 🎯 **Why v2.0.0-beta.1?**

### **Problems with v1.x**
- Too many configuration options
- Complex multi-step setup
- Overwhelming for new users
- Advanced features that most users don't need

### **Solutions in v2.0.0-beta.1**
- **Simplicity first** - Only essential options
- **Single-step setup** - Quick and easy
- **Sensible defaults** - Works out of the box
- **Clear purpose** - Focus on core functionality

## 🔮 **Future Plans**

### **v2.1.0** (Planned)
- Add packet loss monitoring
- Add DNS reliability testing
- Add basic alerting

### **v2.2.0** (Planned)
- Add historical data storage
- Add network quality scoring
- Add more IP information providers

### **v3.0.0** (Future)
- Advanced features for power users
- Custom target configuration
- Multiple ISP monitoring

## 🆓 **No API Keys Required**

All core features work without any external API keys or paid services. Optional API tokens only provide higher rate limits.

## 📋 **System Requirements**

- Home Assistant 2023.1.0 or later
- Internet connectivity
- `ping` command (for latency testing)
- `speedtest-cli` (for speed testing, optional)

## 🐛 **Beta Testing**

This is a beta release focused on simplicity and user experience. Please report any issues or suggestions.

## 📄 **License**

MIT License - see LICENSE file for details.

---

**v2.0.0-beta.1** - *Simple ISP health monitoring that just works*
