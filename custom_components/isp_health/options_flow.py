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
        
        # Create simplified schema
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_INTERVAL, 
                    default=current_data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
                
                vol.Required(
                    CONF_IP_INFO_SOURCE, 
                    default=current_data.get(CONF_IP_INFO_SOURCE, DEFAULT_IP_INFO_SOURCE)
                ): vol.In(list(IP_INFO_SOURCES.keys())),
                
                vol.Optional(
                    CONF_IP_INFO_TOKEN, 
                    default=current_data.get(CONF_IP_INFO_TOKEN, "")
                ): str,
                
                # Essential sensors only
                vol.Required(
                    "enable_latency", 
                    default=current_sensors.get("latency", {}).get("enabled", True)
                ): bool,
                
                vol.Required(
                    "enable_speed_test", 
                    default=current_sensors.get("throughput", {}).get("enabled", False)
                ): bool,
            }
        )
        
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    def _create_sensors_config(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Create simplified sensor configuration from user input."""
        sensors_config = {}
        
        # Core sensors (always enabled)
        sensors_config["ip_info"] = {
            "enabled": True,
            "interval": 60  # Fixed interval for simplicity
        }
        sensors_config["dns_config"] = {
            "enabled": True,
            "interval": 60  # Fixed interval for simplicity
        }
        
        # Essential sensors only
        sensors_config["latency"] = {
            "enabled": user_input.get("enable_latency", True),
            "interval": 60  # Fixed interval for simplicity
        }
        
        # Speed test (optional)
        sensors_config["throughput"] = {
            "enabled": user_input.get("enable_speed_test", False),
            "interval": 3600,  # 1 hour default
            "test_download": True,
            "test_upload": True,
            "test_ping": True,
        }
        
        return sensors_config
