# AWS CLI IAM Permissions Analyzer

**Copyright (c) 2025 Jeff Pacheco JchecoPhotography. All rights reserved.**

An enterprise-grade tool that analyzes AWS CLI commands and generates minimal IAM permissions required to execute them securely. This project helps developers, DevOps engineers, and security teams create least-privilege IAM roles and policies by automatically mapping AWS CLI workflows to precise permission requirements.

## 🌟 Key Features

### Core Capabilities
- **Intelligent Command Analysis**: Advanced parsing of AWS CLI commands to extract services, actions, and resource ARNs
- **Comprehensive Permission Mapping**: Database of 52 AWS services with 300+ command mappings covering all major AWS services
- **Multiple Interfaces**: CLI tool, modern React web interface, and comprehensive REST API
- **Smart Role Generation**: Create complete IAM roles with appropriate trust policies in multiple formats

### ✨ Enhanced IAM Features (v2.0)
- **Policy Validation Engine**: Comprehensive validation with AWS size limits, security scoring (0-100), and actionable recommendations
- **Cross-Service Dependency Analysis**: Automatic detection of service dependencies (Lambda → CloudWatch Logs, ECS → ECR, Step Functions → Lambda, etc.)
- **Conditional Policy Generation**: Advanced security with MFA, IP, time, VPC, and resource-tag restrictions
- **Policy Optimization**: Intelligent size reduction, statement consolidation, and security improvements
- **Compliance Checking**: SOC2, PCI, HIPAA, and GDPR compliance analysis with detailed scoring
- **Security Recommendations**: Service-specific best practices and vulnerability detection with remediation steps
- **Policy Templates**: Pre-built enterprise templates for common use cases (Lambda execution, S3 operations, EC2 management, RDS access)

### Advanced Analysis Modes
- **Resource-Specific Policy Generation**: Precise ARN targeting instead of wildcards for enhanced security
- **Least Privilege Optimization**: Minimal required permissions with automatic security condition injection
- **Service Usage Analysis**: Detailed breakdowns of AWS services, permissions, and usage patterns
- **Batch Analysis**: Process multiple commands with comprehensive summaries and dependency mapping

### Output & Integration
- **Multiple Output Formats**: JSON, Terraform HCL, CloudFormation YAML/JSON, AWS CLI commands
- **One-Click Generation**: All formats generated simultaneously in a single API call (no format selection needed)
- **Advanced Web Interface**: Modern React frontend with shadcn/ui components and enhanced batch analyzer
- **Production Ready**: Fully containerized with Docker Compose, Nginx proxy, and health checks
- **Security Best Practices**: Automatic security condition injection and least privilege enforcement
- **Hot Reload Development**: Full development stack with automatic code reloading for rapid iteration

## 🚀 Architecture Overview

This project provides three complementary interfaces:

### 1. Command Line Interface (CLI)
```bash
# Direct CLI usage for automation and scripting (requires PYTHONPATH)
PYTHONPATH=backend python -m iam_generator.main analyze s3 ls s3://my-bucket
PYTHONPATH=backend python -m iam_generator.main generate-role --role-name S3ReadRole s3 ls s3://my-bucket

# Or install as package first
cd backend && pip install -e .
iam-generator analyze s3 ls s3://my-bucket
iam-generator generate-role --role-name S3ReadRole s3 ls s3://my-bucket
```

### 2. Web Interface (Recommended)
Modern React frontend with shadcn/ui components for interactive analysis and enhanced IAM features:

![IAM Policy Generator Web Interface](docs/ui.png)

**Available Tabs & Features:**
- **Analyze**: Single command analysis with detailed permission breakdown and resource-specific ARN detection
- **Generate**: **✨ One-click role generation** - All formats (JSON, Terraform, CloudFormation, AWS CLI) generated simultaneously in a single API call
- **Batch**: Advanced batch analysis with multiple analysis modes:
  - Standard analysis with permission mapping
  - Resource-specific analysis with ARN targeting
  - Least privilege optimization with security conditions
  - Service summary with usage patterns and dependency analysis
- **Validate**: **✨ Policy validation engine** with:
  - Security scoring (0-100) with detailed breakdown
  - AWS policy size limit validation (6144 characters)
  - Security issue detection and remediation recommendations
  - Best practices compliance checking
- **Advanced**: **✨ Enhanced IAM features** including:
  - Cross-service dependency analysis with interactive visualization
  - Conditional policy generation with MFA, IP, time, VPC, and tag-based restrictions
  - Security recommendations with service-specific best practices
  - Compliance checking for SOC2, PCI, HIPAA, and GDPR frameworks
  - Policy templates for enterprise use cases

```bash
# Complete application stack with Docker
docker-compose up -d

# Access interfaces:
# Web UI: http://localhost:3000
# API: http://localhost:8000  
# API Docs: http://localhost:8000/docs
```

### 3. REST API
FastAPI backend for programmatic integration with comprehensive endpoints:

**Core Endpoints:**
```bash
# Basic command analysis
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"command": "aws s3 ls s3://my-bucket"}'

# Generate role (single format - legacy endpoint)
curl -X POST "http://localhost:8000/generate-role" \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 ls", "role_name": "S3Role", "output_format": "terraform"}'

# ✨ Generate role (all formats simultaneously - recommended)
curl -X POST "http://localhost:8000/generate-role-all-formats" \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 ls", "role_name": "S3Role", "trust_policy": "ec2"}'
```

**🆕 Enhanced IAM API Endpoints:**
```bash
# Policy validation with security scoring
curl -X POST "http://localhost:8000/enhanced/validate-policy" \
  -H "Content-Type: application/json" \
  -d '{"policy": {...}, "policy_type": "managed"}'

# Cross-service dependency analysis  
curl -X POST "http://localhost:8000/enhanced/cross-service-dependencies" \
  -H "Content-Type: application/json" \
  -d '{"commands": ["lambda invoke --function-name test"], "include_implicit": true}'

# Conditional policy generation
curl -X POST "http://localhost:8000/enhanced/conditional-policy" \
  -H "Content-Type: application/json" \
  -d '{"commands": ["s3 ls"], "conditions": {"require_mfa": true, "ip_restrictions": ["10.0.0.0/8"]}}'

# Security recommendations
curl -X GET "http://localhost:8000/enhanced/security-recommendations/s3"

# Compliance checking
curl -X POST "http://localhost:8000/enhanced/compliance-check/soc2" \
  -H "Content-Type: application/json" \
  -d '{"policy": {...}}'
```

## 📦 Installation & Deployment

### Option 1: Docker Deployment (Recommended)

The project includes a complete containerized stack with production-ready configuration:

```bash
# Clone the repository
git clone https://github.com/jpacheco87/iam_generator.git
cd iam_generator

# Production deployment
make start
# OR: docker-compose up -d

# Development environment
make dev
# OR: docker-compose -f docker-compose.dev.yml up -d

# 🔥 HOT RELOAD FEATURES:
# Backend: Automatic Python code reloading with uvicorn --reload
# Frontend: Vite HMR (Hot Module Replacement) for instant updates
# Volume mounts: ./backend/app:/app/app and ./backend/iam_generator:/app/iam_generator

# View service status
make status

# View logs
make logs
```

**Available Make Commands:**
- `make build` - Build Docker images
- `make start` - Start production environment  
- `make dev` - Start development environment
- `make stop` - Stop all services
- `make restart` - Restart services
- `make status` - Show service status
- `make logs` - Show service logs
- `make health` - Check service health
- `make cleanup` - Clean up resources

### Option 2: Local Development Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt
pip install -e .

# Now you can use the CLI without PYTHONPATH
iam-generator --help

# Or use with PYTHONPATH from project root
PYTHONPATH=backend python -m iam_generator.main --help

# Optional: Install frontend dependencies
cd ../frontend
npm install
npm run build
```

## 🎯 Quick Start Examples

### Analyze Individual Commands
```bash
# S3 operations analysis
PYTHONPATH=backend python -m iam_generator.main analyze s3 sync s3://source/ s3://dest/ --delete

# EC2 management with JSON output
PYTHONPATH=backend python -m iam_generator.main analyze --output json ec2 run-instances --image-id ami-12345

# Lambda function analysis
PYTHONPATH=backend python -m iam_generator.main analyze lambda create-function --function-name test

# Or with installed package
iam-generator analyze s3 sync s3://source/ s3://dest/ --delete
iam-generator analyze --output json ec2 run-instances --image-id ami-12345
iam-generator analyze lambda create-function --function-name test
```

### 🆕 One-Click Role Generation (All Formats)
The latest update enables generating all output formats simultaneously:

```bash
# Generate role with all formats (JSON, Terraform, CloudFormation, AWS CLI)
# Via Web Interface: Simply click "Generate IAM Role" - no format selection needed!

# Via API: All formats returned in single response
curl -X POST "http://localhost:8000/generate-role-all-formats" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "s3 ls s3://my-bucket",
    "role_name": "S3ReadRole", 
    "trust_policy": "ec2",
    "description": "Role for S3 read access"
  }'

# Response includes:
# - role_name, trust_policy, permissions_policy (JSON)
# - terraform_config (Complete HCL)
# - cloudformation_config (YAML/JSON template)  
# - aws_cli_commands (Ready-to-run commands)
```

### Generate IAM Roles (Individual Formats)
```bash
# Basic S3 role
PYTHONPATH=backend python -m iam_generator.main generate-role --role-name S3ReadRole s3 ls s3://my-bucket

# Lambda execution role with Terraform output
PYTHONPATH=backend python -m iam_generator.main generate-role \
  --role-name LambdaExecutionRole \
  --trust-policy lambda \
  --output-format terraform \
  lambda invoke --function-name my-function

# Cross-account access role
PYTHONPATH=backend python -m iam_generator.main generate-role \
  --role-name CrossAccountRole \
  --trust-policy cross-account \
  --account-id 123456789012 \
  s3 ls s3://shared-bucket

# Or with installed package
iam-generator generate-role --role-name S3ReadRole s3 ls s3://my-bucket
iam-generator generate-role \
  --role-name LambdaExecutionRole \
  --trust-policy lambda \
  --output-format terraform \
  lambda invoke --function-name my-function
```

### Batch Analysis
```bash
# Create command list file
cat > commands.txt << EOF
s3 ls s3://bucket1
s3 cp file.txt s3://bucket2/
ec2 describe-instances
lambda list-functions
dynamodb scan --table-name MyTable
EOF

# Analyze all commands with detailed output
PYTHONPATH=backend python -m iam_generator.main batch-analyze commands.txt --output-dir ./results

# Or with installed package
iam-generator batch-analyze commands.txt --output-dir ./results
```

## 🔧 Advanced Features

### 🆕 Enhanced IAM Features (Latest Release)

#### 1. Policy Validation Engine
Comprehensive validation with AWS limits, security scoring, and recommendations:

```bash
# Web Interface: Use the "Validate" tab for interactive policy validation

# API usage
curl -X POST "http://localhost:8000/enhanced/validate-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": {
      "Version": "2012-10-17",
      "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]
    },
    "policy_type": "managed"
  }'

# Returns:
# - is_valid: boolean
# - policy_size: number (AWS 6144 char limit check)
# - score: 0-100 security score
# - issues: detailed security and syntax issues
# - recommendations: improvement suggestions
```

#### 2. Cross-Service Dependency Analysis
Automatic detection of service dependencies with enhanced policies:

```bash
# Web Interface: Use "Advanced" > "Dependencies" tab

# API usage
curl -X POST "http://localhost:8000/enhanced/cross-service-dependencies" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["lambda invoke --function-name my-function"],
    "include_implicit": true
  }'

# Detects dependencies like:
# - Lambda → CloudWatch Logs (for logging)
# - Lambda → VPC (for network access)
# - ECS → ECR (for container images)
# - Lambda → X-Ray (for tracing)
```

#### 3. Conditional Policy Generation
Generate policies with MFA, IP, time, and VPC restrictions:

```bash
# Web Interface: Use "Advanced" > "Conditional Policies" tab

# API usage
curl -X POST "http://localhost:8000/enhanced/conditional-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["s3 list-buckets"],
    "conditions": {
      "require_mfa": true,
      "ip_restrictions": ["203.0.113.0/24"],
      "time_restrictions": {
        "start_time": "09:00",
        "end_time": "17:00",
        "timezone": "UTC"
      }
    }
  }'

# Generates policies with IAM conditions:
# - aws:MultiFactorAuthPresent
# - aws:SourceIp
# - aws:CurrentTime
# - aws:SourceVpc
```

#### 4. Security Recommendations & Compliance
Service-specific best practices and compliance checking:

```bash
# Get security recommendations for a service
curl -X GET "http://localhost:8000/enhanced/security-recommendations/s3"

# Check compliance against frameworks
curl -X POST "http://localhost:8000/enhanced/compliance-check/soc2" \
  -H "Content-Type: application/json" \
  -d '{"policy": {...}}'

# Supported frameworks: SOC2, PCI, HIPAA, GDPR
```

#### 5. Policy Optimization & Templates
Optimize existing policies and use pre-built templates:

```bash
# Optimize a policy for size and security
curl -X POST "http://localhost:8000/enhanced/optimize-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": {...},
    "optimization_level": "standard"
  }'

# Get policy templates for common use cases
curl -X GET "http://localhost:8000/enhanced/policy-templates/lambda-basic"
curl -X GET "http://localhost:8000/enhanced/policy-templates/s3-read-only"

# Available templates: lambda-basic, lambda-vpc, s3-read-only, s3-full-bucket, ec2-developer, rds-admin
```

### Standard Analysis Modes

#### 1. Resource-Specific Policy Generation
Generate policies with specific ARN patterns instead of wildcards:

```bash
# CLI usage
PYTHONPATH=backend python -m iam_generator.main analyze s3 cp s3://my-bucket/file.txt ./local-file
PYTHONPATH=backend python -m iam_generator.main analyze ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Or with installed package
iam-generator analyze s3 cp s3://my-bucket/file.txt ./local-file
iam-generator analyze ec2 terminate-instances --instance-ids i-1234567890abcdef0

# API usage
curl -X POST "http://localhost:8000/analyze-resource-specific" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["aws s3 ls s3://my-bucket", "aws ec2 describe-instances --instance-ids i-1234567890abcdef0"],
    "account_id": "123456789012",
    "region": "us-east-1",
    "strict_mode": true
  }'
```

#### 2. Least Privilege Policy Optimization
Generate minimal required permissions with enhanced security conditions:

```bash
# CLI usage
PYTHONPATH=backend python -m iam_generator.main generate-role \
  --role-name OptimizedRole \
  --least-privilege \
  s3 ls s3://bucket \
  s3 cp s3://bucket/file.txt ./file \
  ec2 describe-instances

# Or with installed package
iam-generator generate-role \
  --role-name OptimizedRole \
  --least-privilege \
  s3 ls s3://bucket \
  s3 cp s3://bucket/file.txt ./file \
  ec2 describe-instances

# API usage
curl -X POST "http://localhost:8000/analyze-least-privilege" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["aws s3 ls s3://my-bucket", "aws ec2 describe-instances"],
    "account_id": "123456789012",
    "region": "us-east-1"
  }'
```

#### 3. Service Usage Summary Analysis
Get comprehensive breakdown of AWS services, actions, and permissions:

```bash
# CLI usage
PYTHONPATH=backend python -m iam_generator.main service-summary \
  s3 ls s3://bucket \
  ec2 describe-instances \
  lambda list-functions

# Or with installed package
iam-generator service-summary \
  s3 ls s3://bucket \
  ec2 describe-instances \
  lambda list-functions

# API usage
curl -X POST "http://localhost:8000/service-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["aws s3 ls s3://my-bucket", "aws ec2 describe-instances", "aws lambda list-functions"]
  }'
```

### Enhanced Web Interface Features
- **Interactive Analysis Modes**: Switch between standard, resource-specific, least privilege, and service summary analysis
- **Real-time Results**: View detailed policy documents, metadata, and statistics
- **Export Capabilities**: Download generated policies in multiple formats
- **Hot Reload Development**: Full development environment with automatic code reloading
# Get comprehensive service usage analysis
iam-generator service-summary \
  s3 ls s3://bucket \
  ec2 describe-instances \
  lambda list-functions
```

## 📊 Supported AWS Services

**52 AWS Services** with comprehensive command coverage:

| Service Category | Services | Commands |
|------------------|----------|----------|
| **Core Services** | S3, EC2, IAM, Lambda | 50+ |
| **AI/ML Services** | Bedrock, Bedrock Runtime, Textract, Rekognition, Comprehend, Polly, Transcribe, Translate | 19+ |
| **Container Services** | ECS, ECR, EKS | 25+ |
| **DevOps & CI/CD** | CodeCommit, CodeBuild, CodeDeploy, CodePipeline | 35+ |
| **Data & Analytics** | SageMaker, Glue, Athena, EMR, Redshift, OpenSearch, Kinesis | 60+ |
| **Database Services** | RDS, DynamoDB, ElastiCache | 15+ |
| **Networking** | VPC, Route53, ELB/ELBv2, Auto Scaling | 20+ |
| **Security Services** | KMS, Secrets Manager, ACM, Cognito (User Pools & Identity) | 25+ |
| **Application Services** | SNS, SQS, API Gateway, Step Functions, AppSync | 30+ |
| **Management** | CloudFormation, CloudWatch, CloudTrail, EventBridge, Systems Manager | 35+ |
| **Storage** | EFS | 5+ |
| **Identity** | STS | 2+ |

**Complete service list:**
```bash
# View all supported services and their commands
PYTHONPATH=backend python -m iam_generator.main list-services

# Or with installed package
iam-generator list-services
```

## 🔑 Output Formats

### 1. Terraform
```bash
PYTHONPATH=backend python -m iam_generator.main generate-role --output-format terraform --role-name MyRole s3 ls
# Or: iam-generator generate-role --output-format terraform --role-name MyRole s3 ls
```

### 2. CloudFormation
```bash
PYTHONPATH=backend python -m iam_generator.main generate-role --output-format cloudformation --role-name MyRole s3 ls
# Or: iam-generator generate-role --output-format cloudformation --role-name MyRole s3 ls
```

### 3. AWS CLI
```bash
PYTHONPATH=backend python -m iam_generator.main generate-role --output-format aws-cli --role-name MyRole s3 ls
# Or: iam-generator generate-role --output-format aws-cli --role-name MyRole s3 ls
```

### 4. JSON Policy
```bash
PYTHONPATH=backend python -m iam_generator.main analyze --output json s3 cp file.txt s3://bucket/
# Or: iam-generator analyze --output json s3 cp file.txt s3://bucket/
```

### 5. YAML
```bash
PYTHONPATH=backend python -m iam_generator.main analyze --output yaml ec2 describe-instances
# Or: iam-generator analyze --output yaml ec2 describe-instances
```

## 🛠️ Development Setup

### Project Structure
```
iam_generator/
├── backend/                    # Python backend
│   ├── iam_generator/          # Core Python package
│   │   ├── analyzer.py         # Permission analysis engine
│   │   ├── parser.py           # AWS CLI command parser
│   │   ├── permissions_db.py   # Permission database (52 services)
│   │   ├── role_generator.py   # IAM role generator
│   │   └── cli.py              # CLI interface
│   ├── app/                    # FastAPI web application
│   │   ├── main.py             # FastAPI app setup
│   │   ├── models.py           # API schemas
│   │   ├── services.py         # Business logic
│   │   ├── routers/            # API endpoints
│   │   └── core/               # Configuration
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Backend documentation
├── frontend/                   # React TypeScript frontend
│   ├── src/components/         # UI components (shadcn/ui)
│   └── src/lib/               # API client and utilities
├── tests/                      # Comprehensive test suite
├── docker-compose.yml          # Production deployment
├── docker-compose.dev.yml      # Development environment
├── Makefile                    # Development commands
└── docs/                       # Documentation and examples
```

### Running Tests
```bash
# Run full test suite
PYTHONPATH=backend pytest

# Run specific test categories
PYTHONPATH=backend pytest tests/test_analyzer.py      # Core analysis tests
PYTHONPATH=backend pytest tests/test_parser.py        # CLI parsing tests
PYTHONPATH=backend pytest tests/test_permissions_db.py # Database tests
PYTHONPATH=backend pytest tests/test_integration.py   # Integration tests

# Run with coverage
PYTHONPATH=backend pytest --cov=iam_generator --cov-report=html
```

### API Endpoints

The FastAPI backend provides these endpoints:

**Core Analysis:**
- `POST /analyze` - Analyze single AWS CLI command
- `POST /batch-analyze` - Analyze multiple commands with comprehensive results
- `POST /generate-role` - Generate IAM role configuration  
- `GET /services` - List supported AWS services

**Enhanced Analysis (✅ Fully Implemented):**
- `POST /analyze-resource-specific` - Generate resource-specific policies with precise ARNs
- `POST /analyze-least-privilege` - Generate minimal permission policies with security conditions
- `POST /service-summary` - Get detailed service usage summary and statistics

**Utility:**
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)

All endpoints support comprehensive request/response validation and detailed error handling.

## 🔒 Trust Policy Types

### EC2 Instance Profile
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Cross-Account Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::ACCOUNT-ID:root"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## 📈 Production Deployment

### Docker Compose Stack
The project includes production-ready deployment with:

- **Backend**: FastAPI server with Python 3.12
- **Frontend**: React TypeScript app with Vite
- **Reverse Proxy**: Nginx configuration
- **Health Checks**: Automated service monitoring
- **Persistent Storage**: Data and logs volumes
- **Security**: Non-root user, proper file permissions

### Environment Configuration
```bash
# Production environment variables
PORT=8000
PYTHONPATH=/app/src
LOG_LEVEL=info

# Optional AWS credentials (for development)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the coding guidelines
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

**Development Guidelines:**
- Follow Python PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for classes and functions
- Implement proper error handling and logging
- Focus on AWS IAM security best practices

## 📄 License

This project is proprietary software. All rights reserved. See the [LICENSE](LICENSE) file for complete terms and conditions.

**Important**: This software is protected by copyright and proprietary license terms. Commercial use requires a separate license agreement. Contact the copyright holder for licensing inquiries.

## 📞 Support & Contact

- **Documentation**: Check the [docs/](docs/) directory for detailed documentation
- **Issues**: Report bugs and request features via GitHub Issues
- **Examples**: See [docs/examples.md](docs/examples.md) for more usage examples
- **License Inquiries**: jcheco731@gmail.com

## 🚀 Roadmap

**✅ Recently Completed (v2.3.0 - June 2025):**
- ✅ **Enhanced IAM Features Suite**: Complete enterprise-grade analysis capabilities
  - ✅ Policy Validation Engine with security scoring (0-100) and AWS compliance
  - ✅ Cross-Service Dependency Analysis with automatic relationship detection
  - ✅ Conditional Policy Generation with MFA, IP, time, VPC restrictions
  - ✅ Compliance Checking for SOC2, PCI, HIPAA, GDPR frameworks
  - ✅ Security Recommendations with service-specific best practices
  - ✅ Policy Templates for common enterprise use cases
- ✅ **One-Click Role Generation**: All formats (JSON, Terraform, CloudFormation, AWS CLI) simultaneously
- ✅ **Advanced Web Interface**: Enhanced UI with PolicyValidator, CrossServiceDependencies, ConditionalPolicyGenerator
- ✅ Support for 52 AWS services with 300+ commands covering all major AWS services
- ✅ Modern React web interface with shadcn/ui components and enhanced features
- ✅ FastAPI REST API backend with 15 comprehensive endpoints
- ✅ Multiple output formats with intelligent role generation
- ✅ Resource-specific ARN generation for enhanced security
- ✅ Docker containerization with production-ready deployment and hot reload development
- ✅ Comprehensive test suite with integration testing for all enhanced features

**🚀 Future Enhancements:**
- [ ] **Additional AWS Services**: IoT, Blockchain, AR/VR, Quantum Computing services
- [ ] **Advanced Conditions**: More granular policy conditions and restrictions
- [ ] **Cost Analysis**: Permission cost optimization and resource usage analytics
- [ ] **Multi-Region Support**: Region-specific resources and permission handling
- [ ] **VS Code Extension**: Direct integration into development workflows
- [ ] **CI/CD Integration**: Pipeline integration for automated IAM analysis
- [ ] **Custom Mappings**: User-defined service definitions and permission mappings
- [ ] **Audit Capabilities**: Permission usage analysis and optimization recommendations
- [ ] **Multi-Account Support**: Enhanced cross-account access patterns
- [ ] **Performance Optimization**: Caching, query optimization, and horizontal scaling

---

**Built with ❤️ by [Jeff Pacheco](mailto:jcheco731@gmail.com)**
