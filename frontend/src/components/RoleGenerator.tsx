import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Settings, Download, Copy, AlertCircle, CheckCircle2, Shield, FileText, Code, Terminal } from 'lucide-react'
import { generateRoleAllFormats } from '@/lib/api'

interface RoleConfig {
  role_name: string
  trust_policy: any
  permissions_policy: any
  terraform_config?: string
  cloudformation_config?: string
  aws_cli_commands?: string[]
}

export function RoleGenerator() {
  const [command, setCommand] = useState('')
  const [roleName, setRoleName] = useState('GeneratedRole')
  const [trustPolicy, setTrustPolicy] = useState('ec2')
  const [accountId, setAccountId] = useState('')
  const [result, setResult] = useState<RoleConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const trustPolicyOptions = [
    { value: 'ec2', label: 'EC2 Service', description: 'For EC2 instances with instance profiles' },
    { value: 'lambda', label: 'Lambda Service', description: 'For Lambda function execution roles' },
    { value: 'ecs', label: 'ECS Service', description: 'For ECS task execution roles' },
    { value: 'cross-account', label: 'Cross-Account', description: 'For cross-account access' }
  ]

  const handleGenerate = async () => {
    if (!command.trim() || !roleName.trim()) return

    if (trustPolicy === 'cross-account' && !accountId.trim()) {
      setError('Account ID is required for cross-account trust policy')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const roleConfig = await generateRoleAllFormats({
        command: command.trim(),
        role_name: roleName.trim(),
        trust_policy: trustPolicy,
        account_id: accountId.trim() || undefined
      })
      setResult(roleConfig)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Role generation failed')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const downloadFile = (content: string, filename: string, mimeType: string = 'text/plain') => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-8">
      {/* Input Section */}
      <Card className="aws-surface-raised border-l-4 border-l-aws-orange shadow-lg">
        <CardHeader className="bg-gradient-to-r from-aws-orange/5 to-orange-50 rounded-t-lg border-b border-aws-gray-200">
          <CardTitle className="flex items-center gap-3 text-aws-gray-900">
            <div className="p-2 bg-aws-orange/10 rounded-lg">
              <Settings className="h-5 w-5 text-aws-orange" />
            </div>
            Generate IAM Role Configuration
          </CardTitle>
          <CardDescription className="text-aws-gray-600">
            Create complete IAM role configurations with trust policies and permissions for infrastructure deployment
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          {/* Command Input */}
          <div className="space-y-3">
            <label htmlFor="role-command" className="text-sm font-semibold text-aws-gray-900">
              AWS CLI Command
            </label>
            <Textarea
              id="role-command"
              placeholder="aws s3 get-object --bucket my-bucket --key my-file.txt"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              className="min-h-[100px] font-mono text-sm bg-aws-gray-50 border-aws-gray-200 focus:border-aws-orange focus:ring-aws-orange/20 transition-all duration-200"
            />
          </div>

          {/* Configuration Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Role Name */}
            <div className="space-y-3">
              <label htmlFor="role-name" className="text-sm font-semibold text-aws-gray-900">
                Role Name
              </label>
              <Input
                id="role-name"
                placeholder="MyApplicationRole"
                value={roleName}
                onChange={(e) => setRoleName(e.target.value)}
                className="bg-aws-gray-50 border-aws-gray-200 focus:border-aws-orange focus:ring-aws-orange/20 transition-all duration-200"
              />
            </div>

            {/* Account ID (conditional) */}
            {trustPolicy === 'cross-account' && (
              <div className="space-y-3">
                <label htmlFor="account-id" className="text-sm font-semibold text-aws-gray-900">
                  Trusted Account ID <span className="text-red-500">*</span>
                </label>
                <Input
                  id="account-id"
                  placeholder="123456789012"
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  className="bg-aws-gray-50 border-aws-gray-200 focus:border-aws-orange focus:ring-aws-orange/20 transition-all duration-200"
                />
              </div>
            )}
          </div>

          {/* Trust Policy Options */}
          <div className="space-y-3">
            <label className="text-sm font-semibold text-aws-gray-900">Trust Policy Type</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {trustPolicyOptions.map((option) => (
                <div
                  key={option.value}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                    trustPolicy === option.value
                      ? 'border-aws-orange bg-orange-50 shadow-md'
                      : 'border-aws-gray-200 bg-white hover:border-aws-gray-300 hover:shadow-sm'
                  }`}
                  onClick={() => setTrustPolicy(option.value)}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`w-4 h-4 rounded-full border-2 transition-all duration-200 ${
                      trustPolicy === option.value ? 'border-aws-orange bg-aws-orange' : 'border-aws-gray-300'
                    }`}>
                      {trustPolicy === option.value && (
                        <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                      )}
                    </div>
                    <span className="font-medium text-aws-gray-900">{option.label}</span>
                  </div>
                  <p className="text-sm text-aws-gray-600">{option.description}</p>
                </div>
              ))}
            </div>
          </div>

          <Button 
            onClick={handleGenerate} 
            disabled={loading || !command.trim() || !roleName.trim()}
            className="w-full h-12 bg-aws-orange hover:bg-aws-orange/90 text-white font-medium transition-all duration-200 shadow-lg"
            size="lg"
          >
            <Settings className="h-4 w-4 mr-2" />
            {loading ? 'Generating Role...' : 'Generate IAM Role'}
          </Button>

          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg shadow-sm">
              <div className="p-1 bg-red-100 rounded">
                <AlertCircle className="h-4 w-4 text-red-600" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-red-800 text-sm">Generation Failed</h4>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Section */}
      {result && (
        <Card className="aws-surface-raised border-l-4 border-l-green-500 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-t-lg border-b border-aws-gray-200">
            <CardTitle className="flex items-center gap-3 text-aws-gray-900">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              Generated Role Configuration
            </CardTitle>
            <CardDescription className="flex items-center gap-2 text-aws-gray-600">
              <Shield className="h-4 w-4" />
              Role: <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">{result.role_name}</Badge>
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <Tabs defaultValue="trust-policy" className="w-full">
              <TabsList className="grid w-full grid-cols-5 bg-aws-gray-50 p-1 h-12">
                <TabsTrigger value="trust-policy" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">
                  <Shield className="h-4 w-4 mr-2" />
                  Trust Policy
                </TabsTrigger>
                <TabsTrigger value="permissions" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">
                  <FileText className="h-4 w-4 mr-2" />
                  Permissions
                </TabsTrigger>
                <TabsTrigger value="terraform" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">
                  <Code className="h-4 w-4 mr-2" />
                  Terraform
                </TabsTrigger>
                <TabsTrigger value="cloudformation" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">
                  <Code className="h-4 w-4 mr-2" />
                  CloudFormation
                </TabsTrigger>
                <TabsTrigger value="aws-cli" className="data-[state=active]:bg-white data-[state=active]:text-aws-gray-900 data-[state=active]:shadow-sm transition-all duration-200">
                  <Terminal className="h-4 w-4 mr-2" />
                  AWS CLI
                </TabsTrigger>
              </TabsList>

              <TabsContent value="trust-policy" className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-aws-gray-900">Trust Policy</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(result.trust_policy, null, 2))}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadFile(
                        JSON.stringify(result.trust_policy, null, 2),
                        `${result.role_name}-trust-policy.json`,
                        'application/json'
                      )}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="bg-aws-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-sm font-mono border shadow-inner">
                  {JSON.stringify(result.trust_policy, null, 2)}
                </pre>
              </TabsContent>

              <TabsContent value="permissions" className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-aws-gray-900">Permissions Policy</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(result.permissions_policy, null, 2))}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadFile(
                        JSON.stringify(result.permissions_policy, null, 2),
                        `${result.role_name}-permissions-policy.json`,
                        'application/json'
                      )}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="bg-aws-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-sm font-mono border shadow-inner">
                  {JSON.stringify(result.permissions_policy, null, 2)}
                </pre>
              </TabsContent>

              <TabsContent value="terraform" className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-aws-gray-900">Terraform Configuration</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(result.terraform_config || '')}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadFile(
                        result.terraform_config || '',
                        `${result.role_name}.tf`,
                        'text/plain'
                      )}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="bg-aws-gray-900 text-cyan-400 p-4 rounded-lg overflow-auto text-sm font-mono border shadow-inner">
                  {result.terraform_config || 'Terraform configuration not available'}
                </pre>
              </TabsContent>

              <TabsContent value="cloudformation" className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-aws-gray-900">CloudFormation Template</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(result.cloudformation_config || '')}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadFile(
                        result.cloudformation_config || '',
                        `${result.role_name}-template.yaml`,
                        'text/yaml'
                      )}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="bg-aws-gray-900 text-yellow-400 p-4 rounded-lg overflow-auto text-sm font-mono border shadow-inner">
                  {result.cloudformation_config || 'CloudFormation template not available'}
                </pre>
              </TabsContent>

              <TabsContent value="aws-cli" className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-aws-gray-900">AWS CLI Commands</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(result.aws_cli_commands?.join('\n') || '')}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadFile(
                        result.aws_cli_commands?.join('\n') || '',
                        `${result.role_name}-commands.sh`,
                        'text/plain'
                      )}
                      className="hover:bg-aws-gray-50 border-aws-gray-200"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="bg-aws-gray-900 text-orange-400 p-4 rounded-lg overflow-auto text-sm font-mono border shadow-inner">
                  {result.aws_cli_commands?.join('\n') || 'AWS CLI commands not available'}
                </pre>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
