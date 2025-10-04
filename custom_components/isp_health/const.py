"""Constants for ISP Health Monitor integration."""

from __future__ import annotations

DOMAIN = "isp_health"

# Configuration keys
CONF_UPDATE_INTERVAL = "update_interval"
CONF_IP_INFO_SOURCE = "ip_info_source"
CONF_IP_INFO_TOKEN = "ip_info_token"
CONF_SENSORS = "sensors"

# Default values
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_IP_INFO_SOURCE = "ipapi"

# Sensor types
SENSOR_TYPES = {
    "ip_info": {
        "name": "Public WAN IP",
        "icon": "mdi:earth",
        "unit_of_measurement": None,  # IP address - no unit
        "device_class": None,
    },
    "dns_config": {
        "name": "WAN DNS Server", 
        "icon": "mdi:dns",
        "unit_of_measurement": None,  # IP address - no unit
        "device_class": None,
    },
    "latency": {
        "name": "WAN Latency",
        "icon": "mdi:speedometer",
        "unit_of_measurement": "ms",  # Milliseconds
        "device_class": "duration",
    },
    "packet_loss": {
        "name": "WAN Packet Loss",
        "icon": "mdi:network-off",
        "unit_of_measurement": "%",  # Percentage
        "device_class": None,
    },
    "jitter": {
        "name": "WAN Jitter",
        "icon": "mdi:chart-line",
        "unit_of_measurement": "ms",  # Milliseconds
        "device_class": "duration",
    },
    "throughput": {
        "name": "WAN Throughput",
        "icon": "mdi:download",
        "unit_of_measurement": "Mbit/s",  # Megabits per second (HA standard)
        "device_class": "data_rate",
    },
    "dns_reliability": {
        "name": "DNS Reliability",
        "icon": "mdi:check-circle",
        "unit_of_measurement": "%",  # Percentage
        "device_class": None,
    },
    "route_stability": {
        "name": "Route Stability",
        "icon": "mdi:map-marker-path",
        "unit_of_measurement": "%",  # Percentage (0-100)
        "device_class": None,
    },
}

# IP Info sources
IP_INFO_SOURCES = {
    "ipapi": "ip-api.com (Free - Most Reliable)",
    "ipinfo": "ipinfo.io (Free - High Quality Data)",
    "ipgeolocation": "ipgeolocation.io (Premium - API Key Required)",
}
