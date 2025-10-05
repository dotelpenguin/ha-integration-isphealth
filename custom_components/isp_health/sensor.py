"""Enhanced sensor platform for ISP Health Monitor."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import ISPHealthDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ISP Health Monitor sensors based on a config entry."""
    coordinator: ISPHealthDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Get enabled sensors from config
    sensors_config = entry.data.get("sensors", {})
    enabled_sensors = [
        sensor_type for sensor_type, config in sensors_config.items()
        if isinstance(config, dict) and config.get("enabled", True)
    ]
    
    # Always add core sensors
    core_sensors = ["ip_info", "dns_config"]
    for sensor_type in core_sensors:
        if sensor_type not in enabled_sensors:
            enabled_sensors.append(sensor_type)
    
    # Create sensor entities
    entities = []
    for sensor_type in enabled_sensors:
        if sensor_type in SENSOR_TYPES:
            entities.append(ISPHealthSensor(coordinator, sensor_type))
    
    async_add_entities(entities)


class ISPHealthSensor(CoordinatorEntity[ISPHealthDataUpdateCoordinator], SensorEntity):
    """Representation of an ISP Health Monitor sensor."""

    def __init__(
        self,
        coordinator: ISPHealthDataUpdateCoordinator,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = SENSOR_TYPES[sensor_type]['name']
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{sensor_type}"
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit_of_measurement"]
        self._attr_device_class = SENSOR_TYPES[sensor_type]["device_class"]
        # Only set state_class for numeric sensors
        if self._sensor_type in ["latency", "packet_loss", "jitter", "throughput", "dns_reliability", "route_stability"]:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": "ISP Health Monitor",
            "manufacturer": "ISP Health Monitor",
            "model": "Network Monitor",
            "sw_version": "1.0.8-beta.7",
            "hw_version": "Python 3.x",
            "configuration_url": "https://github.com/dotelpenguin/ha-integration-isphealth",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        sensor_data = self.coordinator.data.get("sensors", {}).get(self._sensor_type, {})
        
        if not sensor_data or sensor_data.get("status") == "error":
            return None
        
        # Return appropriate value based on sensor type
        if self._sensor_type == "ip_info":
            return sensor_data.get("ip", "Unknown")
        elif self._sensor_type == "dns_config":
            return sensor_data.get("primary_dns", "Unknown")
        elif self._sensor_type == "latency":
            return sensor_data.get("average")
        elif self._sensor_type == "packet_loss":
            return sensor_data.get("average")
        elif self._sensor_type == "jitter":
            return sensor_data.get("average")
        elif self._sensor_type == "throughput":
            return sensor_data.get("download_mbps")
        elif self._sensor_type == "dns_reliability":
            return sensor_data.get("overall_success_rate")
        elif self._sensor_type == "route_stability":
            return sensor_data.get("overall_stability")
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
            
        sensor_data = self.coordinator.data.get("sensors", {}).get(self._sensor_type, {})
        
        if not sensor_data:
            return {}
        
        # Return all sensor data as attributes
        attrs = {}
        
        # Add common attributes
        if "timestamp" in sensor_data:
            attrs["last_update"] = sensor_data["timestamp"]
        if "status" in sensor_data:
            attrs["status"] = sensor_data["status"]
        
        # Add sensor-specific attributes
        if self._sensor_type == "ip_info":
            attrs.update({
                "hostname": sensor_data.get("hostname"),
                "city": sensor_data.get("city"),
                "region": sensor_data.get("region"),
                "country": sensor_data.get("country"),
                "latitude": sensor_data.get("latitude"),
                "longitude": sensor_data.get("longitude"),
                "organization": sensor_data.get("organization"),
                "postal_code": sensor_data.get("postal_code"),
                "timezone": sensor_data.get("timezone"),
                "source": sensor_data.get("source"),
            })
        elif self._sensor_type == "dns_config":
            attrs.update({
                "primary_dns": sensor_data.get("primary_dns"),
                "secondary_dns": sensor_data.get("secondary_dns"),
                "all_dns_servers": sensor_data.get("all_dns_servers", []),
                "source": sensor_data.get("source"),
                "resolution_test": sensor_data.get("resolution_test", {}),
                # Per-method detection results
                "supervisor_dns": sensor_data.get("supervisor_dns", []),
                "docker_host_dns": sensor_data.get("docker_host_dns", []),
                "gateway_dns": sensor_data.get("gateway_dns", []),
                "systemd_resolve_dns": sensor_data.get("systemd_resolve_dns", []),
                "resolv_conf_dns": sensor_data.get("resolv_conf_dns", []),
                "public_fallback_dns": sensor_data.get("public_fallback_dns", []),
                # Raw
                "supervisor_dns_raw": sensor_data.get("supervisor_dns_raw", []),
                "docker_host_dns_raw": sensor_data.get("docker_host_dns_raw", []),
                "gateway_dns_raw": sensor_data.get("gateway_dns_raw", []),
                "systemd_resolve_dns_raw": sensor_data.get("systemd_resolve_dns_raw", []),
                "resolv_conf_dns_raw": sensor_data.get("resolv_conf_dns_raw", []),
                "public_fallback_dns_raw": sensor_data.get("public_fallback_dns_raw", []),
            })
        elif self._sensor_type == "latency":
            attrs.update({
                "minimum": sensor_data.get("minimum"),
                "maximum": sensor_data.get("maximum"),
                "results": sensor_data.get("results", []),
            })
        elif self._sensor_type == "packet_loss":
            attrs.update({
                "minimum": sensor_data.get("minimum"),
                "maximum": sensor_data.get("maximum"),
                "results": sensor_data.get("results", []),
            })
        elif self._sensor_type == "jitter":
            attrs.update({
                "minimum": sensor_data.get("minimum"),
                "maximum": sensor_data.get("maximum"),
                "results": sensor_data.get("results", []),
            })
        elif self._sensor_type == "throughput":
            attrs.update({
                "upload_mbps": sensor_data.get("upload_mbps"),
                "server": sensor_data.get("server", {}),
                "test_type": sensor_data.get("test_type"),
            })
        elif self._sensor_type == "dns_reliability":
            attrs.update({
                "average_response_time": sensor_data.get("average_response_time"),
                "results": sensor_data.get("results", []),
            })
        elif self._sensor_type == "route_stability":
            attrs.update({
                "total_route_changes": sensor_data.get("total_route_changes"),
                "average_hop_count": sensor_data.get("average_hop_count"),
                "results": sensor_data.get("results", []),
            })
        
        return attrs