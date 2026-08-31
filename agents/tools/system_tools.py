#!/usr/bin/env python3
"""System Monitoring and Management Tools.

Tools for system information, process management, and monitoring.
"""

import logging
import platform
from typing import Any

import psutil
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SystemConfig(BaseModel):
    """Configuration for system tools."""

    interval: float = Field(default=1.0, gt=0, description="Monitoring interval in seconds")
    cpu_percent_interval: float = Field(default=0.1, description="CPU sampling interval")


class SystemInfoTool:
    """Get system information."""

    name: str = "system_info"
    description: str = "Get system information (OS, CPU, memory, disk)"

    def __init__(self, config: SystemConfig | None = None) -> None:
        """Initialize system info tool."""
        self.config = config or SystemConfig()

    def execute(self, info_type: str = "all", **kwargs: Any) -> dict[str, Any]:
        """Get system information.

        Args:
            info_type: Type of info to get (all, os, cpu, memory, disk, network)
            **kwargs: Additional parameters

        Returns:
            System information
        """
        try:
            result = {"status": "success"}

            if info_type in ["all", "os"]:
                result["os"] = {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version(),
                }

            if info_type in ["all", "cpu"]:
                result["cpu"] = {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True),
                    "cpu_percent": psutil.cpu_percent(interval=self.config.cpu_percent_interval),
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                }

            if info_type in ["all", "memory"]:
                mem = psutil.virtual_memory()
                result["memory"] = {
                    "total": mem.total,
                    "available": mem.available,
                    "used": mem.used,
                    "percent": mem.percent,
                }

            if info_type in ["all", "disk"]:
                disk = psutil.disk_usage("/")
                result["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                }

            if info_type in ["all", "network"]:
                net_io = psutil.net_io_counters()
                result["network"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                }

            return result

        except Exception as e:
            logger.error(f"System info retrieval failed: {e}")
            return {"status": "error", "error": str(e)}


class ProcessMonitorTool:
    """Monitor and manage processes."""

    name: str = "process_monitor"
    description: str = "Monitor running processes and their resource usage"

    def __init__(self, config: SystemConfig | None = None) -> None:
        """Initialize process monitor tool."""
        self.config = config or SystemConfig()

    def execute(
        self, action: str = "list", pid: int | None = None, name: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute process operation.

        Args:
            action: Action to perform (list, info, kill)
            pid: Process ID for specific operations
            name: Process name filter
            **kwargs: Additional parameters

        Returns:
            Process information or operation result
        """
        try:
            if action == "list":
                processes = []
                for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                    try:
                        info = proc.info
                        if name is None or name.lower() in info["name"].lower():
                            processes.append(
                                {
                                    "pid": info["pid"],
                                    "name": info["name"],
                                    "cpu_percent": info["cpu_percent"],
                                    "memory_percent": info["memory_percent"],
                                }
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Sort by CPU usage
                processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

                return {
                    "status": "success",
                    "action": "list",
                    "processes": processes[:50],  # Limit to top 50
                    "count": len(processes),
                }

            elif action == "info":
                if pid is None:
                    return {"status": "error", "error": "PID required for info action"}

                proc = psutil.Process(pid)
                return {
                    "status": "success",
                    "action": "info",
                    "process": {
                        "pid": proc.pid,
                        "name": proc.name(),
                        "status": proc.status(),
                        "cpu_percent": proc.cpu_percent(interval=0.1),
                        "memory_percent": proc.memory_percent(),
                        "num_threads": proc.num_threads(),
                        "create_time": proc.create_time(),
                    },
                }

            elif action == "kill":
                if pid is None:
                    return {"status": "error", "error": "PID required for kill action"}

                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc.kill()

                return {"status": "success", "action": "kill", "pid": pid, "name": proc_name}

            else:
                return {"status": "error", "error": f"Unknown action: {action}"}

        except psutil.NoSuchProcess:
            return {"status": "error", "error": f"Process not found: {pid}"}
        except Exception as e:
            logger.error(f"Process operation failed: {e}")
            return {"status": "error", "error": str(e), "action": action}


class ResourceMonitorTool:
    """Monitor system resource usage over time."""

    name: str = "resource_monitor"
    description: str = "Monitor CPU, memory, disk, and network usage"

    def __init__(self, config: SystemConfig | None = None) -> None:
        """Initialize resource monitor tool."""
        self.config = config or SystemConfig()

    def execute(
        self, duration: int = 5, interval: float | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Monitor resources over time.

        Args:
            duration: Monitoring duration in seconds
            interval: Sampling interval (uses config default if not provided)
            **kwargs: Additional parameters

        Returns:
            Resource usage metrics over time
        """
        import time

        try:
            interval = interval or self.config.interval
            samples = []
            start_time = time.time()

            while time.time() - start_time < duration:
                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": psutil.disk_io_counters()._asdict()
                    if psutil.disk_io_counters()
                    else None,
                    "net_io": psutil.net_io_counters()._asdict(),
                }
                samples.append(sample)
                time.sleep(interval)

            # Calculate averages
            avg_cpu = sum(s["cpu_percent"] for s in samples) / len(samples)
            avg_memory = sum(s["memory_percent"] for s in samples) / len(samples)

            return {
                "status": "success",
                "duration": duration,
                "samples": samples,
                "averages": {
                    "cpu_percent": round(avg_cpu, 2),
                    "memory_percent": round(avg_memory, 2),
                },
                "sample_count": len(samples),
            }

        except Exception as e:
            logger.error(f"Resource monitoring failed: {e}")
            return {"status": "error", "error": str(e)}


class HealthCheckTool:
    """Perform system health checks."""

    name: str = "health_check"
    description: str = "Check system health and resource availability"

    def __init__(self, config: SystemConfig | None = None) -> None:
        """Initialize health check tool."""
        self.config = config or SystemConfig()

    def execute(self, thresholds: dict[str, float] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform health check.

        Args:
            thresholds: Custom thresholds for health checks
            **kwargs: Additional parameters

        Returns:
            Health check results
        """
        try:
            default_thresholds = {"cpu_percent": 90.0, "memory_percent": 90.0, "disk_percent": 90.0}
            thresholds = thresholds or default_thresholds

            checks = {}
            healthy = True

            # CPU check
            cpu_percent = psutil.cpu_percent(interval=0.5)
            checks["cpu"] = {
                "value": cpu_percent,
                "threshold": thresholds["cpu_percent"],
                "healthy": cpu_percent < thresholds["cpu_percent"],
            }
            if not checks["cpu"]["healthy"]:
                healthy = False

            # Memory check
            memory_percent = psutil.virtual_memory().percent
            checks["memory"] = {
                "value": memory_percent,
                "threshold": thresholds["memory_percent"],
                "healthy": memory_percent < thresholds["memory_percent"],
            }
            if not checks["memory"]["healthy"]:
                healthy = False

            # Disk check
            disk_percent = psutil.disk_usage("/").percent
            checks["disk"] = {
                "value": disk_percent,
                "threshold": thresholds["disk_percent"],
                "healthy": disk_percent < thresholds["disk_percent"],
            }
            if not checks["disk"]["healthy"]:
                healthy = False

            return {"status": "success", "healthy": healthy, "checks": checks}

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e), "healthy": False}


def system_info_tool(config: dict[str, Any] | None = None) -> SystemInfoTool:
    """Factory function for system info tool."""
    cfg = SystemConfig(**config) if config else SystemConfig()
    return SystemInfoTool(cfg)


def process_monitor_tool(config: dict[str, Any] | None = None) -> ProcessMonitorTool:
    """Factory function for process monitor tool."""
    cfg = SystemConfig(**config) if config else SystemConfig()
    return ProcessMonitorTool(cfg)


def resource_monitor_tool(config: dict[str, Any] | None = None) -> ResourceMonitorTool:
    """Factory function for resource monitor tool."""
    cfg = SystemConfig(**config) if config else SystemConfig()
    return ResourceMonitorTool(cfg)


def health_check_tool(config: dict[str, Any] | None = None) -> HealthCheckTool:
    """Factory function for health check tool."""
    cfg = SystemConfig(**config) if config else SystemConfig()
    return HealthCheckTool(cfg)


__all__ = [
    "HealthCheckTool",
    "ProcessMonitorTool",
    "ResourceMonitorTool",
    "SystemConfig",
    "SystemInfoTool",
    "health_check_tool",
    "process_monitor_tool",
    "resource_monitor_tool",
    "system_info_tool",
]
