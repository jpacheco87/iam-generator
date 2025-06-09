import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Download, Copy, AlertCircle, BarChart3, Layers, Target, Shield, Database } from 'lucide-react'
import { iamGeneratorApi, BatchAnalysisResult, ResourceSpecificResult, ServiceSummaryResult } from '@/lib/api'

interface Props {
  onBatchAnalyze: (commands: string[]) => Promise<BatchAnalysisResult>
}

type AnalysisMode = 'standard' | 'resource-specific' | 'least-privilege' | 'service-summary'

export function EnhancedBatchAnalyzer({ onBatchAnalyze }: Props) {
  const [commands, setCommands] = useState('')
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('standard')
  const [accountId, setAccountId] = useState('')
  const [region, setRegion] = useState('us-east-1')
  const [strictMode, setStrictMode] = useState(true)
  
  // Results for different analysis types
  const [standardResult, setStandardResult] = useState<BatchAnalysisResult | null>(null)
  const [resourceSpecificResult, setResourceSpecificResult] = useState<ResourceSpecificResult | null>(null)
  const [leastPrivilegeResult, setLeastPrivilegeResult] = useState<{ policy_document: any } | null>(null)
  const [serviceSummaryResult, setServiceSummaryResult] = useState<ServiceSummaryResult | null>(null)
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    const commandList = commands
      .split('\n')
      .map(cmd => cmd.trim())
      .filter(cmd => cmd.length > 0 && !cmd.startsWith('#'))

    if (commandList.length === 0) {
      setError('Please enter at least one command')
      return
    }

    setLoading(true)
    setError(null)

    try {
      switch (analysisMode) {
        case 'standard':
          const standardRes = await onBatchAnalyze(commandList)
          setStandardResult(standardRes)
          break
          
        case 'resource-specific':
          const resourceRes = await iamGeneratorApi.generateResourceSpecificPolicy({
            commands: commandList,
            account_id: accountId || undefined,
            region: region || undefined,
            strict_mode: strictMode
          })
          setResourceSpecificResult(resourceRes)
          break
          
        case 'least-privilege':
          const leastPrivRes = await iamGeneratorApi.generateLeastPrivilegePolicy({
            commands: commandList,
            account_id: accountId || undefined,
            region: region || undefined
          })
          setLeastPrivilegeResult(leastPrivRes)
          break
          
        case 'service-summary':
          const summaryRes = await iamGeneratorApi.getServiceSummary({
            commands: commandList
          })
          setServiceSummaryResult(summaryRes)
          break
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const downloadPolicy = (policy: any, filename: string) => {
    const blob = new Blob([JSON.stringify(policy, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const renderAnalysisModeSelector = () => (
    <div className="space-y-4">
      <div>
        <Label htmlFor="analysis-mode">Analysis Mode</Label>
        <Select value={analysisMode} onValueChange={(value: AnalysisMode) => setAnalysisMode(value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select analysis mode" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="standard">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Standard Analysis
              </div>
            </SelectItem>
            <SelectItem value="resource-specific">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                Resource-Specific Policy
              </div>
            </SelectItem>
            <SelectItem value="least-privilege">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Least Privilege Policy
              </div>
            </SelectItem>
            <SelectItem value="service-summary">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                Service Summary
              </div>
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      {(analysisMode === 'resource-specific' || analysisMode === 'least-privilege') && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="account-id">AWS Account ID (Optional)</Label>
            <Input
              id="account-id"
              placeholder="123456789012"
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="region">AWS Region</Label>
            <Select value={region} onValueChange={setRegion}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="us-east-1">us-east-1</SelectItem>
                <SelectItem value="us-west-2">us-west-2</SelectItem>
                <SelectItem value="eu-west-1">eu-west-1</SelectItem>
                <SelectItem value="ap-southeast-1">ap-southeast-1</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}

      {analysisMode === 'resource-specific' && (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="strict-mode"
            checked={strictMode}
            onChange={(e) => setStrictMode(e.target.checked)}
            className="rounded border-gray-300"
          />
          <Label htmlFor="strict-mode">Strict Mode (Use specific resources when available)</Label>
        </div>
      )}
    </div>
  )

  const renderResourceSpecificResult = () => {
    if (!resourceSpecificResult) return null

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Resource-Specific IAM Policy
              </CardTitle>
              <CardDescription>
                Enhanced policy with specific ARNs instead of wildcards
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(JSON.stringify(resourceSpecificResult.policy_document, null, 2))}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => downloadPolicy(resourceSpecificResult.policy_document, 'resource-specific-policy.json')}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="p-3">
                <div className="text-sm font-medium">Commands Analyzed</div>
                <div className="text-2xl font-bold">{resourceSpecificResult.commands_analyzed}</div>
              </Card>
              <Card className="p-3">
                <div className="text-sm font-medium">Specific Resources</div>
                <div className="text-2xl font-bold">{resourceSpecificResult.specific_resources_found}</div>
              </Card>
              <Card className="p-3">
                <div className="text-sm font-medium">Account ID</div>
                <div className="text-sm font-mono">{resourceSpecificResult.metadata.account_id || 'Not specified'}</div>
              </Card>
              <Card className="p-3">
                <div className="text-sm font-medium">Region</div>
                <div className="text-sm font-mono">{resourceSpecificResult.metadata.region || 'Not specified'}</div>
              </Card>
            </div>
            
            <div>
              <Label>Generated Policy</Label>
              <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-auto max-h-96">
                {JSON.stringify(resourceSpecificResult.policy_document, null, 2)}
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderServiceSummaryResult = () => {
    if (!serviceSummaryResult) return null

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Service Usage Summary
          </CardTitle>
          <CardDescription>
            Overview of AWS services and actions used by your commands
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Card className="p-3">
                <div className="text-sm font-medium">Total Services</div>
                <div className="text-2xl font-bold">{serviceSummaryResult.total_services}</div>
              </Card>
              <Card className="p-3">
                <div className="text-sm font-medium">Total Actions</div>
                <div className="text-2xl font-bold">{serviceSummaryResult.total_actions}</div>
              </Card>
            </div>

            <div>
              <Label>Service Breakdown</Label>
              <div className="space-y-2">
                {Object.entries(serviceSummaryResult.summary).map(([service, details]) => (
                  <Card key={service} className="p-3">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{service.toUpperCase()}</div>
                      <Badge variant="secondary">{details.actions.length} actions</Badge>
                    </div>
                    <div className="text-sm text-gray-600 mt-2">
                      <div>Actions: {details.actions.join(', ')}</div>
                      {details.resources.length > 0 && (
                        <div className="mt-1">Resources: {details.resources.slice(0, 3).join(', ')}
                          {details.resources.length > 3 && ` +${details.resources.length - 3} more`}
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderLeastPrivilegeResult = () => {
    if (!leastPrivilegeResult) return null

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Least Privilege IAM Policy
              </CardTitle>
              <CardDescription>
                Optimized policy with enhanced security conditions
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(JSON.stringify(leastPrivilegeResult.policy_document, null, 2))}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => downloadPolicy(leastPrivilegeResult.policy_document, 'least-privilege-policy.json')}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div>
            <Label>Generated Policy</Label>
            <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-auto max-h-96">
              {JSON.stringify(leastPrivilegeResult.policy_document, null, 2)}
            </pre>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-5 w-5" />
            Enhanced Batch Analysis
          </CardTitle>
          <CardDescription>
            Analyze multiple AWS CLI commands with advanced policy generation options
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {renderAnalysisModeSelector()}
          
          <div>
            <Label htmlFor="commands">AWS CLI Commands</Label>
            <Textarea
              id="commands"
              placeholder={`Enter AWS CLI commands (one per line):
aws s3 ls s3://my-bucket
aws ec2 describe-instances --instance-ids i-1234567890abcdef0
aws lambda invoke --function-name my-function output.json
# Comments are ignored`}
              value={commands}
              onChange={(e) => setCommands(e.target.value)}
              className="min-h-32 font-mono text-sm"
            />
          </div>

          <Button onClick={handleAnalyze} disabled={loading || !commands.trim()}>
            {loading ? 'Analyzing...' : `Run ${analysisMode.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} Analysis`}
          </Button>

          {error && (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-md">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {analysisMode === 'standard' && standardResult && (
        <Card>
          <CardHeader>
            <CardTitle>Standard Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Render standard results - you can reuse existing logic */}
            <div className="text-sm text-gray-600">
              {standardResult.summary.total_commands} commands analyzed across {standardResult.summary.services_used.length} services
            </div>
          </CardContent>
        </Card>
      )}

      {analysisMode === 'resource-specific' && renderResourceSpecificResult()}
      {analysisMode === 'least-privilege' && renderLeastPrivilegeResult()}
      {analysisMode === 'service-summary' && renderServiceSummaryResult()}
    </div>
  )
}
