"""IP Information providers and data normalization"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp
import requests

logger = logging.getLogger(__name__)


class IPInfoProvider:
    """Base class for IP information providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    async def get_ip_info(self) -> Dict[str, Any]:
        """Get IP information from the provider"""
        raise NotImplementedError
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data to standard format"""
        raise NotImplementedError


class IPInfoIOProvider(IPInfoProvider):
    """ipinfo.io provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://ipinfo.io"
        self.token = config.get("token")
    
    async def get_ip_info(self) -> Dict[str, Any]:
        """Get IP information from ipinfo.io"""
        url = f"{self.base_url}/json"
        if self.token:
            url += f"?token={self.token}"
        
        try:
            # Use a shorter timeout and add connection timeout
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                logger.info(f"Fetching IP info from ipinfo.io: {url}")
                async with session.get(url) as response:
                    logger.info(f"ipinfo.io response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"ipinfo.io data received: {list(data.keys())}")
                        return self.normalize_data(data)
                    else:
                        error_text = await response.text()
                        logger.error(f"ipinfo.io HTTP {response.status}: {error_text}")
                        raise Exception(f"HTTP {response.status}: {error_text}")
        except asyncio.TimeoutError:
            logger.error("ipinfo.io request timed out")
            raise Exception("Request timed out")
        except Exception as e:
            logger.error(f"Error fetching IP info from ipinfo.io: {e}")
            raise
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ipinfo.io data"""
        # Parse location coordinates
        loc = raw_data.get("loc", "").split(",")
        lat, lon = (float(loc[0]), float(loc[1])) if len(loc) == 2 else (None, None)
        
        return {
            "ip": raw_data.get("ip"),
            "hostname": raw_data.get("hostname"),
            "city": raw_data.get("city"),
            "region": raw_data.get("region"),
            "country": raw_data.get("country"),
            "latitude": lat,
            "longitude": lon,
            "organization": raw_data.get("org"),
            "postal_code": raw_data.get("postal"),
            "timezone": raw_data.get("timezone"),
            "source": "ipinfo.io",
            "timestamp": datetime.now().isoformat()
        }


class IPAPIProvider(IPInfoProvider):
    """ip-api.com provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "http://ip-api.com/json"
        self.token = config.get("token")
    
    async def get_ip_info(self) -> Dict[str, Any]:
        """Get IP information from ip-api.com"""
        url = self.base_url
        if self.token:
            url += f"?token={self.token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            return self.normalize_data(data)
                        else:
                            raise Exception(f"API error: {data.get('message', 'Unknown error')}")
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            logger.error(f"Error fetching IP info from ip-api.com: {e}")
            raise
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ip-api.com data"""
        return {
            "ip": raw_data.get("query"),
            "hostname": raw_data.get("reverse"),
            "city": raw_data.get("city"),
            "region": raw_data.get("regionName"),
            "country": raw_data.get("country"),
            "latitude": raw_data.get("lat"),
            "longitude": raw_data.get("lon"),
            "organization": raw_data.get("isp"),
            "postal_code": raw_data.get("zip"),
            "timezone": raw_data.get("timezone"),
            "source": "ip-api.com",
            "timestamp": datetime.now().isoformat()
        }


class IPGeolocationProvider(IPInfoProvider):
    """ipgeolocation.io provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.ipgeolocation.io/ipgeo"
        self.api_key = config.get("api_key")
        # Note: This service requires an API key, so we'll skip it if not provided
    
    async def get_ip_info(self) -> Dict[str, Any]:
        """Get IP information from ipgeolocation.io"""
        if not self.api_key:
            raise Exception("API key required for ipgeolocation.io")
        url = f"{self.base_url}?apiKey={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.normalize_data(data)
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            logger.error(f"Error fetching IP info from ipgeolocation.io: {e}")
            raise
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ipgeolocation.io data"""
        return {
            "ip": raw_data.get("ip"),
            "hostname": raw_data.get("hostname"),
            "city": raw_data.get("city"),
            "region": raw_data.get("state_prov"),
            "country": raw_data.get("country_name"),
            "latitude": raw_data.get("latitude"),
            "longitude": raw_data.get("longitude"),
            "organization": raw_data.get("organization"),
            "postal_code": raw_data.get("zipcode"),
            "timezone": raw_data.get("time_zone", {}).get("name"),
            "source": "ipgeolocation.io",
            "timestamp": datetime.now().isoformat()
        }


class IPInfoManager:
    """Manages IP information providers with fallback support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        # Prioritize free services that don't require API keys
        self.fallback_order = ["ipapi", "ipinfo", "ipgeolocation"]
    
    def _initialize_providers(self) -> Dict[str, IPInfoProvider]:
        """Initialize available providers"""
        providers = {}
        
        # ipinfo.io
        if "ipinfo" in self.config:
            try:
                providers["ipinfo"] = IPInfoIOProvider(self.config["ipinfo"])
            except Exception as e:
                logger.warning(f"Failed to initialize ipinfo.io provider: {e}")
        
        # ip-api.com
        if "ipapi" in self.config:
            try:
                providers["ipapi"] = IPAPIProvider(self.config["ipapi"])
            except Exception as e:
                logger.warning(f"Failed to initialize ip-api.com provider: {e}")
        
        # ipgeolocation.io (requires API key)
        if "ipgeolocation" in self.config and self.config["ipgeolocation"].get("api_key"):
            try:
                providers["ipgeolocation"] = IPGeolocationProvider(self.config["ipgeolocation"])
            except Exception as e:
                logger.warning(f"Failed to initialize ipgeolocation.io provider: {e}")
        elif "ipgeolocation" in self.config:
            logger.info("Skipping ipgeolocation.io provider (no API key provided)")
        
        return providers
    
    async def get_ip_info(self, preferred_source: str = None) -> Dict[str, Any]:
        """Get IP information with fallback support"""
        sources_to_try = []
        
        if preferred_source and preferred_source in self.providers:
            sources_to_try.append(preferred_source)
        
        # Add other sources in fallback order
        for source in self.fallback_order:
            if source in self.providers and source not in sources_to_try:
                sources_to_try.append(source)
        
        last_error = None
        
        for source in sources_to_try:
            try:
                logger.info(f"Trying IP info source: {source}")
                provider = self.providers[source]
                data = await provider.get_ip_info()
                logger.info(f"Successfully got IP info from {source}")
                return data
            except Exception as e:
                logger.warning(f"Failed to get IP info from {source}: {e}")
                last_error = e
                continue
        
        # If all sources failed, raise the last error
        raise Exception(f"All IP info sources failed. Last error: {last_error}")
    
    def get_available_sources(self) -> List[str]:
        """Get list of available IP info sources"""
        return list(self.providers.keys())
