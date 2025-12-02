"""System metrics tools for CPU and memory utilization.

This module provides tools for real-time monitoring of CPU and memory
utilization on the Unraid system.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_metrics_tools(mcp: FastMCP) -> None:
    """Register all metrics tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def get_system_metrics() -> dict[str, Any]:
        """Retrieves real-time CPU and memory utilization metrics.

        Returns:
            Dict containing CPU and memory utilization data including:
            - CPU total percentage and per-core breakdown
            - Memory usage (total, used, free, available) with percentages
            - Swap usage with percentages
        """
        query = """
        query GetSystemMetrics {
          metrics {
            cpu {
              percentTotal
              cpus {
                percentTotal
                percentUser
                percentSystem
                percentIdle
                percentIrq
              }
            }
            memory {
              total
              used
              free
              available
              active
              buffcache
              percentTotal
              swapTotal
              swapUsed
              swapFree
              percentSwapTotal
            }
          }
        }
        """
        try:
            logger.info("Executing get_system_metrics tool")
            response_data = await make_graphql_request(query)
            metrics = response_data.get("metrics", {})

            if not metrics:
                raise ToolError("No metrics data returned from Unraid API")

            # Format the response for better readability
            result: dict[str, Any] = {}

            if metrics.get("cpu"):
                cpu = metrics["cpu"]
                result["cpu"] = {
                    "total_percent": cpu.get("percentTotal"),
                    "cores": cpu.get("cpus", []),
                }

            if metrics.get("memory"):
                mem = metrics["memory"]
                result["memory"] = {
                    "total_bytes": mem.get("total"),
                    "used_bytes": mem.get("used"),
                    "free_bytes": mem.get("free"),
                    "available_bytes": mem.get("available"),
                    "active_bytes": mem.get("active"),
                    "buffcache_bytes": mem.get("buffcache"),
                    "percent_used": mem.get("percentTotal"),
                    "swap": {
                        "total_bytes": mem.get("swapTotal"),
                        "used_bytes": mem.get("swapUsed"),
                        "free_bytes": mem.get("swapFree"),
                        "percent_used": mem.get("percentSwapTotal"),
                    },
                }

            return result

        except Exception as e:
            logger.error(f"Error in get_system_metrics: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve system metrics: {str(e)}") from e

    @mcp.tool()
    async def get_cpu_utilization() -> dict[str, Any]:
        """Retrieves detailed CPU utilization metrics including per-core breakdown.

        Returns:
            Dict containing CPU utilization data:
            - total_percent: Overall CPU usage percentage
            - cores: List of per-core metrics including user, system, idle, and IRQ percentages
        """
        query = """
        query GetCpuUtilization {
          metrics {
            cpu {
              percentTotal
              cpus {
                percentTotal
                percentUser
                percentSystem
                percentIdle
                percentIrq
              }
            }
          }
        }
        """
        try:
            logger.info("Executing get_cpu_utilization tool")
            response_data = await make_graphql_request(query)

            if response_data.get("metrics") and response_data["metrics"].get("cpu"):
                cpu = response_data["metrics"]["cpu"]
                return {
                    "total_percent": cpu.get("percentTotal"),
                    "core_count": len(cpu.get("cpus", [])),
                    "cores": cpu.get("cpus", []),
                }

            raise ToolError("No CPU metrics returned from Unraid API")

        except Exception as e:
            logger.error(f"Error in get_cpu_utilization: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve CPU utilization: {str(e)}") from e

    @mcp.tool()
    async def get_memory_utilization() -> dict[str, Any]:
        """Retrieves detailed memory and swap utilization metrics.

        Returns:
            Dict containing memory utilization data:
            - Memory: total, used, free, available, active, buffcache (in bytes)
            - Swap: total, used, free (in bytes)
            - Percentage usage for both memory and swap
        """
        query = """
        query GetMemoryUtilization {
          metrics {
            memory {
              total
              used
              free
              available
              active
              buffcache
              percentTotal
              swapTotal
              swapUsed
              swapFree
              percentSwapTotal
            }
          }
        }
        """
        try:
            logger.info("Executing get_memory_utilization tool")
            response_data = await make_graphql_request(query)

            if response_data.get("metrics") and response_data["metrics"].get("memory"):
                mem = response_data["metrics"]["memory"]

                # Helper to format bytes
                def format_bytes(bytes_value: int | None) -> str:
                    if bytes_value is None:
                        return "N/A"
                    value = float(int(bytes_value))
                    for unit in ["B", "KB", "MB", "GB", "TB"]:
                        if value < 1024.0:
                            return f"{value:.2f} {unit}"
                        value /= 1024.0
                    return f"{value:.2f} PB"

                return {
                    "memory": {
                        "total": mem.get("total"),
                        "total_formatted": format_bytes(mem.get("total")),
                        "used": mem.get("used"),
                        "used_formatted": format_bytes(mem.get("used")),
                        "free": mem.get("free"),
                        "free_formatted": format_bytes(mem.get("free")),
                        "available": mem.get("available"),
                        "available_formatted": format_bytes(mem.get("available")),
                        "active": mem.get("active"),
                        "buffcache": mem.get("buffcache"),
                        "percent_used": mem.get("percentTotal"),
                    },
                    "swap": {
                        "total": mem.get("swapTotal"),
                        "total_formatted": format_bytes(mem.get("swapTotal")),
                        "used": mem.get("swapUsed"),
                        "used_formatted": format_bytes(mem.get("swapUsed")),
                        "free": mem.get("swapFree"),
                        "free_formatted": format_bytes(mem.get("swapFree")),
                        "percent_used": mem.get("percentSwapTotal"),
                    },
                }

            raise ToolError("No memory metrics returned from Unraid API")

        except Exception as e:
            logger.error(f"Error in get_memory_utilization: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve memory utilization: {str(e)}") from e

    logger.info("Metrics tools registered successfully")
