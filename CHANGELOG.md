# Changelog

All notable changes to the AWS CLI IAM Permissions Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- **Expanded Service Coverage**: Now supports 44 AWS services with 200+ commands
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
