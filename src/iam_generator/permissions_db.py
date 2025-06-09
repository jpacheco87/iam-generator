"""
IAM Permissions Database

This module provides a comprehensive database of AWS CLI commands and their required IAM permissions.
It includes mappings from AWS CLI actions to the corresponding IAM permissions needed.
"""

import json
import os
from typing import Dict, List, Set, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field


class IAMPermission(BaseModel):
    """Represents an IAM permission."""
    
    action: str = Field(description="IAM action (e.g., 's3:ListBucket')")
    resource: str = Field(default="*", description="Resource ARN or pattern")
    condition: Optional[Dict] = Field(default=None, description="IAM condition block")
    effect: str = Field(default="Allow", description="Permission effect (Allow/Deny)")


class CommandPermissions(BaseModel):
    """Permissions required for a specific AWS CLI command."""
    
    service: str = Field(description="AWS service name")
    action: str = Field(description="CLI action name")
    permissions: List[IAMPermission] = Field(description="Required IAM permissions")
    description: str = Field(default="", description="Command description")
    resource_patterns: List[str] = Field(default_factory=list, description="Resource ARN patterns")


class IAMPermissionsDatabase:
    """Database of AWS CLI commands and their required IAM permissions."""
    
    def __init__(self):
        """Initialize the permissions database."""
        self._permissions_map: Dict[str, Dict[str, CommandPermissions]] = {}
        self._load_permissions_data()
    
    def _load_permissions_data(self):
        """Load permissions data from built-in database."""
        # Core IAM permissions mapping
        self._permissions_map = {
            "s3": {
                "ls": CommandPermissions(
                    service="s3",
                    action="ls",
                    permissions=[
                        IAMPermission(action="s3:ListBucket", resource="arn:aws:s3:::*"),
                        IAMPermission(action="s3:ListAllMyBuckets", resource="*"),
                    ],
                    description="List S3 buckets and objects",
                    resource_patterns=["arn:aws:s3:::*"]
                ),
                "cp": CommandPermissions(
                    service="s3",
                    action="cp",
                    permissions=[
                        IAMPermission(action="s3:GetObject", resource="*"),
                        IAMPermission(action="s3:PutObject", resource="*"),
                        IAMPermission(action="s3:ListBucket", resource="*"),
                    ],
                    description="Copy files to/from S3",
                    resource_patterns=["arn:aws:s3:::*", "arn:aws:s3:::*/*"]
                ),
                "sync": CommandPermissions(
                    service="s3",
                    action="sync",
                    permissions=[
                        IAMPermission(action="s3:GetObject", resource="*"),
                        IAMPermission(action="s3:PutObject", resource="*"),
                        IAMPermission(action="s3:DeleteObject", resource="*"),
                        IAMPermission(action="s3:ListBucket", resource="*"),
                    ],
                    description="Sync directories with S3",
                    resource_patterns=["arn:aws:s3:::*", "arn:aws:s3:::*/*"]
                ),
                "rm": CommandPermissions(
                    service="s3",
                    action="rm",
                    permissions=[
                        IAMPermission(action="s3:DeleteObject", resource="*"),
                        IAMPermission(action="s3:ListBucket", resource="*"),
                    ],
                    description="Remove S3 objects",
                    resource_patterns=["arn:aws:s3:::*", "arn:aws:s3:::*/*"]
                ),
                "mb": CommandPermissions(
                    service="s3",
                    action="mb",
                    permissions=[
                        IAMPermission(action="s3:CreateBucket", resource="*"),
                    ],
                    description="Create S3 bucket",
                    resource_patterns=["arn:aws:s3:::*"]
                ),
                "rb": CommandPermissions(
                    service="s3",
                    action="rb",
                    permissions=[
                        IAMPermission(action="s3:DeleteBucket", resource="*"),
                        IAMPermission(action="s3:ListBucket", resource="*"),
                    ],
                    description="Remove S3 bucket",
                    resource_patterns=["arn:aws:s3:::*"]
                ),
            },
            "ec2": {
                "describe-instances": CommandPermissions(
                    service="ec2",
                    action="describe-instances",
                    permissions=[
                        IAMPermission(action="ec2:DescribeInstances", resource="*"),
                    ],
                    description="Describe EC2 instances",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*"]
                ),
                "start-instances": CommandPermissions(
                    service="ec2",
                    action="start-instances",
                    permissions=[
                        IAMPermission(action="ec2:StartInstances", resource="*"),
                    ],
                    description="Start EC2 instances",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*"]
                ),
                "stop-instances": CommandPermissions(
                    service="ec2",
                    action="stop-instances",
                    permissions=[
                        IAMPermission(action="ec2:StopInstances", resource="*"),
                    ],
                    description="Stop EC2 instances",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*"]
                ),
                "terminate-instances": CommandPermissions(
                    service="ec2",
                    action="terminate-instances",
                    permissions=[
                        IAMPermission(action="ec2:TerminateInstances", resource="*"),
                    ],
                    description="Terminate EC2 instances",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*"]
                ),
                "run-instances": CommandPermissions(
                    service="ec2",
                    action="run-instances",
                    permissions=[
                        IAMPermission(action="ec2:RunInstances", resource="*"),
                        IAMPermission(action="ec2:DescribeImages", resource="*"),
                        IAMPermission(action="ec2:DescribeInstanceTypes", resource="*"),
                        IAMPermission(action="ec2:DescribeVpcs", resource="*"),
                        IAMPermission(action="ec2:DescribeSubnets", resource="*"),
                        IAMPermission(action="ec2:DescribeSecurityGroups", resource="*"),
                    ],
                    description="Launch EC2 instances",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*", "arn:aws:ec2:*:*:volume/*"]
                ),
                "describe-volumes": CommandPermissions(
                    service="ec2",
                    action="describe-volumes",
                    permissions=[
                        IAMPermission(action="ec2:DescribeVolumes", resource="*"),
                    ],
                    description="Describe EBS volumes",
                    resource_patterns=["arn:aws:ec2:*:*:volume/*"]
                ),
                "create-volume": CommandPermissions(
                    service="ec2",
                    action="create-volume",
                    permissions=[
                        IAMPermission(action="ec2:CreateVolume", resource="*"),
                    ],
                    description="Create EBS volume",
                    resource_patterns=["arn:aws:ec2:*:*:volume/*"]
                ),
                "describe-security-groups": CommandPermissions(
                    service="ec2",
                    action="describe-security-groups",
                    permissions=[
                        IAMPermission(action="ec2:DescribeSecurityGroups", resource="*"),
                    ],
                    description="Describe security groups",
                    resource_patterns=["arn:aws:ec2:*:*:security-group/*"]
                ),
            },
            "iam": {
                "list-users": CommandPermissions(
                    service="iam",
                    action="list-users",
                    permissions=[
                        IAMPermission(action="iam:ListUsers", resource="*"),
                    ],
                    description="List IAM users",
                    resource_patterns=["arn:aws:iam::*:user/*"]
                ),
                "list-roles": CommandPermissions(
                    service="iam",
                    action="list-roles",
                    permissions=[
                        IAMPermission(action="iam:ListRoles", resource="*"),
                    ],
                    description="List IAM roles",
                    resource_patterns=["arn:aws:iam::*:role/*"]
                ),
                "get-user": CommandPermissions(
                    service="iam",
                    action="get-user",
                    permissions=[
                        IAMPermission(action="iam:GetUser", resource="*"),
                    ],
                    description="Get IAM user details",
                    resource_patterns=["arn:aws:iam::*:user/*"]
                ),
                "create-user": CommandPermissions(
                    service="iam",
                    action="create-user",
                    permissions=[
                        IAMPermission(action="iam:CreateUser", resource="*"),
                    ],
                    description="Create IAM user",
                    resource_patterns=["arn:aws:iam::*:user/*"]
                ),
                "delete-user": CommandPermissions(
                    service="iam",
                    action="delete-user",
                    permissions=[
                        IAMPermission(action="iam:DeleteUser", resource="*"),
                    ],
                    description="Delete IAM user",
                    resource_patterns=["arn:aws:iam::*:user/*"]
                ),
                "attach-user-policy": CommandPermissions(
                    service="iam",
                    action="attach-user-policy",
                    permissions=[
                        IAMPermission(action="iam:AttachUserPolicy", resource="*"),
                        IAMPermission(action="iam:GetPolicy", resource="*"),
                    ],
                    description="Attach policy to user",
                    resource_patterns=["arn:aws:iam::*:user/*", "arn:aws:iam::*:policy/*"]
                ),
                "create-role": CommandPermissions(
                    service="iam",
                    action="create-role",
                    permissions=[
                        IAMPermission(action="iam:CreateRole", resource="*"),
                    ],
                    description="Create IAM role",
                    resource_patterns=["arn:aws:iam::*:role/*"]
                ),
                "list-attached-user-policies": CommandPermissions(
                    service="iam",
                    action="list-attached-user-policies",
                    permissions=[
                        IAMPermission(action="iam:ListAttachedUserPolicies", resource="*"),
                    ],
                    description="List attached user policies",
                    resource_patterns=["arn:aws:iam::*:user/*"]
                ),
            },
            "lambda": {
                "list-functions": CommandPermissions(
                    service="lambda",
                    action="list-functions",
                    permissions=[
                        IAMPermission(action="lambda:ListFunctions", resource="*"),
                    ],
                    description="List Lambda functions",
                    resource_patterns=["arn:aws:lambda:*:*:function/*"]
                ),
                "get-function": CommandPermissions(
                    service="lambda",
                    action="get-function",
                    permissions=[
                        IAMPermission(action="lambda:GetFunction", resource="*"),
                    ],
                    description="Get Lambda function details",
                    resource_patterns=["arn:aws:lambda:*:*:function/*"]
                ),
                "invoke": CommandPermissions(
                    service="lambda",
                    action="invoke",
                    permissions=[
                        IAMPermission(action="lambda:InvokeFunction", resource="*"),
                    ],
                    description="Invoke Lambda function",
                    resource_patterns=["arn:aws:lambda:*:*:function/*"]
                ),
                "create-function": CommandPermissions(
                    service="lambda",
                    action="create-function",
                    permissions=[
                        IAMPermission(action="lambda:CreateFunction", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create Lambda function",
                    resource_patterns=["arn:aws:lambda:*:*:function/*", "arn:aws:iam::*:role/*"]
                ),
            },
            "logs": {
                "describe-log-groups": CommandPermissions(
                    service="logs",
                    action="describe-log-groups",
                    permissions=[
                        IAMPermission(action="logs:DescribeLogGroups", resource="*"),
                    ],
                    description="Describe CloudWatch log groups",
                    resource_patterns=["arn:aws:logs:*:*:log-group:*"]
                ),
                "get-log-events": CommandPermissions(
                    service="logs",
                    action="get-log-events",
                    permissions=[
                        IAMPermission(action="logs:GetLogEvents", resource="*"),
                    ],
                    description="Get CloudWatch log events",
                    resource_patterns=["arn:aws:logs:*:*:log-group:*"]
                ),
            },
            "sts": {
                "get-caller-identity": CommandPermissions(
                    service="sts",
                    action="get-caller-identity",
                    permissions=[
                        IAMPermission(action="sts:GetCallerIdentity", resource="*"),
                    ],
                    description="Get caller identity",
                    resource_patterns=["*"]
                ),
                "assume-role": CommandPermissions(
                    service="sts",
                    action="assume-role",
                    permissions=[
                        IAMPermission(action="sts:AssumeRole", resource="*"),
                    ],
                    description="Assume IAM role",
                    resource_patterns=["arn:aws:iam::*:role/*"]
                ),
            },
            "vpc": {
                "describe-vpcs": CommandPermissions(
                    service="vpc",
                    action="describe-vpcs",
                    permissions=[
                        IAMPermission(action="ec2:DescribeVpcs", resource="*"),
                    ],
                    description="Describe VPCs",
                    resource_patterns=["arn:aws:ec2:*:*:vpc/*"]
                ),
                "create-vpc": CommandPermissions(
                    service="vpc",
                    action="create-vpc",
                    permissions=[
                        IAMPermission(action="ec2:CreateVpc", resource="*"),
                    ],
                    description="Create VPC",
                    resource_patterns=["arn:aws:ec2:*:*:vpc/*"]
                ),
                "delete-vpc": CommandPermissions(
                    service="vpc",
                    action="delete-vpc",
                    permissions=[
                        IAMPermission(action="ec2:DeleteVpc", resource="*"),
                    ],
                    description="Delete VPC",
                    resource_patterns=["arn:aws:ec2:*:*:vpc/*"]
                ),
                "describe-subnets": CommandPermissions(
                    service="vpc",
                    action="describe-subnets",
                    permissions=[
                        IAMPermission(action="ec2:DescribeSubnets", resource="*"),
                    ],
                    description="Describe subnets",
                    resource_patterns=["arn:aws:ec2:*:*:subnet/*"]
                ),
                "create-subnet": CommandPermissions(
                    service="vpc",
                    action="create-subnet",
                    permissions=[
                        IAMPermission(action="ec2:CreateSubnet", resource="*"),
                    ],
                    description="Create subnet",
                    resource_patterns=["arn:aws:ec2:*:*:subnet/*"]
                ),
            },
            "rds": {
                "describe-db-instances": CommandPermissions(
                    service="rds",
                    action="describe-db-instances",
                    permissions=[
                        IAMPermission(action="rds:DescribeDBInstances", resource="*"),
                    ],
                    description="Describe RDS database instances",
                    resource_patterns=["arn:aws:rds:*:*:db:*"]
                ),
                "create-db-instance": CommandPermissions(
                    service="rds",
                    action="create-db-instance",
                    permissions=[
                        IAMPermission(action="rds:CreateDBInstance", resource="*"),
                        IAMPermission(action="rds:DescribeDBSubnetGroups", resource="*"),
                        IAMPermission(action="rds:DescribeDBParameterGroups", resource="*"),
                    ],
                    description="Create RDS database instance",
                    resource_patterns=["arn:aws:rds:*:*:db:*"]
                ),
                "delete-db-instance": CommandPermissions(
                    service="rds",
                    action="delete-db-instance",
                    permissions=[
                        IAMPermission(action="rds:DeleteDBInstance", resource="*"),
                    ],
                    description="Delete RDS database instance",
                    resource_patterns=["arn:aws:rds:*:*:db:*"]
                ),
                "describe-db-snapshots": CommandPermissions(
                    service="rds",
                    action="describe-db-snapshots",
                    permissions=[
                        IAMPermission(action="rds:DescribeDBSnapshots", resource="*"),
                    ],
                    description="Describe RDS database snapshots",
                    resource_patterns=["arn:aws:rds:*:*:snapshot:*"]
                ),
                "create-db-snapshot": CommandPermissions(
                    service="rds",
                    action="create-db-snapshot",
                    permissions=[
                        IAMPermission(action="rds:CreateDBSnapshot", resource="*"),
                    ],
                    description="Create RDS database snapshot",
                    resource_patterns=["arn:aws:rds:*:*:snapshot:*"]
                ),
            },
            "dynamodb": {
                "list-tables": CommandPermissions(
                    service="dynamodb",
                    action="list-tables",
                    permissions=[
                        IAMPermission(action="dynamodb:ListTables", resource="*"),
                    ],
                    description="List DynamoDB tables",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "describe-table": CommandPermissions(
                    service="dynamodb",
                    action="describe-table",
                    permissions=[
                        IAMPermission(action="dynamodb:DescribeTable", resource="*"),
                    ],
                    description="Describe DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "create-table": CommandPermissions(
                    service="dynamodb",
                    action="create-table",
                    permissions=[
                        IAMPermission(action="dynamodb:CreateTable", resource="*"),
                    ],
                    description="Create DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "delete-table": CommandPermissions(
                    service="dynamodb",
                    action="delete-table",
                    permissions=[
                        IAMPermission(action="dynamodb:DeleteTable", resource="*"),
                    ],
                    description="Delete DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "put-item": CommandPermissions(
                    service="dynamodb",
                    action="put-item",
                    permissions=[
                        IAMPermission(action="dynamodb:PutItem", resource="*"),
                    ],
                    description="Put item in DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "get-item": CommandPermissions(
                    service="dynamodb",
                    action="get-item",
                    permissions=[
                        IAMPermission(action="dynamodb:GetItem", resource="*"),
                    ],
                    description="Get item from DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "scan": CommandPermissions(
                    service="dynamodb",
                    action="scan",
                    permissions=[
                        IAMPermission(action="dynamodb:Scan", resource="*"),
                    ],
                    description="Scan DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
                "query": CommandPermissions(
                    service="dynamodb",
                    action="query",
                    permissions=[
                        IAMPermission(action="dynamodb:Query", resource="*"),
                    ],
                    description="Query DynamoDB table",
                    resource_patterns=["arn:aws:dynamodb:*:*:table/*"]
                ),
            },
            "sns": {
                "list-topics": CommandPermissions(
                    service="sns",
                    action="list-topics",
                    permissions=[
                        IAMPermission(action="sns:ListTopics", resource="*"),
                    ],
                    description="List SNS topics",
                    resource_patterns=["arn:aws:sns:*:*:*"]
                ),
                "create-topic": CommandPermissions(
                    service="sns",
                    action="create-topic",
                    permissions=[
                        IAMPermission(action="sns:CreateTopic", resource="*"),
                    ],
                    description="Create SNS topic",
                    resource_patterns=["arn:aws:sns:*:*:*"]
                ),
                "delete-topic": CommandPermissions(
                    service="sns",
                    action="delete-topic",
                    permissions=[
                        IAMPermission(action="sns:DeleteTopic", resource="*"),
                    ],
                    description="Delete SNS topic",
                    resource_patterns=["arn:aws:sns:*:*:*"]
                ),
                "publish": CommandPermissions(
                    service="sns",
                    action="publish",
                    permissions=[
                        IAMPermission(action="sns:Publish", resource="*"),
                    ],
                    description="Publish message to SNS topic",
                    resource_patterns=["arn:aws:sns:*:*:*"]
                ),
                "subscribe": CommandPermissions(
                    service="sns",
                    action="subscribe",
                    permissions=[
                        IAMPermission(action="sns:Subscribe", resource="*"),
                    ],
                    description="Subscribe to SNS topic",
                    resource_patterns=["arn:aws:sns:*:*:*"]
                ),
            },
            "sqs": {
                "list-queues": CommandPermissions(
                    service="sqs",
                    action="list-queues",
                    permissions=[
                        IAMPermission(action="sqs:ListQueues", resource="*"),
                    ],
                    description="List SQS queues",
                    resource_patterns=["arn:aws:sqs:*:*:*"]
                ),
                "create-queue": CommandPermissions(
                    service="sqs",
                    action="create-queue",
                    permissions=[
                        IAMPermission(action="sqs:CreateQueue", resource="*"),
                    ],
                    description="Create SQS queue",
                    resource_patterns=["arn:aws:sqs:*:*:*"]
                ),
                "delete-queue": CommandPermissions(
                    service="sqs",
                    action="delete-queue",
                    permissions=[
                        IAMPermission(action="sqs:DeleteQueue", resource="*"),
                    ],
                    description="Delete SQS queue",
                    resource_patterns=["arn:aws:sqs:*:*:*"]
                ),
                "send-message": CommandPermissions(
                    service="sqs",
                    action="send-message",
                    permissions=[
                        IAMPermission(action="sqs:SendMessage", resource="*"),
                    ],
                    description="Send message to SQS queue",
                    resource_patterns=["arn:aws:sqs:*:*:*"]
                ),
                "receive-message": CommandPermissions(
                    service="sqs",
                    action="receive-message",
                    permissions=[
                        IAMPermission(action="sqs:ReceiveMessage", resource="*"),
                    ],
                    description="Receive message from SQS queue",
                    resource_patterns=["arn:aws:sqs:*:*:*"]
                ),
                "delete-message": CommandPermissions(
                    service="sqs",
                    action="delete-message",
                    permissions=[
                        IAMPermission(action="sqs:DeleteMessage", resource="*"),
                    ],
                    description="Delete message from SQS queue",
                    resource_patterns=["arn:aws:sqs:*:*:*"]
                ),
            },
            "cloudformation": {
                "list-stacks": CommandPermissions(
                    service="cloudformation",
                    action="list-stacks",
                    permissions=[
                        IAMPermission(action="cloudformation:ListStacks", resource="*"),
                    ],
                    description="List CloudFormation stacks",
                    resource_patterns=["arn:aws:cloudformation:*:*:stack/*/*"]
                ),
                "describe-stacks": CommandPermissions(
                    service="cloudformation",
                    action="describe-stacks",
                    permissions=[
                        IAMPermission(action="cloudformation:DescribeStacks", resource="*"),
                    ],
                    description="Describe CloudFormation stacks",
                    resource_patterns=["arn:aws:cloudformation:*:*:stack/*/*"]
                ),
                "create-stack": CommandPermissions(
                    service="cloudformation",
                    action="create-stack",
                    permissions=[
                        IAMPermission(action="cloudformation:CreateStack", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create CloudFormation stack",
                    resource_patterns=["arn:aws:cloudformation:*:*:stack/*/*"]
                ),
                "update-stack": CommandPermissions(
                    service="cloudformation",
                    action="update-stack",
                    permissions=[
                        IAMPermission(action="cloudformation:UpdateStack", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Update CloudFormation stack",
                    resource_patterns=["arn:aws:cloudformation:*:*:stack/*/*"]
                ),
                "delete-stack": CommandPermissions(
                    service="cloudformation",
                    action="delete-stack",
                    permissions=[
                        IAMPermission(action="cloudformation:DeleteStack", resource="*"),
                    ],
                    description="Delete CloudFormation stack",
                    resource_patterns=["arn:aws:cloudformation:*:*:stack/*/*"]
                ),
                "describe-stack-events": CommandPermissions(
                    service="cloudformation",
                    action="describe-stack-events",
                    permissions=[
                        IAMPermission(action="cloudformation:DescribeStackEvents", resource="*"),
                    ],
                    description="Describe CloudFormation stack events",
                    resource_patterns=["arn:aws:cloudformation:*:*:stack/*/*"]
                ),
            },
            "cloudwatch": {
                "describe-alarms": CommandPermissions(
                    service="cloudwatch",
                    action="describe-alarms",
                    permissions=[
                        IAMPermission(action="cloudwatch:DescribeAlarms", resource="*"),
                    ],
                    description="Describe CloudWatch alarms",
                    resource_patterns=["arn:aws:cloudwatch:*:*:alarm:*"]
                ),
                "put-metric-alarm": CommandPermissions(
                    service="cloudwatch",
                    action="put-metric-alarm",
                    permissions=[
                        IAMPermission(action="cloudwatch:PutMetricAlarm", resource="*"),
                    ],
                    description="Create CloudWatch alarm",
                    resource_patterns=["arn:aws:cloudwatch:*:*:alarm:*"]
                ),
                "delete-alarms": CommandPermissions(
                    service="cloudwatch",
                    action="delete-alarms",
                    permissions=[
                        IAMPermission(action="cloudwatch:DeleteAlarms", resource="*"),
                    ],
                    description="Delete CloudWatch alarms",
                    resource_patterns=["arn:aws:cloudwatch:*:*:alarm:*"]
                ),
                "get-metric-statistics": CommandPermissions(
                    service="cloudwatch",
                    action="get-metric-statistics",
                    permissions=[
                        IAMPermission(action="cloudwatch:GetMetricStatistics", resource="*"),
                    ],
                    description="Get CloudWatch metric statistics",
                    resource_patterns=["*"]
                ),
                "put-metric-data": CommandPermissions(
                    service="cloudwatch",
                    action="put-metric-data",
                    permissions=[
                        IAMPermission(action="cloudwatch:PutMetricData", resource="*"),
                    ],
                    description="Put CloudWatch metric data",
                    resource_patterns=["*"]
                ),
                "list-metrics": CommandPermissions(
                    service="cloudwatch",
                    action="list-metrics",
                    permissions=[
                        IAMPermission(action="cloudwatch:ListMetrics", resource="*"),
                    ],
                    description="List CloudWatch metrics",
                    resource_patterns=["*"]
                ),
            },
            "route53": {
                "list-hosted-zones": CommandPermissions(
                    service="route53",
                    action="list-hosted-zones",
                    permissions=[
                        IAMPermission(action="route53:ListHostedZones", resource="*"),
                    ],
                    description="List Route53 hosted zones",
                    resource_patterns=["arn:aws:route53:::hostedzone/*"]
                ),
                "create-hosted-zone": CommandPermissions(
                    service="route53",
                    action="create-hosted-zone",
                    permissions=[
                        IAMPermission(action="route53:CreateHostedZone", resource="*"),
                    ],
                    description="Create Route53 hosted zone",
                    resource_patterns=["arn:aws:route53:::hostedzone/*"]
                ),
                "delete-hosted-zone": CommandPermissions(
                    service="route53",
                    action="delete-hosted-zone",
                    permissions=[
                        IAMPermission(action="route53:DeleteHostedZone", resource="*"),
                    ],
                    description="Delete Route53 hosted zone",
                    resource_patterns=["arn:aws:route53:::hostedzone/*"]
                ),
                "list-resource-record-sets": CommandPermissions(
                    service="route53",
                    action="list-resource-record-sets",
                    permissions=[
                        IAMPermission(action="route53:ListResourceRecordSets", resource="*"),
                    ],
                    description="List Route53 resource record sets",
                    resource_patterns=["arn:aws:route53:::hostedzone/*"]
                ),
                "change-resource-record-sets": CommandPermissions(
                    service="route53",
                    action="change-resource-record-sets",
                    permissions=[
                        IAMPermission(action="route53:ChangeResourceRecordSets", resource="*"),
                    ],
                    description="Change Route53 resource record sets",
                    resource_patterns=["arn:aws:route53:::hostedzone/*"]
                ),
            },
            "kms": {
                "list-keys": CommandPermissions(
                    service="kms",
                    action="list-keys",
                    permissions=[
                        IAMPermission(action="kms:ListKeys", resource="*"),
                    ],
                    description="List KMS keys",
                    resource_patterns=["arn:aws:kms:*:*:key/*"]
                ),
                "describe-key": CommandPermissions(
                    service="kms",
                    action="describe-key",
                    permissions=[
                        IAMPermission(action="kms:DescribeKey", resource="*"),
                    ],
                    description="Describe KMS key",
                    resource_patterns=["arn:aws:kms:*:*:key/*"]
                ),
                "create-key": CommandPermissions(
                    service="kms",
                    action="create-key",
                    permissions=[
                        IAMPermission(action="kms:CreateKey", resource="*"),
                    ],
                    description="Create KMS key",
                    resource_patterns=["arn:aws:kms:*:*:key/*"]
                ),
                "encrypt": CommandPermissions(
                    service="kms",
                    action="encrypt",
                    permissions=[
                        IAMPermission(action="kms:Encrypt", resource="*"),
                    ],
                    description="Encrypt data with KMS key",
                    resource_patterns=["arn:aws:kms:*:*:key/*"]
                ),
                "decrypt": CommandPermissions(
                    service="kms",
                    action="decrypt",
                    permissions=[
                        IAMPermission(action="kms:Decrypt", resource="*"),
                    ],
                    description="Decrypt data with KMS key",
                    resource_patterns=["arn:aws:kms:*:*:key/*"]
                ),
                "generate-data-key": CommandPermissions(
                    service="kms",
                    action="generate-data-key",
                    permissions=[
                        IAMPermission(action="kms:GenerateDataKey", resource="*"),
                    ],
                    description="Generate data key",
                    resource_patterns=["arn:aws:kms:*:*:key/*"]
                ),
            },
            "ecs": {
                "list-clusters": CommandPermissions(
                    service="ecs",
                    action="list-clusters",
                    permissions=[
                        IAMPermission(action="ecs:ListClusters", resource="*"),
                    ],
                    description="List ECS clusters",
                    resource_patterns=["arn:aws:ecs:*:*:cluster/*"]
                ),
                "describe-clusters": CommandPermissions(
                    service="ecs",
                    action="describe-clusters",
                    permissions=[
                        IAMPermission(action="ecs:DescribeClusters", resource="*"),
                    ],
                    description="Describe ECS clusters",
                    resource_patterns=["arn:aws:ecs:*:*:cluster/*"]
                ),
                "create-cluster": CommandPermissions(
                    service="ecs",
                    action="create-cluster",
                    permissions=[
                        IAMPermission(action="ecs:CreateCluster", resource="*"),
                    ],
                    description="Create ECS cluster",
                    resource_patterns=["arn:aws:ecs:*:*:cluster/*"]
                ),
                "delete-cluster": CommandPermissions(
                    service="ecs",
                    action="delete-cluster",
                    permissions=[
                        IAMPermission(action="ecs:DeleteCluster", resource="*"),
                    ],
                    description="Delete ECS cluster",
                    resource_patterns=["arn:aws:ecs:*:*:cluster/*"]
                ),
                "list-services": CommandPermissions(
                    service="ecs",
                    action="list-services",
                    permissions=[
                        IAMPermission(action="ecs:ListServices", resource="*"),
                    ],
                    description="List ECS services",
                    resource_patterns=["arn:aws:ecs:*:*:service/*"]
                ),
                "describe-services": CommandPermissions(
                    service="ecs",
                    action="describe-services",
                    permissions=[
                        IAMPermission(action="ecs:DescribeServices", resource="*"),
                    ],
                    description="Describe ECS services",
                    resource_patterns=["arn:aws:ecs:*:*:service/*"]
                ),
                "create-service": CommandPermissions(
                    service="ecs",
                    action="create-service",
                    permissions=[
                        IAMPermission(action="ecs:CreateService", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create ECS service",
                    resource_patterns=["arn:aws:ecs:*:*:service/*"]
                ),
                "list-tasks": CommandPermissions(
                    service="ecs",
                    action="list-tasks",
                    permissions=[
                        IAMPermission(action="ecs:ListTasks", resource="*"),
                    ],
                    description="List ECS tasks",
                    resource_patterns=["arn:aws:ecs:*:*:task/*"]
                ),
                "run-task": CommandPermissions(
                    service="ecs",
                    action="run-task",
                    permissions=[
                        IAMPermission(action="ecs:RunTask", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Run ECS task",
                    resource_patterns=["arn:aws:ecs:*:*:task/*"]
                ),
            },
            "ecr": {
                "describe-repositories": CommandPermissions(
                    service="ecr",
                    action="describe-repositories",
                    permissions=[
                        IAMPermission(action="ecr:DescribeRepositories", resource="*"),
                    ],
                    description="Describe ECR repositories",
                    resource_patterns=["arn:aws:ecr:*:*:repository/*"]
                ),
                "create-repository": CommandPermissions(
                    service="ecr",
                    action="create-repository",
                    permissions=[
                        IAMPermission(action="ecr:CreateRepository", resource="*"),
                    ],
                    description="Create ECR repository",
                    resource_patterns=["arn:aws:ecr:*:*:repository/*"]
                ),
                "delete-repository": CommandPermissions(
                    service="ecr",
                    action="delete-repository",
                    permissions=[
                        IAMPermission(action="ecr:DeleteRepository", resource="*"),
                    ],
                    description="Delete ECR repository",
                    resource_patterns=["arn:aws:ecr:*:*:repository/*"]
                ),
                "get-login-token": CommandPermissions(
                    service="ecr",
                    action="get-login-token",
                    permissions=[
                        IAMPermission(action="ecr:GetAuthorizationToken", resource="*"),
                    ],
                    description="Get ECR login token",
                    resource_patterns=["*"]
                ),
                "list-images": CommandPermissions(
                    service="ecr",
                    action="list-images",
                    permissions=[
                        IAMPermission(action="ecr:ListImages", resource="*"),
                    ],
                    description="List ECR images",
                    resource_patterns=["arn:aws:ecr:*:*:repository/*"]
                ),
                "put-image": CommandPermissions(
                    service="ecr",
                    action="put-image",
                    permissions=[
                        IAMPermission(action="ecr:PutImage", resource="*"),
                        IAMPermission(action="ecr:InitiateLayerUpload", resource="*"),
                        IAMPermission(action="ecr:UploadLayerPart", resource="*"),
                        IAMPermission(action="ecr:CompleteLayerUpload", resource="*"),
                    ],
                    description="Push image to ECR",
                    resource_patterns=["arn:aws:ecr:*:*:repository/*"]
                ),
            },
            "apigateway": {
                "get-rest-apis": CommandPermissions(
                    service="apigateway",
                    action="get-rest-apis",
                    permissions=[
                        IAMPermission(action="apigateway:GET", resource="arn:aws:apigateway:*::/restapis"),
                    ],
                    description="Get REST APIs",
                    resource_patterns=["arn:aws:apigateway:*::/restapis/*"]
                ),
                "create-rest-api": CommandPermissions(
                    service="apigateway",
                    action="create-rest-api",
                    permissions=[
                        IAMPermission(action="apigateway:POST", resource="arn:aws:apigateway:*::/restapis"),
                    ],
                    description="Create REST API",
                    resource_patterns=["arn:aws:apigateway:*::/restapis/*"]
                ),
                "delete-rest-api": CommandPermissions(
                    service="apigateway",
                    action="delete-rest-api",
                    permissions=[
                        IAMPermission(action="apigateway:DELETE", resource="arn:aws:apigateway:*::/restapis/*"),
                    ],
                    description="Delete REST API",
                    resource_patterns=["arn:aws:apigateway:*::/restapis/*"]
                ),
                "create-deployment": CommandPermissions(
                    service="apigateway",
                    action="create-deployment",
                    permissions=[
                        IAMPermission(action="apigateway:POST", resource="arn:aws:apigateway:*::/restapis/*/deployments"),
                    ],
                    description="Create API Gateway deployment",
                    resource_patterns=["arn:aws:apigateway:*::/restapis/*"]
                ),
            },
            "efs": {
                "describe-file-systems": CommandPermissions(
                    service="efs",
                    action="describe-file-systems",
                    permissions=[
                        IAMPermission(action="elasticfilesystem:DescribeFileSystems", resource="*"),
                    ],
                    description="Describe EFS file systems",
                    resource_patterns=["arn:aws:elasticfilesystem:*:*:file-system/*"]
                ),
                "create-file-system": CommandPermissions(
                    service="efs",
                    action="create-file-system",
                    permissions=[
                        IAMPermission(action="elasticfilesystem:CreateFileSystem", resource="*"),
                    ],
                    description="Create EFS file system",
                    resource_patterns=["arn:aws:elasticfilesystem:*:*:file-system/*"]
                ),
                "delete-file-system": CommandPermissions(
                    service="efs",
                    action="delete-file-system",
                    permissions=[
                        IAMPermission(action="elasticfilesystem:DeleteFileSystem", resource="*"),
                    ],
                    description="Delete EFS file system",
                    resource_patterns=["arn:aws:elasticfilesystem:*:*:file-system/*"]
                ),
                "describe-mount-targets": CommandPermissions(
                    service="efs",
                    action="describe-mount-targets",
                    permissions=[
                        IAMPermission(action="elasticfilesystem:DescribeMountTargets", resource="*"),
                    ],
                    description="Describe EFS mount targets",
                    resource_patterns=["arn:aws:elasticfilesystem:*:*:file-system/*"]
                ),
            },
            "elasticache": {
                "describe-cache-clusters": CommandPermissions(
                    service="elasticache",
                    action="describe-cache-clusters",
                    permissions=[
                        IAMPermission(action="elasticache:DescribeCacheClusters", resource="*"),
                    ],
                    description="Describe ElastiCache clusters",
                    resource_patterns=["arn:aws:elasticache:*:*:cluster:*"]
                ),
                "create-cache-cluster": CommandPermissions(
                    service="elasticache",
                    action="create-cache-cluster",
                    permissions=[
                        IAMPermission(action="elasticache:CreateCacheCluster", resource="*"),
                    ],
                    description="Create ElastiCache cluster",
                    resource_patterns=["arn:aws:elasticache:*:*:cluster:*"]
                ),
                "delete-cache-cluster": CommandPermissions(
                    service="elasticache",
                    action="delete-cache-cluster",
                    permissions=[
                        IAMPermission(action="elasticache:DeleteCacheCluster", resource="*"),
                    ],
                    description="Delete ElastiCache cluster",
                    resource_patterns=["arn:aws:elasticache:*:*:cluster:*"]
                ),
                "describe-replication-groups": CommandPermissions(
                    service="elasticache",
                    action="describe-replication-groups",
                    permissions=[
                        IAMPermission(action="elasticache:DescribeReplicationGroups", resource="*"),
                    ],
                    description="Describe ElastiCache replication groups",
                    resource_patterns=["arn:aws:elasticache:*:*:replicationgroup:*"]
                ),
            },
            "secretsmanager": {
                "list-secrets": CommandPermissions(
                    service="secretsmanager",
                    action="list-secrets",
                    permissions=[
                        IAMPermission(action="secretsmanager:ListSecrets", resource="*"),
                    ],
                    description="List Secrets Manager secrets",
                    resource_patterns=["arn:aws:secretsmanager:*:*:secret:*"]
                ),
                "create-secret": CommandPermissions(
                    service="secretsmanager",
                    action="create-secret",
                    permissions=[
                        IAMPermission(action="secretsmanager:CreateSecret", resource="*"),
                    ],
                    description="Create Secrets Manager secret",
                    resource_patterns=["arn:aws:secretsmanager:*:*:secret:*"]
                ),
                "delete-secret": CommandPermissions(
                    service="secretsmanager",
                    action="delete-secret",
                    permissions=[
                        IAMPermission(action="secretsmanager:DeleteSecret", resource="*"),
                    ],
                    description="Delete Secrets Manager secret",
                    resource_patterns=["arn:aws:secretsmanager:*:*:secret:*"]
                ),
                "get-secret-value": CommandPermissions(
                    service="secretsmanager",
                    action="get-secret-value",
                    permissions=[
                        IAMPermission(action="secretsmanager:GetSecretValue", resource="*"),
                    ],
                    description="Get Secrets Manager secret value",
                    resource_patterns=["arn:aws:secretsmanager:*:*:secret:*"]
                ),
                "put-secret-value": CommandPermissions(
                    service="secretsmanager",
                    action="put-secret-value",
                    permissions=[
                        IAMPermission(action="secretsmanager:PutSecretValue", resource="*"),
                    ],
                    description="Put Secrets Manager secret value",
                    resource_patterns=["arn:aws:secretsmanager:*:*:secret:*"]
                ),
            },
            "stepfunctions": {
                "list-state-machines": CommandPermissions(
                    service="stepfunctions",
                    action="list-state-machines",
                    permissions=[
                        IAMPermission(action="states:ListStateMachines", resource="*"),
                    ],
                    description="List Step Functions state machines",
                    resource_patterns=["arn:aws:states:*:*:stateMachine:*"]
                ),
                "create-state-machine": CommandPermissions(
                    service="stepfunctions",
                    action="create-state-machine",
                    permissions=[
                        IAMPermission(action="states:CreateStateMachine", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create Step Functions state machine",
                    resource_patterns=["arn:aws:states:*:*:stateMachine:*"]
                ),
                "start-execution": CommandPermissions(
                    service="stepfunctions",
                    action="start-execution",
                    permissions=[
                        IAMPermission(action="states:StartExecution", resource="*"),
                    ],
                    description="Start Step Functions execution",
                    resource_patterns=["arn:aws:states:*:*:stateMachine:*"]
                ),
                "describe-execution": CommandPermissions(
                    service="stepfunctions",
                    action="describe-execution",
                    permissions=[
                        IAMPermission(action="states:DescribeExecution", resource="*"),
                    ],
                    description="Describe Step Functions execution",
                    resource_patterns=["arn:aws:states:*:*:execution:*"]
                ),
            },
            "kinesis": {
                "list-streams": CommandPermissions(
                    service="kinesis",
                    action="list-streams",
                    permissions=[
                        IAMPermission(action="kinesis:ListStreams", resource="*"),
                    ],
                    description="List Kinesis streams",
                    resource_patterns=["arn:aws:kinesis:*:*:stream/*"]
                ),
                "create-stream": CommandPermissions(
                    service="kinesis",
                    action="create-stream",
                    permissions=[
                        IAMPermission(action="kinesis:CreateStream", resource="*"),
                    ],
                    description="Create Kinesis stream",
                    resource_patterns=["arn:aws:kinesis:*:*:stream/*"]
                ),
                "delete-stream": CommandPermissions(
                    service="kinesis",
                    action="delete-stream",
                    permissions=[
                        IAMPermission(action="kinesis:DeleteStream", resource="*"),
                    ],
                    description="Delete Kinesis stream",
                    resource_patterns=["arn:aws:kinesis:*:*:stream/*"]
                ),
                "put-record": CommandPermissions(
                    service="kinesis",
                    action="put-record",
                    permissions=[
                        IAMPermission(action="kinesis:PutRecord", resource="*"),
                    ],
                    description="Put record to Kinesis stream",
                    resource_patterns=["arn:aws:kinesis:*:*:stream/*"]
                ),
                "get-records": CommandPermissions(
                    service="kinesis",
                    action="get-records",
                    permissions=[
                        IAMPermission(action="kinesis:GetRecords", resource="*"),
                        IAMPermission(action="kinesis:GetShardIterator", resource="*"),
                    ],
                    description="Get records from Kinesis stream",
                    resource_patterns=["arn:aws:kinesis:*:*:stream/*"]
                ),
            },
            "elb": {
                "describe-load-balancers": CommandPermissions(
                    service="elb",
                    action="describe-load-balancers",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:DescribeLoadBalancers", resource="*"),
                    ],
                    description="Describe Classic Load Balancers",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:loadbalancer/*"]
                ),
                "create-load-balancer": CommandPermissions(
                    service="elb",
                    action="create-load-balancer",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:CreateLoadBalancer", resource="*"),
                    ],
                    description="Create Classic Load Balancer",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:loadbalancer/*"]
                ),
                "delete-load-balancer": CommandPermissions(
                    service="elb",
                    action="delete-load-balancer",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:DeleteLoadBalancer", resource="*"),
                    ],
                    description="Delete Classic Load Balancer",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:loadbalancer/*"]
                ),
            },
            "elbv2": {
                "describe-load-balancers": CommandPermissions(
                    service="elbv2",
                    action="describe-load-balancers",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:DescribeLoadBalancers", resource="*"),
                    ],
                    description="Describe Application/Network Load Balancers",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:loadbalancer/*"]
                ),
                "create-load-balancer": CommandPermissions(
                    service="elbv2",
                    action="create-load-balancer",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:CreateLoadBalancer", resource="*"),
                    ],
                    description="Create Application/Network Load Balancer",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:loadbalancer/*"]
                ),
                "describe-target-groups": CommandPermissions(
                    service="elbv2",
                    action="describe-target-groups",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:DescribeTargetGroups", resource="*"),
                    ],
                    description="Describe ELB target groups",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:targetgroup/*"]
                ),
                "create-target-group": CommandPermissions(
                    service="elbv2",
                    action="create-target-group",
                    permissions=[
                        IAMPermission(action="elasticloadbalancing:CreateTargetGroup", resource="*"),
                    ],
                    description="Create ELB target group",
                    resource_patterns=["arn:aws:elasticloadbalancing:*:*:targetgroup/*"]
                ),
            },
            "autoscaling": {
                "describe-auto-scaling-groups": CommandPermissions(
                    service="autoscaling",
                    action="describe-auto-scaling-groups",
                    permissions=[
                        IAMPermission(action="autoscaling:DescribeAutoScalingGroups", resource="*"),
                    ],
                    description="Describe Auto Scaling groups",
                    resource_patterns=["arn:aws:autoscaling:*:*:autoScalingGroup:*"]
                ),
                "create-auto-scaling-group": CommandPermissions(
                    service="autoscaling",
                    action="create-auto-scaling-group",
                    permissions=[
                        IAMPermission(action="autoscaling:CreateAutoScalingGroup", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create Auto Scaling group",
                    resource_patterns=["arn:aws:autoscaling:*:*:autoScalingGroup:*"]
                ),
                "delete-auto-scaling-group": CommandPermissions(
                    service="autoscaling",
                    action="delete-auto-scaling-group",
                    permissions=[
                        IAMPermission(action="autoscaling:DeleteAutoScalingGroup", resource="*"),
                    ],
                    description="Delete Auto Scaling group",
                    resource_patterns=["arn:aws:autoscaling:*:*:autoScalingGroup:*"]
                ),
                "update-auto-scaling-group": CommandPermissions(
                    service="autoscaling",
                    action="update-auto-scaling-group",
                    permissions=[
                        IAMPermission(action="autoscaling:UpdateAutoScalingGroup", resource="*"),
                    ],
                    description="Update Auto Scaling group",
                    resource_patterns=["arn:aws:autoscaling:*:*:autoScalingGroup:*"]
                ),
            },
            "cloudtrail": {
                "describe-trails": CommandPermissions(
                    service="cloudtrail",
                    action="describe-trails",
                    permissions=[
                        IAMPermission(action="cloudtrail:DescribeTrails", resource="*"),
                    ],
                    description="Describe CloudTrail trails",
                    resource_patterns=["arn:aws:cloudtrail:*:*:trail/*"]
                ),
                "create-trail": CommandPermissions(
                    service="cloudtrail",
                    action="create-trail",
                    permissions=[
                        IAMPermission(action="cloudtrail:CreateTrail", resource="*"),
                    ],
                    description="Create CloudTrail trail",
                    resource_patterns=["arn:aws:cloudtrail:*:*:trail/*"]
                ),
                "start-logging": CommandPermissions(
                    service="cloudtrail",
                    action="start-logging",
                    permissions=[
                        IAMPermission(action="cloudtrail:StartLogging", resource="*"),
                    ],
                    description="Start CloudTrail logging",
                    resource_patterns=["arn:aws:cloudtrail:*:*:trail/*"]
                ),
                "stop-logging": CommandPermissions(
                    service="cloudtrail",
                    action="stop-logging",
                    permissions=[
                        IAMPermission(action="cloudtrail:StopLogging", resource="*"),
                    ],
                    description="Stop CloudTrail logging",
                    resource_patterns=["arn:aws:cloudtrail:*:*:trail/*"]
                ),
                "lookup-events": CommandPermissions(
                    service="cloudtrail",
                    action="lookup-events",
                    permissions=[
                        IAMPermission(action="cloudtrail:LookupEvents", resource="*"),
                    ],
                    description="Lookup CloudTrail events",
                    resource_patterns=["*"]
                ),
            },
            "eks": {
                "list-clusters": CommandPermissions(
                    service="eks",
                    action="list-clusters",
                    permissions=[
                        IAMPermission(action="eks:ListClusters", resource="*"),
                    ],
                    description="List EKS clusters",
                    resource_patterns=["arn:aws:eks:*:*:cluster/*"]
                ),
                "describe-cluster": CommandPermissions(
                    service="eks",
                    action="describe-cluster",
                    permissions=[
                        IAMPermission(action="eks:DescribeCluster", resource="*"),
                    ],
                    description="Describe EKS cluster",
                    resource_patterns=["arn:aws:eks:*:*:cluster/*"]
                ),
                "create-cluster": CommandPermissions(
                    service="eks",
                    action="create-cluster",
                    permissions=[
                        IAMPermission(action="eks:CreateCluster", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                        IAMPermission(action="ec2:DescribeSubnets", resource="*"),
                        IAMPermission(action="ec2:DescribeVpcs", resource="*"),
                    ],
                    description="Create EKS cluster",
                    resource_patterns=["arn:aws:eks:*:*:cluster/*"]
                ),
                "delete-cluster": CommandPermissions(
                    service="eks",
                    action="delete-cluster",
                    permissions=[
                        IAMPermission(action="eks:DeleteCluster", resource="*"),
                    ],
                    description="Delete EKS cluster",
                    resource_patterns=["arn:aws:eks:*:*:cluster/*"]
                ),
                "update-kubeconfig": CommandPermissions(
                    service="eks",
                    action="update-kubeconfig",
                    permissions=[
                        IAMPermission(action="eks:DescribeCluster", resource="*"),
                    ],
                    description="Update kubeconfig for EKS cluster",
                    resource_patterns=["arn:aws:eks:*:*:cluster/*"]
                ),
                "list-nodegroups": CommandPermissions(
                    service="eks",
                    action="list-nodegroups",
                    permissions=[
                        IAMPermission(action="eks:ListNodegroups", resource="*"),
                    ],
                    description="List EKS node groups",
                    resource_patterns=["arn:aws:eks:*:*:cluster/*"]
                ),
                "create-nodegroup": CommandPermissions(
                    service="eks",
                    action="create-nodegroup",
                    permissions=[
                        IAMPermission(action="eks:CreateNodegroup", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                        IAMPermission(action="ec2:DescribeSubnets", resource="*"),
                    ],
                    description="Create EKS node group",
                    resource_patterns=["arn:aws:eks:*:*:nodegroup/*/*"]
                ),
                "delete-nodegroup": CommandPermissions(
                    service="eks",
                    action="delete-nodegroup",
                    permissions=[
                        IAMPermission(action="eks:DeleteNodegroup", resource="*"),
                    ],
                    description="Delete EKS node group",
                    resource_patterns=["arn:aws:eks:*:*:nodegroup/*/*"]
                ),
            },
            "codecommit": {
                "list-repositories": CommandPermissions(
                    service="codecommit",
                    action="list-repositories",
                    permissions=[
                        IAMPermission(action="codecommit:ListRepositories", resource="*"),
                    ],
                    description="List CodeCommit repositories",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "get-repository": CommandPermissions(
                    service="codecommit",
                    action="get-repository",
                    permissions=[
                        IAMPermission(action="codecommit:GetRepository", resource="*"),
                    ],
                    description="Get CodeCommit repository details",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "create-repository": CommandPermissions(
                    service="codecommit",
                    action="create-repository",
                    permissions=[
                        IAMPermission(action="codecommit:CreateRepository", resource="*"),
                    ],
                    description="Create CodeCommit repository",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "delete-repository": CommandPermissions(
                    service="codecommit",
                    action="delete-repository",
                    permissions=[
                        IAMPermission(action="codecommit:DeleteRepository", resource="*"),
                    ],
                    description="Delete CodeCommit repository",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "get-branch": CommandPermissions(
                    service="codecommit",
                    action="get-branch",
                    permissions=[
                        IAMPermission(action="codecommit:GetBranch", resource="*"),
                    ],
                    description="Get CodeCommit branch details",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "create-branch": CommandPermissions(
                    service="codecommit",
                    action="create-branch",
                    permissions=[
                        IAMPermission(action="codecommit:CreateBranch", resource="*"),
                    ],
                    description="Create CodeCommit branch",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "put-file": CommandPermissions(
                    service="codecommit",
                    action="put-file",
                    permissions=[
                        IAMPermission(action="codecommit:PutFile", resource="*"),
                    ],
                    description="Put file to CodeCommit repository",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
                "get-file": CommandPermissions(
                    service="codecommit",
                    action="get-file",
                    permissions=[
                        IAMPermission(action="codecommit:GetFile", resource="*"),
                    ],
                    description="Get file from CodeCommit repository",
                    resource_patterns=["arn:aws:codecommit:*:*:*"]
                ),
            },
            "codebuild": {
                "list-projects": CommandPermissions(
                    service="codebuild",
                    action="list-projects",
                    permissions=[
                        IAMPermission(action="codebuild:ListProjects", resource="*"),
                    ],
                    description="List CodeBuild projects",
                    resource_patterns=["arn:aws:codebuild:*:*:project/*"]
                ),
                "batch-get-projects": CommandPermissions(
                    service="codebuild",
                    action="batch-get-projects",
                    permissions=[
                        IAMPermission(action="codebuild:BatchGetProjects", resource="*"),
                    ],
                    description="Get details for multiple CodeBuild projects",
                    resource_patterns=["arn:aws:codebuild:*:*:project/*"]
                ),
                "create-project": CommandPermissions(
                    service="codebuild",
                    action="create-project",
                    permissions=[
                        IAMPermission(action="codebuild:CreateProject", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create CodeBuild project",
                    resource_patterns=["arn:aws:codebuild:*:*:project/*"]
                ),
                "delete-project": CommandPermissions(
                    service="codebuild",
                    action="delete-project",
                    permissions=[
                        IAMPermission(action="codebuild:DeleteProject", resource="*"),
                    ],
                    description="Delete CodeBuild project",
                    resource_patterns=["arn:aws:codebuild:*:*:project/*"]
                ),
                "start-build": CommandPermissions(
                    service="codebuild",
                    action="start-build",
                    permissions=[
                        IAMPermission(action="codebuild:StartBuild", resource="*"),
                    ],
                    description="Start CodeBuild build",
                    resource_patterns=["arn:aws:codebuild:*:*:project/*"]
                ),
                "batch-get-builds": CommandPermissions(
                    service="codebuild",
                    action="batch-get-builds",
                    permissions=[
                        IAMPermission(action="codebuild:BatchGetBuilds", resource="*"),
                    ],
                    description="Get details for multiple CodeBuild builds",
                    resource_patterns=["arn:aws:codebuild:*:*:build/*"]
                ),
                "list-builds": CommandPermissions(
                    service="codebuild",
                    action="list-builds",
                    permissions=[
                        IAMPermission(action="codebuild:ListBuilds", resource="*"),
                    ],
                    description="List CodeBuild builds",
                    resource_patterns=["arn:aws:codebuild:*:*:build/*"]
                ),
                "stop-build": CommandPermissions(
                    service="codebuild",
                    action="stop-build",
                    permissions=[
                        IAMPermission(action="codebuild:StopBuild", resource="*"),
                    ],
                    description="Stop CodeBuild build",
                    resource_patterns=["arn:aws:codebuild:*:*:build/*"]
                ),
            },
            "codedeploy": {
                "list-applications": CommandPermissions(
                    service="codedeploy",
                    action="list-applications",
                    permissions=[
                        IAMPermission(action="codedeploy:ListApplications", resource="*"),
                    ],
                    description="List CodeDeploy applications",
                    resource_patterns=["arn:aws:codedeploy:*:*:application:*"]
                ),
                "get-application": CommandPermissions(
                    service="codedeploy",
                    action="get-application",
                    permissions=[
                        IAMPermission(action="codedeploy:GetApplication", resource="*"),
                    ],
                    description="Get CodeDeploy application details",
                    resource_patterns=["arn:aws:codedeploy:*:*:application:*"]
                ),
                "create-application": CommandPermissions(
                    service="codedeploy",
                    action="create-application",
                    permissions=[
                        IAMPermission(action="codedeploy:CreateApplication", resource="*"),
                    ],
                    description="Create CodeDeploy application",
                    resource_patterns=["arn:aws:codedeploy:*:*:application:*"]
                ),
                "delete-application": CommandPermissions(
                    service="codedeploy",
                    action="delete-application",
                    permissions=[
                        IAMPermission(action="codedeploy:DeleteApplication", resource="*"),
                    ],
                    description="Delete CodeDeploy application",
                    resource_patterns=["arn:aws:codedeploy:*:*:application:*"]
                ),
                "list-deployment-groups": CommandPermissions(
                    service="codedeploy",
                    action="list-deployment-groups",
                    permissions=[
                        IAMPermission(action="codedeploy:ListDeploymentGroups", resource="*"),
                    ],
                    description="List CodeDeploy deployment groups",
                    resource_patterns=["arn:aws:codedeploy:*:*:deploymentgroup:*"]
                ),
                "create-deployment-group": CommandPermissions(
                    service="codedeploy",
                    action="create-deployment-group",
                    permissions=[
                        IAMPermission(action="codedeploy:CreateDeploymentGroup", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create CodeDeploy deployment group",
                    resource_patterns=["arn:aws:codedeploy:*:*:deploymentgroup:*"]
                ),
                "delete-deployment-group": CommandPermissions(
                    service="codedeploy",
                    action="delete-deployment-group",
                    permissions=[
                        IAMPermission(action="codedeploy:DeleteDeploymentGroup", resource="*"),
                    ],
                    description="Delete CodeDeploy deployment group",
                    resource_patterns=["arn:aws:codedeploy:*:*:deploymentgroup:*"]
                ),
                "create-deployment": CommandPermissions(
                    service="codedeploy",
                    action="create-deployment",
                    permissions=[
                        IAMPermission(action="codedeploy:CreateDeployment", resource="*"),
                    ],
                    description="Create CodeDeploy deployment",
                    resource_patterns=["arn:aws:codedeploy:*:*:deploymentgroup:*"]
                ),
                "get-deployment": CommandPermissions(
                    service="codedeploy",
                    action="get-deployment",
                    permissions=[
                        IAMPermission(action="codedeploy:GetDeployment", resource="*"),
                    ],
                    description="Get CodeDeploy deployment details",
                    resource_patterns=["arn:aws:codedeploy:*:*:deploymentgroup:*"]
                ),
                "list-deployments": CommandPermissions(
                    service="codedeploy",
                    action="list-deployments",
                    permissions=[
                        IAMPermission(action="codedeploy:ListDeployments", resource="*"),
                    ],
                    description="List CodeDeploy deployments",
                    resource_patterns=["arn:aws:codedeploy:*:*:deploymentgroup:*"]
                ),
            },
            "codepipeline": {
                "list-pipelines": CommandPermissions(
                    service="codepipeline",
                    action="list-pipelines",
                    permissions=[
                        IAMPermission(action="codepipeline:ListPipelines", resource="*"),
                    ],
                    description="List CodePipeline pipelines",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "get-pipeline": CommandPermissions(
                    service="codepipeline",
                    action="get-pipeline",
                    permissions=[
                        IAMPermission(action="codepipeline:GetPipeline", resource="*"),
                    ],
                    description="Get CodePipeline pipeline details",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "create-pipeline": CommandPermissions(
                    service="codepipeline",
                    action="create-pipeline",
                    permissions=[
                        IAMPermission(action="codepipeline:CreatePipeline", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create CodePipeline pipeline",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "delete-pipeline": CommandPermissions(
                    service="codepipeline",
                    action="delete-pipeline",
                    permissions=[
                        IAMPermission(action="codepipeline:DeletePipeline", resource="*"),
                    ],
                    description="Delete CodePipeline pipeline",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "start-pipeline-execution": CommandPermissions(
                    service="codepipeline",
                    action="start-pipeline-execution",
                    permissions=[
                        IAMPermission(action="codepipeline:StartPipelineExecution", resource="*"),
                    ],
                    description="Start CodePipeline execution",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "get-pipeline-execution": CommandPermissions(
                    service="codepipeline",
                    action="get-pipeline-execution",
                    permissions=[
                        IAMPermission(action="codepipeline:GetPipelineExecution", resource="*"),
                    ],
                    description="Get CodePipeline execution details",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "list-pipeline-executions": CommandPermissions(
                    service="codepipeline",
                    action="list-pipeline-executions",
                    permissions=[
                        IAMPermission(action="codepipeline:ListPipelineExecutions", resource="*"),
                    ],
                    description="List CodePipeline executions",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
                "stop-pipeline-execution": CommandPermissions(
                    service="codepipeline",
                    action="stop-pipeline-execution",
                    permissions=[
                        IAMPermission(action="codepipeline:StopPipelineExecution", resource="*"),
                    ],
                    description="Stop CodePipeline execution",
                    resource_patterns=["arn:aws:codepipeline:*:*:pipeline/*"]
                ),
            },
            "sagemaker": {
                "list-models": CommandPermissions(
                    service="sagemaker",
                    action="list-models",
                    permissions=[
                        IAMPermission(action="sagemaker:ListModels", resource="*"),
                    ],
                    description="List SageMaker models",
                    resource_patterns=["arn:aws:sagemaker:*:*:model/*"]
                ),
                "describe-model": CommandPermissions(
                    service="sagemaker",
                    action="describe-model",
                    permissions=[
                        IAMPermission(action="sagemaker:DescribeModel", resource="*"),
                    ],
                    description="Describe SageMaker model",
                    resource_patterns=["arn:aws:sagemaker:*:*:model/*"]
                ),
                "create-model": CommandPermissions(
                    service="sagemaker",
                    action="create-model",
                    permissions=[
                        IAMPermission(action="sagemaker:CreateModel", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create SageMaker model",
                    resource_patterns=["arn:aws:sagemaker:*:*:model/*"]
                ),
                "delete-model": CommandPermissions(
                    service="sagemaker",
                    action="delete-model",
                    permissions=[
                        IAMPermission(action="sagemaker:DeleteModel", resource="*"),
                    ],
                    description="Delete SageMaker model",
                    resource_patterns=["arn:aws:sagemaker:*:*:model/*"]
                ),
                "list-training-jobs": CommandPermissions(
                    service="sagemaker",
                    action="list-training-jobs",
                    permissions=[
                        IAMPermission(action="sagemaker:ListTrainingJobs", resource="*"),
                    ],
                    description="List SageMaker training jobs",
                    resource_patterns=["arn:aws:sagemaker:*:*:training-job/*"]
                ),
                "describe-training-job": CommandPermissions(
                    service="sagemaker",
                    action="describe-training-job",
                    permissions=[
                        IAMPermission(action="sagemaker:DescribeTrainingJob", resource="*"),
                    ],
                    description="Describe SageMaker training job",
                    resource_patterns=["arn:aws:sagemaker:*:*:training-job/*"]
                ),
                "create-training-job": CommandPermissions(
                    service="sagemaker",
                    action="create-training-job",
                    permissions=[
                        IAMPermission(action="sagemaker:CreateTrainingJob", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create SageMaker training job",
                    resource_patterns=["arn:aws:sagemaker:*:*:training-job/*"]
                ),
                "stop-training-job": CommandPermissions(
                    service="sagemaker",
                    action="stop-training-job",
                    permissions=[
                        IAMPermission(action="sagemaker:StopTrainingJob", resource="*"),
                    ],
                    description="Stop SageMaker training job",
                    resource_patterns=["arn:aws:sagemaker:*:*:training-job/*"]
                ),
                "list-endpoints": CommandPermissions(
                    service="sagemaker",
                    action="list-endpoints",
                    permissions=[
                        IAMPermission(action="sagemaker:ListEndpoints", resource="*"),
                    ],
                    description="List SageMaker endpoints",
                    resource_patterns=["arn:aws:sagemaker:*:*:endpoint/*"]
                ),
                "describe-endpoint": CommandPermissions(
                    service="sagemaker",
                    action="describe-endpoint",
                    permissions=[
                        IAMPermission(action="sagemaker:DescribeEndpoint", resource="*"),
                    ],
                    description="Describe SageMaker endpoint",
                    resource_patterns=["arn:aws:sagemaker:*:*:endpoint/*"]
                ),
                "create-endpoint": CommandPermissions(
                    service="sagemaker",
                    action="create-endpoint",
                    permissions=[
                        IAMPermission(action="sagemaker:CreateEndpoint", resource="*"),
                    ],
                    description="Create SageMaker endpoint",
                    resource_patterns=["arn:aws:sagemaker:*:*:endpoint/*"]
                ),
                "delete-endpoint": CommandPermissions(
                    service="sagemaker",
                    action="delete-endpoint",
                    permissions=[
                        IAMPermission(action="sagemaker:DeleteEndpoint", resource="*"),
                    ],
                    description="Delete SageMaker endpoint",
                    resource_patterns=["arn:aws:sagemaker:*:*:endpoint/*"]
                ),
                "invoke-endpoint": CommandPermissions(
                    service="sagemaker",
                    action="invoke-endpoint",
                    permissions=[
                        IAMPermission(action="sagemaker:InvokeEndpoint", resource="*"),
                    ],
                    description="Invoke SageMaker endpoint for prediction",
                    resource_patterns=["arn:aws:sagemaker:*:*:endpoint/*"]
                ),
            },
            "glue": {
                "get-databases": CommandPermissions(
                    service="glue",
                    action="get-databases",
                    permissions=[
                        IAMPermission(action="glue:GetDatabases", resource="*"),
                    ],
                    description="Get Glue databases",
                    resource_patterns=["arn:aws:glue:*:*:database/*"]
                ),
                "get-database": CommandPermissions(
                    service="glue",
                    action="get-database",
                    permissions=[
                        IAMPermission(action="glue:GetDatabase", resource="*"),
                    ],
                    description="Get Glue database details",
                    resource_patterns=["arn:aws:glue:*:*:database/*"]
                ),
                "create-database": CommandPermissions(
                    service="glue",
                    action="create-database",
                    permissions=[
                        IAMPermission(action="glue:CreateDatabase", resource="*"),
                    ],
                    description="Create Glue database",
                    resource_patterns=["arn:aws:glue:*:*:database/*"]
                ),
                "delete-database": CommandPermissions(
                    service="glue",
                    action="delete-database",
                    permissions=[
                        IAMPermission(action="glue:DeleteDatabase", resource="*"),
                    ],
                    description="Delete Glue database",
                    resource_patterns=["arn:aws:glue:*:*:database/*"]
                ),
                "get-tables": CommandPermissions(
                    service="glue",
                    action="get-tables",
                    permissions=[
                        IAMPermission(action="glue:GetTables", resource="*"),
                    ],
                    description="Get Glue tables",
                    resource_patterns=["arn:aws:glue:*:*:table/*"]
                ),
                "get-table": CommandPermissions(
                    service="glue",
                    action="get-table",
                    permissions=[
                        IAMPermission(action="glue:GetTable", resource="*"),
                    ],
                    description="Get Glue table details",
                    resource_patterns=["arn:aws:glue:*:*:table/*"]
                ),
                "create-table": CommandPermissions(
                    service="glue",
                    action="create-table",
                    permissions=[
                        IAMPermission(action="glue:CreateTable", resource="*"),
                    ],
                    description="Create Glue table",
                    resource_patterns=["arn:aws:glue:*:*:table/*"]
                ),
                "delete-table": CommandPermissions(
                    service="glue",
                    action="delete-table",
                    permissions=[
                        IAMPermission(action="glue:DeleteTable", resource="*"),
                    ],
                    description="Delete Glue table",
                    resource_patterns=["arn:aws:glue:*:*:table/*"]
                ),
                "get-jobs": CommandPermissions(
                    service="glue",
                    action="get-jobs",
                    permissions=[
                        IAMPermission(action="glue:GetJobs", resource="*"),
                    ],
                    description="Get Glue jobs",
                    resource_patterns=["arn:aws:glue:*:*:job/*"]
                ),
                "get-job": CommandPermissions(
                    service="glue",
                    action="get-job",
                    permissions=[
                        IAMPermission(action="glue:GetJob", resource="*"),
                    ],
                    description="Get Glue job details",
                    resource_patterns=["arn:aws:glue:*:*:job/*"]
                ),
                "create-job": CommandPermissions(
                    service="glue",
                    action="create-job",
                    permissions=[
                        IAMPermission(action="glue:CreateJob", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create Glue job",
                    resource_patterns=["arn:aws:glue:*:*:job/*"]
                ),
                "start-job-run": CommandPermissions(
                    service="glue",
                    action="start-job-run",
                    permissions=[
                        IAMPermission(action="glue:StartJobRun", resource="*"),
                    ],
                    description="Start Glue job run",
                    resource_patterns=["arn:aws:glue:*:*:job/*"]
                ),
            },
            "athena": {
                "list-work-groups": CommandPermissions(
                    service="athena",
                    action="list-work-groups",
                    permissions=[
                        IAMPermission(action="athena:ListWorkGroups", resource="*"),
                    ],
                    description="List Athena work groups",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "get-work-group": CommandPermissions(
                    service="athena",
                    action="get-work-group",
                    permissions=[
                        IAMPermission(action="athena:GetWorkGroup", resource="*"),
                    ],
                    description="Get Athena work group details",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "create-work-group": CommandPermissions(
                    service="athena",
                    action="create-work-group",
                    permissions=[
                        IAMPermission(action="athena:CreateWorkGroup", resource="*"),
                    ],
                    description="Create Athena work group",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "delete-work-group": CommandPermissions(
                    service="athena",
                    action="delete-work-group",
                    permissions=[
                        IAMPermission(action="athena:DeleteWorkGroup", resource="*"),
                    ],
                    description="Delete Athena work group",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "start-query-execution": CommandPermissions(
                    service="athena",
                    action="start-query-execution",
                    permissions=[
                        IAMPermission(action="athena:StartQueryExecution", resource="*"),
                        IAMPermission(action="s3:GetObject", resource="*"),
                        IAMPermission(action="s3:ListBucket", resource="*"),
                        IAMPermission(action="s3:PutObject", resource="*"),
                    ],
                    description="Start Athena query execution",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "get-query-execution": CommandPermissions(
                    service="athena",
                    action="get-query-execution",
                    permissions=[
                        IAMPermission(action="athena:GetQueryExecution", resource="*"),
                    ],
                    description="Get Athena query execution details",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "get-query-results": CommandPermissions(
                    service="athena",
                    action="get-query-results",
                    permissions=[
                        IAMPermission(action="athena:GetQueryResults", resource="*"),
                        IAMPermission(action="s3:GetObject", resource="*"),
                    ],
                    description="Get Athena query results",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
                "list-query-executions": CommandPermissions(
                    service="athena",
                    action="list-query-executions",
                    permissions=[
                        IAMPermission(action="athena:ListQueryExecutions", resource="*"),
                    ],
                    description="List Athena query executions",
                    resource_patterns=["arn:aws:athena:*:*:workgroup/*"]
                ),
            },
            "emr": {
                "list-clusters": CommandPermissions(
                    service="emr",
                    action="list-clusters",
                    permissions=[
                        IAMPermission(action="elasticmapreduce:ListClusters", resource="*"),
                    ],
                    description="List EMR clusters",
                    resource_patterns=["arn:aws:elasticmapreduce:*:*:cluster/*"]
                ),
                "describe-cluster": CommandPermissions(
                    service="emr",
                    action="describe-cluster",
                    permissions=[
                        IAMPermission(action="elasticmapreduce:DescribeCluster", resource="*"),
                    ],
                    description="Describe EMR cluster",
                    resource_patterns=["arn:aws:elasticmapreduce:*:*:cluster/*"]
                ),
                "run-job-flow": CommandPermissions(
                    service="emr",
                    action="run-job-flow",
                    permissions=[
                        IAMPermission(action="elasticmapreduce:RunJobFlow", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                        IAMPermission(action="ec2:DescribeSubnets", resource="*"),
                        IAMPermission(action="ec2:DescribeVpcs", resource="*"),
                    ],
                    description="Run EMR job flow (create cluster)",
                    resource_patterns=["arn:aws:elasticmapreduce:*:*:cluster/*"]
                ),
                "terminate-job-flows": CommandPermissions(
                    service="emr",
                    action="terminate-job-flows",
                    permissions=[
                        IAMPermission(action="elasticmapreduce:TerminateJobFlows", resource="*"),
                    ],
                    description="Terminate EMR job flows (clusters)",
                    resource_patterns=["arn:aws:elasticmapreduce:*:*:cluster/*"]
                ),
                "list-steps": CommandPermissions(
                    service="emr",
                    action="list-steps",
                    permissions=[
                        IAMPermission(action="elasticmapreduce:ListSteps", resource="*"),
                    ],
                    description="List EMR steps",
                    resource_patterns=["arn:aws:elasticmapreduce:*:*:cluster/*"]
                ),
                "add-job-flow-steps": CommandPermissions(
                    service="emr",
                    action="add-job-flow-steps",
                    permissions=[
                        IAMPermission(action="elasticmapreduce:AddJobFlowSteps", resource="*"),
                    ],
                    description="Add steps to EMR cluster",
                    resource_patterns=["arn:aws:elasticmapreduce:*:*:cluster/*"]
                ),
            },
            "redshift": {
                "describe-clusters": CommandPermissions(
                    service="redshift",
                    action="describe-clusters",
                    permissions=[
                        IAMPermission(action="redshift:DescribeClusters", resource="*"),
                    ],
                    description="Describe Redshift clusters",
                    resource_patterns=["arn:aws:redshift:*:*:cluster:*"]
                ),
                "create-cluster": CommandPermissions(
                    service="redshift",
                    action="create-cluster",
                    permissions=[
                        IAMPermission(action="redshift:CreateCluster", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create Redshift cluster",
                    resource_patterns=["arn:aws:redshift:*:*:cluster:*"]
                ),
                "delete-cluster": CommandPermissions(
                    service="redshift",
                    action="delete-cluster",
                    permissions=[
                        IAMPermission(action="redshift:DeleteCluster", resource="*"),
                    ],
                    description="Delete Redshift cluster",
                    resource_patterns=["arn:aws:redshift:*:*:cluster:*"]
                ),
                "modify-cluster": CommandPermissions(
                    service="redshift",
                    action="modify-cluster",
                    permissions=[
                        IAMPermission(action="redshift:ModifyCluster", resource="*"),
                    ],
                    description="Modify Redshift cluster",
                    resource_patterns=["arn:aws:redshift:*:*:cluster:*"]
                ),
                "reboot-cluster": CommandPermissions(
                    service="redshift",
                    action="reboot-cluster",
                    permissions=[
                        IAMPermission(action="redshift:RebootCluster", resource="*"),
                    ],
                    description="Reboot Redshift cluster",
                    resource_patterns=["arn:aws:redshift:*:*:cluster:*"]
                ),
                "describe-cluster-snapshots": CommandPermissions(
                    service="redshift",
                    action="describe-cluster-snapshots",
                    permissions=[
                        IAMPermission(action="redshift:DescribeClusterSnapshots", resource="*"),
                    ],
                    description="Describe Redshift cluster snapshots",
                    resource_patterns=["arn:aws:redshift:*:*:snapshot:*"]
                ),
                "create-cluster-snapshot": CommandPermissions(
                    service="redshift",
                    action="create-cluster-snapshot",
                    permissions=[
                        IAMPermission(action="redshift:CreateClusterSnapshot", resource="*"),
                    ],
                    description="Create Redshift cluster snapshot",
                    resource_patterns=["arn:aws:redshift:*:*:snapshot:*"]
                ),
            },
            "opensearch": {
                "list-domain-names": CommandPermissions(
                    service="opensearch",
                    action="list-domain-names",
                    permissions=[
                        IAMPermission(action="es:ListDomainNames", resource="*"),
                    ],
                    description="List OpenSearch domain names",
                    resource_patterns=["arn:aws:es:*:*:domain/*"]
                ),
                "describe-domain": CommandPermissions(
                    service="opensearch",
                    action="describe-domain",
                    permissions=[
                        IAMPermission(action="es:DescribeElasticsearchDomain", resource="*"),
                    ],
                    description="Describe OpenSearch domain",
                    resource_patterns=["arn:aws:es:*:*:domain/*"]
                ),
                "create-domain": CommandPermissions(
                    service="opensearch",
                    action="create-domain",
                    permissions=[
                        IAMPermission(action="es:CreateElasticsearchDomain", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create OpenSearch domain",
                    resource_patterns=["arn:aws:es:*:*:domain/*"]
                ),
                "delete-domain": CommandPermissions(
                    service="opensearch",
                    action="delete-domain",
                    permissions=[
                        IAMPermission(action="es:DeleteElasticsearchDomain", resource="*"),
                    ],
                    description="Delete OpenSearch domain",
                    resource_patterns=["arn:aws:es:*:*:domain/*"]
                ),
                "update-domain-config": CommandPermissions(
                    service="opensearch",
                    action="update-domain-config",
                    permissions=[
                        IAMPermission(action="es:UpdateElasticsearchDomainConfig", resource="*"),
                    ],
                    description="Update OpenSearch domain configuration",
                    resource_patterns=["arn:aws:es:*:*:domain/*"]
                ),
            },
            "events": {
                "list-rules": CommandPermissions(
                    service="events",
                    action="list-rules",
                    permissions=[
                        IAMPermission(action="events:ListRules", resource="*"),
                    ],
                    description="List EventBridge rules",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "describe-rule": CommandPermissions(
                    service="events",
                    action="describe-rule",
                    permissions=[
                        IAMPermission(action="events:DescribeRule", resource="*"),
                    ],
                    description="Describe EventBridge rule",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "put-rule": CommandPermissions(
                    service="events",
                    action="put-rule",
                    permissions=[
                        IAMPermission(action="events:PutRule", resource="*"),
                    ],
                    description="Create or update EventBridge rule",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "delete-rule": CommandPermissions(
                    service="events",
                    action="delete-rule",
                    permissions=[
                        IAMPermission(action="events:DeleteRule", resource="*"),
                    ],
                    description="Delete EventBridge rule",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "put-targets": CommandPermissions(
                    service="events",
                    action="put-targets",
                    permissions=[
                        IAMPermission(action="events:PutTargets", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Add targets to EventBridge rule",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "remove-targets": CommandPermissions(
                    service="events",
                    action="remove-targets",
                    permissions=[
                        IAMPermission(action="events:RemoveTargets", resource="*"),
                    ],
                    description="Remove targets from EventBridge rule",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "list-targets-by-rule": CommandPermissions(
                    service="events",
                    action="list-targets-by-rule",
                    permissions=[
                        IAMPermission(action="events:ListTargetsByRule", resource="*"),
                    ],
                    description="List targets for EventBridge rule",
                    resource_patterns=["arn:aws:events:*:*:rule/*"]
                ),
                "put-events": CommandPermissions(
                    service="events",
                    action="put-events",
                    permissions=[
                        IAMPermission(action="events:PutEvents", resource="*"),
                    ],
                    description="Send events to EventBridge",
                    resource_patterns=["arn:aws:events:*:*:event-bus/*"]
                ),
            },
            "ssm": {
                "get-parameter": CommandPermissions(
                    service="ssm",
                    action="get-parameter",
                    permissions=[
                        IAMPermission(action="ssm:GetParameter", resource="*"),
                    ],
                    description="Get Systems Manager parameter",
                    resource_patterns=["arn:aws:ssm:*:*:parameter/*"]
                ),
                "get-parameters": CommandPermissions(
                    service="ssm",
                    action="get-parameters",
                    permissions=[
                        IAMPermission(action="ssm:GetParameters", resource="*"),
                    ],
                    description="Get multiple Systems Manager parameters",
                    resource_patterns=["arn:aws:ssm:*:*:parameter/*"]
                ),
                "put-parameter": CommandPermissions(
                    service="ssm",
                    action="put-parameter",
                    permissions=[
                        IAMPermission(action="ssm:PutParameter", resource="*"),
                    ],
                    description="Put Systems Manager parameter",
                    resource_patterns=["arn:aws:ssm:*:*:parameter/*"]
                ),
                "delete-parameter": CommandPermissions(
                    service="ssm",
                    action="delete-parameter",
                    permissions=[
                        IAMPermission(action="ssm:DeleteParameter", resource="*"),
                    ],
                    description="Delete Systems Manager parameter",
                    resource_patterns=["arn:aws:ssm:*:*:parameter/*"]
                ),
                "describe-parameters": CommandPermissions(
                    service="ssm",
                    action="describe-parameters",
                    permissions=[
                        IAMPermission(action="ssm:DescribeParameters", resource="*"),
                    ],
                    description="Describe Systems Manager parameters",
                    resource_patterns=["arn:aws:ssm:*:*:parameter/*"]
                ),
                "get-parameters-by-path": CommandPermissions(
                    service="ssm",
                    action="get-parameters-by-path",
                    permissions=[
                        IAMPermission(action="ssm:GetParametersByPath", resource="*"),
                    ],
                    description="Get Systems Manager parameters by path",
                    resource_patterns=["arn:aws:ssm:*:*:parameter/*"]
                ),
                "start-session": CommandPermissions(
                    service="ssm",
                    action="start-session",
                    permissions=[
                        IAMPermission(action="ssm:StartSession", resource="*"),
                        IAMPermission(action="ssm:DescribeInstanceInformation", resource="*"),
                    ],
                    description="Start Systems Manager session",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*"]
                ),
                "terminate-session": CommandPermissions(
                    service="ssm",
                    action="terminate-session",
                    permissions=[
                        IAMPermission(action="ssm:TerminateSession", resource="*"),
                    ],
                    description="Terminate Systems Manager session",
                    resource_patterns=["arn:aws:ssm:*:*:session/*"]
                ),
                "send-command": CommandPermissions(
                    service="ssm",
                    action="send-command",
                    permissions=[
                        IAMPermission(action="ssm:SendCommand", resource="*"),
                        IAMPermission(action="ssm:DescribeInstanceInformation", resource="*"),
                    ],
                    description="Send command via Systems Manager",
                    resource_patterns=["arn:aws:ec2:*:*:instance/*"]
                ),
            },
            "acm": {
                "list-certificates": CommandPermissions(
                    service="acm",
                    action="list-certificates",
                    permissions=[
                        IAMPermission(action="acm:ListCertificates", resource="*"),
                    ],
                    description="List ACM certificates",
                    resource_patterns=["arn:aws:acm:*:*:certificate/*"]
                ),
                "describe-certificate": CommandPermissions(
                    service="acm",
                    action="describe-certificate",
                    permissions=[
                        IAMPermission(action="acm:DescribeCertificate", resource="*"),
                    ],
                    description="Describe ACM certificate",
                    resource_patterns=["arn:aws:acm:*:*:certificate/*"]
                ),
                "request-certificate": CommandPermissions(
                    service="acm",
                    action="request-certificate",
                    permissions=[
                        IAMPermission(action="acm:RequestCertificate", resource="*"),
                    ],
                    description="Request ACM certificate",
                    resource_patterns=["arn:aws:acm:*:*:certificate/*"]
                ),
                "delete-certificate": CommandPermissions(
                    service="acm",
                    action="delete-certificate",
                    permissions=[
                        IAMPermission(action="acm:DeleteCertificate", resource="*"),
                    ],
                    description="Delete ACM certificate",
                    resource_patterns=["arn:aws:acm:*:*:certificate/*"]
                ),
                "import-certificate": CommandPermissions(
                    service="acm",
                    action="import-certificate",
                    permissions=[
                        IAMPermission(action="acm:ImportCertificate", resource="*"),
                    ],
                    description="Import certificate to ACM",
                    resource_patterns=["arn:aws:acm:*:*:certificate/*"]
                ),
                "export-certificate": CommandPermissions(
                    service="acm",
                    action="export-certificate",
                    permissions=[
                        IAMPermission(action="acm:ExportCertificate", resource="*"),
                    ],
                    description="Export ACM certificate",
                    resource_patterns=["arn:aws:acm:*:*:certificate/*"]
                ),
            },
            "appsync": {
                "list-graphql-apis": CommandPermissions(
                    service="appsync",
                    action="list-graphql-apis",
                    permissions=[
                        IAMPermission(action="appsync:ListGraphqlApis", resource="*"),
                    ],
                    description="List AppSync GraphQL APIs",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*"]
                ),
                "get-graphql-api": CommandPermissions(
                    service="appsync",
                    action="get-graphql-api",
                    permissions=[
                        IAMPermission(action="appsync:GetGraphqlApi", resource="*"),
                    ],
                    description="Get AppSync GraphQL API details",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*"]
                ),
                "create-graphql-api": CommandPermissions(
                    service="appsync",
                    action="create-graphql-api",
                    permissions=[
                        IAMPermission(action="appsync:CreateGraphqlApi", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create AppSync GraphQL API",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*"]
                ),
                "delete-graphql-api": CommandPermissions(
                    service="appsync",
                    action="delete-graphql-api",
                    permissions=[
                        IAMPermission(action="appsync:DeleteGraphqlApi", resource="*"),
                    ],
                    description="Delete AppSync GraphQL API",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*"]
                ),
                "update-graphql-api": CommandPermissions(
                    service="appsync",
                    action="update-graphql-api",
                    permissions=[
                        IAMPermission(action="appsync:UpdateGraphqlApi", resource="*"),
                    ],
                    description="Update AppSync GraphQL API",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*"]
                ),
                "list-data-sources": CommandPermissions(
                    service="appsync",
                    action="list-data-sources",
                    permissions=[
                        IAMPermission(action="appsync:ListDataSources", resource="*"),
                    ],
                    description="List AppSync data sources",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*/datasources/*"]
                ),
                "create-data-source": CommandPermissions(
                    service="appsync",
                    action="create-data-source",
                    permissions=[
                        IAMPermission(action="appsync:CreateDataSource", resource="*"),
                        IAMPermission(action="iam:PassRole", resource="*"),
                    ],
                    description="Create AppSync data source",
                    resource_patterns=["arn:aws:appsync:*:*:apis/*/datasources/*"]
                ),
            },
            "cognito-idp": {
                "list-user-pools": CommandPermissions(
                    service="cognito-idp",
                    action="list-user-pools",
                    permissions=[
                        IAMPermission(action="cognito-idp:ListUserPools", resource="*"),
                    ],
                    description="List Cognito user pools",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "describe-user-pool": CommandPermissions(
                    service="cognito-idp",
                    action="describe-user-pool",
                    permissions=[
                        IAMPermission(action="cognito-idp:DescribeUserPool", resource="*"),
                    ],
                    description="Describe Cognito user pool",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "create-user-pool": CommandPermissions(
                    service="cognito-idp",
                    action="create-user-pool",
                    permissions=[
                        IAMPermission(action="cognito-idp:CreateUserPool", resource="*"),
                    ],
                    description="Create Cognito user pool",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "delete-user-pool": CommandPermissions(
                    service="cognito-idp",
                    action="delete-user-pool",
                    permissions=[
                        IAMPermission(action="cognito-idp:DeleteUserPool", resource="*"),
                    ],
                    description="Delete Cognito user pool",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "list-user-pool-clients": CommandPermissions(
                    service="cognito-idp",
                    action="list-user-pool-clients",
                    permissions=[
                        IAMPermission(action="cognito-idp:ListUserPoolClients", resource="*"),
                    ],
                    description="List Cognito user pool clients",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "create-user-pool-client": CommandPermissions(
                    service="cognito-idp",
                    action="create-user-pool-client",
                    permissions=[
                        IAMPermission(action="cognito-idp:CreateUserPoolClient", resource="*"),
                    ],
                    description="Create Cognito user pool client",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "list-users": CommandPermissions(
                    service="cognito-idp",
                    action="list-users",
                    permissions=[
                        IAMPermission(action="cognito-idp:ListUsers", resource="*"),
                    ],
                    description="List users in Cognito user pool",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "admin-create-user": CommandPermissions(
                    service="cognito-idp",
                    action="admin-create-user",
                    permissions=[
                        IAMPermission(action="cognito-idp:AdminCreateUser", resource="*"),
                    ],
                    description="Admin create user in Cognito user pool",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
                "admin-delete-user": CommandPermissions(
                    service="cognito-idp",
                    action="admin-delete-user",
                    permissions=[
                        IAMPermission(action="cognito-idp:AdminDeleteUser", resource="*"),
                    ],
                    description="Admin delete user from Cognito user pool",
                    resource_patterns=["arn:aws:cognito-idp:*:*:userpool/*"]
                ),
            },
            "cognito-identity": {
                "list-identity-pools": CommandPermissions(
                    service="cognito-identity",
                    action="list-identity-pools",
                    permissions=[
                        IAMPermission(action="cognito-identity:ListIdentityPools", resource="*"),
                    ],
                    description="List Cognito identity pools",
                    resource_patterns=["arn:aws:cognito-identity:*:*:identitypool/*"]
                ),
                "describe-identity-pool": CommandPermissions(
                    service="cognito-identity",
                    action="describe-identity-pool",
                    permissions=[
                        IAMPermission(action="cognito-identity:DescribeIdentityPool", resource="*"),
                    ],
                    description="Describe Cognito identity pool",
                    resource_patterns=["arn:aws:cognito-identity:*:*:identitypool/*"]
                ),
                "create-identity-pool": CommandPermissions(
                    service="cognito-identity",
                    action="create-identity-pool",
                    permissions=[
                        IAMPermission(action="cognito-identity:CreateIdentityPool", resource="*"),
                    ],
                    description="Create Cognito identity pool",
                    resource_patterns=["arn:aws:cognito-identity:*:*:identitypool/*"]
                ),
                "delete-identity-pool": CommandPermissions(
                    service="cognito-identity",
                    action="delete-identity-pool",
                    permissions=[
                        IAMPermission(action="cognito-identity:DeleteIdentityPool", resource="*"),
                    ],
                    description="Delete Cognito identity pool",
                    resource_patterns=["arn:aws:cognito-identity:*:*:identitypool/*"]
                ),
                "get-id": CommandPermissions(
                    service="cognito-identity",
                    action="get-id",
                    permissions=[
                        IAMPermission(action="cognito-identity:GetId", resource="*"),
                    ],
                    description="Get ID for Cognito identity",
                    resource_patterns=["arn:aws:cognito-identity:*:*:identitypool/*"]
                ),
                "get-credentials-for-identity": CommandPermissions(
                    service="cognito-identity",
                    action="get-credentials-for-identity",
                    permissions=[
                        IAMPermission(action="cognito-identity:GetCredentialsForIdentity", resource="*"),
                    ],
                    description="Get credentials for Cognito identity",
                    resource_patterns=["arn:aws:cognito-identity:*:*:identitypool/*"]
                ),
            },
        }
    
    def get_permissions(self, service: str, action: str) -> List[Dict]:
        """
        Get permissions for a specific AWS CLI command.
        
        Args:
            service: AWS service name
            action: CLI action name
            
        Returns:
            List of permission dictionaries, empty list if not found
        """
        service = service.lower()
        action = action.lower()
        
        if service in self._permissions_map:
            cmd_perms = self._permissions_map[service].get(action)
            if cmd_perms:
                return [
                    {
                        "action": perm.action,
                        "resource": perm.resource,
                        "condition": perm.condition,
                        "effect": perm.effect
                    }
                    for perm in cmd_perms.permissions
                ]
        return []
    
    def get_permissions_object(self, service: str, action: str) -> Optional[CommandPermissions]:
        """
        Get permissions as CommandPermissions object.
        
        Args:
            service: AWS service name
            action: CLI action name
            
        Returns:
            CommandPermissions object if found, None otherwise
        """
        service = service.lower()
        action = action.lower()
        
        if service in self._permissions_map:
            return self._permissions_map[service].get(action)
        return None
    
    def get_supported_services(self) -> List[str]:
        """
        Get list of supported AWS services.
        
        Returns:
            List of supported service names
        """
        return list(self._permissions_map.keys())
    
    def search_permissions(self, query: str) -> List[CommandPermissions]:
        """
        Search for permissions by service, action, or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching CommandPermissions
        """
        results = []
        query = query.lower()
        
        for service_commands in self._permissions_map.values():
            for command_perms in service_commands.values():
                # Search in service, action, or description
                if (query in command_perms.service.lower() or 
                    query in command_perms.action.lower() or 
                    query in command_perms.description.lower()):
                    results.append(command_perms)
        
        return results
    
    def get_all_services(self) -> List[str]:
        """Get list of all supported services."""
        return list(self._permissions_map.keys())
    
    def get_service_actions(self, service: str) -> List[str]:
        """Get list of all actions for a service."""
        service = service.lower()
        if service in self._permissions_map:
            return list(self._permissions_map[service].keys())
        return []
    
    def add_custom_permission(self, command_permissions: CommandPermissions):
        """
        Add custom permission mapping.
        
        Args:
            command_permissions: Custom command permissions to add
        """
        service = command_permissions.service.lower()
        action = command_permissions.action.lower()
        
        if service not in self._permissions_map:
            self._permissions_map[service] = {}
        
        self._permissions_map[service][action] = command_permissions
    
    def get_minimal_permissions(self, commands: List[str]) -> Set[str]:
        """
        Get minimal set of IAM permissions for multiple commands.
        
        Args:
            commands: List of AWS CLI commands
            
        Returns:
            Set of unique IAM action strings
        """
        from .parser import AWSCLIParser
        
        parser = AWSCLIParser()
        all_permissions = set()
        
        for command in commands:
            try:
                parsed = parser.parse_command(command)
                perms = self.get_permissions(parsed.service, parsed.action)
                
                if perms:
                    for perm in perms:
                        all_permissions.add(perm["action"])
                else:
                    # Fallback: create basic permission pattern
                    basic_action = f"{parsed.service}:{self._convert_action_to_iam(parsed.action)}"
                    all_permissions.add(basic_action)
            
            except ValueError:
                continue
        
        return all_permissions
    
    def _convert_action_to_iam(self, cli_action: str) -> str:
        """
        Convert CLI action to IAM action format.
        
        Args:
            cli_action: CLI action name (e.g., 'list-buckets')
            
        Returns:
            IAM action name (e.g., 'ListBuckets')
        """
        # Convert kebab-case to PascalCase
        parts = cli_action.split('-')
        return ''.join(word.capitalize() for word in parts)
    
    def generate_policy_document(self, commands: List[str]) -> Dict:
        """
        Generate IAM policy document for given commands.
        
        Args:
            commands: List of AWS CLI commands
            
        Returns:
            IAM policy document as dictionary
        """
        from .parser import AWSCLIParser
        
        parser = AWSCLIParser()
        statements = []
        
        for command in commands:
            try:
                parsed = parser.parse_command(command)
                perms = self.get_permissions(parsed.service, parsed.action)
                cmd_perms = self.get_permissions_object(parsed.service, parsed.action)
                
                if perms:
                    actions = [perm["action"] for perm in perms]
                    resources = ["*"]  # Default to all resources
                    
                    # Try to be more specific with resources if possible
                    if parsed.resource_arns:
                        resources = parsed.resource_arns
                    elif cmd_perms and cmd_perms.resource_patterns:
                        resources = cmd_perms.resource_patterns
                    
                    statement = {
                        "Effect": "Allow",
                        "Action": actions,
                        "Resource": resources
                    }
                    statements.append(statement)
            
            except ValueError:
                continue
        
        # Consolidate similar statements
        consolidated_statements = self._consolidate_statements(statements)
        
        return {
            "Version": "2012-10-17",
            "Statement": consolidated_statements
        }
    
    def _consolidate_statements(self, statements: List[Dict]) -> List[Dict]:
        """Consolidate similar policy statements to reduce redundancy."""
        if not statements:
            return statements
        
        # Group by resource patterns
        resource_groups = {}
        
        for stmt in statements:
            resource_key = json.dumps(sorted(stmt.get("Resource", [])))
            if resource_key not in resource_groups:
                resource_groups[resource_key] = {
                    "Effect": stmt["Effect"],
                    "Action": [],
                    "Resource": stmt["Resource"]
                }
            
            actions = stmt["Action"]
            if isinstance(actions, str):
                actions = [actions]
            
            resource_groups[resource_key]["Action"].extend(actions)
        
        # Remove duplicates and sort
        for group in resource_groups.values():
            group["Action"] = sorted(list(set(group["Action"])))
        
        return list(resource_groups.values())


# Example usage
if __name__ == "__main__":
    db = IAMPermissionsDatabase()
    
    # Test permission lookup
    s3_ls_perms = db.get_permissions("s3", "ls")
    print("S3 ls permissions:", s3_ls_perms)
    
    # Test policy generation
    commands = [
        "aws s3 ls",
        "aws s3 cp file.txt s3://my-bucket/",
        "aws ec2 describe-instances",
        "aws iam list-users"
    ]
    
    policy = db.generate_policy_document(commands)
    print("\nGenerated policy:")
    print(json.dumps(policy, indent=2))
