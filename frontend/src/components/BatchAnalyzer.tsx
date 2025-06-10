import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Download, Copy, AlertCircle, CheckCircle2, Upload, BarChart3, Layers } from 'lucide-react'

interface BatchResult {
  original_command: string
  service: string
  action: string
  required_permissions: Array<{
    action: string
    resource: string
    condition?: any
  }>
  warnings: string[]
}

interface BatchAnalysisResult {
  results: BatchResult[]
  summary: {
    total_commands: number
    unique_services: number
    unique_actions: number
    total_permissions: number
    services_used: string[]
  }
  combined_policy: any
}

interface Props {
  onBatchAnalyze: (commands: string[]) => Promise<BatchAnalysisResult>
}

export function BatchAnalyzer({ onBatchAnalyze }: Props) {
  const [commands, setCommands] = useState('')
  const [result, setResult] = useState<BatchAnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    const commandList = commands
      .split('\n')
      .map(cmd => cmd.trim())
      .filter(cmd => cmd.length > 0)

    if (commandList.length === 0) return

    setLoading(true)
    setError(null)
    try {
      const batchResult = await onBatchAnalyze(commandList)
      setResult(batchResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Batch analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        setCommands(content)
      }
      reader.readAsText(file)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const downloadJson = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const generateCommandsFile = () => {
    const content = [
      '# AWS CLI Commands for IAM Analysis',
      '# Add one command per line',
      '# Comments (lines starting with #) will be ignored',
      '',
      'aws s3 ls s3://my-bucket',
      'aws ec2 describe-instances',
      'aws lambda list-functions',
      'aws iam list-users'
    ].join('\n')
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'aws-commands.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-8">
      <Card className="aws-surface-raised border-l-4 border-l-aws-blue shadow-lg">
        <CardHeader className="bg-gradient-to-r from-aws-blue/5 to-blue-50 rounded-t-lg border-b border-aws-gray-200">
          <CardTitle className="flex items-center gap-3 text-aws-gray-900">
            <div className="p-2 bg-aws-blue/10 rounded-lg">
              <Layers className="h-5 w-5 text-aws-blue" />
            </div>
            Batch Command Analysis
          </CardTitle>
          <CardDescription className="text-aws-gray-600">
            Analyze multiple AWS CLI commands at once to generate consolidated permissions and comprehensive IAM policies
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label htmlFor="commands" className="text-sm font-semibold text-aws-gray-900">
                AWS CLI Commands (one per line)
              </label>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={generateCommandsFile}
                  className="hover:bg-aws-gray-50 border-aws-gray-200"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Sample File
                </Button>
                <label className="cursor-pointer">
                  <Button variant="outline" size="sm" asChild className="hover:bg-aws-gray-50 border-aws-gray-200">
                    <span>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload File
                    </span>
                  </Button>
                  <input
                    type="file"
                    accept=".txt,.sh"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </div>
            <Textarea
              id="commands"
              placeholder={`aws s3 ls s3://my-bucket
aws ec2 describe-instances --region us-west-2
aws lambda list-functions
aws iam list-users`}
              value={commands}
              onChange={(e) => setCommands(e.target.value)}
              className="min-h-[200px] font-mono text-sm bg-aws-gray-50 border-aws-gray-200 focus:border-aws-blue focus:ring-aws-blue/20 transition-all duration-200"
            />
            <p className="text-xs text-aws-gray-500">
              Enter multiple AWS CLI commands, one per line. Comments starting with # will be ignored.
            </p>
          </div>
          
          <Button 
            onClick={handleAnalyze} 
            disabled={loading || !commands.trim()}
            className="w-full h-12 bg-aws-blue hover:bg-aws-blue/90 text-white font-medium transition-all duration-200 shadow-lg"
            size="lg"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            {loading ? 'Analyzing Commands...' : 'Analyze Commands'}
          </Button>

          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg shadow-sm">
              <div className="p-1 bg-red-100 rounded">
                <AlertCircle className="h-4 w-4 text-red-600" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-red-800 text-sm">Analysis Failed</h4>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {result && (
        <Card className="aws-surface-raised border-l-4 border-l-green-500 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-t-lg border-b border-aws-gray-200">
            <CardTitle className="flex items-center gap-3 text-aws-gray-900">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              Batch Analysis Results
            </CardTitle>
            <CardDescription className="text-aws-gray-600">
              Analyzed {result.summary.total_commands} commands across{' '}
              {result.summary.services_used.length} AWS services
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <Tabs defaultValue="summary" className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-aws-gray-50 p-1 h-12">
                <TabsTrigger value="summary" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">Summary</TabsTrigger>
                <TabsTrigger value="commands" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">Commands</TabsTrigger>
                <TabsTrigger value="policy" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">Combined Policy</TabsTrigger>
              </TabsList>

              <TabsContent value="summary" className="mt-6 space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                    <div className="text-2xl font-bold text-blue-800">{result.summary.total_commands}</div>
                    <div className="text-sm text-blue-600">Commands</div>
                  </Card>
                  <Card className="p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                    <div className="text-2xl font-bold text-green-800">{result.summary.services_used.length}</div>
                    <div className="text-sm text-green-600">Services</div>
                  </Card>
                  <Card className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                    <div className="text-2xl font-bold text-purple-800">{result.summary.total_permissions}</div>
                    <div className="text-sm text-purple-600">Total Permissions</div>
                  </Card>
                  <Card className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                    <div className="text-2xl font-bold text-orange-800">{result.summary.unique_actions}</div>
                    <div className="text-sm text-orange-600">Unique Actions</div>
                  </Card>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-aws-gray-900">Services Used</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.summary.services_used.map((service, index) => (
                        <Badge key={index} variant="outline" className="bg-aws-blue/10 text-aws-blue border-aws-blue/30">{service}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="commands" className="mt-6 space-y-4">
                <h3 className="text-lg font-semibold text-aws-gray-900">Command Results</h3>
                <div className="space-y-4">
                  {result.results.map((cmdResult, index) => (
                    <Card key={index} className="border-l-4 border-l-aws-blue/30 shadow-sm">
                      <CardHeader className="pb-3 bg-gradient-to-r from-aws-blue/5 to-transparent">
                        <div className="flex items-center gap-2">
                          <Badge className="bg-aws-blue text-white">{cmdResult.service}</Badge>
                          <Badge variant="outline" className="border-aws-gray-300">{cmdResult.action}</Badge>
                        </div>
                        <code className="text-sm bg-aws-gray-900 text-green-400 p-3 rounded-lg font-mono block overflow-x-auto">
                          {cmdResult.original_command}
                        </code>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div>
                            <strong className="text-sm text-aws-gray-900">Required Permissions:</strong>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {cmdResult.required_permissions.map((perm, permIndex) => (
                                <Badge key={permIndex} variant="secondary" className="text-xs bg-green-100 text-green-800 border-green-200">
                                  {perm.action}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          {cmdResult.warnings.length > 0 && (
                            <div>
                              <strong className="text-sm text-amber-700">Warnings:</strong>
                              <ul className="text-sm text-amber-700 mt-2 space-y-1">
                                {cmdResult.warnings.map((warning, warnIndex) => (
                                  <li key={warnIndex} className="text-xs flex items-start gap-2">
                                    <span className="text-amber-500 mt-0.5">•</span>
                                    <span>{warning}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="policy" className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-aws-gray-900">Combined IAM Policy</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(result.combined_policy, null, 2))}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadJson(result.combined_policy, 'combined-iam-policy.json')}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="bg-aws-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-sm font-mono border shadow-inner">
                  {JSON.stringify(result.combined_policy, null, 2)}
                </pre>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
