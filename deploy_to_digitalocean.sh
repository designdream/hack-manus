#!/bin/bash
# Manus Bridge DigitalOcean Deployment Script
# Created: April 18, 2025

set -e

# Configuration
DROPLET_NAME="manus-bridge"
DROPLET_REGION="sfo3"
DROPLET_SIZE="s-1vcpu-2gb"
DROPLET_IMAGE="ubuntu-22-04-x64"
PROJECT_DIR=$(pwd)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Manus Bridge deployment to DigitalOcean...${NC}"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl is not installed. Please install it first.${NC}"
    echo "Visit https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if doctl is authenticated
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Error: doctl is not authenticated. Please run 'doctl auth init' first.${NC}"
    exit 1
fi

# Check for SSH keys
SSH_KEYS=$(doctl compute ssh-key list --format ID --no-header)
if [ -z "$SSH_KEYS" ]; then
    echo -e "${RED}Error: No SSH keys found in your DigitalOcean account.${NC}"
    echo "Please add an SSH key using 'doctl compute ssh-key import' or via the web interface."
    exit 1
fi

echo -e "${GREEN}Creating Droplet '${DROPLET_NAME}'...${NC}"
# Create the Droplet
DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
    --region $DROPLET_REGION \
    --size $DROPLET_SIZE \
    --image $DROPLET_IMAGE \
    --ssh-keys $SSH_KEYS \
    --format ID \
    --no-header)

if [ -z "$DROPLET_ID" ]; then
    echo -e "${RED}Error: Failed to create Droplet.${NC}"
    exit 1
fi

echo -e "${GREEN}Droplet created with ID: ${DROPLET_ID}${NC}"
echo -e "${YELLOW}Waiting for Droplet to become active...${NC}"

# Wait for the Droplet to become active
while true; do
    STATUS=$(doctl compute droplet get $DROPLET_ID --format Status --no-header)
    if [ "$STATUS" == "active" ]; then
        break
    fi
    echo -n "."
    sleep 5
done

echo -e "\n${GREEN}Droplet is now active!${NC}"

# Get the Droplet's IP address
IP_ADDRESS=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
echo -e "${GREEN}Droplet IP address: ${IP_ADDRESS}${NC}"

echo -e "${YELLOW}Waiting for SSH to become available...${NC}"
# Wait for SSH to become available
while ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$IP_ADDRESS echo &> /dev/null; do
    echo -n "."
    sleep 5
done

echo -e "\n${GREEN}SSH is now available!${NC}"

echo -e "${YELLOW}Setting up the Droplet...${NC}"
# Set up the Droplet
ssh -o StrictHostKeyChecking=no root@$IP_ADDRESS << 'EOF'
# Update the system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv git nginx

# Create directory for the application
mkdir -p /opt/manus-bridge

# Create a user for running the application
useradd -m -s /bin/bash manus
EOF

echo -e "${GREEN}Droplet setup completed!${NC}"

echo -e "${YELLOW}Deploying Manus Bridge...${NC}"
# Deploy the application
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
    $PROJECT_DIR/ root@$IP_ADDRESS:/opt/manus-bridge/

# Configure the application
ssh -o StrictHostKeyChecking=no root@$IP_ADDRESS << 'EOF'
# Set up Python virtual environment
cd /opt/manus-bridge
python3 -m venv venv
source venv/bin/activate

# Install the application
cd manus-bridge
pip install -e .

# Create systemd service
cat > /etc/systemd/system/manus-bridge.service << 'EOT'
[Unit]
Description=Manus Bridge Service
After=network.target

[Service]
User=manus
WorkingDirectory=/opt/manus-bridge/manus-bridge
ExecStart=/opt/manus-bridge/venv/bin/python run.py
Restart=always
Environment="MANUS_BRIDGE_API_HOST=0.0.0.0"
Environment="MANUS_BRIDGE_API_PORT=8080"
Environment="MANUS_OPT_PATH=/opt/manus"
Environment="MANUS_OPT2_PATH=/opt/manus2"
Environment="MANUS_OPT3_PATH=/opt/manus3"
Environment="MANUS_BRIDGE_DB_URL=sqlite:///manus_bridge.db"

[Install]
WantedBy=multi-user.target
EOT

# Set permissions
chown -R manus:manus /opt/manus-bridge

# Configure Nginx as a reverse proxy
cat > /etc/nginx/sites-available/manus-bridge << 'EOT'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOT

# Enable the Nginx site
ln -sf /etc/nginx/sites-available/manus-bridge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx

# Enable and start the service
systemctl enable manus-bridge
systemctl start manus-bridge

# Check the status
systemctl status manus-bridge
EOF

echo -e "${GREEN}Manus Bridge deployment completed!${NC}"
echo -e "${GREEN}You can access the Manus Bridge API at: http://${IP_ADDRESS}/${NC}"
echo -e "${YELLOW}To check the service status:${NC} ssh root@$IP_ADDRESS 'systemctl status manus-bridge'"
echo -e "${YELLOW}To view logs:${NC} ssh root@$IP_ADDRESS 'journalctl -u manus-bridge'"
