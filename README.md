# Unraid MCP Server

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://ghcr.io/mlamoure/unraid-mcp)

A Model Context Protocol (MCP) server providing 55+ tools to interact with an Unraid server's GraphQL API.

## Prerequisites

### Unraid API Key
You need an API key from your Unraid server. To create one:

1. Open your Unraid web interface
2. Navigate to **Settings → Management Access → API Keys**
3. Click **Add API Key** and configure permissions
4. Copy the generated key for use in the configuration below

For detailed instructions, see the [official Unraid API documentation](https://docs.unraid.net/API/how-to-use-the-api/).

## Installation

### Docker Run
```bash
docker run -d \
  --name unraid-mcp \
  --restart unless-stopped \
  -p 6970:6970 \
  -e UNRAID_API_URL="https://your-unraid-server/graphql" \
  -e UNRAID_API_KEY="your_api_key" \
  ghcr.io/mlamoure/unraid-mcp:latest
```

### Docker Compose
```yaml
services:
  unraid-mcp:
    image: ghcr.io/mlamoure/unraid-mcp:latest
    restart: unless-stopped
    ports:
      - "6970:6970"
    environment:
      UNRAID_API_URL: "https://your-unraid-server/graphql"
      UNRAID_API_KEY: "your_api_key"
```

## MCP Client Configuration

Once the server is running, configure your MCP client to connect to `http://localhost:6970/mcp`.

### Claude Desktop
Add to your Claude Desktop configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "unraid": {
      "url": "http://localhost:6970/mcp"
    }
  }
}
```

### Claude Code
Add to your Claude Code MCP settings:
```json
{
  "mcpServers": {
    "unraid": {
      "type": "url",
      "url": "http://localhost:6970/mcp"
    }
  }
}
```

## Development

```bash
git clone https://github.com/mlamoure/unraid-mcp && cd unraid-mcp
uv sync
cp .env.example .env  # Edit with your settings
./dev.sh
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `UNRAID_API_URL` | GraphQL endpoint (required) | - |
| `UNRAID_API_KEY` | API key (required) | - |
| `UNRAID_MCP_TRANSPORT` | `streamable-http`, `sse`, `stdio` | `streamable-http` |
| `UNRAID_MCP_HOST` | Server host | `0.0.0.0` |
| `UNRAID_MCP_PORT` | Server port | `6970` |
| `UNRAID_MCP_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `UNRAID_VERIFY_SSL` | SSL verification | `true` |

## Available Tools

### System Information
| Tool | Description |
|------|-------------|
| `get_system_info` | OS, CPU, memory, and hardware information |
| `get_array_status` | Array state, capacity, disk health, and parity status |
| `get_unraid_variables` | System variables and settings |
| `get_network_config` | Network configuration and URLs |
| `get_registration_info` | Unraid registration details |
| `get_connect_settings` | Unraid Connect configuration |
| `get_device_info` | GPU, PCI, USB, and network devices |
| `list_plugins` | Installed plugins |
| `get_flash_info` | Flash drive details |

### Array Management
| Tool | Description |
|------|-------------|
| `manage_array_state` | Start or stop the array |
| `mount_array_disk` | Mount a disk |
| `unmount_array_disk` | Unmount a disk |
| `clear_disk_statistics` | Clear disk I/O statistics |

### Docker
| Tool | Description |
|------|-------------|
| `list_docker_containers` | List all containers |
| `manage_docker_container` | Start/stop containers |
| `get_docker_container_details` | Container details |
| `list_docker_networks` | List networks with IPAM config |
| `get_container_update_statuses` | Check for container updates |

### Virtual Machines
| Tool | Description |
|------|-------------|
| `list_vms` | List VMs and states |
| `manage_vm` | Start/stop/pause/resume/reboot VMs |
| `get_vm_details` | VM details |

### Storage
| Tool | Description |
|------|-------------|
| `get_shares_info` | User shares information |
| `list_physical_disks` | Physical disk list |
| `get_disk_details` | SMART data and partitions |

### System Metrics
| Tool | Description |
|------|-------------|
| `get_system_metrics` | CPU and memory utilization |
| `get_cpu_utilization` | Per-core CPU metrics |
| `get_memory_utilization` | Memory and swap usage |

### UPS Management
| Tool | Description |
|------|-------------|
| `list_ups_devices` | List UPS devices |
| `get_ups_device` | UPS details |
| `get_ups_configuration` | UPS daemon configuration |
| `configure_ups` | Update UPS settings |

### Parity Operations
| Tool | Description |
|------|-------------|
| `get_parity_history` | Historical parity results |
| `get_parity_status` | Current parity status |
| `start_parity_check` | Start parity check/sync |
| `pause_parity_check` | Pause parity check |
| `resume_parity_check` | Resume parity check |
| `cancel_parity_check` | Cancel parity check |

### Notifications
| Tool | Description |
|------|-------------|
| `get_notifications_overview` | Notification counts |
| `list_notifications` | List notifications |
| `create_notification` | Create notification |
| `archive_notification` | Archive notification |
| `archive_notifications` | Archive multiple |
| `archive_all_notifications` | Archive all |
| `delete_notification` | Delete notification |
| `delete_archived_notifications` | Delete all archived |

### Monitoring
| Tool | Description |
|------|-------------|
| `health_check` | System health assessment |
| `list_available_log_files` | Available log files |
| `get_logs` | Log file content |

### Cloud Storage (RClone)
| Tool | Description |
|------|-------------|
| `list_rclone_remotes` | List configured remotes |
| `get_rclone_config_form` | Configuration schemas |
| `create_rclone_remote` | Create remote |
| `delete_rclone_remote` | Delete remote |
| `initiate_flash_backup` | Backup flash to remote |

### Subscriptions
| Tool | Description |
|------|-------------|
| `test_subscription_query` | Test GraphQL subscriptions |
| `diagnose_subscriptions` | Subscription diagnostics |

## Acknowledgments

This project is a fork of [unraid-mcp](https://github.com/jmagar/unraid-mcp) by **[jmagar](https://github.com/jmagar)**.

### Fork Improvements
- **29 new tools**: System metrics, UPS management, parity operations, array management, Docker networks, notifications, flash backup
- **Schema compatibility**: Updated GraphQL queries for Unraid 7.x API
- **Infrastructure**: Python 3.12+, FastMCP 2.13.2, GitHub Actions CI/CD, pre-built Docker images on GHCR
- **Code quality**: Black formatting, ruff linting, mypy type checking

## License

MIT License - see [LICENSE](LICENSE)
