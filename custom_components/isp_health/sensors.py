"""Sensor implementation classes for ISP Health Monitor."""

import asyncio
import os
import logging
import subprocess
import time
from typing import Dict, Any, List, Optional
import speedtest
import dns.resolver
import dns.exception
import aiohttp

logger = logging.getLogger(__name__)


class BaseSensor:
    """Base class for all ISP health sensors."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def get_data(self) -> Dict[str, Any]:
        """Get sensor data. Must be implemented by subclasses."""
        raise NotImplementedError


class DNSConfigSensor(BaseSensor):
    """DNS configuration sensor."""
    
    async def get_data(self) -> Dict[str, Any]:
        """Get DNS configuration"""
        try:
            dns_servers, source = await self._get_system_dns_servers()
            resolution_test = await self._test_dns_resolution()
            
            if dns_servers:
                primary_dns = dns_servers[0] if len(dns_servers) > 0 else "Unknown"
                secondary_dns = dns_servers[1] if len(dns_servers) > 1 else "None"
            else:
                primary_dns = "Unknown"
                secondary_dns = "None"
            
            return {
                "primary_dns": primary_dns,
                "secondary_dns": secondary_dns,
                "all_dns_servers": dns_servers,
                "source": source,
                "status": "online" if resolution_test else "offline",
                "error": None if resolution_test else "DNS resolution failed"
            }
        except Exception as e:
            self.logger.error(f"Error getting DNS config: {e}")
            return {
                "primary_dns": "Error",
                "secondary_dns": "Error", 
                "status": "offline",
                "error": str(e)
            }
    
    async def _get_system_dns_servers(self) -> (List[str], str):
        """Get upstream DNS servers (not container DNS) and the source used."""
        dns_servers: List[str] = []
        source_used: str = "unknown"
        
        # Try multiple methods to detect real DNS servers
        methods = [
            self._get_supervisor_dns,
            self._get_docker_host_dns,
            self._get_gateway_dns,
            self._get_systemd_resolve_dns,
            self._get_resolv_conf_dns,
            self._get_common_dns_servers
        ]
        
        for method in methods:
            try:
                detected_dns = await method()
                if detected_dns:
                    # Filter out container/internal DNS
                    filtered_dns = [dns for dns in detected_dns if not self._is_container_dns(dns)]
                    if filtered_dns:
                        dns_servers.extend(filtered_dns)
                        logger.info(f"Detected DNS servers via {method.__name__}: {filtered_dns}")
                        source_used = method.__name__
                        break  # Use first successful method
            except Exception as e:
                logger.debug(f"DNS detection method {method.__name__} failed: {e}")
        
        # If no real DNS found, return common public DNS as fallback
        if not dns_servers:
            dns_servers = ["8.8.8.8", "1.1.1.1"]
            logger.info(f"No real DNS detected, using fallback: {dns_servers}")
            source_used = "public_fallback"
        
        return dns_servers, source_used

    async def _get_supervisor_dns(self) -> List[str]:
        """Get upstream DNS servers from Home Assistant Supervisor (if available)."""
        try:
            supervisor_token = os.environ.get("SUPERVISOR_TOKEN")
            if not supervisor_token:
                return []

            # Supervisor API endpoint for DNS info
            url = "http://supervisor/dns/info"
            headers = {
                "Authorization": f"Bearer {supervisor_token}",
                "Content-Type": "application/json",
            }

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        return []
                    payload = await resp.json()

            # Expected structure includes upstream servers under key 'servers'
            data = payload.get("data") if isinstance(payload, dict) else None
            servers = None
            if isinstance(data, dict):
                servers = data.get("servers") or data.get("upstream_servers")
            if servers and isinstance(servers, list):
                filtered = [s for s in servers if isinstance(s, str) and not self._is_container_dns(s)]
                return filtered
        except Exception as e:
            logger.debug(f"Supervisor DNS query failed: {e}")
        return []
    
    def _is_container_dns(self, dns_ip: str) -> bool:
        """Check if DNS IP is from container/internal network"""
        container_networks = [
            "127.0.0.1", "::1",  # localhost
            "172.",  # Docker default
            "192.168.",  # Private networks
            "10.",  # Private networks
            "169.254.",  # Link-local
        ]
        return any(dns_ip.startswith(network) for network in container_networks)
    
    async def _get_docker_host_dns(self) -> List[str]:
        """Get DNS from Docker host (if running in container)"""
        try:
            # Try to get host's DNS by querying host.docker.internal
            process = await asyncio.create_subprocess_exec(
                "nslookup", "host.docker.internal",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                # Try to get DNS from host network
                return await self._get_gateway_dns()
        except Exception:
            pass
        return []
    
    async def _get_gateway_dns(self) -> List[str]:
        """Get DNS from network gateway"""
        try:
            # Get default gateway
            process = await asyncio.create_subprocess_exec(
                "ip", "route", "show", "default",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                lines = stdout.decode('utf-8').split('\n')
            for line in lines:
                    if 'default via' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            gateway = parts[2]
                            # Gateway is often the DNS server too
                            if not self._is_container_dns(gateway):
                                return [gateway]
        except Exception:
            pass
        return []
    
    async def _get_systemd_resolve_dns(self) -> List[str]:
        """Get DNS from systemd-resolve"""
        try:
            process = await asyncio.create_subprocess_exec(
                "systemd-resolve", "--status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                dns_servers = []
                lines = stdout.decode('utf-8').split('\n')
                for line in lines:
                    if 'DNS Servers:' in line or 'Current DNS Server:' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            dns_ip = parts[1].strip()
                            if dns_ip and not self._is_container_dns(dns_ip):
                                dns_servers.append(dns_ip)
                return dns_servers
        except Exception:
            pass
        return []
    
    async def _get_resolv_conf_dns(self) -> List[str]:
        """Get DNS from resolv.conf (last resort)"""
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = []
                for line in f:
                    if line.startswith('nameserver'):
                        dns_ip = line.split()[1].strip()
                        if not self._is_container_dns(dns_ip):
                            dns_servers.append(dns_ip)
            return dns_servers
        except Exception:
            pass
        return []
    
    async def _get_common_dns_servers(self) -> List[str]:
        """Return common public DNS servers as fallback"""
        return ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    
    
    async def _test_dns_resolution(self) -> bool:
        """Test DNS resolution"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            result = resolver.resolve("google.com", "A")
            return len(result) > 0
        except Exception as e:
            logger.debug(f"DNS resolution test failed: {e}")
            return False


class LatencySensor(BaseSensor):
    """Network latency sensor."""
    
    async def get_data(self) -> Dict[str, Any]:
        """Get network latency"""
        try:
            target = self.config.get("target", "8.8.8.8")
            count = self.config.get("count", 3)
            
            latencies = []
            for _ in range(count):
                latency = await self._ping_host(target)
                if latency is not None:
                    latencies.append(latency)
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                return {
                    "average": round(avg_latency, 2),
                    "min": round(min(latencies), 2),
                    "max": round(max(latencies), 2),
                    "status": "online",
                    "error": None
                }
            else:
                return {
                    "average": 0,
                    "min": 0,
                    "max": 0,
                    "status": "offline",
                    "error": "All ping attempts failed"
                }
        except Exception as e:
            self.logger.error(f"Error measuring latency: {e}")
            return {
                "average": 0,
                "min": 0,
                "max": 0,
                "status": "offline",
                "error": str(e)
            }
    
    async def _ping_host(self, host: str) -> Optional[float]:
        """Ping a host and return latency in ms"""
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "5", host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                output = stdout.decode('utf-8')
                # Parse ping output for time
                for line in output.split('\n'):
                    if 'time=' in line:
                        time_part = line.split('time=')[1].split()[0]
                        return float(time_part)
                return None
        except Exception as e:
            logger.debug(f"Ping failed for {host}: {e}")
            return None


class PacketLossSensor(BaseSensor):
    """Packet loss sensor."""
    
    async def get_data(self) -> Dict[str, Any]:
        """Get packet loss percentage"""
        try:
            target = self.config.get("target", "8.8.8.8")
            count = self.config.get("count", 10)
            
            successful_pings = 0
            for _ in range(count):
                latency = await self._ping_host(target)
                if latency is not None:
                    successful_pings += 1
            
            packet_loss = ((count - successful_pings) / count) * 100
            
            return {
                "average": round(packet_loss, 2),
                "status": "online" if packet_loss < 50 else "offline",
                "error": None
            }
        except Exception as e:
            self.logger.error(f"Error measuring packet loss: {e}")
            return {
                "average": 100,
                "status": "offline",
                "error": str(e)
            }
    
    async def _ping_host(self, host: str) -> Optional[float]:
        """Ping a host and return latency in ms"""
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "5", host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                output = stdout.decode('utf-8')
                for line in output.split('\n'):
                    if 'time=' in line:
                        time_part = line.split('time=')[1].split()[0]
                        return float(time_part)
            return None
        except Exception as e:
            logger.debug(f"Ping failed for {host}: {e}")
            return None


class JitterSensor(BaseSensor):
    """Network jitter sensor."""
    
    async def get_data(self) -> Dict[str, Any]:
        """Get network jitter"""
        try:
            target = self.config.get("target", "8.8.8.8")
            count = self.config.get("count", 10)
            
            latencies = []
            for _ in range(count):
                latency = await self._ping_host(target)
                if latency is not None:
                    latencies.append(latency)
            
            if len(latencies) < 2:
                return {
                    "average": 0,
                    "status": "offline",
                    "error": "Insufficient data for jitter calculation"
                }
            
            # Calculate jitter as standard deviation of latencies
            mean_latency = sum(latencies) / len(latencies)
            variance = sum((x - mean_latency) ** 2 for x in latencies) / len(latencies)
            jitter = variance ** 0.5
            
            return {
                "average": round(jitter, 2),
                "status": "online",
                "error": None
            }
        except Exception as e:
            self.logger.error(f"Error measuring jitter: {e}")
            return {
                "average": 0,
                "status": "offline",
                "error": str(e)
            }
    
    async def _ping_host(self, host: str) -> Optional[float]:
        """Ping a host and return latency in ms"""
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "5", host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                output = stdout.decode('utf-8')
                for line in output.split('\n'):
                    if 'time=' in line:
                        time_part = line.split('time=')[1].split()[0]
                        return float(time_part)
            return None
        except Exception as e:
            logger.debug(f"Ping failed for {host}: {e}")
            return None


class ThroughputSensor(BaseSensor):
    """Network throughput sensor."""
    
    async def get_data(self) -> Dict[str, Any]:
        """Get network throughput"""
        try:
            # Run speedtest in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_speedtest)
            
            if result:
                return {
                    "download_mbps": round(result["download"] / 1000000, 2),
                    "upload_mbps": round(result["upload"] / 1000000, 2),
                    "ping": round(result["ping"], 2),
                    "status": "online",
                    "error": None
                }
            else:
                return {
                    "download_mbps": 0,
                    "upload_mbps": 0,
                    "ping": 0,
                    "status": "offline",
                    "error": "Speedtest failed"
                }
        except Exception as e:
            self.logger.error(f"Error measuring throughput: {e}")
            return {
                "download_mbps": 0,
                "upload_mbps": 0,
                "ping": 0,
                "status": "offline",
                "error": str(e)
            }
    
    def _run_speedtest(self) -> Optional[Dict[str, float]]:
        """Run speedtest-cli"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            st.download()
            st.upload()
            results = st.results.dict()
            return {
                "download": results["download"],
                "upload": results["upload"],
                "ping": results["ping"]
            }
        except Exception as e:
            logger.error(f"Speedtest failed: {e}")
            return None


class DNSReliabilitySensor(BaseSensor):
    """DNS reliability sensor."""
    
    async def get_data(self) -> Dict[str, Any]:
        """Get DNS reliability"""
        try:
            test_domains = ["google.com", "cloudflare.com", "github.com"]
            successful_queries = 0
            total_queries = len(test_domains)
            
            for domain in test_domains:
                if await self._test_dns_query(domain):
                    successful_queries += 1
            
            success_rate = (successful_queries / total_queries) * 100
            
            return {
                "overall_success_rate": round(success_rate, 2),
                "successful_queries": successful_queries,
                "total_queries": total_queries,
                "status": "online" if success_rate > 50 else "offline",
                "error": None
            }
        except Exception as e:
            self.logger.error(f"Error measuring DNS reliability: {e}")
            return {
                "overall_success_rate": 0,
                "successful_queries": 0,
                "total_queries": 0,
                "status": "offline",
                "error": str(e)
            }
    
    async def _test_dns_query(self, domain: str) -> bool:
        """Test DNS query for a domain"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            result = resolver.resolve(domain, "A")
            return len(result) > 0
        except Exception as e:
            logger.debug(f"DNS query failed for {domain}: {e}")
            return False


class RouteStabilitySensor(BaseSensor):
    """Route stability sensor."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.route_history = []
        self.max_history = 10
    
    async def get_data(self) -> Dict[str, Any]:
        """Get route stability"""
        try:
            target = self.config.get("target", "google.com")
            current_route = await self._get_route(target)
            
            if current_route:
                self.route_history.append(current_route)
                if len(self.route_history) > self.max_history:
                    self.route_history.pop(0)
                
                stability = self._calculate_stability()
                
                return {
                    "overall_stability": round(stability, 2),
                    "route_changes": len(self.route_history) - 1,
                    "current_route": current_route,
                    "status": "online",
                    "error": None
                }
            else:
                return {
                    "overall_stability": 0,
                    "route_changes": 0,
                    "current_route": "Unknown",
                    "status": "offline",
                    "error": "Failed to get route"
                }
        except Exception as e:
            self.logger.error(f"Error measuring route stability: {e}")
            return {
                "overall_stability": 0,
                "route_changes": 0,
                "current_route": "Error",
                "status": "offline",
                "error": str(e)
            }
    
    async def _get_route(self, target: str) -> Optional[List[str]]:
        """Get route to target using traceroute"""
        try:
            process = await asyncio.create_subprocess_exec(
                "traceroute", "-n", "-m", "10", target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                route = []
                for line in stdout.decode('utf-8').split('\n'):
                    if 'traceroute' not in line and line.strip():
                        parts = line.split()
                        if len(parts) >= 3 and parts[1] != '*':
                            route.append(parts[1])
                return route
            return None
        except Exception as e:
            logger.debug(f"Traceroute failed for {target}: {e}")
            return None
    
    def _calculate_stability(self) -> float:
        """Calculate route stability based on history"""
        if len(self.route_history) < 2:
            return 100.0
        
        # Compare current route with previous routes
        current_route = self.route_history[-1]
        matches = 0
        total_comparisons = 0
        
        for i in range(len(self.route_history) - 1):
            previous_route = self.route_history[i]
            total_comparisons += 1
            
            # Compare routes (simplified - just check if they're the same)
            if current_route == previous_route:
                matches += 1
        
        if total_comparisons == 0:
            return 100.0
        
        stability = (matches / total_comparisons) * 100
        return stability
