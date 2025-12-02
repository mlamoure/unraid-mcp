"""UPS monitoring and management tools.

This module provides tools for monitoring UPS devices and managing
UPS configuration on the Unraid system.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_ups_tools(mcp: FastMCP) -> None:
    """Register all UPS tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def list_ups_devices() -> list[dict[str, Any]]:
        """Lists all UPS devices connected to the Unraid system.

        Returns:
            List of UPS device information including:
            - id, name, model, status
            - Battery: charge level, estimated runtime, health
            - Power: input/output voltage, load percentage
        """
        query = """
        query ListUpsDevices {
          upsDevices {
            id
            name
            model
            status
            battery {
              chargeLevel
              estimatedRuntime
              health
            }
            power {
              inputVoltage
              outputVoltage
              loadPercentage
            }
          }
        }
        """
        try:
            logger.info("Executing list_ups_devices tool")
            response_data = await make_graphql_request(query)
            devices = response_data.get("upsDevices", [])
            return list(devices) if isinstance(devices, list) else []
        except Exception as e:
            logger.error(f"Error in list_ups_devices: {e}", exc_info=True)
            raise ToolError(f"Failed to list UPS devices: {str(e)}") from e

    @mcp.tool()
    async def get_ups_device(ups_id: str) -> dict[str, Any]:
        """Retrieves detailed information for a specific UPS device.

        Args:
            ups_id: The ID of the UPS device to retrieve

        Returns:
            Dict containing detailed UPS information including battery and power status
        """
        query = """
        query GetUpsDevice($id: String!) {
          upsDeviceById(id: $id) {
            id
            name
            model
            status
            battery {
              chargeLevel
              estimatedRuntime
              health
            }
            power {
              inputVoltage
              outputVoltage
              loadPercentage
            }
          }
        }
        """
        variables = {"id": ups_id}
        try:
            logger.info(f"Executing get_ups_device for ID: {ups_id}")
            response_data = await make_graphql_request(query, variables)
            device = response_data.get("upsDeviceById")

            if not device:
                raise ToolError(f"UPS device '{ups_id}' not found")

            # Enhance with formatted runtime
            if device.get("battery") and device["battery"].get("estimatedRuntime"):
                runtime_seconds = device["battery"]["estimatedRuntime"]
                hours = runtime_seconds // 3600
                minutes = (runtime_seconds % 3600) // 60
                device["battery"]["estimatedRuntimeFormatted"] = (
                    f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                )

            return dict(device)

        except Exception as e:
            logger.error(f"Error in get_ups_device: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve UPS device details: {str(e)}") from e

    @mcp.tool()
    async def get_ups_configuration() -> dict[str, Any]:
        """Retrieves the current UPS daemon configuration.

        Returns:
            Dict containing UPS configuration settings including:
            - service: Enable/disable state
            - upsCable: Cable type (usb, smart, ether, custom)
            - upsType: Communication type
            - device: Device path or network address
            - batteryLevel: Shutdown threshold percentage
            - minutes: Runtime shutdown threshold
            - timeout: Time on battery before shutdown
        """
        query = """
        query GetUpsConfiguration {
          upsConfiguration {
            service
            upsCable
            customUpsCable
            upsType
            device
            overrideUpsCapacity
            batteryLevel
            minutes
            timeout
            killUps
          }
        }
        """
        try:
            logger.info("Executing get_ups_configuration tool")
            response_data = await make_graphql_request(query)
            config = response_data.get("upsConfiguration", {})
            return dict(config) if isinstance(config, dict) else {}
        except Exception as e:
            logger.error(f"Error in get_ups_configuration: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve UPS configuration: {str(e)}") from e

    @mcp.tool()
    async def configure_ups(
        service: str | None = None,
        ups_cable: str | None = None,
        custom_ups_cable: str | None = None,
        ups_type: str | None = None,
        device: str | None = None,
        override_ups_capacity: int | None = None,
        battery_level: int | None = None,
        minutes: int | None = None,
        timeout: int | None = None,
        kill_ups: str | None = None,
    ) -> dict[str, Any]:
        """Updates UPS daemon configuration.

        Args:
            service: Enable or disable the UPS service (ENABLE, DISABLE)
            ups_cable: Cable type (USB, SIMPLE, SMART, ETHER, CUSTOM)
            custom_ups_cable: Custom cable configuration (only when ups_cable is CUSTOM)
            ups_type: UPS communication protocol (USB, NET, SNMP, etc.)
            device: Device path or network address (e.g., '/dev/ttyUSB0', '192.168.1.100:3551')
            override_ups_capacity: Override capacity in watts
            battery_level: Battery percentage for shutdown (0-100)
            minutes: Runtime minutes threshold for shutdown
            timeout: Seconds on battery before shutdown (0 to disable)
            kill_ups: Kill UPS power after shutdown (ENABLED, DISABLED, BIOS_SETTING)

        Returns:
            Dict containing success status and applied configuration
        """
        # Build config input from provided parameters
        config_input: dict[str, Any] = {}

        if service is not None:
            config_input["service"] = service.upper()
        if ups_cable is not None:
            config_input["upsCable"] = ups_cable.upper()
        if custom_ups_cable is not None:
            config_input["customUpsCable"] = custom_ups_cable
        if ups_type is not None:
            config_input["upsType"] = ups_type.upper()
        if device is not None:
            config_input["device"] = device
        if override_ups_capacity is not None:
            config_input["overrideUpsCapacity"] = override_ups_capacity
        if battery_level is not None:
            if not 0 <= battery_level <= 100:
                raise ToolError("battery_level must be between 0 and 100")
            config_input["batteryLevel"] = battery_level
        if minutes is not None:
            config_input["minutes"] = minutes
        if timeout is not None:
            config_input["timeout"] = timeout
        if kill_ups is not None:
            config_input["killUps"] = kill_ups.upper()

        if not config_input:
            raise ToolError("At least one configuration parameter must be provided")

        mutation = """
        mutation ConfigureUps($config: UPSConfigInput!) {
          configureUps(config: $config)
        }
        """
        variables = {"config": config_input}

        try:
            logger.info(f"Executing configure_ups with config: {config_input}")
            response_data = await make_graphql_request(mutation, variables)

            success = response_data.get("configureUps", False)
            return {
                "success": success,
                "applied_config": config_input,
                "message": (
                    "UPS configuration updated successfully"
                    if success
                    else "Failed to update UPS configuration"
                ),
            }

        except Exception as e:
            logger.error(f"Error in configure_ups: {e}", exc_info=True)
            raise ToolError(f"Failed to configure UPS: {str(e)}") from e

    logger.info("UPS tools registered successfully")
