# AWS IAM Generator - Frontend

A modern React frontend for the AWS CLI IAM Permissions Analyzer tool, built with shadcn/ui components and Tailwind CSS.

## Features

- **Command Analysis**: Analyze single AWS CLI commands to extract required IAM permissions
- **Role Generation**: Generate complete IAM roles with trust policies and permission policies
- **Batch Processing**: Analyze multiple commands at once
- **Multiple Output Formats**: Support for JSON, Terraform, CloudFormation, and AWS CLI outputs
- **Real-time Analysis**: Interactive interface with real-time feedback
- **Modern UI**: Built with shadcn/ui components for a clean, professional interface

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **shadcn/ui** for UI components
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Axios** for API communication

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

### 3. Batch Analysis

1. Open the "Batch Analysis" tab
2. Enter multiple AWS CLI commands (one per line)
3. Click "Analyze Batch"
4. View comprehensive analysis results and summary

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── CommandAnalyzer.tsx    # Single command analysis
│   │   ├── RoleGenerator.tsx      # IAM role generation
│   │   ├── BatchAnalyzer.tsx      # Batch command analysis
│   │   └── ui/                    # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts                 # API client for backend communication
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

- `GET /health` - Health check
- `GET /services` - Get supported AWS services
- `POST /analyze` - Analyze single command
- `POST /batch-analyze` - Analyze multiple commands
- `POST /generate-role` - Generate IAM role

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
