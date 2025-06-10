# AWS IAM Generator - Quick Start Guide

This guide will help you get started with the AWS IAM Generator frontend and backend.

## What You've Built

You now have a complete AWS IAM permissions analyzer with:

✅ **Modern React Frontend** - Built with shadcn/ui components and Tailwind CSS
✅ **FastAPI Backend** - RESTful API that wraps your existing Python CLI tool
✅ **Enhanced Analysis Modes**:
   - Single command analysis with detailed breakdowns
   - IAM role generation with multiple output formats
   - Standard batch command processing
   - **Resource-specific policy generation** with precise ARN targeting
   - **Least privilege optimization** with security conditions
   - **Service usage analysis** with comprehensive breakdowns
✅ **Multiple Output Formats** - JSON, Terraform, CloudFormation, AWS CLI
✅ **Real-time Analysis** - Interactive web interface with hot-reload development
✅ **Professional UI** - Clean, responsive design with enhanced batch analyzer
✅ **Production Ready** - Docker containerization with full development environment

## Quick Start

### Option 1: Docker Development Environment (Recommended) 🔥
```bash
# Start development environment with hot reload
make dev
# OR: docker-compose -f docker-compose.dev.yml up -d

# Access services:
# Frontend: http://localhost:3000 (with HMR - Hot Module Replacement)
# Backend: http://localhost:8000 (with auto-reload on Python changes)
# API Docs: http://localhost:8000/docs

# 🔥 HOT RELOAD FEATURES:
# - Backend automatically reloads when you edit Python files in backend/app/ or backend/iam_generator/
# - Frontend automatically updates when you edit React/TypeScript files in frontend/src/
# - Volume mounts enable live code editing without container rebuilds
# - Debug logging enabled for comprehensive development feedback
```

### Option 2: Docker Production Environment
```bash
# Start production environment
make start
# OR: docker-compose up -d

# Access services:
# Web UI: http://localhost:3000
# API: http://localhost:8000
```

### Option 3: Local Development
```bash
# Terminal 1: Start Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Frontend
cd frontend
npm install
npm run dev
```

## Usage Examples

### 1. Web Interface

1. Open http://localhost:3000
2. Try these sample commands:

**S3 Operations:**
```
aws s3 ls s3://my-bucket
aws s3 cp file.txt s3://my-bucket/folder/
aws s3 sync ./local-folder s3://my-bucket/remote-folder
```

**EC2 Operations:**
```
aws ec2 describe-instances
aws ec2 run-instances --image-id ami-12345 --instance-type t3.micro
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

**Lambda Operations:**
```
aws lambda list-functions
aws lambda invoke --function-name my-function output.json
aws lambda create-function --function-name test --runtime python3.9
```

### 2. API Examples

**Analyze a Command:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"command": "aws s3 ls s3://my-bucket"}'
```

**Generate an IAM Role:**
```bash
curl -X POST "http://localhost:8000/generate-role" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "aws s3 ls s3://my-bucket",
    "role_name": "S3ReadRole",
    "trust_policy": "ec2",
    "output_format": "terraform"
  }'
```

**Standard Batch Analysis:**
```bash
curl -X POST "http://localhost:8000/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "aws s3 ls s3://bucket1",
      "aws s3 cp file.txt s3://bucket2/",
      "aws ec2 describe-instances"
    ]
  }'
```

**Enhanced Analysis - Resource-Specific:**
```bash
curl -X POST "http://localhost:8000/analyze-resource-specific" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "aws s3 ls s3://my-bucket",
      "aws ec2 describe-instances --instance-ids i-1234567890abcdef0"
    ],
    "account_id": "123456789012",
    "region": "us-east-1",
    "strict_mode": true
  }'

# Returns policies with specific ARNs:
# "Resource": "arn:aws:s3:::my-bucket"
# "Resource": "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"
```

**Enhanced Analysis - Least Privilege:**
```bash
curl -X POST "http://localhost:8000/analyze-least-privilege" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "aws s3 ls s3://my-bucket",
      "aws ec2 describe-instances"
    ],
    "account_id": "123456789012",
    "region": "us-east-1"
  }'

# Returns optimized policies with security conditions:
# "Condition": {"Bool": {"aws:SecureTransport": "true"}}
# Minimal required permissions with enhanced security
```

**Enhanced Analysis - Service Summary:**
```bash
curl -X POST "http://localhost:8000/service-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "aws s3 ls s3://my-bucket",
      "aws ec2 describe-instances",
      "aws lambda list-functions"
    ]
  }'

# Returns detailed service breakdown:
# - Service-specific analysis (S3, EC2, Lambda)
# - Actions and permissions per service
# - Resource patterns and usage statistics
# - Comprehensive policy document generation
```

### 3. CLI (Original Tool)

The original CLI tool still works as before:
```bash
# Analyze commands
iam-generator analyze s3 ls s3://my-bucket
iam-generator analyze ec2 describe-instances

# Generate roles
iam-generator generate-role --role-name MyRole s3 ls s3://my-bucket
iam-generator generate-role --trust-policy lambda lambda invoke --function-name func

# Batch analysis
echo "s3 ls s3://bucket1\nec2 describe-instances" > commands.txt
iam-generator batch-analyze commands.txt
```

## Key Features to Explore

### 1. Command Analysis Tab
- Enter AWS CLI commands for detailed analysis
- View required permissions in a clean, organized table
- See the generated IAM policy document with syntax highlighting
- Check specific resource ARNs and security warnings
- Export results in multiple formats

### 2. Role Generator Tab
- Generate complete IAM roles with comprehensive configurations
- Choose trust policy types (EC2, Lambda, ECS, Cross-account)
- Export in multiple formats (JSON, Terraform, CloudFormation, AWS CLI)
- Configure role names, account IDs, and descriptions
- Download or copy generated configurations

### 3. Standard Batch Analysis Tab
- Analyze multiple commands simultaneously
- Get comprehensive summaries with statistics
- View detailed results for each command
- See combined policy documents
- Export batch results and summaries

### 4. Enhanced Batch Analysis Tab ✨ **FULLY IMPLEMENTED**
- **Multiple Analysis Modes**: Choose from standard, resource-specific, least privilege, or service summary
- **Resource-Specific Analysis**: Generate policies with precise ARNs like `arn:aws:s3:::my-bucket` instead of wildcards
- **Least Privilege Optimization**: Get minimal required permissions with enhanced security conditions like `"aws:SecureTransport":"true"`
- **Service Usage Summary**: Detailed breakdown of AWS services (S3, EC2, Lambda) with actions, permissions, and resources
- **Advanced Configuration**: Set AWS account ID, region, and strict mode options
- **Real-time Results**: Interactive viewing of generated policies and comprehensive metadata
- **Verified Functionality**: All endpoints now return actual analysis data (no longer placeholder/stub data)

## Project Structure

```
iam_generator/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── lib/             # API client and utilities
│   │   └── App.tsx          # Main application
│   └── README.md            # Frontend documentation
├── backend_server.py        # FastAPI backend wrapper
├── start.sh                 # Launch script
├── src/iam_generator/       # Original Python CLI tool
└── README.md               # Main documentation
```

## API Documentation

Visit http://localhost:8000/docs to see the interactive API documentation (Swagger UI).

## Next Steps

1. **Customize the UI**: Modify components in `frontend/src/components/`
2. **Add New Features**: Extend the API in `backend_server.py`
3. **Deploy**: Build for production with `npm run build` and deploy both services
4. **Integrate**: Use the REST API to integrate with your existing tools

## Troubleshooting

**Port Conflicts:**
- Backend (8000): Change port in `backend_server.py`
- Frontend (3000): Change port in `frontend/vite.config.ts`

**Dependencies:**
- Python: `pip install -r requirements.txt`
- Node.js: `cd frontend && npm install`

**CORS Issues:**
- The backend is configured to allow frontend requests
- Check `backend_server.py` CORS settings if needed

## Support

- 📖 Documentation: See README files in each directory
- 🐛 Issues: Check error messages in browser console and terminal
- 🔧 API: Use the Swagger docs at http://localhost:8000/docs

Enjoy using your new AWS IAM Generator frontend! 🎉
