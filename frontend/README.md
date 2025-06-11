# AWS IAM Generator - Frontend

A modern React frontend for the AWS CLI IAM Permissions Analyzer tool, featuring enterprise-grade IAM analysis capabilities, built with shadcn/ui components and Tailwind CSS.

## Features

### Core Analysis
- **Command Analysis**: Analyze single AWS CLI commands to extract required IAM permissions with resource-specific ARN detection
- **Enhanced Role Generation**: ✨ **One-click generation** of all output formats simultaneously (JSON, Terraform, CloudFormation, AWS CLI)
- **Advanced Batch Processing**: Analyze multiple commands with comprehensive summaries and dependency mapping

### ✨ Enhanced IAM Features (v2.3)
- **Policy Validation**: Interactive policy validation with security scoring (0-100), issue detection, and actionable recommendations
- **Cross-Service Dependencies**: Visual dependency analysis with automatic service relationship detection
- **Conditional Policy Generation**: Advanced policy creation with MFA, IP, time, VPC, and tag-based restrictions
- **Security Recommendations**: Service-specific best practices and vulnerability detection
- **Compliance Checking**: SOC2, PCI, HIPAA, and GDPR compliance analysis with detailed scoring
- **Policy Templates**: Enterprise-ready templates for common use cases

### Advanced Analysis Modes
- **Resource-Specific Analysis**: Generate policies with precise ARNs instead of wildcards
- **Least Privilege Optimization**: Create minimal permission policies with automatic security conditions
- **Service Usage Summary**: Detailed breakdown of AWS services, actions, permissions, and dependencies

### User Experience
- **One-Click Role Generation**: All formats generated simultaneously without format selection
- **5-Tab Interface**: Easy switching between Trust Policy, Permissions, Terraform, CloudFormation, and AWS CLI
- **Real-time Analysis**: Interactive interface with instant feedback and validation
- **Modern UI**: Professional interface built with shadcn/ui components
- **Hot Reload Development**: Instant updates during development with Vite HMR

## Tech Stack

- **React 18** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **shadcn/ui** for enterprise-grade UI components
- **Tailwind CSS** for responsive styling
- **Lucide React** for consistent iconography
- **Axios** for robust API communication
- **Custom Hooks** for state management and API integration

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python backend server running (see main README)

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Backend Integration

The frontend communicates with a FastAPI backend server that wraps the Python CLI tool. Make sure the backend is running on `http://localhost:8000` (default configuration).

To start the backend:
```bash
# From the project root
python backend_server.py
```

## Usage

### 1. Command Analysis

1. Open the "Analyze Command" tab
2. Enter an AWS CLI command (e.g., `aws s3 ls s3://my-bucket`)
3. Click "Analyze Command"
4. View the required permissions, policy document, resources, and warnings

### 2. Role Generation

1. Open the "Generate Role" tab
2. Enter an AWS CLI command
3. Configure role settings:
   - Role name
   - Trust policy type (EC2, Lambda, ECS, Cross-account)
   - Output format (JSON, Terraform, CloudFormation, AWS CLI)
   - Account ID (for cross-account roles)
4. Click "Generate Role"
5. Download or copy the generated configuration

### 3. Standard Batch Analysis

1. Open the "Batch Analysis" tab
2. Enter multiple AWS CLI commands (one per line)
3. Click "Analyze Batch"
4. View comprehensive analysis results and summary

### 4. Enhanced Batch Analysis ✨ **NEW**

1. Open the "Enhanced Batch Analysis" tab
2. Choose analysis mode:
   - **Standard**: Traditional batch analysis with summaries
   - **Resource-Specific**: Generate policies with precise ARNs (e.g., `arn:aws:s3:::my-bucket`)
   - **Least Privilege**: Optimized policies with security conditions
   - **Service Summary**: Detailed service usage breakdown
3. Configure advanced options (Account ID, Region, Strict Mode)
4. Enter multiple AWS CLI commands (one per line)
5. Click "Analyze Commands"
6. View real-time results with enhanced metadata and policy documents

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── CommandAnalyzer.tsx    # Single command analysis
│   │   ├── RoleGenerator.tsx      # IAM role generation
│   │   ├── BatchAnalyzer.tsx      # Standard batch command analysis
│   │   ├── EnhancedBatchAnalyzer.tsx  # ✨ Enhanced analysis modes
│   │   └── ui/                    # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts                 # API client with enhanced endpoints
│   │   └── utils.ts               # Utility functions
│   ├── App.tsx                    # Main application component
│   └── main.tsx                   # Application entry point
├── index.html                     # HTML template
├── package.json                   # Dependencies and scripts
├── tailwind.config.js             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript configuration
└── vite.config.ts                 # Vite configuration
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code

### Adding New Components

This project uses shadcn/ui. To add new components:

```bash
npx shadcn@latest add [component-name]
```

### Backend API Endpoints

The frontend communicates with these backend endpoints:

**Core Analysis:**
- `GET /health` - Health check
- `GET /services` - Get supported AWS services  
- `POST /analyze` - Analyze single command
- `POST /batch-analyze` - Analyze multiple commands
- `POST /generate-role` - Generate IAM role

**Enhanced Analysis** ✨ **FULLY IMPLEMENTED:**
- `POST /analyze-resource-specific` - Resource-specific policy generation with precise ARNs
- `POST /analyze-least-privilege` - Least privilege optimization with security conditions
- `POST /service-summary` - Service usage summary with detailed breakdowns

## Styling

The project uses Tailwind CSS with shadcn/ui's design system. Key styling features:

- **Dark/Light mode support** (configured via CSS variables)
- **Responsive design** for mobile and desktop
- **Consistent component styling** via shadcn/ui
- **Custom color scheme** optimized for AWS console familiarity

## Browser Support

- Chrome/Chromium 88+
- Firefox 88+
- Safari 14+
- Edge 88+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the main project LICENSE file for details.
