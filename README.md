# 🚀 Unraid MCP Server

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://ghcr.io/mlamoure/unraid-mcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A powerful MCP (Model Context Protocol) server that provides comprehensive tools to interact with an Unraid server's GraphQL API.**

## ✨ Features

- 🔧 **55+ Tools**: Complete Unraid management through MCP protocol
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible codebase
- ⚡ **High Performance**: Async/concurrent operations with optimized timeouts
- 🔄 **Real-time Data**: WebSocket subscriptions for live log streaming
- 📊 **Health Monitoring**: Comprehensive system diagnostics and status
- 🔋 **UPS Management**: Monitor and configure UPS devices
- 🛡️ **Parity Operations**: Full parity check lifecycle control
- 📈 **System Metrics**: Real-time CPU and memory utilization
- 🐳 **Docker Ready**: Full containerization support with Docker Compose
- 🔒 **Secure**: Proper SSL/TLS configuration and API key management
- 📝 **Rich Logging**: Structured logging with rotation and multiple levels

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Available Tools & Resources](#-available-tools--resources)
- [Development](#-development)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Docker (recommended) OR Python 3.12+ with [uv](https://github.com/astral-sh/uv)
- Unraid server with GraphQL API enabled

### Using Pre-built Image (Recommended)

**Docker Run:**
```bash
docker run -d \
  --name unraid-mcp \
  --restart unless-stopped \
  -p 6970:6970 \
  -e UNRAID_API_URL="https://your-unraid-server/graphql" \
  -e UNRAID_API_KEY="your_api_key" \
  ghcr.io/mlamoure/unraid-mcp:latest
```

**Docker Compose:**
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

### Building from Source (Development)
```bash
# Clone repository
git clone https://github.com/mlamoure/unraid-mcp
cd unraid-mcp

# Option 1: Docker build
docker build -t unraid-mcp .
docker run -d -p 6970:6970 -e UNRAID_API_URL="..." -e UNRAID_API_KEY="..." unraid-mcp

# Option 2: Local development
uv sync
./dev.sh
```

---

## 📦 Installation

### 🐳 Docker Deployment (Recommended)

The easiest way to run the Unraid MCP Server is with the pre-built Docker image:

```bash
# Using Docker Run
docker run -d \
  --name unraid-mcp \
  --restart unless-stopped \
  -p 6970:6970 \
  -e UNRAID_API_URL="https://your-unraid-server/graphql" \
  -e UNRAID_API_KEY="your_api_key_here" \
  ghcr.io/mlamoure/unraid-mcp:latest

# View logs
docker logs -f unraid-mcp
```

#### Using Docker Compose

Create a `docker-compose.yml`:
```yaml
services:
  unraid-mcp:
    image: ghcr.io/mlamoure/unraid-mcp:latest
    restart: unless-stopped
    ports:
      - "6970:6970"
    environment:
      UNRAID_API_URL: "https://your-unraid-server/graphql"
      UNRAID_API_KEY: "your_api_key_here"
      UNRAID_MCP_LOG_LEVEL: "INFO"
```

Then run:
```bash
docker compose up -d
docker compose logs -f unraid-mcp
```

### 🔧 Development Installation

For development and testing:

```bash
# Clone repository
git clone https://github.com/mlamoure/unraid-mcp
cd unraid-mcp

# Install dependencies with uv
uv sync

# Install development dependencies
uv sync --group dev

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run development server
./dev.sh
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in the project root:

```bash
# Core API Configuration (Required)
UNRAID_API_URL=https://your-unraid-server-url/graphql
UNRAID_API_KEY=your_unraid_api_key

# MCP Server Settings
UNRAID_MCP_TRANSPORT=streamable-http  # streamable-http (recommended), sse (deprecated), stdio
UNRAID_MCP_HOST=0.0.0.0
UNRAID_MCP_PORT=6970

# Logging Configuration
UNRAID_MCP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
UNRAID_MCP_LOG_FILE=unraid-mcp.log

# SSL/TLS Configuration  
UNRAID_VERIFY_SSL=true  # true, false, or path to CA bundle

# Optional: Log Stream Configuration
# UNRAID_AUTOSTART_LOG_PATH=/var/log/syslog  # Path for log streaming resource
```

### Transport Options

| Transport | Description | Use Case |
|-----------|-------------|----------|
| `streamable-http` | HTTP-based (recommended) | Most compatible, best performance |
| `sse` | Server-Sent Events (deprecated) | Legacy support only |
| `stdio` | Standard I/O | Direct integration scenarios |

---

## 🛠️ Available Tools & Resources

### System Information & Status
- `get_system_info()` - Comprehensive system, OS, CPU, memory, hardware info
- `get_array_status()` - Storage array status, capacity, disk details, and parity check status
- `get_unraid_variables()` - System variables and settings
- `get_network_config()` - Network configuration and access URLs
- `get_registration_info()` - Unraid registration details
- `get_connect_settings()` - Unraid Connect configuration
- `get_device_info()` - Device identification (GUID, model, timezone)
- `list_plugins()` - Installed plugins with metadata
- `get_flash_info()` - Flash drive details (GUID, vendor, product)

### Array Management
- `manage_array_state(action)` - Start/stop array operations (START, STOP)
- `mount_array_disk(disk_id)` - Mount a specific array disk
- `unmount_array_disk(disk_id)` - Unmount a specific array disk
- `clear_disk_statistics()` - Clear disk I/O statistics

### Docker Container Management
- `list_docker_containers()` - List all containers with update availability status
- `manage_docker_container(id, action)` - Start/stop containers (idempotent)
- `get_docker_container_details(identifier)` - Detailed container information
- `list_docker_networks(skip_cache)` - List Docker networks with IPAM config
- `get_container_update_statuses()` - Check which containers have updates available

### Virtual Machine Management
- `list_vms()` - List all VMs and their states
- `manage_vm(vm_id, action)` - VM lifecycle (start/stop/pause/resume/reboot/reset/forceStop)
- `get_vm_details(identifier)` - Detailed VM information

### Storage & File Systems
- `get_shares_info()` - User shares information
- `list_physical_disks()` - Physical disk discovery
- `get_disk_details(disk_id)` - SMART data, partitions, and detailed disk info

### System Metrics (Real-time)
- `get_system_metrics()` - Combined CPU and memory utilization
- `get_cpu_utilization()` - Detailed CPU metrics with per-core breakdown
- `get_memory_utilization()` - Memory and swap usage with formatted values

### UPS Management
- `list_ups_devices()` - List connected UPS devices with battery and power status
- `get_ups_device(ups_id)` - Detailed UPS information
- `get_ups_configuration()` - Current UPS daemon configuration
- `configure_ups(...)` - Update UPS daemon settings

### Parity Check Operations
- `get_parity_history()` - Historical parity check results
- `get_parity_status()` - Current parity check status
- `start_parity_check(correct)` - Start parity check or parity sync
- `pause_parity_check()` - Pause running parity check
- `resume_parity_check()` - Resume paused parity check
- `cancel_parity_check()` - Cancel running/paused parity check

### Notification Management
- `get_notifications_overview()` - Notification counts by severity
- `list_notifications(type, offset, limit)` - Filtered notification listing
- `create_notification(title, subject, description, importance)` - Create new notification
- `archive_notification(id)` - Archive a single notification
- `archive_notifications(ids)` - Archive multiple notifications
- `archive_all_notifications(importance)` - Archive all notifications
- `delete_notification(id, type)` - Delete a notification
- `delete_archived_notifications()` - Delete all archived notifications

### Monitoring & Diagnostics
- `health_check()` - Comprehensive system health assessment
- `list_available_log_files()` - Available system logs
- `get_logs(path, tail_lines)` - Log file content retrieval

### Cloud Storage (RClone)
- `list_rclone_remotes()` - List configured remotes
- `get_rclone_config_form(provider)` - Configuration schemas
- `create_rclone_remote(name, type, config)` - Create new remote
- `delete_rclone_remote(name)` - Remove existing remote
- `initiate_flash_backup(remote_name, source, dest)` - Backup flash drive to remote

### Real-time Subscriptions & Resources
- `test_subscription_query(query)` - Test GraphQL subscriptions
- `diagnose_subscriptions()` - Subscription system diagnostics

### MCP Resources (Real-time Data)
- `unraid://logs/stream` - Live log streaming from `/var/log/syslog` with WebSocket subscriptions

> **Note**: MCP Resources provide real-time data streams that can be accessed via MCP clients. The log stream resource automatically connects to your Unraid system logs and provides live updates.

---


## 🔧 Development

### Project Structure
```
unraid-mcp/
├── unraid_mcp/               # Main package
│   ├── main.py               # Entry point
│   ├── server.py             # FastMCP server setup
│   ├── config/               # Configuration management
│   │   ├── settings.py       # Environment & settings
│   │   └── logging.py        # Logging setup
│   ├── core/                 # Core infrastructure
│   │   ├── client.py         # GraphQL client
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── types.py          # Shared data types
│   ├── subscriptions/        # Real-time subscriptions
│   │   ├── manager.py        # WebSocket management
│   │   ├── resources.py      # MCP resources
│   │   └── diagnostics.py    # Diagnostic tools
│   └── tools/                # MCP tool categories (55+ tools)
│       ├── docker.py         # Container & network management
│       ├── health.py         # Health checks
│       ├── metrics.py        # CPU/memory utilization
│       ├── parity.py         # Parity check operations
│       ├── rclone.py         # Cloud storage & flash backup
│       ├── storage.py        # Storage, disks & notifications
│       ├── system.py         # System info & array management
│       ├── ups.py            # UPS monitoring & configuration
│       └── virtualization.py # VM management
├── logs/                     # Log files (auto-created)
├── dev.sh                    # Development script
└── docker-compose.yml        # Docker Compose deployment
```

### Code Quality Commands
```bash
# Format code
uv run black unraid_mcp/

# Lint code  
uv run ruff check unraid_mcp/

# Type checking
uv run mypy unraid_mcp/

# Run tests
uv run pytest
```

### Development Workflow
```bash
# Start development server (kills existing processes safely)
./dev.sh

# Stop server only
./dev.sh --kill
```

---

## 🏗️ Architecture

### Core Principles
- **Modular Design**: Separate concerns across focused modules
- **Async First**: All operations are non-blocking and concurrent-safe  
- **Error Resilience**: Comprehensive error handling with graceful degradation
- **Configuration Driven**: Environment-based configuration with validation
- **Observability**: Structured logging and health monitoring

### Key Components

| Component | Purpose |
|-----------|---------|
| **FastMCP Server** | MCP protocol implementation and tool registration |
| **GraphQL Client** | Async HTTP client with timeout management |
| **Subscription Manager** | WebSocket connections for real-time data |
| **Tool Modules** | Domain-specific business logic (Docker, VMs, etc.) |
| **Configuration System** | Environment loading and validation |
| **Logging Framework** | Structured logging with file rotation |

---

## 🐛 Troubleshooting

### Common Issues

**🔥 Port Already in Use**
```bash
./dev.sh  # Automatically kills existing processes
```

**🔧 Connection Refused**
```bash
# Check Unraid API configuration
curl -k "${UNRAID_API_URL}" -H "X-API-Key: ${UNRAID_API_KEY}"
```

**📝 Import Errors**  
```bash
# Reinstall dependencies
uv sync --reinstall
```

**🔍 Debug Mode**
```bash
# Enable debug logging
export UNRAID_MCP_LOG_LEVEL=DEBUG
uv run unraid-mcp-server
```

### Health Check
```bash
# Use the built-in health check tool via MCP client
# or check logs at: logs/unraid-mcp.log
```

---

## 🙏 Acknowledgments

This project is a fork of the original [unraid-mcp](https://github.com/jmagar/unraid-mcp) created by **[jmagar](https://github.com/jmagar)**.

### Fork Updates

The following enhancements have been made since forking:

#### New Tool Modules (29 new tools)
- **System Metrics**: Real-time CPU/memory utilization monitoring (`metrics.py`)
- **UPS Management**: Monitor and configure UPS devices (`ups.py`)
- **Parity Operations**: Full parity check lifecycle control (`parity.py`)
- **Array Management**: Start/stop array, mount/unmount disks
- **Docker Networks**: List networks, check container update statuses
- **Notification Management**: Create, archive, and delete notifications
- **Flash Backup**: Initiate flash drive backups via RClone

#### Schema Compatibility Updates
- **Updated GraphQL Queries**: Compatible with latest Unraid API schema
- **Nested Versions Structure**: Updated to `versions.core.unraid` path
- **Enhanced Docker Info**: Added `isUpdateAvailable`, `isRebuildReady` fields
- **Enhanced Array Status**: Added `isSpinning`, `parityCheckStatus` fields
- **VM ID Updates**: Replaced deprecated `uuid` with `id` parameter
- **Disk Details**: Added interface type, SMART status, partition info

#### Infrastructure Improvements
- **Python 3.12+**: Upgraded from Python 3.10 to 3.12+ (Docker uses 3.13)
- **FastMCP 2.13.2**: Upgraded from FastMCP 2.11.2 to 2.13.2
- **CI/CD Pipeline**: Added GitHub Actions workflow for automated Docker builds
- **Pre-built Images**: Docker images automatically published to GHCR on every push
- **Code Quality**: Applied black formatting, ruff linting, and mypy type checking
- **Modern Type Hints**: Added PEP 695 type statements and improved type annotations
- **Configurable Paths**: Container environment paths now configurable via environment variables
- **Dependency Updates**: Updated websockets to 14.x+ and other dependencies

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`  
3. Run tests: `uv run pytest`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

---

## 📞 Support

- 📚 Documentation: Check inline code documentation
- 🐛 Issues: [GitHub Issues](https://github.com/mlamoure/unraid-mcp/issues)
- 💬 Discussions: Use GitHub Discussions for questions

---

*Built with ❤️ for the Unraid community*