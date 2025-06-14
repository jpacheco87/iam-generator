# Development Guide - Restructured Backend

## New Project Structure

The project has been restructured with a clean separation between backend and frontend:

```
iam_generator/
├── backend/                    # 🐍 All Python code
│   ├── iam_generator/          # Core business logic
│   │   ├── analyzer.py         # Permission analysis engine
│   │   ├── parser.py           # AWS CLI command parser
│   │   ├── permissions_db.py   # Database (52 AWS services)
│   │   ├── role_generator.py   # IAM role generator
│   │   ├── cli.py              # CLI interface
│   │   └── main.py             # CLI entry point
│   ├── app/                    # FastAPI web application
│   │   ├── main.py             # FastAPI app setup
│   │   ├── models.py           # Pydantic schemas
│   │   ├── services.py         # Business logic services
│   │   ├── routers/            # API endpoint modules
│   │   │   ├── health.py       # Health checks
│   │   │   ├── analysis.py     # Command analysis
│   │   │   ├── roles.py        # Role generation
│   │   │   └── advanced.py     # Advanced features
│   │   └── core/               # Configuration
│   │       └── config.py       # App settings
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Backend docs
├── frontend/                   # ⚛️  React application
│   ├── src/                    # TypeScript source
│   └── package.json            # Node.js dependencies
└── tests/                      # 🧪 Test suite
```

## Development Commands

### CLI Usage
```bash
# Run the CLI tool from project root (recommended)
PYTHONPATH=backend python -m iam_generator.main --help

# Analyze a command
PYTHONPATH=backend python -m iam_generator.main analyze s3 ls

# Generate a role
PYTHONPATH=backend python -m iam_generator.main generate-role s3 ls --role-name S3ReadRole

# Alternative: Install as package first
cd backend && pip install -e .
iam-generator --help
iam-generator analyze s3 ls
iam-generator generate-role s3 ls --role-name S3ReadRole
```

### API Server
```bash
# Start the FastAPI backend
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or from project root
PYTHONPATH=backend uvicorn backend.app.main:app --reload
```

### Testing
```bash
# Run all tests
PYTHONPATH=backend pytest

# Run specific test files
PYTHONPATH=backend pytest tests/test_analyzer.py
PYTHONPATH=backend pytest tests/test_parser.py

# Run with coverage
PYTHONPATH=backend pytest --cov=iam_generator --cov-report=html
```

### Docker Development
```bash
# Full stack development with hot reload 🔥
docker-compose -f docker-compose.dev.yml up

# HOT RELOAD FEATURES:
# Backend: Automatic Python code reloading with uvicorn --reload
# Frontend: Vite HMR (Hot Module Replacement) for instant updates
# Volume mounts: 
#   - ./backend/app:/app/app
#   - ./backend/iam_generator:/app/iam_generator
#   - ./tests:/app/tests

# Backend only
docker-compose -f docker-compose.dev.yml up backend-dev

# Frontend only  
docker-compose -f docker-compose.dev.yml up frontend-dev
```

## Key Benefits of New Structure

### ✅ Clean Separation
- **Backend**: All Python code in one place
- **Frontend**: All React/TypeScript code in one place
- **Tests**: Clear test organization with proper imports

### ✅ Modular Architecture
- **Core Logic**: `backend/iam_generator/` - Reusable business logic
- **Web API**: `backend/app/` - FastAPI web layer
- **Frontend**: `frontend/` - React UI layer

### ✅ Independent Development
- Backend and frontend can be developed independently
- Clear API contract between layers
- Separate Docker containers and build processes

### ✅ Enhanced Analysis Features (Fully Implemented)
- **Resource-Specific Analysis**: Generate policies with precise ARNs
- **Least Privilege Optimization**: Minimal permissions with security conditions
- **Service Usage Summary**: Comprehensive service breakdown and statistics
- **Hot Reload Development**: Real-time code changes without container rebuilds

### ✅ Better Maintainability
- Organized imports and dependencies
- Clear responsibility boundaries
- Easier testing and debugging

## Migration Notes

### Import Changes
**Old imports:**
```python
from iam_generator.analyzer import IAMPermissionAnalyzer
```

**New imports (with PYTHONPATH=backend):**
```python
from iam_generator.analyzer import IAMPermissionAnalyzer
```

### Environment Setup
Always set `PYTHONPATH=backend` when running Python commands from the project root.

### VS Code Tasks
New task available: "Run IAM Generator CLI (Backend)" with proper path setup.

## Next Steps for Development

1. **Enhanced Services**: Complete the advanced analysis implementations
2. **Error Handling**: Add comprehensive error handling middleware
3. **Authentication**: Implement API authentication if needed
4. **Logging**: Add structured logging throughout
5. **Documentation**: Auto-generate API docs from OpenAPI spec

## Troubleshooting Development Environment

### Hot Reload Not Working

**Backend Hot Reload Issues:**
```bash
# Check if RELOAD=true is set
docker-compose -f docker-compose.dev.yml exec backend-dev env | grep RELOAD

# Check uvicorn is running with --reload flag
docker-compose -f docker-compose.dev.yml logs backend-dev | grep reload

# Restart backend container
docker-compose -f docker-compose.dev.yml restart backend-dev
```

**Frontend Hot Reload Issues:**
```bash
# Check Vite HMR status
docker-compose -f docker-compose.dev.yml logs frontend-dev | grep HMR

# Restart frontend container
docker-compose -f docker-compose.dev.yml restart frontend-dev
```

### Volume Mount Issues
```bash
# Verify volume mounts are working
docker-compose -f docker-compose.dev.yml exec backend-dev ls -la /app/app
docker-compose -f docker-compose.dev.yml exec backend-dev ls -la /app/iam_generator

# Check for file permissions
docker-compose -f docker-compose.dev.yml exec backend-dev whoami
```

### API Endpoint Issues
```bash
# Test enhanced analysis endpoints
curl -X POST "http://localhost:8000/analyze-resource-specific" \
  -H "Content-Type: application/json" \
  -d '{"commands": ["aws s3 ls s3://test"], "account_id": "123456789012", "region": "us-east-1"}'

# Check API documentation
open http://localhost:8000/docs
```

### Container Health Checks
```bash
# Check container status
docker-compose -f docker-compose.dev.yml ps

# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:3000  # Should return React app
```
