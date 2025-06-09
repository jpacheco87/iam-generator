import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Play, Copy, Download, AlertCircle, CheckCircle2, Terminal, Shield, FileText } from 'lucide-react'

interface Permission {
  action: string
  resource: string
  condition?: any
}

interface AnalysisResult {
  service: string
  action: string
  required_permissions: Permission[]
  policy_document: any
  warnings: string[]
  resource_arns: string[]
}

interface Props {
  onAnalyze: (command: string) => Promise<AnalysisResult>
}

export function CommandAnalyzer({ onAnalyze }: Props) {
  const [command, setCommand] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    if (!command.trim()) return

    setLoading(true)
    setError(null)
    try {
      const analysisResult = await onAnalyze(command.trim())
      setResult(analysisResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
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

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card className="aws-surface-raised">
        <CardHeader className="bg-gradient-to-r from-aws-blue/5 to-aws-blue/10 rounded-t-lg border-b border-aws-gray-200">
          <CardTitle className="flex items-center gap-3 text-aws-gray-900">
            <div className="p-2 bg-aws-blue-light rounded-lg">
              <Terminal className="h-5 w-5 text-aws-blue" />
            </div>
            AWS CLI Command Analysis
          </CardTitle>
          <CardDescription className="text-aws-gray-500">
            Enter an AWS CLI command to analyze its required IAM permissions and generate least-privilege policies
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div className="space-y-3">
            <label htmlFor="command" className="text-sm font-semibold text-aws-gray-900">
              AWS CLI Command
            </label>
            <Textarea
              id="command"
              placeholder="aws s3 ls s3://my-bucket --recursive"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              className="min-h-[120px] font-mono text-sm bg-aws-gray-50 border-aws-gray-200 focus:border-aws-blue focus:ring-aws-blue/20"
            />
            <div className="flex items-start gap-2">
              <div className="p-1 bg-blue-100 rounded">
                <CheckCircle2 className="h-3 w-3 text-blue-600" />
              </div>
              <p className="text-xs text-aws-gray-500 leading-relaxed">
                Include the full AWS CLI command. The 'aws' prefix is optional. 
                Examples: <code className="bg-aws-gray-100 px-1 py-0.5 rounded text-xs">s3 ls</code>, 
                <code className="bg-aws-gray-100 px-1 py-0.5 rounded text-xs">ec2 describe-instances</code>
              </p>
            </div>
          </div>
          
          <Button 
            onClick={handleAnalyze} 
            disabled={loading || !command.trim()}
            className="w-full h-12 bg-aws-blue hover:bg-aws-blue/90 text-white font-medium transition-all duration-200"
            size="lg"
          >
            <Play className="h-4 w-4 mr-2" />
            {loading ? 'Analyzing Command...' : 'Analyze IAM Permissions'}
          </Button>

          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
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

      {/* Results Section */}
      {result && (
        <Card className="aws-surface-raised">
          <CardHeader className="bg-gradient-to-r from-green-50 to-green-100 rounded-t-lg border-b border-green-200">
            <CardTitle className="flex items-center gap-3 text-aws-gray-900">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              Analysis Results
            </CardTitle>
            <CardDescription className="flex items-center gap-4 text-aws-gray-600">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Service:</span>
                <Badge className="bg-aws-blue text-white">{result.service}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Action:</span>
                <Badge className="bg-aws-orange text-white">{result.action}</Badge>
              </div>
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Tabs defaultValue="permissions" className="w-full">
              <div className="border-b border-aws-gray-200 bg-aws-gray-50">
                <TabsList className="w-full grid grid-cols-4 bg-transparent h-12 p-1">
                  <TabsTrigger 
                    value="permissions" 
                    className="flex items-center gap-2 h-10 text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-aws-blue data-[state=active]:shadow-sm"
                  >
                    <Shield className="h-4 w-4" />
                    Permissions
                  </TabsTrigger>
                  <TabsTrigger 
                    value="policy" 
                    className="flex items-center gap-2 h-10 text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-aws-blue data-[state=active]:shadow-sm"
                  >
                    <FileText className="h-4 w-4" />
                    Policy
                  </TabsTrigger>
                  <TabsTrigger 
                    value="resources" 
                    className="flex items-center gap-2 h-10 text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-aws-blue data-[state=active]:shadow-sm"
                  >
                    <Terminal className="h-4 w-4" />
                    Resources
                  </TabsTrigger>
                  <TabsTrigger 
                    value="warnings" 
                    className="flex items-center gap-2 h-10 text-aws-gray-700 data-[state=active]:bg-white data-[state=active]:text-aws-blue data-[state=active]:shadow-sm"
                  >
                    <AlertCircle className="h-4 w-4" />
                    Warnings
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="p-6">
                <TabsContent value="permissions" className="mt-0 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-aws-gray-900">Required Permissions</h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(result.required_permissions, null, 2))}
                      className="border-aws-gray-300 text-aws-gray-700 hover:bg-aws-gray-50"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy JSON
                    </Button>
                  </div>
                  <div className="space-y-3">
                    {result.required_permissions.map((perm: Permission, index: number) => (
                      <Card key={index} className="aws-surface border-l-4 border-l-aws-blue">
                        <CardContent className="p-4">
                          <div className="space-y-3">
                            <div className="flex items-center gap-2">
                              <Badge className="bg-aws-blue text-white font-mono text-xs">
                                {perm.action}
                              </Badge>
                            </div>
                            <div className="text-sm">
                              <span className="font-medium text-aws-gray-900">Resource:</span>
                              <code className="ml-2 bg-aws-gray-100 px-2 py-1 rounded text-xs font-mono">
                                {perm.resource}
                              </code>
                            </div>
                            {perm.condition && (
                              <div className="text-sm">
                                <span className="font-medium text-aws-gray-900">Condition:</span>
                                <code className="ml-2 bg-aws-gray-100 px-2 py-1 rounded text-xs font-mono">
                                  {JSON.stringify(perm.condition)}
                                </code>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="policy" className="mt-0 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-aws-gray-900">IAM Policy Document</h3>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(result.policy_document, null, 2))}
                        className="border-aws-gray-300 text-aws-gray-700 hover:bg-aws-gray-50"
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadJson(result.policy_document, 'iam-policy.json')}
                        className="border-aws-gray-300 text-aws-gray-700 hover:bg-aws-gray-50"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </div>
                  <div className="bg-aws-gray-900 rounded-lg p-4 overflow-auto">
                    <pre className="text-green-400 text-sm font-mono leading-relaxed">
                      {JSON.stringify(result.policy_document, null, 2)}
                    </pre>
                  </div>
                </TabsContent>

                <TabsContent value="resources" className="mt-0 space-y-4">
                  <h3 className="text-lg font-semibold text-aws-gray-900">Resource ARNs</h3>
                  {result.resource_arns.length > 0 ? (
                    <div className="space-y-2">
                      {result.resource_arns.map((arn: string, index: number) => (
                        <div key={index} className="p-3 bg-aws-gray-50 border border-aws-gray-200 rounded-lg">
                          <code className="text-sm font-mono text-aws-gray-800">{arn}</code>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="p-3 bg-aws-gray-100 rounded-lg inline-block mb-3">
                        <Terminal className="h-6 w-6 text-aws-gray-400" />
                      </div>
                      <p className="text-aws-gray-500">No specific resource ARNs identified</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="warnings" className="mt-0 space-y-4">
                  <h3 className="text-lg font-semibold text-aws-gray-900">Security Warnings</h3>
                  {result.warnings.length > 0 ? (
                    <div className="space-y-3">
                      {result.warnings.map((warning: string, index: number) => (
                        <div key={index} className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <div className="p-1 bg-yellow-100 rounded">
                            <AlertCircle className="h-4 w-4 text-yellow-600" />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm text-yellow-800 leading-relaxed">{warning}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="p-3 bg-green-100 rounded-lg inline-block mb-3">
                        <CheckCircle2 className="h-6 w-6 text-green-600" />
                      </div>
                      <p className="text-aws-gray-500">No security warnings detected</p>
                    </div>
                  )}
                </TabsContent>
              </div>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
