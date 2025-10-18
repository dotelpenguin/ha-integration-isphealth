# 🔍 ISP Health Monitor API Debug Tool

## 🎯 Purpose

This debug tool tests all three IP information API endpoints and compares their responses, especially focusing on hostname data to help identify why some providers return null hostnames.

## 🚀 Quick Start

### **Option 1: Run the script directly**
```bash
python3 debug_api_test.py
```

### **Option 2: Use the runner script**
```bash
./run_debug.sh
```

## 📊 What It Tests

### **🌐 ip-api.com (Free)**
- **URL**: `http://ip-api.com/json`
- **Token**: Optional (for higher rate limits)
- **Rate Limit**: 45 requests/minute
- **Fields**: IP, hostname, city, region, country, coordinates, organization, postal code, timezone

### **🔍 ipinfo.io (Free/Premium)**
- **URL**: `https://ipinfo.io/json`
- **Token**: Optional (for higher rate limits)
- **Rate Limit**: 50k requests/month (free)
- **Fields**: IP, hostname, city, region, country, coordinates, organization, postal code, timezone

### **💎 ipgeolocation.io (Premium)**
- **URL**: `https://api.ipgeolocation.io/ipgeo`
- **API Key**: Required
- **Rate Limit**: Depends on plan
- **Fields**: IP, hostname, city, region, country, coordinates, organization, postal code, timezone

## 🔍 What It Shows

### **📊 Detailed Output**
- **Raw API responses** from each provider
- **Field-by-field comparison** of all data
- **Hostname analysis** showing which providers return hostnames
- **Data type information** for each field
- **Error handling** for failed requests

### **📋 Comparison Table**
The tool creates a comparison table showing:
- **IP Address** - Should be the same from all providers
- **Hostname** - Key field we're debugging
- **City/Region/Country** - Location data comparison
- **Coordinates** - Latitude/longitude comparison
- **Organization** - ISP information comparison
- **Postal Code** - ZIP/postal code comparison
- **Timezone** - Timezone information comparison

## 🎯 Hostname Analysis

### **🔍 What to Look For**
- **Which providers return hostnames** vs null/empty
- **Data types** - String vs null vs empty string
- **Hostname formats** - Different formats between providers
- **Consistency** - Same hostname from multiple providers

### **📊 Expected Results**
Based on your previous data:
- **ip-api.com**: Likely returns `null` for hostname
- **ipinfo.io**: Likely returns `syn-071-010-063-200.res.spectrum.com`
- **ipgeolocation.io**: Unknown (requires API key)

## 📁 Output Files

### **🖥️ Console Output**
- Real-time testing progress
- Field-by-field comparison
- Summary analysis
- Error messages

### **💾 JSON File**
- Detailed results saved to `api_debug_results_YYYYMMDD_HHMMSS.json`
- Complete raw responses from all providers
- Structured data for further analysis

## 🔧 Configuration

### **API Keys (Optional)**
Edit the script to add your API keys:
```python
ipinfo_token = "your_ipinfo_token_here"  # For higher rate limits
ipgeolocation_key = "your_api_key_here"  # Required for ipgeolocation.io
```

### **Customization**
- **Timeout settings** - Adjust request timeouts
- **Additional fields** - Add more fields to compare
- **Error handling** - Customize error reporting

## 🎯 Troubleshooting

### **❌ Common Issues**
- **No internet connection** - Check your internet connectivity
- **Rate limiting** - Wait a few minutes between runs
- **API key issues** - Verify your API keys are correct
- **Python dependencies** - Install aiohttp if missing

### **🔧 Dependencies**
```bash
pip install aiohttp
```

## 📊 Example Output

```
🚀 ISP Health Monitor API Debug Tool
==================================================
⏰ Started at: 2024-01-15T10:30:00

🌐 Testing ip-api.com...
   📡 Requesting: http://ip-api.com/json
   📊 Status: 200
   ✅ Success! Got 12 fields
   🏠 Hostname: 'null' (type: <class 'NoneType'>)
   🏢 Organization: 'Charter Communications'
   📍 Location: Brighton, Michigan, United States

🔍 Testing ipinfo.io...
   📡 Requesting: https://ipinfo.io/json
   📊 Status: 200
   ✅ Success! Got 8 fields
   🏠 Hostname: 'syn-071-010-063-200.res.spectrum.com' (type: <class 'str'>)
   🏢 Organization: 'AS20115 Charter Communications LLC'
   📍 Location: Whitmore Lake, Michigan, US

📊 COMPARISON RESULTS
================================================================================

🔍 HOSTNAME:
   ip-api.com      : 'None' (NoneType)
   ipinfo.io       : 'syn-071-010-063-200.res.spectrum.com' (str)
   ipgeolocation.io: ERROR - No API key provided

🏠 HOSTNAME ANALYSIS:
   ✅ ip-api.com      : null/empty
   ✅ ipinfo.io       : 'syn-071-010-063-200.res.spectrum.com'
   ⚠️  ipgeolocation.io: ERROR - No API key provided

📋 SUMMARY:
   ✅ Successful providers: ip-api.com, ipinfo.io
   🏠 Hostname available from: ipinfo.io
```

## 🎯 Next Steps

1. **Run the debug tool** to see current API responses
2. **Compare the results** with your Home Assistant data
3. **Identify discrepancies** between API responses and HA sensor data
4. **Share the results** to help debug the hostname null issue

This tool will help us understand exactly what data each API returns and why the hostname might be showing as null in Home Assistant!
