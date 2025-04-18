# Manus Manager

A comprehensive system for orchestrating, starting, stopping, and tracking Manus AI agents from your local machine.

## Features

- **Agent Management**: Create, configure, start, stop, and monitor Manus agents
- **Task Tracking**: Assign tasks to agents and track their progress
- **Real-time Monitoring**: WebSocket-based real-time updates on agent status and task progress
- **Analytics Dashboard**: Visualize agent performance and task completion metrics
- **Multi-account Support**: Manage multiple Manus accounts with up to 5 tasks per instance

## System Architecture

The Manus Manager consists of three main components:

1. **Backend API**: Built with FastAPI, provides RESTful endpoints and WebSocket connections
2. **Frontend UI**: React-based web interface with Material-UI components
3. **Database**: PostgreSQL for data persistence

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/manus-manager.git
cd manus-manager
```

2. Start the system using Docker Compose:
```bash
docker-compose up -d
```

3. Access the web interface at http://localhost:3000

### Initial Setup

1. Create an admin user:
```bash
docker-compose exec backend python -c "from app.db.session import SessionLocal; from app.schemas.schemas import UserCreate; from app.services.user_service import create_user; db = SessionLocal(); admin_user = UserCreate(username='admin', email='admin@example.com', password='secure-password', is_active=True, is_superuser=True); create_user(db, admin_user); db.close()"
```

2. Log in with the admin credentials:
   - Username: admin
   - Password: secure-password

## Documentation

- [User Guide](docs/user_guide.md): Instructions for using the system
- [Deployment Guide](docs/deployment_guide.md): Detailed deployment instructions
- [Architecture Documentation](docs/architecture.md): System design and component interactions

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

## Deployment Options

The system can be deployed to:
- **Digital Ocean**: Using Docker or App Platform
- **Cloudflare Workers**: For the frontend (backend requires separate hosting)

See the [Deployment Guide](docs/deployment_guide.md) for detailed instructions.

## License

[MIT License](LICENSE)

## Acknowledgements

- Built for managing [Manus.im](https://manus.im) AI agents
- Uses FastAPI, React, and PostgreSQL
