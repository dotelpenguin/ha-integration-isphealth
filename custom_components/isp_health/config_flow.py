"""Simplified config flow for ISP Health Monitor integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_IP_INFO_SOURCE,
    CONF_IP_INFO_TOKEN,
    CONF_SENSORS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_IP_INFO_SOURCE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    IP_INFO_SOURCES,
    SENSOR_TYPES,
)
# Options flow disabled to prevent reconfiguration after initial setup

_LOGGER = logging.getLogger(__name__)

# v2.0.0-beta.1: Simplified configuration
# Single step with only essential options
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_UPDATE_INTERVAL, default=60): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=300)
        ),
        vol.Required(CONF_IP_INFO_SOURCE, default="ipapi"): vol.In(
            list(IP_INFO_SOURCES.keys())
        ),
        vol.Optional(CONF_IP_INFO_TOKEN, default=""): str,
        # Essential sensors only
        vol.Required("enable_latency", default=True): bool,
        vol.Required("enable_speed_test", default=False): bool,
    }
)


class ISPHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ISP Health Monitor."""

    VERSION = 2  # Updated for v2.0.0-beta.1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create simplified sensor configuration
            sensors_config = self._create_sensors_config(user_input)
            
            # Create the entry
            return self.async_create_entry(
                title="ISP Health Monitor",
                data={
                    **user_input,
                    CONF_SENSORS: sensors_config,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "sources": ", ".join(IP_INFO_SOURCES.values()),
                "note": "Simple ISP health monitoring. All features work without API keys.",
            },
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""