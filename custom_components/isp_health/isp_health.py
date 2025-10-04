"""Main ISP Health Monitor class"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .config import Config
from .ip_info import IPInfoManager
from .sensors import (
    DNSConfigSensor, LatencySensor, PacketLossSensor, JitterSensor,
    ThroughputSensor, DNSReliabilitySensor, RouteStabilitySensor
)

logger = logging.getLogger(__name__)


class ISPHealthMonitor:
    """Main ISP Health Monitor class"""
    
    def __init__(self, config: Config):
        self.config = config
        # Convert Pydantic models to dictionaries for IPInfoManager
        ip_config_dict = {k: v.model_dump() for k, v in config.ip_info_config.items()}
        self.ip_info_manager = IPInfoManager(ip_config_dict)
        self.sensors = self._initialize_sensors()
    
    def _initialize_sensors(self) -> Dict[str, Any]:
        """Initialize all sensors based on configuration"""
        sensors = {}
        
        # DNS Configuration Sensor
        if self.config.sensors.dns_config.enabled:
            sensors["dns_config"] = DNSConfigSensor(self.config.sensors.dns_config.dict())
        
        # Latency Sensor
        if self.config.sensors.latency.enabled:
            sensors["latency"] = LatencySensor(self.config.sensors.latency.dict())
        
        # Packet Loss Sensor
        if self.config.sensors.packet_loss.enabled:
            sensors["packet_loss"] = PacketLossSensor(self.config.sensors.packet_loss.dict())
        
        # Jitter Sensor
        if self.config.sensors.jitter.enabled:
            sensors["jitter"] = JitterSensor(self.config.sensors.jitter.dict())
        
        # Throughput Sensor
        if self.config.sensors.throughput.enabled:
            sensors["throughput"] = ThroughputSensor(self.config.sensors.throughput.dict())
        
        # DNS Reliability Sensor
        if self.config.sensors.dns_reliability.enabled:
            sensors["dns_reliability"] = DNSReliabilitySensor(self.config.sensors.dns_reliability.dict())
        
        # Route Stability Sensor
        if self.config.sensors.route_stability.enabled:
            sensors["route_stability"] = RouteStabilitySensor(self.config.sensors.route_stability.dict())
        
        return sensors
    
    async def get_ip_information(self) -> Dict[str, Any]:
        """Get IP information using the configured source"""
        try:
            # Add timeout to prevent hanging
            logger.info(f"Getting IP information from source: {self.config.ip_info_source}")
            result = await asyncio.wait_for(
                self.ip_info_manager.get_ip_info(self.config.ip_info_source),
                timeout=30  # 30 second timeout
            )
            logger.info(f"Successfully got IP information: {result.get('ip', 'unknown')}")
            return result
        except asyncio.TimeoutError:
            logger.error("IP information request timed out")
            return {
                "status": "error",
                "error": "Request timed out",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get IP information: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_dns_configuration(self) -> Dict[str, Any]:
        """Get DNS configuration"""
        if "dns_config" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["dns_config"].get_data()
        except Exception as e:
            logger.error(f"Failed to get DNS configuration: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_latency(self) -> Dict[str, Any]:
        """Get latency measurements"""
        if "latency" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["latency"].get_data()
        except Exception as e:
            logger.error(f"Failed to get latency: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_packet_loss(self) -> Dict[str, Any]:
        """Get packet loss measurements"""
        if "packet_loss" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["packet_loss"].get_data()
        except Exception as e:
            logger.error(f"Failed to get packet loss: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_jitter(self) -> Dict[str, Any]:
        """Get jitter measurements"""
        if "jitter" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["jitter"].get_data()
        except Exception as e:
            logger.error(f"Failed to get jitter: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_throughput(self) -> Dict[str, Any]:
        """Get throughput measurements"""
        if "throughput" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["throughput"].get_data()
        except Exception as e:
            logger.error(f"Failed to get throughput: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_dns_reliability(self) -> Dict[str, Any]:
        """Get DNS reliability measurements"""
        if "dns_reliability" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["dns_reliability"].get_data()
        except Exception as e:
            logger.error(f"Failed to get DNS reliability: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_route_stability(self) -> Dict[str, Any]:
        """Get route stability measurements"""
        if "route_stability" not in self.sensors:
            return {"status": "disabled"}
        
        try:
            return await self.sensors["route_stability"].get_data()
        except Exception as e:
            logger.error(f"Failed to get route stability: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_all_sensor_data(self) -> Dict[str, Any]:
        """Get data from all enabled sensors"""
        results = {}
        
        # Get IP information (always available)
        results["ip_info"] = await self.get_ip_information()
        
        # Get data from all enabled sensors
        for sensor_name, sensor in self.sensors.items():
            try:
                results[sensor_name] = await sensor.get_data()
            except Exception as e:
                logger.error(f"Failed to get data from {sensor_name}: {e}")
                results[sensor_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def get_enabled_sensors(self) -> list:
        """Get list of enabled sensor names"""
        return list(self.sensors.keys())
    
    def get_sensor_status(self) -> Dict[str, bool]:
        """Get status of all sensors"""
        return {
            "ip_info": True,  # Always available
            **{name: sensor.is_enabled() for name, sensor in self.sensors.items()}
        }
