# Manus Bridge

A bridge between manus-manager and Manus for orchestrating, starting, stopping, and tracking Manus AI agents.

## Overview

Manus Bridge provides an integration layer between the manus-manager application and the Manus system. It exposes a REST API that allows manus-manager to control Manus agents.

## Features

- Start, stop, and pause Manus agents
- Monitor agent status
- List available agent templates
- Seamless integration with manus-manager

## How It Works

Manus Bridge works by:

1. Discovering the Manus system components in the opt directories
2. Providing a REST API that mimics the expected behavior of Manus agents
3. Translating manus-manager commands into actions that control Manus agents
4. Monitoring agent status and reporting back to manus-manager

## Installation

### Prerequisites

- Python 3.7+
- Access to Manus system files
- manus-manager installation

### Option 1: Install from source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/manus-bridge.git
   cd manus-bridge
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Configure environment variables:
   ```bash
   export MANUS_OPT_PATH="/Users/feliperecalde/Downloads/Manual Library/opt"
   export MANUS_OPT2_PATH="/Users/feliperecalde/Downloads/Manual Library/opt 2"
   export MANUS_OPT3_PATH="/Users/feliperecalde/Downloads/Manual Library/opt 3"
   ```

### Option 2: Install dependencies only

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Integration with manus-manager

To integrate Manus Bridge with an existing manus-manager installation:

1. Run the integration script:
   ```bash
   python integration.py --manus-manager-path /path/to/manus-manager
   ```

2. This will:
   - Patch the agent_service.py file to use Manus Bridge
   - Create a Manus Bridge API client
   - Update the .env file with the Manus Bridge API URL

## Usage

### Starting the Manus Bridge API Server

```bash
# Option 1: Using the run script
python run.py --host 127.0.0.1 --port 8080

# Option 2: Using the module
python -m manus_bridge.api

# Option 3: Using the console script (if installed with pip)
manus-bridge
```

### Starting manus-manager with Manus Bridge

1. Start the Manus Bridge API server:
   ```bash
   python run.py
   ```

2. Start the manus-manager backend:
   ```bash
   cd /path/to/manus-manager/backend
   uvicorn app.main:app --reload
   ```

3. Start the manus-manager frontend:
   ```bash
   cd /path/to/manus-manager/frontend
   npm start
   ```

4. Access the manus-manager web interface at http://localhost:3000

## API Endpoints

The Manus Bridge API provides the following endpoints:

- `GET /`: Root endpoint
- `GET /health`: Health check endpoint
- `POST /agents/start`: Start a Manus agent
- `POST /agents/{agent_id}/stop`: Stop a Manus agent
- `POST /agents/{agent_id}/pause`: Pause a Manus agent
- `POST /agents/{agent_id}/resume`: Resume a paused Manus agent
- `GET /agents/{agent_id}/status`: Get the status of a Manus agent
- `GET /templates`: List available templates for Manus agents

## Troubleshooting

### Common Issues

1. **Manus Bridge API server fails to start**
   - Check that the Manus paths in config.py are correct
   - Ensure you have the necessary permissions to access the Manus files

2. **manus-manager cannot connect to Manus Bridge**
   - Verify that the MANUS_BRIDGE_API_URL in the .env file is correct
   - Check that the Manus Bridge API server is running

3. **Agent operations fail**
   - Check the logs for error messages
   - Verify that the Manus system files are accessible

## License

MIT License
