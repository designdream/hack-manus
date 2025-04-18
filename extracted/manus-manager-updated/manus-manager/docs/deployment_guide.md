# Deployment Guide for Manus Manager

This document provides instructions for deploying the Manus Manager system to either Digital Ocean or Cloudflare Workers.

## Prerequisites

- Node.js 16+ and npm
- Python 3.10+
- PostgreSQL database (for production)
- Git

## Backend Deployment (Digital Ocean)

### 1. Prepare the Backend

1. Update the database configuration in `backend/app/core/config.py` to use PostgreSQL:

```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/manus_manager")
```

2. Create a production requirements file:

```
cd backend
pip freeze > requirements.txt
```

3. Create a Dockerfile for the backend:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Deploy to Digital Ocean

1. Create a Digital Ocean Droplet or App Platform application
2. Set up environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Secret key for JWT token generation
   - `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS
3. Deploy the backend code to Digital Ocean
4. Set up a PostgreSQL database
5. Run database migrations

```bash
cd backend
alembic upgrade head
```

## Frontend Deployment (Digital Ocean)

### 1. Prepare the Frontend

1. Update the API URL in the frontend:

```
cd frontend
echo "REACT_APP_API_URL=https://your-backend-url.com" > .env.production
echo "REACT_APP_WS_URL=wss://your-backend-url.com" >> .env.production
```

2. Build the frontend:

```bash
npm install
npm run build
```

3. Create a Dockerfile for the frontend:

```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

4. Create an nginx.conf file:

```
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass https://your-backend-url.com;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 2. Deploy to Digital Ocean

1. Create a Digital Ocean Droplet or App Platform application
2. Deploy the frontend code to Digital Ocean
3. Configure the domain and SSL certificate

## Alternative: Cloudflare Workers Deployment

### 1. Prepare for Cloudflare Workers

1. Install Wrangler CLI:

```bash
npm install -g wrangler
```

2. Create a wrangler.toml file in the frontend directory:

```toml
name = "manus-manager-frontend"
type = "webpack"
account_id = "your-account-id"
workers_dev = true
route = "your-domain.com/*"
zone_id = "your-zone-id"

[site]
bucket = "./build"
entry-point = "workers-site"
```

3. Build the frontend:

```bash
npm run build
```

### 2. Deploy to Cloudflare Workers

1. Authenticate with Cloudflare:

```bash
wrangler login
```

2. Publish the frontend:

```bash
wrangler publish
```

3. For the backend, you can use Cloudflare Workers with a serverless database like Fauna or D1, but this requires significant refactoring of the backend code.

## Setting Up a Production Database

### PostgreSQL on Digital Ocean

1. Create a managed PostgreSQL database on Digital Ocean
2. Configure the connection string in your backend environment variables
3. Run migrations to set up the database schema

```bash
cd backend
alembic upgrade head
```

4. Create an initial admin user:

```python
from app.db.session import SessionLocal
from app.schemas.schemas import UserCreate
from app.services.user_service import create_user

db = SessionLocal()
admin_user = UserCreate(
    username="admin",
    email="admin@example.com",
    password="secure-password",
    is_active=True,
    is_superuser=True
)
create_user(db, admin_user)
db.close()
```

## Monitoring and Maintenance

1. Set up logging with a service like Papertrail or Logtail
2. Configure monitoring with Digital Ocean Monitoring or a third-party service
3. Set up regular database backups
4. Implement a CI/CD pipeline for automated deployments

## Security Considerations

1. Use HTTPS for all communications
2. Implement rate limiting for API endpoints
3. Regularly update dependencies
4. Use secure password hashing (already implemented with bcrypt)
5. Implement proper input validation (already implemented with Pydantic)
6. Set up proper CORS configuration
7. Use environment variables for sensitive information
