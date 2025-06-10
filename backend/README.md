# IAM Generator Backend

FastAPI-based backend service for the AWS IAM Generator application.

## Overview

This backend provides REST API endpoints for analyzing AWS CLI commands and generating appropriate IAM permissions and policies. It's built with FastAPI and follows modern Python application architecture patterns.

## Structure

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application setup
│   ├── models.py            # Pydantic models for API schemas
│   ├── services.py          # Business logic services
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Application configuration
│   └── routers/
│       ├── __init__.py
│       ├── health.py        # Health check endpoints
│       ├── analysis.py      # Command analysis endpoints
│       ├── roles.py         # IAM role generation endpoints
│       └── advanced.py      # Advanced analysis features
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup configuration
└── README.md               # This file
```

## API Endpoints

### Health
- `GET /health` - Health check for container orchestration

### Analysis
- `POST /analyze` - Analyze single AWS CLI command
- `POST /batch-analyze` - Analyze multiple commands
- `GET /services` - Get supported AWS services

### Roles
- `POST /generate-role` - Generate IAM role configuration

### Advanced Features (✅ Fully Implemented)
- `POST /analyze-resource-specific` - Generate policies with specific ARNs instead of wildcards
- `POST /analyze-least-privilege` - Generate minimal permission policies with security conditions
- `POST /service-summary` - Generate comprehensive service usage analysis and statistics

## Enhanced Analysis Capabilities

The backend now provides three advanced analysis modes:

### 1. Resource-Specific Policy Generation
Generates policies with precise ARN targeting:
```json
{
  "commands": ["aws s3 ls s3://my-bucket"],
  "account_id": "123456789012",
  "region": "us-east-1",
  "strict_mode": true
}
```
Returns: Policies with specific ARNs like `arn:aws:s3:::my-bucket`

### 2. Least Privilege Optimization
Creates minimal required permissions with enhanced security:
```json
{
  "commands": ["aws s3 ls s3://my-bucket"],
  "account_id": "123456789012",
  "region": "us-east-1"
}
```
Returns: Optimized policies with security conditions like `"aws:SecureTransport":"true"`

### 3. Service Usage Summary
Provides detailed breakdown of AWS services and permissions:
```json
{
  "commands": ["aws s3 ls", "aws ec2 describe-instances", "aws lambda list-functions"]
}
```
Returns: Service-specific analysis with actions, permissions, and resource patterns

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Development

```bash
# Build and run with Docker
docker build -t iam-generator-backend .
docker run -p 8000:8000 iam-generator-backend
```

## Configuration

Configuration is managed through environment variables and the `core/config.py` module:

- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level
- `CORS_ORIGINS` - Allowed CORS origins for frontend

## Dependencies

- **FastAPI** - Modern web framework for APIs
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation using Python type annotations
- **boto3** - AWS SDK for Python (via iam_generator package)

## Integration

This backend integrates with the core `iam_generator` package located in the `src/` directory, providing the business logic for AWS CLI analysis and IAM policy generation.
