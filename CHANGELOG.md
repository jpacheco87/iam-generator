# Changelog

All notable changes to the AWS CLI IAM Permissions Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.3.0] - 2025-06-11

### Added - Enhanced IAM Features Suite ✨
- **Policy Validation Engine**: Comprehensive validation with enterprise-grade analysis
  - AWS policy size limit validation (6144 characters)
  - Security scoring system (0-100) with detailed breakdown
  - Best practices compliance checking
  - Vulnerability detection with remediation recommendations
  - Support for managed and inline policy types
- **Cross-Service Dependency Analysis**: Intelligent service relationship detection
  - Automatic mapping of service dependencies (Lambda → CloudWatch Logs, ECS → ECR, etc.)
  - Implicit dependency detection for complete permission coverage
  - Interactive dependency visualization
  - Comprehensive relationship database
- **Conditional Policy Generation**: Advanced security restrictions
  - MFA requirements with configurable enforcement
  - IP address restrictions with CIDR support
  - Time-based access controls with date/time ranges
  - VPC restrictions for network-level security
  - Resource tag-based conditions
- **Policy Optimization**: Intelligent policy improvement
  - Automatic size reduction with statement consolidation
  - Security enhancement recommendations
  - Duplicate permission removal
  - Resource optimization suggestions
- **Compliance Checking**: Multi-framework compliance analysis
  - SOC2 compliance with detailed scoring
  - PCI DSS requirements validation
  - HIPAA compliance checking
  - GDPR data protection compliance
  - Detailed compliance reports with remediation steps
- **Security Recommendations**: Service-specific best practices
  - Tailored recommendations for each AWS service
  - Vulnerability detection and mitigation advice
  - Security configuration guidance
  - Risk assessment and scoring
- **Policy Templates**: Enterprise-ready templates
  - Lambda execution roles with best practices
  - S3 access patterns (read-only, read-write, admin)
  - EC2 management roles with instance controls
  - RDS access roles with database security
  - Cross-account access templates

### Added - One-Click Role Generation 🚀
- **New API Endpoint**: `/generate-role-all-formats` for simultaneous format generation
- **Enhanced Role Generator**: Generate all output formats in single API call
  - JSON role definition with trust and permissions policies
  - Complete Terraform HCL configuration
  - CloudFormation YAML/JSON templates
  - AWS CLI commands ready for execution
- **Improved User Experience**: Eliminated format selection requirement
  - Single click generates all formats
  - 5-tab display for easy format switching
  - Reduced user interaction from 5+ clicks to 1 click

### Added - Enhanced Web Interface Components
- **PolicyValidator Component**: Interactive policy validation interface
  - Real-time security scoring with visual indicators
  - Issue detection with severity levels
  - Actionable recommendations display
  - Best practices compliance tracking
- **CrossServiceDependencies Component**: Dependency analysis interface
  - Interactive service relationship visualization
  - Dependency detection with explanation
  - Comprehensive service mapping display
- **ConditionalPolicyGenerator Component**: Advanced policy creation interface
  - Multiple restriction type selection
  - Real-time policy preview
  - Security condition configuration
  - Template-based policy generation

### Enhanced - API Architecture
- **7 New Enhanced Endpoints**: Complete enterprise IAM feature set
  - `/enhanced/validate-policy` - Policy validation with scoring
  - `/enhanced/cross-service-dependencies` - Service relationship analysis
  - `/enhanced/conditional-policy` - Advanced policy generation
  - `/enhanced/optimize-policy` - Policy improvement recommendations
  - `/enhanced/security-recommendations/{service}` - Service-specific guidance
  - `/enhanced/policy-templates` - Enterprise template library
  - `/enhanced/compliance-check/{framework}` - Compliance validation
- **Enhanced Error Handling**: Comprehensive error responses with actionable messages
- **Improved Response Models**: Detailed Pydantic models for all enhanced features

### Enhanced - Frontend Architecture
- **New Tab Structure**: Enhanced navigation with Validate and Advanced tabs
- **API Integration**: Complete TypeScript interfaces for all enhanced features
- **Component Architecture**: Modular design with reusable components
- **State Management**: Improved state handling for complex analysis workflows

### Fixed - Role Generation Issues
- **Parameter Handling**: Fixed "400: Either analysis_result or commands must be provided" error
- **Service Layer**: Corrected role generator service implementation
- **CloudFormation Serialization**: Fixed JSON serialization issues
- **Output Format Generation**: Ensured all formats generate properly with appropriate content

### Enhanced - Documentation
- **README Updates**: Comprehensive documentation of all enhanced features
- **Feature Documentation**: Detailed guides for each enhanced capability
- **API Documentation**: Complete endpoint documentation with examples
- **Deployment Guides**: Updated deployment instructions with enhanced features

### Validated - Comprehensive Testing
- **Enhanced Feature Testing**: Complete test coverage for all 7 enhanced endpoints
- **Role Generation Testing**: Validation of all output formats and trust policy types
- **Integration Testing**: End-to-end testing of enhanced workflow
- **UI Component Testing**: Validation of all new React components

## [2.2.0] - 2025-06-10

### Added
- **Enhanced Analysis Functionality**: Complete implementation of advanced analysis endpoints
  - **Resource-Specific Policy Generation**: Generate policies with precise ARN targeting instead of wildcards
  - **Least Privilege Optimization**: Create minimal permission policies with enhanced security conditions
  - **Service Usage Summary**: Comprehensive breakdown of AWS services, actions, and resources
- **Hot Reload Development Environment**: Full Docker development stack with automatic code reloading
  - Backend hot reload with uvicorn `--reload` and file change monitoring
  - Frontend hot reload with Vite HMR (Hot Module Replacement)
  - Development-specific Docker Compose configuration with volume mounts
- **Enhanced Web Interface**: Advanced batch analyzer with multiple analysis modes
  - Interactive mode switching between standard, resource-specific, least privilege, and service summary
  - Real-time policy generation and metadata viewing
  - Fixed type compatibility issues between frontend and backend APIs
  - Improved user experience with better error handling and responsive design

### Enhanced
- **Backend API Endpoints**: All advanced router endpoints now call actual analyzer methods
  - `/analyze-resource-specific`: Returns policies with specific ARNs like `arn:aws:s3:::my-bucket`
  - `/analyze-least-privilege`: Returns optimized policies with security conditions
  - `/service-summary`: Returns detailed service breakdowns with comprehensive statistics
- **Frontend Components**: Fixed batch analysis functionality and improved type safety
  - Resolved command vs original_command field mismatches
  - Updated API interfaces to match backend response structure
  - Enhanced BatchAnalyzer component with proper error handling
- **Development Workflow**: Streamlined development process with working hot reload
  - Backend automatically reloads on Python file changes
  - Frontend automatically updates on TypeScript/React changes
  - Improved Docker entrypoint script with reload detection

### Fixed
- **Batch Analysis Blank Page Issue**: Resolved type mismatches causing UI rendering failures
- **Enhanced Analysis Endpoints**: Fixed stub implementations that were returning placeholder data
- **API Response Structure**: Aligned frontend interfaces with backend response formats
- **Docker Development Environment**: Proper volume mounts and environment configuration

### Validated
- **All Enhanced Analysis Modes**: Confirmed working with real data analysis
- **Hot Reload Functionality**: Verified both backend and frontend automatic reloading
- **Docker Development Stack**: Full development environment working correctly
- **API Endpoint Integration**: All advanced endpoints returning actual analysis results

## [2.1.0] - 2025-06-09

### Added
- **AI/ML Services Expansion**: Added 8 new artificial intelligence and machine learning services
  - **Amazon Bedrock**: Foundation model access and management
    - `bedrock`: List and get foundation models
    - `bedrock-runtime`: Invoke models with streaming support
  - **Amazon Textract**: Document text and data extraction
    - Document text detection, analysis, and asynchronous processing
  - **Amazon Rekognition**: Image and video analysis
    - Face detection, label recognition, and celebrity identification
  - **Amazon Comprehend**: Natural language processing
    - Sentiment analysis, entity detection, and key phrase extraction
  - **Amazon Polly**: Text-to-speech conversion
    - Speech synthesis with multiple voice options
  - **Amazon Transcribe**: Speech-to-text conversion
    - Audio transcription jobs and real-time processing
  - **Amazon Translate**: Language translation
    - Text translation between supported languages
  - **Enhanced Coverage**: Database expanded from 44 to 52 services (+18% increase)

### Enhanced
- **Auto-Discovery System**: Improved fallback mechanism for unknown services
  - Enhanced pattern-based permission mapping for AI/ML services
  - Better confidence scoring for automatically discovered permissions
  - Optimized response times by adding frequently-requested services to manual database
- **Container Performance**: AI/ML services now use fast manual lookup instead of slower scraper fallback
- **Service Documentation**: Updated comprehensive service list and examples

### Validated
- **Container Integration**: All new services verified working in Docker containers
- **API Functionality**: REST API endpoints confirmed returning correct permissions for all new services
- **Database Integrity**: Validated 52-service count and proper permission mappings

## [2.0.1] - 2025-06-09

### Added
- Comprehensive changelog documentation
- Enhanced documentation for deployment and frontend development

### Fixed
- EC2 security group commands now properly recognized in batch analysis
- Resolved warnings for `create-security-group` and `authorize-security-group-ingress` commands

## [2.0.0] - 2025-06-09

### Added
- **Docker Support**: Full containerization with Docker Compose setup
  - Multi-stage Docker builds for both backend and frontend
  - Production-ready deployment with Nginx proxy
  - Development environment with hot reloading
  - Health checks and proper logging
- **Enhanced Web Interface**: Modern React-based frontend
  - Advanced batch analyzer with multiple analysis modes
  - Real-time command analysis
  - Enhanced role generator with trust policy support
  - Responsive UI with Tailwind CSS and shadcn/ui components
- **Resource-Specific Permissions**: ARN generation for actual resources
  - S3 bucket and object ARNs from command parameters
  - EC2 instance, volume, and security group ARNs
  - Lambda function ARNs
  - DynamoDB table ARNs
  - IAM user, role, and policy ARNs
- **Least Privilege Optimization**: Advanced permission analysis
  - Usage pattern analysis
  - Minimal required permission suggestions
  - Permission optimization recommendations
- **Service Usage Summary**: Comprehensive analysis features
  - Detailed service usage statistics
  - Permission requirement summaries
  - Cross-service dependency analysis
- **Production Deployment**: Enterprise-ready deployment options
  - Docker Compose with Nginx reverse proxy
  - Environment-specific configurations
  - Health monitoring and logging
  - SSL/TLS support ready

### Enhanced
- **Expanded Service Coverage**: Now supports 44 AWS services with 200+ commands (expanded to 52 services in v2.1.0)
  - **Core Services**: S3, EC2, IAM, Lambda
  - **Database Services**: RDS, DynamoDB, ElastiCache, Redshift
  - **Container Services**: ECS, ECR, EKS
  - **DevOps Services**: CodeCommit, CodeBuild, CodeDeploy, CodePipeline
  - **Data & Analytics**: SageMaker, Glue, Athena, EMR, OpenSearch, Kinesis
  - **Networking**: VPC, Route53, ELB/ELBv2, Auto Scaling
  - **Application Services**: SNS, SQS, API Gateway, Step Functions, AppSync
  - **Integration**: EventBridge, Systems Manager
  - **Security**: KMS, Secrets Manager, ACM, Cognito (User Pools & Identity Pools)
  - **Management**: CloudFormation, CloudWatch, CloudTrail
  - **Storage**: EFS
  - **Other**: STS

### Improved
- **Command Parser**: Enhanced AWS CLI command parsing with better parameter extraction
- **Error Handling**: More robust error handling and user feedback
- **Performance**: Optimized permission lookups and database queries
- **Documentation**: Comprehensive guides for deployment and development

## [1.5.0] - 2025-06-09

### Added
- **Security Group Commands**: Complete EC2 security group management
  - `create-security-group`: Create security groups with VPC support
  - `delete-security-group`: Delete security groups
  - `authorize-security-group-ingress`: Add inbound rules
  - `authorize-security-group-egress`: Add outbound rules
  - `revoke-security-group-ingress`: Remove inbound rules
  - `revoke-security-group-egress`: Remove outbound rules
- **Enhanced EC2 Support**: Expanded EC2 command coverage
  - Volume management commands
  - Instance lifecycle operations
  - Network interface management

### Fixed
- Improved permission mapping accuracy for EC2 commands
- Better resource ARN pattern matching
- Enhanced error messages for unsupported commands

## [1.4.0] - 2025-06-09

### Added
- **Cognito Services**: Identity and User Pool management
  - Cognito Identity Pools: Create, delete, describe operations
  - Cognito User Pools: User management, authentication operations
- **ACM (Certificate Manager)**: SSL/TLS certificate management
  - Certificate lifecycle operations
  - Import/export functionality
- **AppSync**: GraphQL API management
  - API creation and data source management
  - Resolver and schema operations

### Enhanced
- **Systems Manager**: Expanded SSM command support
  - Parameter Store operations
  - Session Manager functionality
  - Command execution capabilities

## [1.3.0] - 2025-06-09

### Added
- **EventBridge**: Event-driven architecture support
  - Rule management and target configuration
  - Event publishing and monitoring
- **OpenSearch**: Search and analytics service
  - Domain management and configuration
  - Index and cluster operations
- **Data Analytics Services**:
  - **EMR**: Big data processing clusters
  - **Redshift**: Data warehouse operations
  - **Athena**: Serverless query service

### Enhanced
- **Step Functions**: State machine orchestration
  - Workflow creation and execution
  - State machine monitoring

## [1.2.0] - 2025-06-09

### Added
- **Container Services**: Complete containerization support
  - **ECS**: Cluster, service, and task management
  - **ECR**: Container registry operations
  - **EKS**: Kubernetes cluster management
- **DevOps Pipeline**: CI/CD service integration
  - **CodeCommit**: Git repository management
  - **CodeBuild**: Build automation
  - **CodeDeploy**: Deployment automation
  - **CodePipeline**: Pipeline orchestration

### Enhanced
- **Database Services**: Expanded database support
  - **RDS**: Multi-engine database support
  - **DynamoDB**: NoSQL operations
  - **ElastiCache**: In-memory caching

## [1.1.0] - 2025-06-09

### Added
- **Core AWS Services**: Foundation service support
  - **S3**: Bucket and object operations
  - **EC2**: Instance and resource management
  - **IAM**: Identity and access management
  - **Lambda**: Serverless function operations
- **Infrastructure Services**:
  - **VPC**: Network infrastructure
  - **CloudFormation**: Infrastructure as code
  - **CloudWatch**: Monitoring and logging
  - **CloudTrail**: API auditing

### Enhanced
- **Load Balancing**: Application and network load balancers
  - Classic Load Balancer (ELB)
  - Application/Network Load Balancer (ELBv2)
- **Auto Scaling**: Dynamic scaling capabilities
- **Route53**: DNS management

## [1.0.0] - 2025-06-09

### Added
- **Initial Release**: Core IAM permissions analyzer
- **CLI Interface**: Command-line tool for AWS CLI command analysis
- **Batch Processing**: Analyze multiple commands from file input
- **Role Generation**: Generate IAM roles with proper trust policies
- **Permission Database**: Comprehensive mapping of AWS CLI commands to IAM permissions
- **Policy Generation**: Create JSON IAM policies from command analysis
- **Basic Web Interface**: Simple HTML interface for command analysis

### Features
- Analyze individual AWS CLI commands
- Generate least-privilege IAM policies
- Support for basic AWS services (S3, EC2, IAM)
- JSON policy output
- Command validation and error handling

---

## Development Guidelines

### Version Numbering
- **Major (X.0.0)**: Breaking changes, major feature releases
- **Minor (X.Y.0)**: New features, service additions, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, minor improvements, backward compatible

### Release Process
1. Update version numbers in `setup.py` and relevant files
2. Update this CHANGELOG.md with new features and fixes
3. Create git tag with version number
4. Build and test Docker images
5. Update deployment documentation

### Contributing
When contributing to this project:
1. Add entries to the [Unreleased] section
2. Follow the established format for changelog entries
3. Include appropriate category (Added, Changed, Deprecated, Removed, Fixed, Security)
4. Reference issue numbers when applicable

---

## Support and Documentation

- **Repository**: [AWS CLI IAM Permissions Analyzer](https://github.com/jpacheco87/iam-generator)
- **Documentation**: See `docs/` directory for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Docker**: See [DOCKER.md](DOCKER.md) for containerization details
- **Frontend**: See [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) for UI development

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
