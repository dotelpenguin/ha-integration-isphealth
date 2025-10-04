"""Configuration management for ISP Health Monitor"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class IPInfoConfig(BaseModel):
    """Configuration for IP information sources"""
    token: Optional[str] = None
    api_key: Optional[str] = None


class SensorConfig(BaseModel):
    """Base configuration for sensors"""
    enabled: bool = True
    interval: int = Field(ge=30, le=3600)  # 30 seconds to 1 hour


class LatencyConfig(SensorConfig):
    """Configuration for latency sensor"""
    targets: List[str] = Field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])


class ThroughputConfig(SensorConfig):
    """Configuration for throughput sensor"""
    interval: int = Field(ge=3600, le=86400)  # 1 hour to 24 hours
    test_multiple_servers: bool = Field(default=False)
    max_servers: int = Field(default=3, ge=1, le=10)
    timeout: int = Field(default=30, ge=10, le=120)


class DNSReliabilityConfig(SensorConfig):
    """Configuration for DNS reliability sensor"""
    servers: List[str] = Field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])


class RouteStabilityConfig(SensorConfig):
    """Configuration for route stability sensor"""
    targets: List[str] = Field(default_factory=lambda: ["google.com", "cloudflare.com"])
    max_hops: int = Field(default=15, ge=5, le=30)
    timeout: int = Field(default=30, ge=10, le=120)
    analyze_hops: bool = Field(default=True)


class SensorsConfig(BaseModel):
    """Configuration for all sensors"""
    ip_info: SensorConfig = Field(default_factory=lambda: SensorConfig(interval=60))
    dns_config: SensorConfig = Field(default_factory=lambda: SensorConfig(interval=60))
    latency: LatencyConfig = Field(default_factory=lambda: LatencyConfig(interval=60))
    packet_loss: SensorConfig = Field(default_factory=lambda: SensorConfig(interval=120))
    jitter: SensorConfig = Field(default_factory=lambda: SensorConfig(interval=120))
    throughput: ThroughputConfig = Field(default_factory=lambda: ThroughputConfig(interval=3600))
    dns_reliability: DNSReliabilityConfig = Field(default_factory=lambda: DNSReliabilityConfig(interval=180))
    route_stability: RouteStabilityConfig = Field(default_factory=lambda: RouteStabilityConfig(interval=1800))


class Config(BaseModel):
    """Main configuration class"""
    update_interval: int = Field(default=60, ge=30, le=600)  # 30 seconds to 10 minutes
    ip_info_source: str = Field(default="ipinfo")
    ip_info_config: Dict[str, IPInfoConfig] = Field(default_factory=dict)
    sensors: SensorsConfig = Field(default_factory=SensorsConfig)
    
    @classmethod
    def from_file(cls, file_path: str) -> "Config":
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return cls()
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    def to_file(self, file_path: str) -> None:
        """Save configuration to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.dict(), f, indent=2)
    
    def get_ip_info_config(self) -> IPInfoConfig:
        """Get configuration for the selected IP info source"""
        return self.ip_info_config.get(self.ip_info_source, IPInfoConfig())
