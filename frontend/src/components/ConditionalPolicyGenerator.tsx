import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { generateConditionalPolicy } from '../lib/api';

interface ConditionalPolicyResult {
  policy_document: {
    Version: string;
    Statement: any[];
  };
  conditions_applied: string[];
  security_enhancements: string[];
  metadata: {
    commands_analyzed: number;
    conditions_count: number;
    account_id?: string;
    region?: string;
  };
}

const ConditionalPolicyGenerator: React.FC = () => {
  const [commands, setCommands] = useState('s3 put-object --bucket sensitive-bucket --key file.txt\niam create-user --user-name new-user\nec2 terminate-instances --instance-ids i-1234567890abcdef0');
  const [accountId, setAccountId] = useState('');
  const [region, setRegion] = useState('');
  
  // Security condition settings
  const [mfaRequired, setMfaRequired] = useState(true);
  const [ipRestriction, setIpRestriction] = useState('203.0.113.0/24');
  const [timeRestriction, setTimeRestriction] = useState(false);
  const [timeStart, setTimeStart] = useState('09:00');
  const [timeEnd, setTimeEnd] = useState('17:00');
  const [secureTransport, setSecureTransport] = useState(true);
  const [vpcEndpointOnly, setVpcEndpointOnly] = useState(false);
  const [vpcEndpointId, setVpcEndpointId] = useState('');
  
  const [result, setResult] = useState<ConditionalPolicyResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      const commandList = commands
        .split('\n')
        .map(cmd => cmd.trim())
        .filter(cmd => cmd && !cmd.startsWith('#'));
      
      if (commandList.length === 0) {
        setError('Please enter at least one AWS CLI command');
        return;
      }
      
      // Build conditions object
      const conditions: any = {};
      
      if (mfaRequired) {
        conditions.mfa_required = true;
      }
      
      if (ipRestriction.trim()) {
        conditions.ip_restriction = ipRestriction.split(',').map(ip => ip.trim());
      }
      
      if (timeRestriction && timeStart && timeEnd) {
        conditions.time_restriction = {
          start: `${new Date().toISOString().split('T')[0]}T${timeStart}:00Z`,
          end: `${new Date().toISOString().split('T')[0]}T${timeEnd}:00Z`
        };
      }
      
      if (secureTransport) {
        conditions.secure_transport = true;
      }
      
      if (vpcEndpointOnly && vpcEndpointId.trim()) {
        conditions.vpc_endpoint_only = vpcEndpointId.trim();
      }
      
      const policyResult = await generateConditionalPolicy({
        commands: commandList,
        conditions,
        account_id: accountId || undefined,
        region: region || undefined
      });
      
      setResult(policyResult);
    } catch (err: any) {
      setError(err.message || 'Failed to generate conditional policy');
    } finally {
      setIsGenerating(false);
    }
  };

  const ConditionCard: React.FC<{ title: string; description: string; children: React.ReactNode }> = ({
    title,
    description,
    children
  }) => (
    <div className="p-4 border rounded-lg space-y-3">
      <div>
        <h4 className="font-medium">{title}</h4>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      {children}
    </div>
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔐 Conditional Policy Generator
          </CardTitle>
          <CardDescription>
            Generate IAM policies with advanced security conditions including MFA requirements, IP restrictions, time-based access, and more.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Commands Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">AWS CLI Commands (one per line)</label>
            <Textarea
              value={commands}
              onChange={(e) => setCommands(e.target.value)}
              className="font-mono text-sm min-h-[120px]"
              placeholder="Enter AWS CLI commands (without 'aws' prefix)&#10;Example:&#10;s3 put-object --bucket my-bucket --key file.txt&#10;iam create-user --user-name new-user"
            />
          </div>

          {/* Account and Region */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Account ID (Optional)</label>
              <input
                type="text"
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="123456789012"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Region (Optional)</label>
              <input
                type="text"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="us-east-1"
              />
            </div>
          </div>

          {/* Security Conditions */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Security Conditions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* MFA Requirement */}
              <ConditionCard
                title="Multi-Factor Authentication"
                description="Require MFA for sensitive operations"
              >
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="mfaRequired"
                    checked={mfaRequired}
                    onChange={(e) => setMfaRequired(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="mfaRequired" className="text-sm">
                    Require MFA for destructive actions
                  </label>
                </div>
              </ConditionCard>

              {/* IP Restriction */}
              <ConditionCard
                title="IP Address Restrictions"
                description="Limit access to specific IP addresses or ranges"
              >
                <input
                  type="text"
                  value={ipRestriction}
                  onChange={(e) => setIpRestriction(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  placeholder="203.0.113.0/24, 198.51.100.0/24"
                />
              </ConditionCard>

              {/* Time-based Access */}
              <ConditionCard
                title="Time-based Access Control"
                description="Restrict access to specific time windows"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="timeRestriction"
                      checked={timeRestriction}
                      onChange={(e) => setTimeRestriction(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="timeRestriction" className="text-sm">
                      Enable time restrictions
                    </label>
                  </div>
                  {timeRestriction && (
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="time"
                        value={timeStart}
                        onChange={(e) => setTimeStart(e.target.value)}
                        className="px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        type="time"
                        value={timeEnd}
                        onChange={(e) => setTimeEnd(e.target.value)}
                        className="px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  )}
                </div>
              </ConditionCard>

              {/* Secure Transport */}
              <ConditionCard
                title="Secure Transport"
                description="Require HTTPS/TLS for all API calls"
              >
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="secureTransport"
                    checked={secureTransport}
                    onChange={(e) => setSecureTransport(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="secureTransport" className="text-sm">
                    Require secure transport (HTTPS/TLS)
                  </label>
                </div>
              </ConditionCard>

              {/* VPC Endpoint */}
              <ConditionCard
                title="VPC Endpoint Access"
                description="Restrict access to specific VPC endpoints"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="vpcEndpointOnly"
                      checked={vpcEndpointOnly}
                      onChange={(e) => setVpcEndpointOnly(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="vpcEndpointOnly" className="text-sm">
                      Restrict to VPC endpoint
                    </label>
                  </div>
                  {vpcEndpointOnly && (
                    <input
                      type="text"
                      value={vpcEndpointId}
                      onChange={(e) => setVpcEndpointId(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      placeholder="vpce-1234567890abcdef0"
                    />
                  )}
                </div>
              </ConditionCard>
            </div>
          </div>

          {/* Generate Button */}
          <Button onClick={handleGenerate} disabled={isGenerating} className="w-full">
            {isGenerating ? 'Generating Conditional Policy...' : 'Generate Conditional Policy'}
          </Button>

          {/* Error Display */}
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Conditional Policy</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="policy" className="w-full">
              <TabsList>
                <TabsTrigger value="policy">Policy Document</TabsTrigger>
                <TabsTrigger value="conditions">Applied Conditions</TabsTrigger>
                <TabsTrigger value="security">Security Enhancements</TabsTrigger>
              </TabsList>

              <TabsContent value="policy" className="space-y-4">
                {/* Policy Summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {result.metadata.commands_analyzed}
                    </div>
                    <div className="text-sm text-gray-600">Commands Analyzed</div>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {result.policy_document.Statement?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Policy Statements</div>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {result.metadata.conditions_count}
                    </div>
                    <div className="text-sm text-gray-600">Conditions Applied</div>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {JSON.stringify(result.policy_document).length}
                    </div>
                    <div className="text-sm text-gray-600">Policy Size (chars)</div>
                  </div>
                </div>

                {/* Policy Document */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Policy Document</h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(JSON.stringify(result.policy_document, null, 2));
                      }}
                    >
                      Copy JSON
                    </Button>
                  </div>
                  
                  <div className="bg-gray-50 border rounded-lg">
                    <pre className="p-4 text-sm overflow-x-auto">
                      {JSON.stringify(result.policy_document, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Download Options */}
                <div className="space-y-2">
                  <h4 className="font-medium">Download Policy As:</h4>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const blob = new Blob([JSON.stringify(result.policy_document, null, 2)], {
                          type: 'application/json'
                        });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'conditional-iam-policy.json';
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      JSON Policy
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="conditions" className="space-y-4">
                {result.conditions_applied.length > 0 ? (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Applied Security Conditions</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {result.conditions_applied.map((condition, index) => (
                        <Badge key={index} variant="outline" className="justify-start p-2">
                          {condition}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No additional conditions were applied to the policy.
                  </div>
                )}
              </TabsContent>

              <TabsContent value="security" className="space-y-4">
                {result.security_enhancements.length > 0 ? (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Security Enhancements</h3>
                    <div className="space-y-2">
                      {result.security_enhancements.map((enhancement, index) => (
                        <div key={index} className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span className="text-sm text-green-800">{enhancement}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No additional security enhancements were applied.
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ConditionalPolicyGenerator;
