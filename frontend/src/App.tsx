import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { CommandAnalyzer } from '@/components/CommandAnalyzer'
import { RoleGenerator } from '@/components/RoleGenerator'
import { BatchAnalyzer } from '@/components/BatchAnalyzer'
import { EnhancedBatchAnalyzer } from '@/components/EnhancedBatchAnalyzer'
import { iamGeneratorApi } from '@/lib/api'
import { 
  Play, 
  Settings, 
  FileText, 
  Server, 
  Github, 
  AlertCircle,
  CheckCircle2,
  ExternalLink
} from 'lucide-react'

function App() {
  const [backendStatus, setBackendStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading')
  const [supportedServices, setSupportedServices] = useState<string[]>([])

  useEffect(() => {
    checkBackendStatus()
    fetchSupportedServices()
  }, [])

  const checkBackendStatus = async () => {
    try {
      await iamGeneratorApi.healthCheck()
      setBackendStatus('connected')
    } catch (error) {
      setBackendStatus('disconnected')
    }
  }

  const fetchSupportedServices = async () => {
    try {
      const services = await iamGeneratorApi.getSupportedServices()
      setSupportedServices(services)
    } catch (error) {
      console.error('Failed to fetch supported services:', error)
    }
  }

  const handleAnalyzeCommand = async (command: string) => {
    return await iamGeneratorApi.analyzeCommand({ command })
  }

  const handleGenerateRole = async (params: {
    command: string
    roleName: string
    trustPolicy: string
    outputFormat: string
    accountId?: string
  }) => {
    return await iamGeneratorApi.generateRole({
      command: params.command,
      role_name: params.roleName,
      trust_policy: params.trustPolicy,
      output_format: params.outputFormat,
      account_id: params.accountId
    })
  }

  const handleBatchAnalyze = async (commands: string[]) => {
    return await iamGeneratorApi.batchAnalyze({ commands })
  }

  return (
    <div className="min-h-screen bg-aws-gray-100 text-aws-gray-900">
      {/* AWS-style Header */}
      <header className="bg-aws-gray-800 shadow-md border-b-2 border-aws-orange">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
                <img src="/shield.svg" alt="IAM Policy Generator Logo" className="h-8 w-8" /> 
                <div>
                  <h1 className="text-xl font-semibold text-white">IAM Policy Generator [HOT RELOAD WORKING]</h1>
                  <p className="text-aws-gray-300 text-xs">
                    Analyze AWS CLI commands and generate precise IAM permissions
                  </p>
                </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4 text-aws-gray-300" />
                <span className="text-aws-gray-300 text-xs font-medium">Backend:</span>
                {backendStatus === 'loading' && (
                  <Badge variant="outline" className="bg-aws-gray-700 text-aws-gray-300 border-aws-gray-600 text-xs px-2 py-0.5 rounded">
                    <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse mr-1.5"></div>
                    Checking...
                  </Badge>
                )}
                {backendStatus === 'connected' && (
                  <Badge className="bg-green-600 text-white border-green-500 text-xs px-2 py-0.5 rounded">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Connected
                  </Badge>
                )}
                {backendStatus === 'disconnected' && (
                  <Badge className="bg-red-600 text-white border-red-500 text-xs px-2 py-0.5 rounded">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Disconnected
                  </Badge>
                )}
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                className="bg-aws-gray-700 border-aws-gray-600 text-aws-gray-200 hover:bg-aws-gray-600 hover:text-white transition-colors text-xs px-3 py-1.5 rounded"
                asChild
              >
                <a 
                  href="https://github.com/your-repo/iam-generator" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5"
                >
                  <Github className="h-3.5 w-3.5" />
                  GitHub
                  <ExternalLink className="h-3 w-3 opacity-70" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Enhanced Backend Status Warning */}
      {backendStatus === 'disconnected' && (
        <div className="bg-red-50 border-b border-red-300">
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center gap-3 text-red-700">
              <div className="p-1.5 bg-red-100 rounded-md">
                <AlertCircle className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-sm">Backend Service Unavailable</h3>
                <p className="text-xs text-red-600">
                  Unable to connect to the Python backend server. Please ensure it's running on localhost:8000.
                </p>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={checkBackendStatus}
                className="bg-white border-red-300 text-red-700 hover:bg-red-50 transition-colors text-xs px-3 py-1.5 rounded"
              >
                Retry Connection
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* Hero Section - Simplified for AWS look */}
          <div className="bg-white border border-aws-gray-200 rounded p-6 shadow-sm">
            <div className="max-w-3xl">
              <h2 className="text-2xl font-semibold text-aws-gray-900 mb-3">Welcome to IAM Policy Generator</h2>
              <p className="text-sm text-aws-gray-700 mb-4 leading-normal">
                Automatically analyze AWS CLI commands and generate precise IAM policies with least-privilege permissions. 
                Streamline your security workflow and ensure compliance with AWS best practices.
              </p>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1.5 text-aws-gray-700">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span>Least Privilege</span>
                </div>
                <div className="flex items-center gap-1.5 text-aws-gray-700">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span>Policy Validation</span>
                </div>
                <div className="flex items-center gap-1.5 text-aws-gray-700">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span>Best Practices</span>
                </div>
              </div>
            </div>
          </div>

          {/* Feature Cards - Adjusted for AWS look */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-white hover:shadow-md transition-shadow duration-200 border border-aws-gray-200 rounded">
              <CardHeader className="pb-3 pt-4 px-4">
                <div className="flex items-center gap-2.5 mb-1.5">
                  <div className="p-1.5 bg-aws-blue-light rounded">
                    <Play className="h-5 w-5 text-aws-blue" />
                  </div>
                  <CardTitle className="text-base font-semibold text-aws-gray-900">Single Command Analysis</CardTitle>
                </div>
                <CardDescription className="text-xs text-aws-gray-500">
                  Analyze individual AWS CLI commands and get detailed permission requirements instantly.
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="bg-white hover:shadow-md transition-shadow duration-200 border border-aws-gray-200 rounded">
              <CardHeader className="pb-3 pt-4 px-4">
                <div className="flex items-center gap-2.5 mb-1.5">
                  <div className="p-1.5 bg-orange-100 rounded">
                    <Settings className="h-5 w-5 text-aws-orange" />
                  </div>
                  <CardTitle className="text-base font-semibold text-aws-gray-900">IAM Role Generator</CardTitle>
                </div>
                <CardDescription className="text-xs text-aws-gray-500">
                  Generate complete IAM roles with trust policies and permission boundaries.
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="bg-white hover:shadow-md transition-shadow duration-200 border border-aws-gray-200 rounded">
              <CardHeader className="pb-3 pt-4 px-4">
                <div className="flex items-center gap-2.5 mb-1.5">
                  <div className="p-1.5 bg-green-100 rounded">
                    <FileText className="h-5 w-5 text-green-600" />
                  </div>
                  <CardTitle className="text-base font-semibold text-aws-gray-900">Batch Processing</CardTitle>
                </div>
                <CardDescription className="text-xs text-aws-gray-500">
                  Process multiple commands simultaneously for comprehensive policy analysis.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
          
          {/* Supported Services Badge Section */}
          {supportedServices.length > 0 && (
            <Card className="bg-white border border-aws-gray-200 rounded shadow-sm">
              <CardHeader className="pt-4 pb-3 px-4">
                <CardTitle className="flex items-center gap-2 text-base font-semibold text-aws-gray-900">
                  <div className="p-1 bg-aws-blue-light rounded-sm">
                    <Server className="h-3.5 w-3.5 text-aws-blue" />
                  </div>
                  Supported AWS Services ({supportedServices.length})
                </CardTitle>
                <CardDescription className="text-xs text-aws-gray-500 mt-1">
                  Currently supported AWS services for IAM policy generation
                </CardDescription>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <div className="flex flex-wrap gap-1.5">
                  {supportedServices.map((service) => (
                    <Badge 
                      key={service} 
                      variant="outline"
                      className="bg-aws-gray-100 text-aws-gray-700 border-aws-gray-300 hover:bg-aws-gray-200 hover:text-aws-gray-800 transition-colors text-xs px-2 py-0.5 rounded-sm font-normal"
                    >
                      {service}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Main Tabs */}
          <Card className="bg-white border-aws-gray-200 rounded shadow-sm">
            <Tabs defaultValue="analyze" className="w-full">
              <div className="border-b border-aws-gray-200 bg-aws-gray-50 rounded-t-md">
                <TabsList className="w-full grid grid-cols-4 bg-transparent h-12 px-1 pt-1">
                  <TabsTrigger 
                    value="analyze" 
                    className="flex items-center justify-center gap-1.5 h-full text-sm text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-aws-blue data-[state=active]:shadow-sm data-[state=active]:border-b-2 data-[state=active]:border-aws-blue transition-all duration-150 rounded border-b-2 border-transparent hover:bg-aws-gray-100 data-[state=active]:hover:bg-white"
                  >
                    <Play className="h-3.5 w-3.5" />
                    <span className="font-medium">Analyze Command</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="generate" 
                    className="flex items-center justify-center gap-1.5 h-full text-sm text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-aws-orange data-[state=active]:shadow-sm data-[state=active]:border-b-2 data-[state=active]:border-aws-orange transition-all duration-150 rounded border-b-2 border-transparent hover:bg-aws-gray-100 data-[state=active]:hover:bg-white"
                  >
                    <Settings className="h-3.5 w-3.5" />
                    <span className="font-medium">Generate Role</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="batch" 
                    className="flex items-center justify-center gap-1.5 h-full text-sm text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-green-600 data-[state=active]:shadow-sm data-[state=active]:border-b-2 data-[state=active]:border-green-600 transition-all duration-150 rounded border-b-2 border-transparent hover:bg-aws-gray-100 data-[state=active]:hover:bg-white"
                  >
                    <FileText className="h-3.5 w-3.5" />
                    <span className="font-medium">Batch Analysis</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="enhanced" 
                    className="flex items-center justify-center gap-1.5 h-full text-sm text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-purple-600 data-[state=active]:shadow-sm data-[state=active]:border-b-2 data-[state=active]:border-purple-600 transition-all duration-150 rounded border-b-2 border-transparent hover:bg-aws-gray-100 data-[state=active]:hover:bg-white"
                  >
                    <Settings className="h-3.5 w-3.5" />
                    <span className="font-medium">Enhanced Analysis</span>
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="p-4">
                <TabsContent value="analyze" className="mt-0 p-6 bg-white border border-aws-gray-200 rounded shadow-sm">
                  <CommandAnalyzer onAnalyze={handleAnalyzeCommand} />
                </TabsContent>

                <TabsContent value="generate" className="mt-0 p-6 bg-white border border-aws-gray-200 rounded shadow-sm">
                  <RoleGenerator onGenerateRole={handleGenerateRole} />
                </TabsContent>

                <TabsContent value="batch" className="mt-0 p-6 bg-white border border-aws-gray-200 rounded shadow-sm">
                  <BatchAnalyzer onBatchAnalyze={handleBatchAnalyze} />
                </TabsContent>

                <TabsContent value="enhanced" className="mt-0 p-6 bg-white border border-aws-gray-200 rounded shadow-sm">
                  <EnhancedBatchAnalyzer onBatchAnalyze={handleBatchAnalyze} />
                </TabsContent>
              </div>
            </Tabs>
          </Card>
        </div>
      </main>

      {/* Footer - Simplified for AWS look */}
      <footer className="bg-aws-gray-800 border-t border-aws-gray-700 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-aws-gray-400">
            <span>© {new Date().getFullYear()} IAM Policy Generator. All rights reserved.</span>
            <div className="flex items-center gap-4">
              <a href="#" className="hover:text-aws-orange transition-colors">Privacy</a>
              <span>•</span>
              <a href="#" className="hover:text-aws-orange transition-colors">Terms</a>
              <span>•</span>
              <a href="https://github.com/your-repo/iam-generator" target="_blank" rel="noopener noreferrer" className="hover:text-aws-orange transition-colors">GitHub</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
