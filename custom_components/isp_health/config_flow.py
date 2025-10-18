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

# Step 1: Basic configuration
STEP_BASIC_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Required(CONF_IP_INFO_SOURCE, default=DEFAULT_IP_INFO_SOURCE): vol.In(
            list(IP_INFO_SOURCES.keys())
        ),
        vol.Optional(CONF_IP_INFO_TOKEN, default=""): str,
    }
)

# Step 2: Core sensors configuration
STEP_CORE_SENSORS_SCHEMA = vol.Schema(
    {
        vol.Required("ip_info_interval", default=60): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Required("dns_config_interval", default=60): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Optional("custom_dns", default=""): str,
    }
)

# Step 3: Extended sensors configuration
STEP_EXTENDED_SENSORS_SCHEMA = vol.Schema(
    {
        vol.Required("enable_latency", default=True): bool,
        vol.Required("latency_interval", default=60): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Required("enable_packet_loss", default=True): bool,
        vol.Required("packet_loss_interval", default=120): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=1800)
        ),
        vol.Required("enable_jitter", default=True): bool,
        vol.Required("jitter_interval", default=120): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=1800)
        ),
        vol.Required("enable_dns_reliability", default=True): bool,
        vol.Required("dns_reliability_interval", default=180): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=1800)
        ),
        vol.Required("enable_route_stability", default=False): bool,
        vol.Required("route_stability_interval", default=1800): vol.All(
            vol.Coerce(int), vol.Range(min=300, max=7200)
        ),
    }
)

# Step 4: Throughput sensor configuration
STEP_THROUGHPUT_SCHEMA = vol.Schema(
    {
        vol.Required("enable_throughput", default=False): bool,
        vol.Required("throughput_interval", default=3600): vol.All(
            vol.Coerce(int), vol.Range(min=3600, max=86400)
        ),
        # Test configuration
        vol.Required("test_download", default=True): bool,
        vol.Required("test_upload", default=True): bool,
        vol.Required("test_ping", default=True): bool,
        # Time window configuration
        vol.Required("allowed_hours_start", default=0): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=23)
        ),
        vol.Required("allowed_hours_end", default=23): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=23)
        ),
        vol.Optional("allowed_days", default="0,1,2,3,4,5,6"): str,  # Comma-separated days (0=Monday)
        # Organization filtering
        vol.Optional("organization_pattern", default=""): str,
        vol.Required("require_organization_match", default=False): bool,
    }
)


class ISPHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ISP Health Monitor."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        super().__init__()
        self._config_data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the basic configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._config_data.update(user_input)
            return await self.async_step_core_sensors()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_BASIC_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "sources": ", ".join(IP_INFO_SOURCES.values()),
                "note": "All features work without API keys. Tokens only provide higher rate limits.",
                "rate_limits": "Rate Limits: ip-api.com (45 req/min), ipinfo.io (50k req/month free), ipgeolocation.io (requires API key)",
            },
        )

    async def async_step_core_sensors(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the core sensors configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._config_data.update(user_input)
            return await self.async_step_extended_sensors()

        return self.async_show_form(
            step_id="core_sensors",
            data_schema=STEP_CORE_SENSORS_SCHEMA,
            errors=errors,
            description_placeholders={
                "note": "Core sensors are always enabled and provide basic network information.",
            },
        )

    async def async_step_extended_sensors(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the extended sensors configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._config_data.update(user_input)
            return await self.async_step_throughput()

        return self.async_show_form(
            step_id="extended_sensors",
            data_schema=STEP_EXTENDED_SENSORS_SCHEMA,
            errors=errors,
            description_placeholders={
                "note": "Extended sensors provide detailed network analysis. Enable only what you need.",
            },
        )

    async def async_step_throughput(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the throughput sensor configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._config_data.update(user_input)
            
            # Create sensor configuration
            sensors_config = self._create_sensors_config(self._config_data)
            
            # Create the entry
            return self.async_create_entry(
                title="ISP Health Monitor",
                data={
                    **self._config_data,
                    CONF_SENSORS: sensors_config,
                },
            )

        return self.async_show_form(
            step_id="throughput",
            data_schema=STEP_THROUGHPUT_SCHEMA,
            errors=errors,
            description_placeholders={
                "throughput_note": "Speed testing uses bandwidth and should be run less frequently.",
                "time_window_note": "Configure time windows to minimize bandwidth usage during peak hours.",
                "organization_note": "Use regex patterns to control when speed tests run based on your ISP.",
            },
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""