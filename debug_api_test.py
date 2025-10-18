#!/usr/bin/env python3
"""
Debug script to test all three IP information API endpoints
and compare their responses, especially hostname data.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional


class IPAPIDebugger:
    """Debug tool for testing IP information APIs"""
    
    def __init__(self):
        self.results = {}
    
    async def test_ip_api_com(self, token: str = "") -> Dict[str, Any]:
        """Test ip-api.com endpoint"""
        print("🌐 Testing ip-api.com...")
        
        url = "http://ip-api.com/json"
        if token:
            url += f"?token={token}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                print(f"   📡 Requesting: {url}")
                async with session.get(url) as response:
                    print(f"   📊 Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success! Got {len(data)} fields")
                        
                        # Extract key fields
                        result = {
                            "source": "ip-api.com",
                            "ip": data.get("query"),
                            "hostname": data.get("reverse"),
                            "city": data.get("city"),
                            "region": data.get("regionName"),
                            "country": data.get("country"),
                            "latitude": data.get("lat"),
                            "longitude": data.get("lon"),
                            "organization": data.get("isp"),
                            "postal_code": data.get("zip"),
                            "timezone": data.get("timezone"),
                            "raw_response": data,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        print(f"   🏠 Hostname: '{result['hostname']}' (type: {type(result['hostname'])})")
                        print(f"   🏢 Organization: '{result['organization']}'")
                        print(f"   📍 Location: {result['city']}, {result['region']}, {result['country']}")
                        
                        # Show raw JSON response
                        print(f"   📄 Raw JSON Response:")
                        print(f"   {json.dumps(data, indent=6)}")
                        
                        return result
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP {response.status}: {error_text}")
                        return {"source": "ip-api.com", "error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"source": "ip-api.com", "error": str(e)}
    
    async def test_ipinfo_io(self, token: str = "") -> Dict[str, Any]:
        """Test ipinfo.io endpoint"""
        print("\n🔍 Testing ipinfo.io...")
        
        url = "https://ipinfo.io/json"
        if token:
            url += f"?token={token}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                print(f"   📡 Requesting: {url}")
                async with session.get(url) as response:
                    print(f"   📊 Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success! Got {len(data)} fields")
                        
                        # Extract key fields
                        result = {
                            "source": "ipinfo.io",
                            "ip": data.get("ip"),
                            "hostname": data.get("hostname"),
                            "city": data.get("city"),
                            "region": data.get("region"),
                            "country": data.get("country"),
                            "latitude": data.get("loc", "").split(",")[0] if data.get("loc") else None,
                            "longitude": data.get("loc", "").split(",")[1] if data.get("loc") else None,
                            "organization": data.get("org"),
                            "postal_code": data.get("postal"),
                            "timezone": data.get("timezone"),
                            "raw_response": data,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        print(f"   🏠 Hostname: '{result['hostname']}' (type: {type(result['hostname'])})")
                        print(f"   🏢 Organization: '{result['organization']}'")
                        print(f"   📍 Location: {result['city']}, {result['region']}, {result['country']}")
                        
                        # Show raw JSON response
                        print(f"   📄 Raw JSON Response:")
                        print(f"   {json.dumps(data, indent=6)}")
                        
                        return result
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP {response.status}: {error_text}")
                        return {"source": "ipinfo.io", "error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"source": "ipinfo.io", "error": str(e)}
    
    async def test_ipgeolocation_io(self, api_key: str = "") -> Dict[str, Any]:
        """Test ipgeolocation.io endpoint"""
        print("\n💎 Testing ipgeolocation.io...")
        
        if not api_key:
            print("   ⚠️  No API key provided - skipping ipgeolocation.io")
            return {"source": "ipgeolocation.io", "error": "No API key provided"}
        
        url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                print(f"   📡 Requesting: {url}")
                async with session.get(url) as response:
                    print(f"   📊 Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success! Got {len(data)} fields")
                        
                        # Extract key fields
                        result = {
                            "source": "ipgeolocation.io",
                            "ip": data.get("ip"),
                            "hostname": data.get("hostname"),
                            "city": data.get("city"),
                            "region": data.get("state_prov"),
                            "country": data.get("country_name"),
                            "latitude": data.get("latitude"),
                            "longitude": data.get("longitude"),
                            "organization": data.get("organization"),
                            "postal_code": data.get("zipcode"),
                            "timezone": data.get("time_zone", {}).get("name") if isinstance(data.get("time_zone"), dict) else data.get("time_zone"),
                            "raw_response": data,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        print(f"   🏠 Hostname: '{result['hostname']}' (type: {type(result['hostname'])})")
                        print(f"   🏢 Organization: '{result['organization']}'")
                        print(f"   📍 Location: {result['city']}, {result['region']}, {result['country']}")
                        
                        # Show raw JSON response
                        print(f"   📄 Raw JSON Response:")
                        print(f"   {json.dumps(data, indent=6)}")
                        
                        return result
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP {response.status}: {error_text}")
                        return {"source": "ipgeolocation.io", "error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"source": "ipgeolocation.io", "error": str(e)}
    
    def compare_results(self, results: Dict[str, Dict[str, Any]]) -> None:
        """Compare results from all providers"""
        print("\n" + "="*80)
        print("📊 COMPARISON RESULTS")
        print("="*80)
        
        # Compare key fields
        fields_to_compare = [
            "ip", "hostname", "city", "region", "country", 
            "latitude", "longitude", "organization", "postal_code", "timezone"
        ]
        
        for field in fields_to_compare:
            print(f"\n🔍 {field.upper()}:")
            for source, data in results.items():
                if "error" not in data:
                    value = data.get(field, "N/A")
                    value_type = type(value).__name__
                    print(f"   {source:15}: '{value}' ({value_type})")
                else:
                    print(f"   {source:15}: ERROR - {data['error']}")
        
        # Hostname analysis
        print(f"\n🏠 HOSTNAME ANALYSIS:")
        hostnames = {}
        for source, data in results.items():
            if "error" not in data:
                hostname = data.get("hostname")
                hostnames[source] = hostname
                if hostname:
                    print(f"   ✅ {source:15}: '{hostname}'")
                else:
                    print(f"   ❌ {source:15}: null/empty")
            else:
                print(f"   ⚠️  {source:15}: ERROR - {data['error']}")
        
        # Summary
        print(f"\n📋 SUMMARY:")
        successful = [source for source, data in results.items() if "error" not in data]
        print(f"   ✅ Successful providers: {', '.join(successful)}")
        
        hostname_sources = [source for source, hostname in hostnames.items() if hostname]
        print(f"   🏠 Hostname available from: {', '.join(hostname_sources) if hostname_sources else 'None'}")
        
        if len(hostname_sources) > 1:
            print(f"   🔍 Hostname differences:")
            for source in hostname_sources:
                print(f"      {source}: '{hostnames[source]}'")
    
    async def run_full_test(self, ipinfo_token: str = "", ipgeolocation_key: str = ""):
        """Run full test of all providers"""
        print("🚀 ISP Health Monitor API Debug Tool")
        print("="*50)
        print(f"⏰ Started at: {datetime.now().isoformat()}")
        print()
        
        # Test all providers
        results = {}
        
        # Test ip-api.com (no token needed)
        results["ip-api.com"] = await self.test_ip_api_com()
        
        # Test ipinfo.io
        results["ipinfo.io"] = await self.test_ipinfo_io(ipinfo_token)
        
        # Test ipgeolocation.io
        results["ipgeolocation.io"] = await self.test_ipgeolocation_io(ipgeolocation_key)
        
        # Compare results
        self.compare_results(results)
        
        # Save detailed results to file
        output_file = f"api_debug_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        return results


async def main():
    """Main function"""
    print("ISP Health Monitor API Debug Tool")
    print("This tool tests all three IP information providers")
    print()
    
    # You can add API keys here if you have them
    ipinfo_token = ""  # Add your ipinfo.io token here if you have one
    ipgeolocation_key = ""  # Add your ipgeolocation.io API key here if you have one
    
    debugger = IPAPIDebugger()
    results = await debugger.run_full_test(ipinfo_token, ipgeolocation_key)
    
    print(f"\n🎯 Debug complete! Check the results above and the saved JSON file.")


if __name__ == "__main__":
    asyncio.run(main())
