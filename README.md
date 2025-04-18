# Manus Bridge

A middleware solution for integrating manus-manager with the Manus AI agent system.

## Project Overview

Manus Bridge provides a seamless integration layer between the manus-manager application and the Manus AI agent system, enabling comprehensive agent management and control.

## Repository Structure

- **manus-bridge/**: Core middleware package
  - **manus_bridge/**: Main package modules
    - **api.py**: FastAPI server exposing Manus Bridge functionality
    - **config.py**: Configuration management for paths and settings
    - **manus_bridge.py**: Core functionality for agent lifecycle management
  - **simple_integration.py**: Script for integrating with manus-manager
  - **setup.py**: Package installation configuration
  - **README.md**: Package documentation

## Features

- Discovery and interaction with Manus system components
- Agent lifecycle management (start, stop, pause, resume)
- REST API for remote control of Manus agents
- Integration with manus-manager backend
- Configuration management for different environments

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd hack-manus

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install the package
cd manus-bridge
pip install -e .
```

## Usage

### Starting the Manus Bridge API Server

```bash
cd manus-bridge
python run.py
```

### Integrating with manus-manager

```bash
cd manus-bridge
python simple_integration.py --manus-manager-path "/path/to/manus-manager"
```

## Configuration

The following environment variables can be configured:

- `MANUS_OPT_PATH`: Primary Manus system directory
- `MANUS_OPT2_PATH`: Secondary Manus system directory
- `MANUS_OPT3_PATH`: Sandbox runtime directory
- `MANUS_BRIDGE_API_HOST`: API host (default: 127.0.0.1)
- `MANUS_BRIDGE_API_PORT`: API port (default: 8080)
- `MANUS_BRIDGE_DB_URL`: Database URL (default: SQLite)

## API Endpoints

- `GET /health`: Check API server health
- `GET /agents`: List all agents
- `POST /agents/start`: Start a new agent
- `POST /agents/{agent_id}/stop`: Stop an agent
- `POST /agents/{agent_id}/pause`: Pause an agent
- `POST /agents/{agent_id}/resume`: Resume a paused agent
- `GET /agents/{agent_id}/status`: Get agent status
- `GET /templates`: List available agent templates

## Development

Created on: April 18, 2025

## License

MIT
