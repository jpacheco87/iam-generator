#!/usr/bin/env python3
"""
Quick Database Update

Manually add high-priority AWS services that are commonly requested.
"""

import json
from pathlib import Path

# High-priority services to add with their common commands and permissions
NEW_SERVICES = {
    "bedrock-runtime": {
        "invoke-model": {
            "service": "bedrock-runtime",
            "action": "invoke-model",
            "permissions": [
                {"action": "bedrock:InvokeModel", "resource": "*"},
                {"action": "bedrock:InvokeModelWithResponseStream", "resource": "*"}
            ],
            "description": "Invoke Amazon Bedrock foundation models",
            "resource_patterns": ["*"]
        },
        "invoke-model-with-response-stream": {
            "service": "bedrock-runtime",
            "action": "invoke-model-with-response-stream",
            "permissions": [
                {"action": "bedrock:InvokeModelWithResponseStream", "resource": "*"}
            ],
            "description": "Invoke Amazon Bedrock models with streaming response",
            "resource_patterns": ["*"]
        }
    },
    "bedrock": {
        "list-foundation-models": {
            "service": "bedrock",
            "action": "list-foundation-models",
            "permissions": [
                {"action": "bedrock:ListFoundationModels", "resource": "*"}
            ],
            "description": "List available foundation models in Amazon Bedrock",
            "resource_patterns": ["*"]
        },
        "get-foundation-model": {
            "service": "bedrock",
            "action": "get-foundation-model",
            "permissions": [
                {"action": "bedrock:GetFoundationModel", "resource": "*"}
            ],
            "description": "Get details about a foundation model",
            "resource_patterns": ["*"]
        }
    },
    "textract": {
        "detect-document-text": {
            "service": "textract",
            "action": "detect-document-text",
            "permissions": [
                {"action": "textract:DetectDocumentText", "resource": "*"}
            ],
            "description": "Detect text in documents using Amazon Textract",
            "resource_patterns": ["*"]
        },
        "analyze-document": {
            "service": "textract",
            "action": "analyze-document",
            "permissions": [
                {"action": "textract:AnalyzeDocument", "resource": "*"}
            ],
            "description": "Analyze documents for forms and tables",
            "resource_patterns": ["*"]
        },
        "start-document-text-detection": {
            "service": "textract",
            "action": "start-document-text-detection",
            "permissions": [
                {"action": "textract:StartDocumentTextDetection", "resource": "*"}
            ],
            "description": "Start asynchronous text detection",
            "resource_patterns": ["*"]
        }
    },
    "rekognition": {
        "detect-faces": {
            "service": "rekognition",
            "action": "detect-faces",
            "permissions": [
                {"action": "rekognition:DetectFaces", "resource": "*"}
            ],
            "description": "Detect faces in images",
            "resource_patterns": ["*"]
        },
        "detect-labels": {
            "service": "rekognition",
            "action": "detect-labels",
            "permissions": [
                {"action": "rekognition:DetectLabels", "resource": "*"}
            ],
            "description": "Detect labels in images",
            "resource_patterns": ["*"]
        },
        "recognize-celebrities": {
            "service": "rekognition",
            "action": "recognize-celebrities",
            "permissions": [
                {"action": "rekognition:RecognizeCelebrities", "resource": "*"}
            ],
            "description": "Recognize celebrities in images",
            "resource_patterns": ["*"]
        }
    },
    "comprehend": {
        "detect-sentiment": {
            "service": "comprehend",
            "action": "detect-sentiment",
            "permissions": [
                {"action": "comprehend:DetectSentiment", "resource": "*"}
            ],
            "description": "Detect sentiment in text",
            "resource_patterns": ["*"]
        },
        "detect-entities": {
            "service": "comprehend",
            "action": "detect-entities",
            "permissions": [
                {"action": "comprehend:DetectEntities", "resource": "*"}
            ],
            "description": "Detect entities in text",
            "resource_patterns": ["*"]
        },
        "detect-key-phrases": {
            "service": "comprehend",
            "action": "detect-key-phrases",
            "permissions": [
                {"action": "comprehend:DetectKeyPhrases", "resource": "*"}
            ],
            "description": "Detect key phrases in text",
            "resource_patterns": ["*"]
        }
    },
    "polly": {
        "synthesize-speech": {
            "service": "polly",
            "action": "synthesize-speech",
            "permissions": [
                {"action": "polly:SynthesizeSpeech", "resource": "*"}
            ],
            "description": "Convert text to speech",
            "resource_patterns": ["*"]
        },
        "describe-voices": {
            "service": "polly",
            "action": "describe-voices",
            "permissions": [
                {"action": "polly:DescribeVoices", "resource": "*"}
            ],
            "description": "List available voices",
            "resource_patterns": ["*"]
        }
    },
    "transcribe": {
        "start-transcription-job": {
            "service": "transcribe",
            "action": "start-transcription-job",
            "permissions": [
                {"action": "transcribe:StartTranscriptionJob", "resource": "*"}
            ],
            "description": "Start audio transcription job",
            "resource_patterns": ["*"]
        },
        "get-transcription-job": {
            "service": "transcribe",
            "action": "get-transcription-job",
            "permissions": [
                {"action": "transcribe:GetTranscriptionJob", "resource": "*"}
            ],
            "description": "Get transcription job details",
            "resource_patterns": ["*"]
        }
    },
    "translate": {
        "translate-text": {
            "service": "translate",
            "action": "translate-text",
            "permissions": [
                {"action": "translate:TranslateText", "resource": "*"}
            ],
            "description": "Translate text between languages",
            "resource_patterns": ["*"]
        },
        "list-languages": {
            "service": "translate",
            "action": "list-languages",
            "permissions": [
                {"action": "translate:ListLanguages", "resource": "*"}
            ],
            "description": "List supported languages",
            "resource_patterns": ["*"]
        }
    }
}

def generate_database_update():
    """Generate the database update file."""
    
    # Save the new services to a JSON file
    output_file = Path("new_priority_services.json")
    with open(output_file, 'w') as f:
        json.dump(NEW_SERVICES, f, indent=2)
    
    print(f"✅ Generated database update file: {output_file}")
    print(f"📊 Added {len(NEW_SERVICES)} new services:")
    for service in NEW_SERVICES.keys():
        command_count = len(NEW_SERVICES[service])
        print(f"  • {service} ({command_count} commands)")
    
    # Generate Python code to add to permissions_db.py
    print("\n📝 To integrate into permissions_db.py, add this to the _permissions_map:")
    print("# === NEW AI/ML SERVICES ===")
    for service_name, commands in NEW_SERVICES.items():
        print(f'        "{service_name}": {{')
        for cmd_name, cmd_data in commands.items():
            print(f'            "{cmd_name}": CommandPermissions(')
            print(f'                service="{cmd_data["service"]}",')
            print(f'                action="{cmd_data["action"]}",')
            print(f'                permissions=[')
            for perm in cmd_data["permissions"]:
                print(f'                    IAMPermission(action="{perm["action"]}", resource="{perm["resource"]}"),')
            print(f'                ],')
            print(f'                description="{cmd_data["description"]}",')
            print(f'                resource_patterns={cmd_data["resource_patterns"]}')
            print(f'            ),')
        print(f'        }},')
    
    return output_file

if __name__ == "__main__":
    generate_database_update()
