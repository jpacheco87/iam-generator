# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context
This is an enterprise-grade AWS CLI IAM permissions analyzer tool built in Python with React frontend. The tool accepts AWS CLI commands and returns all IAM permissions required to run those commands, helping users generate appropriate IAM roles with advanced security features and compliance checking.

## Key Components
- **AWS CLI Command Parser**: Advanced parsing and validation of AWS CLI commands with parameter extraction
- **IAM Permissions Database**: Comprehensive mapping of 52 AWS services with 300+ commands to required IAM permissions
- **Permission Analyzer**: Multi-mode analysis (standard, resource-specific, least privilege, service summary)
- **Role Generator**: Generates complete IAM roles with trust policies in multiple formats (JSON, Terraform, CloudFormation, AWS CLI)
- **Policy Validator**: Enterprise-grade policy validation with security scoring and AWS compliance checking
- **Enhanced IAM Services**: Cross-service dependency analysis, conditional policy generation, and compliance frameworks
- **Web Interface**: Modern React frontend with shadcn/ui components and advanced batch analysis
- **REST API**: FastAPI backend with comprehensive endpoints for all features

## Coding Guidelines
- Follow Python best practices and PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all classes and functions
- Implement proper error handling and logging using Python logging module
- Use pytest for comprehensive testing with fixtures and parameterized tests
- Follow AWS IAM security best practices and principle of least privilege
- Ensure the tool can handle complex AWS CLI commands with multiple services and parameters
- Use Pydantic models for data validation and API request/response handling
- Follow React best practices with TypeScript and functional components
- Use proper state management and error boundaries in React components

## Dependencies & Architecture

### Backend Dependencies
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management using Python type annotations
- **uvicorn**: ASGI server implementation for FastAPI
- **pytest**: Testing framework with fixtures and parameterized tests
- **boto3**: AWS SDK for Python (for future AWS service interactions)
- **click**: Command-line interface creation toolkit

### Frontend Dependencies
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server with HMR
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern component library built on Radix UI
- **Lucide React**: Beautiful & consistent icon toolkit

### Infrastructure
- **Docker**: Multi-stage containerization for both backend and frontend
- **Docker Compose**: Orchestration with development and production configurations
- **Nginx**: Reverse proxy and static file serving in production
- **Hot Reload**: Development environment with automatic code reloading

## Current Status & Capabilities

### Supported AWS Services (52 Total)
The tool currently supports 52 AWS services with 300+ total commands:

#### Core Services
- **S3**: Bucket operations, object management, lifecycle policies, versioning
- **EC2**: Instance management, security groups, volumes, key pairs, AMIs
- **IAM**: User/role/policy management, access key operations, permissions boundaries
- **Lambda**: Function management, layer operations, event source mappings

#### AI/ML Services (8 Services)
- **Bedrock**: Foundation model access and management
- **Bedrock Runtime**: Model invocation with streaming support
- **Textract**: Document text and data extraction, asynchronous processing
- **Rekognition**: Image/video analysis, face detection, celebrity identification
- **Comprehend**: Natural language processing, sentiment analysis, entity detection
- **Polly**: Text-to-speech conversion with multiple voice options
- **Transcribe**: Speech-to-text conversion, transcription jobs
- **Translate**: Language translation between supported languages

#### Database Services
- **RDS**: Multi-engine database support, snapshots, parameter groups
- **DynamoDB**: NoSQL operations, table management, global tables
- **ElastiCache**: In-memory caching, cluster management
- **Redshift**: Data warehouse operations, cluster management

#### Container & DevOps Services
- **ECS**: Cluster, service, and task management
- **ECR**: Container registry operations, image management
- **EKS**: Kubernetes cluster management
- **CodeCommit**: Git repository management
- **CodeBuild**: Build automation and project management
- **CodeDeploy**: Deployment automation
- **CodePipeline**: Pipeline orchestration

#### Data & Analytics
- **SageMaker**: Machine learning model management
- **Glue**: ETL operations, data catalog management
- **Athena**: Serverless query service
- **EMR**: Big data processing clusters
- **OpenSearch**: Search and analytics service
- **Kinesis**: Real-time data streaming

#### Networking & Infrastructure
- **VPC**: Virtual private cloud management, subnets, route tables
- **Route53**: DNS management, health checks
- **ELB/ELBv2**: Load balancer management (Classic, Application, Network)
- **Auto Scaling**: Dynamic scaling capabilities

#### Application & Integration Services
- **SNS**: Simple notification service, topic management
- **SQS**: Simple queue service, queue management
- **API Gateway**: REST and WebSocket API management
- **Step Functions**: State machine orchestration
- **AppSync**: GraphQL API management
- **EventBridge**: Event-driven architecture, rule management

#### Security & Management
- **KMS**: Key management service, encryption operations
- **Secrets Manager**: Secret storage and rotation
- **ACM**: Certificate management, SSL/TLS operations
- **Cognito**: User pools and identity pools management
- **CloudFormation**: Infrastructure as code, stack management
- **CloudWatch**: Monitoring, logging, alarm management
- **CloudTrail**: API auditing and compliance logging
- **Systems Manager**: Parameter store, session manager, patch management

#### Storage & Other
- **EFS**: Elastic file system management
- **STS**: Security token service, temporary credentials

## ✅ Enhanced Features Implemented (v2.3.0)

### 1. Policy Validation Engine
- **AWS Policy Limits**: Validate against 6144 character size limit
- **Security Scoring**: 0-100 scoring system with detailed breakdown
- **Best Practices**: Compliance with AWS security best practices
- **Issue Detection**: Vulnerability detection with remediation recommendations
- **Policy Types**: Support for managed and inline policy validation

### 2. Cross-Service Dependency Analysis
- **Automatic Detection**: Maps service relationships (Lambda → CloudWatch Logs, ECS → ECR, etc.)
- **Implicit Dependencies**: Detects hidden service dependencies for complete permission coverage
- **Visualization**: Interactive dependency mapping in web interface
- **Comprehensive Database**: Extensive service relationship mapping

### 3. Conditional Policy Generation
- **MFA Requirements**: Multi-factor authentication enforcement
- **IP Restrictions**: CIDR-based IP address filtering
- **Time Controls**: Date and time-based access restrictions
- **VPC Security**: Network-level access controls
- **Tag Conditions**: Resource tag-based access control

### 4. Policy Optimization
- **Size Reduction**: Intelligent statement consolidation
- **Security Enhancement**: Automatic security improvements
- **Duplicate Removal**: Elimination of redundant permissions
- **Resource Optimization**: Suggestions for resource-specific improvements

### 5. Compliance Checking
- **SOC2**: Service Organization Control 2 compliance
- **PCI DSS**: Payment Card Industry Data Security Standard
- **HIPAA**: Health Insurance Portability and Accountability Act
- **GDPR**: General Data Protection Regulation
- **Detailed Reports**: Compliance scoring with remediation steps

### 6. Security Recommendations
- **Service-Specific**: Tailored recommendations for each AWS service
- **Best Practices**: Security configuration guidance
- **Risk Assessment**: Security risk scoring and mitigation advice
- **Vulnerability Detection**: Security issue identification

### 7. Policy Templates
- **Lambda Execution**: Pre-built Lambda roles with best practices
- **S3 Operations**: Read-only, read-write, and admin access patterns
- **EC2 Management**: Instance control with security boundaries
- **RDS Access**: Database roles with security controls
- **Cross-Account**: Secure cross-account access templates

### 8. One-Click Role Generation
- **All Formats**: Generate JSON, Terraform, CloudFormation, and AWS CLI simultaneously
- **Enhanced UX**: Single API call generates all output formats
- **Trust Policies**: Support for EC2, Lambda, ECS, and custom trust relationships
- **Complete Roles**: Full role definitions ready for deployment

### 9. Enhanced Web Interface
- **5 Main Tabs**: Analyze, Generate, Batch, Validate, Advanced
- **Interactive Components**: Real-time analysis and validation
- **Batch Processing**: Advanced batch analyzer with multiple modes
- **Responsive Design**: Modern UI with shadcn/ui components

### 10. Advanced Analysis Modes
- **Resource-Specific**: Precise ARN targeting instead of wildcards
- **Least Privilege**: Minimal permission optimization
- **Service Summary**: Comprehensive usage analysis
- **Dependency Mapping**: Cross-service relationship analysis

## Development Guidelines

### Backend Development
- Use FastAPI with Pydantic models for all API endpoints
- Implement comprehensive error handling with appropriate HTTP status codes
- Use Python type hints and docstrings for all functions and classes
- Follow dependency injection patterns for services
- Implement proper logging with structured logging for production
- Use pytest with fixtures for comprehensive testing

### Frontend Development
- Use React with TypeScript and functional components
- Implement proper error boundaries and loading states
- Use React hooks for state management
- Follow shadcn/ui component patterns
- Implement proper TypeScript interfaces for API responses
- Use proper form validation and user feedback

### API Design
- Follow RESTful principles with clear endpoint naming
- Use appropriate HTTP methods and status codes
- Implement proper request/response models with Pydantic
- Include comprehensive API documentation with FastAPI docs
- Implement proper error responses with actionable messages

### Testing Strategy
- Unit tests for individual functions and classes
- Integration tests for API endpoints
- Frontend component testing with proper mocking
- End-to-end testing for critical workflows
- Performance testing for batch operations

## Usage Examples

### CLI Usage
```bash
# Analyze individual commands (from project root)
PYTHONPATH=backend python -m iam_generator.main analyze dynamodb create-table
PYTHONPATH=backend python -m iam_generator.main analyze s3 ls s3://my-bucket

# Generate roles for specific use cases
PYTHONPATH=backend python -m iam_generator.main generate-role --role-name S3ReadRole s3 ls s3://my-bucket
PYTHONPATH=backend python -m iam_generator.main generate-role --trust-policy lambda lambda invoke --function-name test

# Batch analyze multiple commands
PYTHONPATH=backend python -m iam_generator.main batch-analyze commands.txt

# With installed package
cd backend && pip install -e . && cd ..
iam-generator analyze dynamodb create-table
iam-generator generate-role --role-name DynamoRole dynamodb create-table
```

### Web Interface Usage
```bash
# Complete application stack
docker-compose up -d

# Development environment with hot reload
docker-compose -f docker-compose.dev.yml up -d

# Access points:
# Web UI: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### API Usage
```bash
# Enhanced IAM features
curl -X POST "http://localhost:8000/enhanced/validate-policy" \
  -H "Content-Type: application/json" \
  -d '{"policy": {...}, "policy_type": "managed"}'

curl -X POST "http://localhost:8000/enhanced/cross-service-dependencies" \
  -H "Content-Type: application/json" \
  -d '{"commands": ["lambda invoke --function-name test"], "include_implicit": true}'

curl -X POST "http://localhost:8000/enhanced/conditional-policy" \
  -H "Content-Type: application/json" \
  -d '{"commands": ["s3 ls"], "conditions": {"require_mfa": true}}'

# One-click role generation
curl -X POST "http://localhost:8000/generate-role-all-formats" \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 ls", "role_name": "S3Role", "trust_policy": "ec2"}'
```

## Future Roadmap

### Next Priority Features
1. **Enhanced ARN Support**: Extend resource-specific ARN generation to all 52 services
2. **Policy Size Optimization**: Advanced algorithms for policy size reduction
3. **Multi-Region Support**: Region-specific resource handling
4. **Cost Analysis**: Permission-based cost estimation
5. **Plugin Architecture**: Custom service definition support

### Additional AWS Services
- **IoT Services**: AWS IoT Core, IoT Device Management
- **Media Services**: Elemental MediaConvert, MediaLive
- **Blockchain**: Managed Blockchain
- **Quantum Computing**: Amazon Braket
- **Game Development**: GameLift

### Integration Enhancements
- **CI/CD Integration**: GitHub Actions, GitLab CI support
- **Infrastructure as Code**: Enhanced Terraform, Pulumi, CDK support
- **SIEM Integration**: Security event monitoring
- **Audit Logging**: Comprehensive audit trail

## Security Best Practices
1. **Principle of Least Privilege**: Always generate minimal required permissions
2. **Security Conditions**: Automatic injection of appropriate security conditions
3. **Resource Specificity**: Use specific ARNs instead of wildcards when possible
4. **Compliance**: Validate against industry standards (SOC2, PCI, HIPAA, GDPR)
5. **Regular Audits**: Support for permission cleanup and optimization
6. **Cross-Account Security**: Proper handling of cross-account access patterns
