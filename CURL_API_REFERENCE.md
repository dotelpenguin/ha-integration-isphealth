# 🔍 Curl Commands for IP Information APIs

## 🚀 Quick Test Script
```bash
./curl_api_test.sh
```

## 📊 Individual API Tests

### **🌐 ip-api.com (Free)**
```bash
# Basic request (no API key needed)
curl -s 'http://ip-api.com/json'

# With optional token for higher rate limits
curl -s 'http://ip-api.com/json?token=YOUR_TOKEN'

# Pretty formatted with jq (if installed)
curl -s 'http://ip-api.com/json' | jq '.'

# Show only hostname field
curl -s 'http://ip-api.com/json' | jq '.reverse'
```

### **🔍 ipinfo.io (Free)**
```bash
# Basic request (no API key needed)
curl -s 'https://ipinfo.io/json'

# With optional token for higher rate limits
curl -s 'https://ipinfo.io/json?token=YOUR_TOKEN'

# Pretty formatted with jq (if installed)
curl -s 'https://ipinfo.io/json' | jq '.'

# Show only hostname field
curl -s 'https://ipinfo.io/json' | jq '.hostname'
```

### **💎 ipgeolocation.io (Premium)**
```bash
# Requires API key
curl -s 'https://api.ipgeolocation.io/ipgeo?apiKey=YOUR_API_KEY'

# Pretty formatted with jq (if installed)
curl -s 'https://api.ipgeolocation.io/ipgeo?apiKey=YOUR_API_KEY' | jq '.'

# Show only hostname field
curl -s 'https://api.ipgeolocation.io/ipgeo?apiKey=YOUR_API_KEY' | jq '.hostname'
```

## 🎯 Key Fields to Check

### **Hostname Analysis**
```bash
# Check hostname from ipinfo.io (most likely to have hostname)
curl -s 'https://ipinfo.io/json' | jq '.hostname'

# Check hostname from ip-api.com (may be null)
curl -s 'http://ip-api.com/json' | jq '.reverse'

# Check hostname from ipgeolocation.io (if you have API key)
curl -s 'https://api.ipgeolocation.io/ipgeo?apiKey=YOUR_API_KEY' | jq '.hostname'
```

### **Complete Field Comparison**
```bash
# Compare all fields from ipinfo.io
curl -s 'https://ipinfo.io/json' | jq '{
  ip: .ip,
  hostname: .hostname,
  city: .city,
  region: .region,
  country: .country,
  org: .org,
  postal: .postal,
  timezone: .timezone
}'
```

## 📊 Expected Results

### **ipinfo.io (Most Reliable for Hostname)**
```json
{
  "ip": "71.10.63.200",
  "hostname": "syn-071-010-063-200.res.spectrum.com",
  "city": "Whitmore Lake",
  "region": "Michigan",
  "country": "US",
  "org": "AS20115 Charter Communications LLC",
  "postal": "48189",
  "timezone": "America/Detroit"
}
```

### **ip-api.com (May Show Null Hostname)**
```json
{
  "query": "71.10.63.200",
  "reverse": null,
  "city": "Brighton",
  "regionName": "Michigan",
  "country": "United States",
  "isp": "Charter Communications",
  "zip": "48116",
  "timezone": "America/Detroit"
}
```

## 🔧 Troubleshooting

### **Install jq for Pretty Formatting**
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# CentOS/RHEL
sudo yum install jq
```

### **Test Network Connectivity**
```bash
# Test if APIs are reachable
curl -I 'http://ip-api.com/json'
curl -I 'https://ipinfo.io/json'
curl -I 'https://api.ipgeolocation.io/ipgeo'
```

### **Check Response Headers**
```bash
# See response headers and status
curl -I 'https://ipinfo.io/json'
curl -I 'http://ip-api.com/json'
```

## 🎯 Debugging Hostname Issues

### **1. Test APIs Directly**
```bash
# Run the test script
./curl_api_test.sh
```

### **2. Compare with Home Assistant**
- **API returns**: `"hostname": "syn-071-010-063-200.res.spectrum.com"`
- **HA shows**: `hostname: null`
- **Conclusion**: Issue in integration pipeline

### **3. Check Specific Fields**
```bash
# Focus on hostname field
echo "ipinfo.io hostname:"
curl -s 'https://ipinfo.io/json' | jq -r '.hostname'

echo "ip-api.com hostname:"
curl -s 'http://ip-api.com/json' | jq -r '.reverse'
```

## 📊 Rate Limits

### **ip-api.com**
- **Free**: 45 requests/minute
- **With token**: 1000 requests/minute

### **ipinfo.io**
- **Free**: 50,000 requests/month
- **With token**: Higher limits

### **ipgeolocation.io**
- **Paid service**: Depends on plan

## 🎯 Quick Commands

### **One-liner Tests**
```bash
# Test all free APIs
echo "ipinfo.io:" && curl -s 'https://ipinfo.io/json' | jq '.hostname'
echo "ip-api.com:" && curl -s 'http://ip-api.com/json' | jq '.reverse'
```

### **Save Results to File**
```bash
# Save all responses to files
curl -s 'https://ipinfo.io/json' > ipinfo_response.json
curl -s 'http://ip-api.com/json' > ipapi_response.json
```

## 🔍 Advanced Testing

### **Test with Different User Agents**
```bash
curl -s -H "User-Agent: Mozilla/5.0" 'https://ipinfo.io/json'
curl -s -H "User-Agent: HomeAssistant" 'https://ipinfo.io/json'
```

### **Test with Timeouts**
```bash
curl -s --max-time 10 'https://ipinfo.io/json'
curl -s --max-time 10 'http://ip-api.com/json'
```

### **Verbose Output**
```bash
curl -v 'https://ipinfo.io/json'
curl -v 'http://ip-api.com/json'
```

## 🎯 Expected Hostname Patterns

### **Common ISP Hostname Formats**
- **Charter/Spectrum**: `syn-xxx-xxx-xxx-xxx.res.spectrum.com`
- **Comcast**: `c-xxx-xxx-xxx-xxx.hsd1.ca.comcast.net`
- **Verizon**: `xxx-xxx-xxx-xxx.dhcp.verizon.net`
- **AT&T**: `xxx-xxx-xxx-xxx.dhcp.att.net`

### **What to Look For**
- **String value**: `"hostname": "syn-071-010-063-200.res.spectrum.com"`
- **Not null**: `"hostname": null` (indicates no reverse DNS)
- **Not empty**: `"hostname": ""` (indicates empty response)

## 🎯 Summary

Use these curl commands to:
1. **Test APIs directly** - Bypass the integration
2. **Compare responses** - See what each API returns
3. **Debug hostname issues** - Identify where data is lost
4. **Verify API functionality** - Confirm APIs work correctly

The curl commands provide a direct way to test the APIs and compare their responses with what Home Assistant receives!
