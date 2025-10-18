"""Complete options flow for ISP Health Monitor integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_IP_INFO_SOURCE,
    CONF_IP_INFO_TOKEN,
    CONF_SENSORS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_IP_INFO_SOURCE,
    DEFAULT_UPDATE_INTERVAL,
    IP_INFO_SOURCES,
)

_LOGGER = logging.getLogger(__name__)


class ISPHealthOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for ISP Health Monitor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ):
        """Manage the options."""
        if user_input is not None:
            # Create sensor configuration
            sensors_config = self._create_sensors_config(user_input)
            
            # Update the entry
            return self.async_create_entry(
                title="",
                data={
                    **user_input,
                    CONF_SENSORS: sensors_config,
                },
            )

        # Get current values with safe defaults
        current_data = self.config_entry.data or {}
        current_sensors = current_data.get(CONF_SENSORS, {})
        
        # Create complete schema
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_INTERVAL, 
                    default=current_data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
                
                vol.Required(
                    CONF_IP_INFO_SOURCE, 
                    default=current_data.get(CONF_IP_INFO_SOURCE, DEFAULT_IP_INFO_SOURCE)
                ): vol.In(list(IP_INFO_SOURCES.keys())),
                
                vol.Optional(
                    CONF_IP_INFO_TOKEN, 
                    default=current_data.get(CONF_IP_INFO_TOKEN, "")
                ): str,
                
                # Core sensors
                vol.Required(
                    "ip_info_interval", 
                    default=current_sensors.get("ip_info", {}).get("interval", 60)
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
                
                vol.Required(
                    "dns_config_interval", 
                    default=current_sensors.get("dns_config", {}).get("interval", 60)
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
                vol.Optional(
                    "custom_dns",
                    default=current_sensors.get("dns_config", {}).get("custom_dns", "")
                ): str,
                
                # Extended sensors
                vol.Required(
                    "enable_latency", 
                    default=current_sensors.get("latency", {}).get("enabled", True)
                ): bool,
                
                vol.Required(
                    "latency_interval", 
                    default=current_sensors.get("latency", {}).get("interval", 60)
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
                
                vol.Required(
                    "enable_packet_loss", 
                    default=current_sensors.get("packet_loss", {}).get("enabled", True)
                ): bool,
                
                vol.Required(
                    "packet_loss_interval", 
                    default=current_sensors.get("packet_loss", {}).get("interval", 120)
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=1800)),
                
                vol.Required(
                    "enable_jitter", 
                    default=current_sensors.get("jitter", {}).get("enabled", True)
                ): bool,
                
                vol.Required(
                    "jitter_interval", 
                    default=current_sensors.get("jitter", {}).get("interval", 120)
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=1800)),
                
                vol.Required(
                    "enable_throughput", 
                    default=current_sensors.get("throughput", {}).get("enabled", False)
                ): bool,
                
                vol.Required(
                    "throughput_interval", 
                    default=current_sensors.get("throughput", {}).get("interval", 3600)
                ): vol.All(vol.Coerce(int), vol.Range(min=3600, max=86400)),
                
                # Throughput test configuration
                vol.Required(
                    "test_download", 
                    default=current_sensors.get("throughput", {}).get("test_download", True)
                ): bool,
                
                vol.Required(
                    "test_upload", 
                    default=current_sensors.get("throughput", {}).get("test_upload", True)
                ): bool,
                
                vol.Required(
                    "test_ping", 
                    default=current_sensors.get("throughput", {}).get("test_ping", True)
                ): bool,
                
                # Time window configuration
                vol.Required(
                    "allowed_hours_start", 
                    default=current_sensors.get("throughput", {}).get("allowed_hours_start", 0)
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
                
                vol.Required(
                    "allowed_hours_end", 
                    default=current_sensors.get("throughput", {}).get("allowed_hours_end", 23)
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
                
                vol.Optional(
                    "allowed_days",
                    default=",".join(map(str, current_sensors.get("throughput", {}).get("allowed_days", list(range(7)))))
                ): str,
                
                # Organization filtering
                vol.Optional(
                    "organization_pattern",
                    default=current_sensors.get("throughput", {}).get("organization_pattern", "")
                ): str,
                
                vol.Required(
                    "require_organization_match", 
                    default=current_sensors.get("throughput", {}).get("require_organization_match", False)
                ): bool,
                
                vol.Required(
                    "enable_dns_reliability", 
                    default=current_sensors.get("dns_reliability", {}).get("enabled", True)
                ): bool,
                
                vol.Required(
                    "dns_reliability_interval", 
                    default=current_sensors.get("dns_reliability", {}).get("interval", 180)
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=1800)),
                
                vol.Required(
                    "enable_route_stability", 
                    default=current_sensors.get("route_stability", {}).get("enabled", False)
                ): bool,
                
                vol.Required(
                    "route_stability_interval", 
                    default=current_sensors.get("route_stability", {}).get("interval", 1800)
                ): vol.All(vol.Coerce(int), vol.Range(min=300, max=7200)),
            }
        )
        
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    def _create_sensors_config(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Create sensor configuration from user input."""
        sensors_config = {}
        
        # Core sensors (always enabled)
        sensors_config["ip_info"] = {
            "enabled": True,
            "interval": user_input.get("ip_info_interval", 60)
        }
        sensors_config["dns_config"] = {
            "enabled": True,
            "interval": user_input.get("dns_config_interval", 60),
            "custom_dns": user_input.get("custom_dns", ""),
        }
        
        # Extended sensors (user configurable)
        sensors_config["latency"] = {
            "enabled": user_input.get("enable_latency", True),
            "interval": user_input.get("latency_interval", 60)
        }
        sensors_config["packet_loss"] = {
            "enabled": user_input.get("enable_packet_loss", True),
            "interval": user_input.get("packet_loss_interval", 120)
        }
        sensors_config["jitter"] = {
            "enabled": user_input.get("enable_jitter", True),
            "interval": user_input.get("jitter_interval", 120)
        }
        # Parse allowed days from comma-separated string
        allowed_days_str = user_input.get("allowed_days", "0,1,2,3,4,5,6")
        try:
            allowed_days = [int(day.strip()) for day in allowed_days_str.split(",") if day.strip()]
        except ValueError:
            allowed_days = list(range(7))  # Default to all days if parsing fails
        
        sensors_config["throughput"] = {
            "enabled": user_input.get("enable_throughput", False),
            "interval": user_input.get("throughput_interval", 3600),
            # Test configuration
            "test_download": user_input.get("test_download", True),
            "test_upload": user_input.get("test_upload", True),
            "test_ping": user_input.get("test_ping", True),
            # Time window configuration
            "allowed_hours_start": user_input.get("allowed_hours_start", 0),
            "allowed_hours_end": user_input.get("allowed_hours_end", 23),
            "allowed_days": allowed_days,
            # Organization filtering
            "organization_pattern": user_input.get("organization_pattern", ""),
            "require_organization_match": user_input.get("require_organization_match", False),
        }
        sensors_config["dns_reliability"] = {
            "enabled": user_input.get("enable_dns_reliability", True),
            "interval": user_input.get("dns_reliability_interval", 180)
        }
        sensors_config["route_stability"] = {
            "enabled": user_input.get("enable_route_stability", False),
            "interval": user_input.get("route_stability_interval", 1800)
        }
        
        return sensors_config
