"""Parity check management tools.

This module provides tools for monitoring and managing parity checks
on the Unraid array including history, status, and control operations.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_parity_tools(mcp: FastMCP) -> None:
    """Register all parity check tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def get_parity_history() -> list[dict[str, Any]]:
        """Retrieves historical parity check results.

        Returns:
            List of parity check records including:
            - date: When the check was performed
            - duration: How long it took (in seconds)
            - speed: Check speed in MB/s
            - status: Result status (COMPLETED, CANCELLED, FAILED, etc.)
            - errors: Number of errors found
        """
        query = """
        query GetParityHistory {
          parityHistory {
            date
            duration
            speed
            status
            errors
            progress
            correcting
            paused
            running
          }
        }
        """
        try:
            logger.info("Executing get_parity_history tool")
            response_data = await make_graphql_request(query)
            history = response_data.get("parityHistory", [])

            # Enhance with formatted duration
            result = []
            for check in history:
                check_dict = dict(check)
                if check_dict.get("duration"):
                    duration_seconds = check_dict["duration"]
                    # Handle potential None or invalid values
                    if isinstance(duration_seconds, (int, float)) and duration_seconds >= 0:
                        hours = int(duration_seconds) // 3600
                        minutes = (int(duration_seconds) % 3600) // 60
                        check_dict["durationFormatted"] = f"{hours}h {minutes}m"
                result.append(check_dict)

            return result

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error in get_parity_history: {e}", exc_info=True)

            # Handle NaN values from backend which GraphQL cannot serialize as Int
            if "NaN" in error_str or "non-integer" in error_str.lower():
                logger.warning("Parity history contains invalid numeric values (NaN)")
                return [
                    {
                        "error": "Parity history data contains invalid values",
                        "message": "The Unraid API returned NaN (Not a Number) for some fields. "
                        "This is typically a backend issue. Use get_parity_status for current status.",
                        "suggestion": "Check parity history directly in the Unraid web UI",
                    }
                ]

            raise ToolError(f"Failed to retrieve parity history: {str(e)}") from e

    @mcp.tool()
    async def get_parity_status() -> dict[str, Any]:
        """Retrieves the current parity check status.

        Returns:
            Dict containing current parity check status:
            - running: Whether a check is currently running
            - paused: Whether a running check is paused
            - correcting: Whether corrections are being written
            - progress: Completion percentage (0-100)
            - speed: Current speed in MB/s
            - errors: Number of errors found so far
            - date: When the current/last check started
        """
        query = """
        query GetParityStatus {
          array {
            parityCheckStatus {
              date
              duration
              speed
              status
              errors
              progress
              correcting
              paused
              running
            }
          }
        }
        """
        try:
            logger.info("Executing get_parity_status tool")
            response_data = await make_graphql_request(query)

            if response_data.get("array") and response_data["array"].get("parityCheckStatus"):
                status = response_data["array"]["parityCheckStatus"]
                return dict(status)

            return {
                "running": False,
                "paused": False,
                "status": "NEVER_RUN",
                "message": "No parity check status available",
            }

        except Exception as e:
            logger.error(f"Error in get_parity_status: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve parity status: {str(e)}") from e

    @mcp.tool()
    async def start_parity_check(correct: bool = False) -> dict[str, Any]:
        """Starts a parity check on the array.

        Args:
            correct: If True, write corrections to parity (parity sync/correct).
                    If False, read-only check (parity check). Default: False.

        Returns:
            Dict containing operation result
        """
        mutation = """
        mutation StartParityCheck($correct: Boolean!) {
          parityCheck {
            start(correct: $correct)
          }
        }
        """
        variables = {"correct": correct}

        try:
            check_type = "parity sync/correct" if correct else "parity check"
            logger.info(f"Executing start_parity_check: correct={correct}")

            response_data = await make_graphql_request(mutation, variables)

            if response_data.get("parityCheck") and response_data["parityCheck"].get("start"):
                return {
                    "success": True,
                    "message": f"Started {check_type}",
                    "correcting": correct,
                    "response": response_data["parityCheck"]["start"],
                }

            raise ToolError(f"Failed to start {check_type}")

        except Exception as e:
            logger.error(f"Error in start_parity_check: {e}", exc_info=True)
            raise ToolError(f"Failed to start parity check: {str(e)}") from e

    @mcp.tool()
    async def pause_parity_check() -> dict[str, Any]:
        """Pauses a running parity check.

        Returns:
            Dict containing operation result
        """
        mutation = """
        mutation PauseParityCheck {
          parityCheck {
            pause
          }
        }
        """

        try:
            logger.info("Executing pause_parity_check")
            response_data = await make_graphql_request(mutation)

            if response_data.get("parityCheck") and response_data["parityCheck"].get("pause"):
                return {
                    "success": True,
                    "message": "Parity check paused",
                    "response": response_data["parityCheck"]["pause"],
                }

            raise ToolError("Failed to pause parity check")

        except Exception as e:
            logger.error(f"Error in pause_parity_check: {e}", exc_info=True)
            raise ToolError(f"Failed to pause parity check: {str(e)}") from e

    @mcp.tool()
    async def resume_parity_check() -> dict[str, Any]:
        """Resumes a paused parity check.

        Returns:
            Dict containing operation result
        """
        mutation = """
        mutation ResumeParityCheck {
          parityCheck {
            resume
          }
        }
        """

        try:
            logger.info("Executing resume_parity_check")
            response_data = await make_graphql_request(mutation)

            if response_data.get("parityCheck") and response_data["parityCheck"].get("resume"):
                return {
                    "success": True,
                    "message": "Parity check resumed",
                    "response": response_data["parityCheck"]["resume"],
                }

            raise ToolError("Failed to resume parity check")

        except Exception as e:
            logger.error(f"Error in resume_parity_check: {e}", exc_info=True)
            raise ToolError(f"Failed to resume parity check: {str(e)}") from e

    @mcp.tool()
    async def cancel_parity_check() -> dict[str, Any]:
        """Cancels a running or paused parity check.

        Returns:
            Dict containing operation result
        """
        mutation = """
        mutation CancelParityCheck {
          parityCheck {
            cancel
          }
        }
        """

        try:
            logger.info("Executing cancel_parity_check")
            response_data = await make_graphql_request(mutation)

            if response_data.get("parityCheck") and response_data["parityCheck"].get("cancel"):
                return {
                    "success": True,
                    "message": "Parity check cancelled",
                    "response": response_data["parityCheck"]["cancel"],
                }

            raise ToolError("Failed to cancel parity check")

        except Exception as e:
            logger.error(f"Error in cancel_parity_check: {e}", exc_info=True)
            raise ToolError(f"Failed to cancel parity check: {str(e)}") from e

    logger.info("Parity tools registered successfully")
