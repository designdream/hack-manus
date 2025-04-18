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

## Deployment Options

### DigitalOcean Deployment

You can deploy the Manus Bridge on DigitalOcean using App Platform or Droplets:

#### Using DigitalOcean App Platform

1. Create a new app on the [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Connect your Git repository
3. Configure the app:
   - Set the environment variables (MANUS_OPT_PATH, etc.)
   - Choose an appropriate plan
   - Set the run command to `python manus-bridge/run.py`
4. Deploy the app

#### Using DigitalOcean Droplets

1. Create a new Droplet with Ubuntu
2. SSH into your Droplet
3. Install dependencies:
   ```bash
   apt update && apt install -y python3 python3-pip git
   ```
4. Clone your repository:
   ```bash
   git clone <repository-url>
   cd hack-manus
   ```
5. Set up the environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   cd manus-bridge
   pip install -e .
   ```
6. Create a systemd service for automatic startup:
   ```bash
   sudo nano /etc/systemd/system/manus-bridge.service
   ```
   Add the following content:
   ```
   [Unit]
   Description=Manus Bridge Service
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/path/to/hack-manus/manus-bridge
   ExecStart=/path/to/hack-manus/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
7. Enable and start the service:
   ```bash
   sudo systemctl enable manus-bridge
   sudo systemctl start manus-bridge
   ```

### Cloudflare Workers Deployment

For Cloudflare Workers deployment, you'll need to adapt the application since Cloudflare Workers are primarily designed for JavaScript/TypeScript. Here's how you can approach it:

1. Create a serverless API with Cloudflare Workers:
   - Use [Cloudflare Workers](https://workers.cloudflare.com/) for the API layer
   - Implement a lightweight JavaScript/TypeScript API that communicates with your Manus Bridge instance

2. Deploy the core Manus Bridge on a server or DigitalOcean:
   - Set up the Manus Bridge as described above
   - Configure it to accept requests from your Cloudflare Worker

3. Use Cloudflare Workers as an API gateway:
   ```javascript
   addEventListener('fetch', event => {
     event.respondWith(handleRequest(event.request))
   })

   async function handleRequest(request) {
     // Route requests to your Manus Bridge instance
     const url = new URL(request.url)
     const manusBridgeUrl = 'https://your-manus-bridge-instance.com'
     
     // Forward the request to Manus Bridge
     const response = await fetch(`${manusBridgeUrl}${url.pathname}`, {
       method: request.method,
       headers: request.headers,
       body: request.body
     })
     
     return response
   }
   ```

4. Deploy the Worker:
   ```bash
   wrangler publish
   ```

Alternatively, you can use [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/platform/functions/) for a more integrated approach with your frontend.

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
