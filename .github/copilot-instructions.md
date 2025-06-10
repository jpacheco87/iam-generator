# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context
This is an AWS CLI IAM permissions analyzer tool built in Python. The tool accepts AWS CLI commands and returns all IAM permissions required to run those commands, helping users generate appropriate IAM roles.

## Key Components
- **AWS CLI Command Parser**: Parses and validates AWS CLI commands
- **IAM Permissions Database**: Maps AWS CLI commands to required IAM permissions
- **Permission Analyzer**: Analyzes commands and extracts required permissions
- **Role Generator**: Generates IAM role policies based on required permissions

## Coding Guidelines
- Follow Python best practices and PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all classes and functions
- Implement proper error handling and logging
- Use pytest for testing
- Focus on AWS IAM security best practices
- Ensure the tool can handle complex AWS CLI commands with multiple services

## Dependencies
- boto3 for AWS service interactions
- click for CLI interface
- pydantic for data validation
- pytest for testing
- JSON for configuration management

## Current Status
The tool currently supports 52 AWS services with 300+ total commands, including:
- **Core services**: S3, EC2, IAM, Lambda
- **AI/ML services**: Bedrock, Bedrock Runtime, Textract, Rekognition, Comprehend, Polly, Transcribe, Translate
- **Database services**: RDS, DynamoDB, ElastiCache, Redshift
- **Container services**: ECS, ECR, EKS
- **DevOps services**: CodeCommit, CodeBuild, CodeDeploy, CodePipeline
- **Data & Analytics**: SageMaker, Glue, Athena, EMR, OpenSearch, Kinesis
- **Networking**: VPC, Route53, ELB/ELBv2, Auto Scaling
- **Application services**: SNS, SQS, API Gateway, Step Functions, AppSync
- **Integration**: EventBridge, Systems Manager
- **Security**: KMS, Secrets Manager, ACM, Cognito (User Pools & Identity Pools)
- **Management**: CloudFormation, CloudWatch, CloudTrail
- **Storage**: EFS
- **Other**: STS

## Next Steps & Recommendations

### Additional Services to Consider for Future Implementation
Since all major roadmap services have been implemented, consider these additional services:
- **IoT Services** - AWS IoT Core, IoT Device Management
- **Additional Machine Learning** - Amazon SageMaker (advanced features), Amazon Personalize, Amazon Forecast
- **Blockchain** - Amazon Managed Blockchain
- **Game Development** - Amazon GameLift
- **Media Services** - AWS Elemental MediaConvert, MediaLive
- **AR/VR** - Amazon Sumerian
- **Quantum Computing** - Amazon Braket
- **Satellite** - AWS Ground Station
- **Industrial** - AWS IoT SiteWise, AWS IoT TwinMaker
- **Edge Computing** - AWS Wavelength, AWS Local Zones services

### Enhanced Features Recently Implemented ✅
1. **AI/ML Services Expansion**: ✅ COMPLETED - Added 8 new AI/ML services (Bedrock, Bedrock Runtime, Textract, Rekognition, Comprehend, Polly, Transcribe, Translate) expanding from 44 to 52 total services
2. **Resource-specific permissions**: ✅ COMPLETED - Replace wildcard `*` resources with actual resource ARNs when provided in commands (supports S3, EC2, Lambda, DynamoDB, IAM)
3. **Least privilege optimization**: ✅ COMPLETED - Analyze usage patterns and suggest minimal required permissions
4. **Service usage summary**: ✅ COMPLETED - Comprehensive analysis of service usage and permission requirements
5. **Enhanced web interface**: ✅ COMPLETED - Advanced batch analyzer with multiple analysis modes
6. **Docker containerization**: ✅ COMPLETED - Full Docker support with FastAPI backend and React frontend
7. **Production deployment**: ✅ COMPLETED - Docker Compose setup with Nginx proxy and health checks
8. **Enhanced Analysis Implementation**: ✅ COMPLETED - All advanced analysis endpoints fully functional with real data analysis
9. **Hot Reload Development Environment**: ✅ COMPLETED - Full Docker development stack with automatic code reloading for both backend and frontend

### Enhanced Features to Develop (Future Roadmap)
1. **Conditional policies**: Add support for IAM conditions based on command parameters (IP restrictions, MFA requirements, etc.)
2. **Policy validation**:
   - Check generated policies against AWS policy size limits (6144 characters)
   - Validate policy syntax and best practices
   - Detect potential security issues (overly broad permissions)
3. **Cross-service dependencies**: Automatically include dependent permissions (e.g., EC2 permissions for Lambda in VPC)
4. **Time-based permissions**: Support for temporary access patterns
5. **Multi-region considerations**: Handle region-specific resources and permissions
6. **Cost optimization**: Estimate costs associated with permissions and suggest alternatives
7. **Enhanced ARN support**: Extend resource-specific ARN generation to all 52 supported AWS services

### Code Quality Improvements
1. **Performance optimization**: Cache permission lookups and optimize database queries
2. **Error handling**: More granular error messages and recovery mechanisms
3. **Logging**: Comprehensive logging for debugging and audit purposes
4. **Configuration management**: Externalize service definitions to JSON/YAML files
5. **Plugin architecture**: Allow custom service definitions and permission mappings
6. **API rate limiting**: Handle AWS API rate limits gracefully
7. **Batch processing**: Optimize for large-scale permission analysis

### User Experience Enhancements
1. **Interactive mode**: Guide users through permission selection
2. **Policy comparison**: Compare different policy versions and highlight changes
3. **Export formats**: Support for Terraform, Pulumi, CDK formats
4. **Web interface**: ✅ COMPLETED - Browser-based GUI for non-technical users with enhanced batch analysis
5. **Integration**: Hooks for CI/CD pipelines and infrastructure as code tools
6. **Documentation**: Auto-generate documentation from permission mappings

### Security Best Practices to Implement
1. **Principle of least privilege**: Always suggest minimal required permissions
2. **Regular permission audits**: Tools to analyze and cleanup unused permissions
3. **Compliance checks**: Validate against SOC, PCI, HIPAA requirements
4. **Risk assessment**: Score policies based on potential security impact
5. **Permission boundaries**: Support for IAM permission boundaries
6. **Cross-account access**: Proper handling of cross-account scenarios

### Usage Examples
```bash
# Analyze individual commands
python -m iam_generator.main analyze dynamodb create-table
python -m iam_generator.main analyze cloudformation create-stack

# Generate roles for specific use cases
python -m iam_generator.main generate-role ecs run-task lambda invoke --trust-policy ecs

# Batch analyze multiple commands
python -m iam_generator.main batch-analyze commands.txt

# Future enhanced commands (roadmap)
python -m iam_generator.main optimize-policy existing-policy.json
python -m iam_generator.main validate-policy --compliance pci
python -m iam_generator.main audit-permissions --report-format html
```
