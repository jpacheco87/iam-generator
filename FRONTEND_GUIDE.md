# AWS IAM Generator - Quick Start Guide

This guide will help you get started with the AWS IAM Generator frontend and backend.

## What You've Built

You now have a complete AWS IAM permissions analyzer with:

✅ **Modern React Frontend** - Built with shadcn/ui components and Tailwind CSS
✅ **FastAPI Backend** - RESTful API that wraps your existing Python CLI tool
✅ **Three Analysis Modes**:
   - Single command analysis
   - IAM role generation
   - Batch command processing
✅ **Multiple Output Formats** - JSON, Terraform, CloudFormation, AWS CLI
✅ **Real-time Analysis** - Interactive web interface
✅ **Professional UI** - Clean, responsive design

## Quick Start

### Option 1: Use the Launch Script (Recommended)
```bash
./start.sh
```
This will start both servers and open the web interface.

### Option 2: Start Services Individually

1. **Start the Backend:**
```bash
python backend_server.py
```
Backend runs on: http://localhost:8000

2. **Start the Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3000

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

**Batch Analysis:**
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
- Enter AWS CLI commands
- View required permissions in a clean table
- See the generated IAM policy document
- Check resource ARNs and warnings

### 2. Role Generator Tab
- Generate complete IAM roles
- Choose trust policy types (EC2, Lambda, ECS, Cross-account)
- Export in multiple formats (Terraform, CloudFormation, etc.)
- Configure role names and account IDs

### 3. Batch Analysis Tab
- Analyze multiple commands at once
- Get comprehensive summaries
- See service usage patterns
- Export batch results

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
