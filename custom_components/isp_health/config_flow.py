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
from .options_flow import ISPHealthOptionsFlowHandler

_LOGGER = logging.getLogger(__name__)

# Single step configuration
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Required(CONF_IP_INFO_SOURCE, default=DEFAULT_IP_INFO_SOURCE): vol.In(
            list(IP_INFO_SOURCES.keys())
        ),
        vol.Optional(CONF_IP_INFO_TOKEN, default=""): str,
        # Core sensors (always enabled)
        vol.Required("ip_info_interval", default=60): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Required("dns_config_interval", default=60): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
        vol.Optional("custom_dns", default=""): str,
        # Extended sensors
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
        vol.Required("enable_throughput", default=False): bool,
        vol.Required("throughput_interval", default=3600): vol.All(
            vol.Coerce(int), vol.Range(min=3600, max=86400)
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


class ISPHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ISP Health Monitor."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return ISPHealthOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create sensor configuration
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
                "note": "All features work without API keys. Tokens only provide higher rate limits.",
                "rate_limits": "Rate Limits: ip-api.com (45 req/min), ipinfo.io (50k req/month free), ipgeolocation.io (requires API key)",
                "throughput_note": "Speed testing uses bandwidth and should be run less frequently.",
                "route_note": "Route analysis is advanced and may take longer to complete."
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
        sensors_config["throughput"] = {
            "enabled": user_input.get("enable_throughput", False),
            "interval": user_input.get("throughput_interval", 3600)
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