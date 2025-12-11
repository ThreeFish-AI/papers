# Admin UI for Agentic AI Papers Management

This directory contains the web-based Admin UI system for managing Agentic AI research papers and their translations.

## Features

### Paper Management
- **Upload**: Upload PDF papers and web articles
- **Organize**: Categorize papers by topics (LLM Agents, Context Engineering, Knowledge Graphs, etc.)
- **Track**: Monitor processing status and progress
- **Search**: Full-text search across all papers

### Translation Pipeline
- **Queue Management**: View and manage translation jobs
- **Progress Tracking**: Real-time progress updates
- **Quality Control**: Review and edit translations
- **Batch Operations**: Process multiple papers simultaneously

### Agent Configuration
- **Agent Settings**: Configure Claude and ADK agents
- **Pipeline Management**: Set up processing pipelines
- **Performance Monitoring**: Track agent performance metrics

## Architecture

```
ui/
├── frontend/          # React frontend
├── backend/           # FastAPI backend
├── docker/           # Docker configurations
└── docs/             # API documentation
```

## Tech Stack

- **Frontend**: React 18, TypeScript, Ant Design
- **Backend**: FastAPI, Python, SQLAlchemy
- **Database**: PostgreSQL
- **Queue**: Redis + Celery
- **Storage**: MinIO (S3-compatible)

## Getting Started

1. Install dependencies:
```bash
# Frontend
cd frontend && npm install

# Backend
cd backend && pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run services:
```bash
# With Docker Compose
docker-compose up -d

# Or manually
npm run dev:frontend
npm run dev:backend
```

4. Access the UI at `http://localhost:3000`

## API Documentation

API documentation is available at `http://localhost:8000/docs` when running the backend.

## Development

- Frontend development server: `npm run dev`
- Backend development server: `uvicorn main:app --reload`
- Run tests: `npm test`
- Build for production: `npm run build`