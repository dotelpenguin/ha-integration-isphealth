"""Enhanced data update coordinator for ISP Health Monitor."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_UPDATE_INTERVAL, CONF_IP_INFO_SOURCE, CONF_IP_INFO_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ISPHealthDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the ISP Health Monitor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.hass = hass
        
        # Get update interval from config
        update_interval = entry.data.get(CONF_UPDATE_INTERVAL, 60)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Import our ISP health monitor modules using relative imports
            _LOGGER.info("Importing ISP health modules using relative imports")
            from .isp_health import ISPHealthMonitor
            from .config import Config
            _LOGGER.info("Successfully imported ISP health modules")
            
            # Create configuration from entry data
            config_data = self._create_config_from_entry()
            _LOGGER.info("Created config data: %s", config_data)
            config = Config(**config_data)
            _LOGGER.info("Successfully created Config object")
            
            # Create monitor
            monitor = ISPHealthMonitor(config)
            _LOGGER.info("Successfully created ISPHealthMonitor")
            
            # Get all sensor data
            _LOGGER.info("Calling get_all_sensor_data()...")
            sensor_data = await monitor.get_all_sensor_data()
            _LOGGER.info("Successfully got sensor data: %s", list(sensor_data.keys()) if sensor_data else "None")
            
            # Wrap in expected structure
            data = {
                "sensors": sensor_data,
                "last_update": datetime.now().isoformat(),
                "update_interval": self.entry.data.get(CONF_UPDATE_INTERVAL, 60),
            }
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error updating ISP health data: %s", err)
            _LOGGER.error("Exception type: %s", type(err).__name__)
            import traceback
            _LOGGER.error("Full traceback: %s", traceback.format_exc())
            # Return mock data as fallback
            return self._get_mock_data()

    def _create_config_from_entry(self) -> dict[str, Any]:
        """Create configuration dictionary from config entry."""
        entry_data = self.entry.data
        
        # Build IP info config
        ip_info_source = entry_data.get(CONF_IP_INFO_SOURCE, "ipapi")
        ip_info_token = entry_data.get(CONF_IP_INFO_TOKEN, "")
        _LOGGER.info("IP Info Source from config: %s", ip_info_source)
        _LOGGER.info("IP Info Token from config: %s", "***" if ip_info_token else "None")
        
        ip_info_config = {
            "ipinfo": {"token": ip_info_token if ip_info_source == "ipinfo" else ""},
            "ipapi": {"token": ip_info_token if ip_info_source == "ipapi" else ""},
            "ipgeolocation": {"api_key": ip_info_token if ip_info_source == "ipgeolocation" else ""},
        }
        _LOGGER.info("IP Info Config created: %s", ip_info_config)
        
        # Build sensors config
        sensors_config = entry_data.get("sensors", {})
        
        # Set default intervals for each sensor type
        default_intervals = {
            "ip_info": 60,
            "dns_config": 60,
            "latency": 60,
            "packet_loss": 120,
            "jitter": 120,
            "throughput": 3600,
            "dns_reliability": 180,
            "route_stability": 1800,
        }
        
        # Ensure all sensors have proper configuration
        for sensor_type, sensor_data in sensors_config.items():
            if isinstance(sensor_data, dict):
                sensor_data.setdefault("interval", default_intervals.get(sensor_type, 60))
            else:
                sensors_config[sensor_type] = {
                    "enabled": sensor_data,
                    "interval": default_intervals.get(sensor_type, 60)
                }
        
        return {
            "update_interval": entry_data.get(CONF_UPDATE_INTERVAL, 60),
            "ip_info_source": ip_info_source,
            "ip_info_config": ip_info_config,
            "sensors": sensors_config,
        }

    def _get_mock_data(self) -> dict[str, Any]:
        """Return mock data for testing/fallback."""
        return {
            "last_update": datetime.now().isoformat(),
            "update_interval": self.entry.data.get(CONF_UPDATE_INTERVAL, 60),
            "sensors": {
                "ip_info": {
                    "ip": "192.168.1.1",
                    "hostname": "mock.example.com",
                    "city": "Test City",
                    "region": "Test Region",
                    "country": "US",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "organization": "Test ISP",
                    "postal_code": "10001",
                    "timezone": "America/New_York",
                    "source": "mock",
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "dns_config": {
                    "primary_dns": "8.8.8.8",
                    "secondary_dns": "8.8.4.4",
                    "all_dns_servers": ["8.8.8.8", "8.8.4.4"],
                    "resolution_test": {
                        "success": True,
                        "success_rate": 100.0,
                        "results": []
                    },
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "latency": {
                    "average": 25.5,
                    "minimum": 20.1,
                    "maximum": 30.9,
                    "results": [
                        {"target": "8.8.8.8", "latency_ms": 25.5, "success": True}
                    ],
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "packet_loss": {
                    "average": 0.0,
                    "minimum": 0.0,
                    "maximum": 0.0,
                    "results": [
                        {"target": "8.8.8.8", "packet_loss_percentage": 0.0, "success": True}
                    ],
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "jitter": {
                    "average": 5.2,
                    "minimum": 3.1,
                    "maximum": 7.8,
                    "results": [
                        {"target": "8.8.8.8", "jitter_ms": 5.2, "success": True}
                    ],
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "throughput": {
                    "download_mbps": 100.0,
                    "upload_mbps": 20.0,
                    "server": {
                        "name": "Test Server",
                        "country": "United States",
                        "distance": 50.0,
                        "latency": 25.0
                    },
                    "test_type": "single_server",
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "dns_reliability": {
                    "overall_success_rate": 100.0,
                    "average_response_time": 15.5,
                    "results": [
                        {"server": "8.8.8.8", "success_rate": 100.0, "average_response_time": 15.5, "success": True}
                    ],
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                },
                "route_stability": {
                    "overall_stability": 1.0,
                    "total_route_changes": 0,
                    "average_hop_count": 12.0,
                    "results": [
                        {
                            "target": "google.com",
                            "hop_count": 12,
                            "route_stability": 1.0,
                            "hop_analysis": {
                                "stable_hops": 12,
                                "unstable_hops": 0,
                                "new_hops": 0,
                                "missing_hops": 0
                            },
                            "route_changes": 0,
                            "success": True
                        }
                    ],
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                }
            }
        }