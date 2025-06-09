# IAM Generator Examples

This directory contains practical examples of using the IAM Generator tool for common AWS scenarios.

## Example 1: S3 Data Pipeline

### Scenario
A data processing pipeline that needs to:
1. Read files from a source S3 bucket
2. Process the data
3. Write results to a destination bucket
4. Clean up temporary files

### Commands
```bash
# Create commands file
cat > s3_pipeline_commands.txt << EOF
s3 ls s3://data-source-bucket/input/
s3 cp s3://data-source-bucket/input/ /tmp/input/ --recursive
s3 sync /tmp/output/ s3://data-dest-bucket/processed/ --delete
s3 rm s3://data-source-bucket/temp/ --recursive
EOF

# Analyze all commands
iam-generator batch-analyze s3_pipeline_commands.txt --output-dir ./s3-pipeline-analysis

# Generate a comprehensive role
iam-generator generate-role \
  --role-name S3DataPipelineRole \
  --trust-policy ec2 \
  --output-format terraform \
  --save s3-pipeline-role.tf \
  s3 sync s3://data-source-bucket/ s3://data-dest-bucket/ --delete
```

### Generated Terraform Output
```hcl
resource "aws_iam_role" "s3_data_pipeline_role" {
  name = "S3DataPipelineRole"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name = "S3DataPipelineRole"
    Purpose = "Data pipeline S3 operations"
  }
}

resource "aws_iam_policy" "s3_data_pipeline_role_policy" {
  name = "S3DataPipelineRolePolicy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::data-source-bucket",
          "arn:aws:s3:::data-source-bucket/*",
          "arn:aws:s3:::data-dest-bucket",
          "arn:aws:s3:::data-dest-bucket/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_data_pipeline_role_attachment" {
  role       = aws_iam_role.s3_data_pipeline_role.name
  policy_arn = aws_iam_policy.s3_data_pipeline_role_policy.arn
}
```

## Example 2: Lambda Function Deployment

### Scenario
Deploying and managing Lambda functions with proper IAM permissions.

### Commands
```bash
# Analyze Lambda operations
iam-generator analyze lambda create-function \
  --function-name data-processor \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip

# Generate Lambda execution role
iam-generator generate-role \
  --role-name LambdaExecutionRole \
  --trust-policy lambda \
  --output-format cloudformation \
  --save lambda-role.yaml \
  lambda invoke --function-name data-processor
```

### Generated CloudFormation Output
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'IAM role for Lambda function data-processor'

Resources:
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: LambdaExecutionRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Tags:
        - Key: Name
          Value: LambdaExecutionRole
        - Key: Purpose
          Value: Lambda execution role for data-processor

  LambdaExecutionRolePolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: LambdaExecutionRolePolicy
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Action:
              - lambda:InvokeFunction
            Resource:
              - !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:data-processor'
      Roles:
        - !Ref LambdaExecutionRole

Outputs:
  LambdaExecutionRoleArn:
    Description: ARN of the Lambda execution role
    Value: !GetAtt LambdaExecutionRole.Arn
    Export:
      Name: !Sub '${AWS::StackName}-LambdaExecutionRoleArn'
```

## Example 3: EC2 Instance Management

### Scenario
EC2 instances that need to manage other EC2 resources and access S3 for configuration.

### Commands
```bash
# Analyze EC2 management commands
iam-generator analyze ec2 describe-instances --filters Name=tag:Environment,Values=production
iam-generator analyze ec2 start-instances --instance-ids i-1234567890abcdef0
iam-generator analyze s3 cp s3://config-bucket/app-config.json /etc/app/

# Generate instance profile role
iam-generator generate-role \
  --role-name EC2ManagementRole \
  --trust-policy ec2 \
  --output-format aws-cli \
  --save ec2-role-commands.sh \
  ec2 describe-instances
```

### Generated AWS CLI Commands
```bash
#!/bin/bash
# AWS CLI commands to create EC2ManagementRole

# Create the IAM role
aws iam create-role \
  --role-name EC2ManagementRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# Create the policy
aws iam create-policy \
  --policy-name EC2ManagementRolePolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:DescribeInstances",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "s3:GetObject"
        ],
        "Resource": [
          "*",
          "arn:aws:s3:::config-bucket/*"
        ]
      }
    ]
  }'

# Attach policy to role
aws iam attach-role-policy \
  --role-name EC2ManagementRole \
  --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/EC2ManagementRolePolicy

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2ManagementRole

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2ManagementRole \
  --role-name EC2ManagementRole

echo "Role created successfully!"
echo "Instance Profile ARN: arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):instance-profile/EC2ManagementRole"
```

## Example 4: Cross-Account Access

### Scenario
A role in Account A needs to access resources in Account B.

### Commands
```bash
# Generate cross-account role for S3 access
iam-generator generate-role \
  --role-name CrossAccountS3Access \
  --trust-policy cross-account \
  --account-id 123456789012 \
  --output-format json \
  --save cross-account-role.json \
  s3 ls s3://shared-bucket
```

### Generated JSON Output
```json
{
  "role_name": "CrossAccountS3Access",
  "trust_policy": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::123456789012:root"
        },
        "Action": "sts:AssumeRole",
        "Condition": {
          "StringEquals": {
            "sts:ExternalId": "unique-external-id"
          }
        }
      }
    ]
  },
  "permissions_policy": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:ListBucket"
        ],
        "Resource": [
          "arn:aws:s3:::shared-bucket"
        ]
      }
    ]
  },
  "description": "Cross-account role for AWS CLI command: aws s3 ls s3://shared-bucket"
}
```

## Example 5: Complex Multi-Service Application

### Scenario
A web application that uses multiple AWS services: S3 for static assets, Lambda for processing, CloudWatch for logging, and STS for temporary credentials.

### Commands File (multi-service-app.txt)
```
s3 cp ./build/ s3://webapp-assets/ --recursive
s3 sync ./uploads/ s3://user-uploads/
lambda invoke --function-name image-processor --payload file://event.json
logs create-log-group --log-group-name /aws/lambda/image-processor
logs put-log-events --log-group-name /aws/lambda/image-processor --log-stream-name test-stream
sts get-caller-identity
```

### Batch Analysis
```bash
# Analyze all application commands
iam-generator batch-analyze multi-service-app.txt \
  --output-dir ./webapp-analysis \
  --format yaml

# Generate comprehensive application role
iam-generator generate-role \
  --role-name WebAppServiceRole \
  --trust-policy ecs \
  --output-format terraform \
  --save webapp-role.tf \
  s3 sync ./uploads/ s3://user-uploads/
```

## Example 6: DevOps Pipeline Role

### Scenario
A CI/CD pipeline that needs to deploy applications, manage infrastructure, and handle secrets.

### Pipeline Commands
```bash
# Create pipeline commands file
cat > devops_pipeline.txt << EOF
s3 cp ./artifacts/ s3://deployment-artifacts/ --recursive
lambda update-function-code --function-name api-service --zip-file fileb://api.zip
ec2 describe-instances --filters Name=tag:Environment,Values=staging
iam list-roles --path-prefix /service/
logs describe-log-groups --log-group-name-prefix /aws/lambda/
sts assume-role --role-arn arn:aws:iam::123456789012:role/deployment-role --role-session-name pipeline-deployment
EOF

# Generate DevOps role
iam-generator generate-role \
  --role-name DevOpsPipelineRole \
  --trust-policy cross-account \
  --account-id 987654321098 \
  --output-format cloudformation \
  --save devops-pipeline-role.yaml \
  lambda update-function-code --function-name api-service
```

## Usage Tips

### 1. Iterative Permission Refinement
Start with broad permissions and gradually narrow them down:

```bash
# Start with basic analysis
iam-generator analyze s3 cp ./file.txt s3://bucket/

# Test the generated role
# If access denied errors occur, analyze the failing command
iam-generator analyze s3 put-object-acl --bucket bucket --key file.txt --acl public-read

# Combine permissions from multiple analyses
```

### 2. Resource-Specific Permissions
Always prefer resource-specific ARNs over wildcards:

```bash
# Good: Specific bucket access
iam-generator analyze s3 ls s3://specific-bucket/path/

# Avoid: Wildcard access (unless truly needed)
# iam-generator analyze s3 ls  # This would generate s3:* permissions
```

### 3. Testing Generated Roles
Use AWS CLI with the generated role to test permissions:

```bash
# Assume the generated role
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/GeneratedRole \
  --role-session-name test-session

# Export credentials and test
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# Run the original command to verify permissions
aws s3 ls s3://my-bucket
```

### 4. Policy Optimization
For applications using many similar commands, consider consolidating permissions:

```bash
# Instead of individual commands, use a representative command with broader scope
iam-generator generate-role \
  --role-name S3FullAccessRole \
  s3 sync s3://source/ s3://dest/ --delete

# This generates comprehensive S3 permissions for most operations
```

## Best Practices

1. **Principle of Least Privilege**: Always start with the minimal permissions and add more only when needed
2. **Regular Reviews**: Periodically review and update IAM roles to remove unused permissions
3. **Resource Specificity**: Use specific resource ARNs instead of wildcards whenever possible
4. **Environment Separation**: Create separate roles for different environments (dev, staging, prod)
5. **Documentation**: Keep track of why specific permissions were granted
6. **Testing**: Always test generated roles in a safe environment before production use
