import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { validatePolicy, optimizePolicy } from '../lib/api';

interface ValidationIssue {
  severity: string;
  category: string;
  message: string;
  location?: string;
  suggestion?: string;
}

interface ValidationResult {
  is_valid: boolean;
  policy_size: number;
  policy_type: string;
  issues: ValidationIssue[];
  score: number;
  recommendations: string[];
}

interface OptimizationResult {
  original_policy: any;
  optimized_policy: any;
  size_reduction: number;
  optimizations_applied: string[];
  validation_result: ValidationResult;
}

const PolicyValidator: React.FC = () => {
  const [policyJson, setPolicyJson] = useState('{\n  "Version": "2012-10-17",\n  "Statement": [\n    {\n      "Effect": "Allow",\n      "Action": "s3:GetObject",\n      "Resource": "*"\n    }\n  ]\n}');
  const [policyType, setPolicyType] = useState('managed');
  const [accountId, setAccountId] = useState('');
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [optimizationLevel, setOptimizationLevel] = useState('standard');
  const [isValidating, setIsValidating] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    setIsValidating(true);
    setError(null);
    
    try {
      // Parse JSON to validate it first
      const policy = JSON.parse(policyJson);
      
      const result = await validatePolicy({
        policy,
        policy_type: policyType,
        account_id: accountId || undefined,
        debug: false
      });
      
      setValidationResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to validate policy');
    } finally {
      setIsValidating(false);
    }
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setError(null);
    
    try {
      const policy = JSON.parse(policyJson);
      
      const result = await optimizePolicy({
        policy,
        optimization_level: optimizationLevel,
        account_id: accountId || undefined
      });
      
      setOptimizationResult(result);
      // Update the policy with optimized version
      setPolicyJson(JSON.stringify(result.optimized_policy, null, 2));
    } catch (err: any) {
      setError(err.message || 'Failed to optimize policy');
    } finally {
      setIsOptimizing(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'error': return 'bg-red-400';
      case 'warning': return 'bg-yellow-400';
      case 'info': return 'bg-blue-400';
      default: return 'bg-gray-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🛡️ IAM Policy Validator & Optimizer
          </CardTitle>
          <CardDescription>
            Validate IAM policies against AWS limits and security best practices, then optimize for size and security.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Policy Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">IAM Policy JSON</label>
            <Textarea
              value={policyJson}
              onChange={(e) => setPolicyJson(e.target.value)}
              className="font-mono text-sm min-h-[200px]"
              placeholder="Enter your IAM policy JSON here..."
            />
          </div>

          {/* Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Policy Type</label>
              <Select value={policyType} onValueChange={setPolicyType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="managed">Managed Policy</SelectItem>
                  <SelectItem value="inline_user">Inline User Policy</SelectItem>
                  <SelectItem value="inline_role">Inline Role Policy</SelectItem>
                  <SelectItem value="inline_group">Inline Group Policy</SelectItem>
                </SelectContent>
              </Select>
            </div>

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
              <label className="text-sm font-medium">Optimization Level</label>
              <Select value={optimizationLevel} onValueChange={setOptimizationLevel}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic">Basic</SelectItem>
                  <SelectItem value="standard">Standard</SelectItem>
                  <SelectItem value="aggressive">Aggressive</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button onClick={handleValidate} disabled={isValidating}>
              {isValidating ? 'Validating...' : 'Validate Policy'}
            </Button>
            <Button onClick={handleOptimize} disabled={isOptimizing} variant="outline">
              {isOptimizing ? 'Optimizing...' : 'Optimize Policy'}
            </Button>
          </div>

          {/* Error Display */}
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {(validationResult || optimizationResult) && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="validation" className="w-full">
              <TabsList>
                <TabsTrigger value="validation">Validation</TabsTrigger>
                {optimizationResult && <TabsTrigger value="optimization">Optimization</TabsTrigger>}
              </TabsList>

              <TabsContent value="validation" className="space-y-4">
                {validationResult && (
                  <>
                    {/* Validation Summary */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold">
                          {validationResult.is_valid ? (
                            <span className="text-green-600">✓ Valid</span>
                          ) : (
                            <span className="text-red-600">✗ Invalid</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-600">Status</div>
                      </div>
                      
                      <div className="text-center p-4 border rounded-lg">
                        <div className={`text-2xl font-bold ${getScoreColor(validationResult.score)}`}>
                          {validationResult.score}/100
                        </div>
                        <div className="text-sm text-gray-600">Security Score</div>
                        <Progress value={validationResult.score} className="mt-2" />
                      </div>
                      
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {validationResult.policy_size}
                        </div>
                        <div className="text-sm text-gray-600">Size (chars)</div>
                      </div>
                      
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {validationResult.issues.length}
                        </div>
                        <div className="text-sm text-gray-600">Issues Found</div>
                      </div>
                    </div>

                    {/* Issues */}
                    {validationResult.issues.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold">Issues Found</h3>
                        <div className="space-y-2">
                          {validationResult.issues.map((issue, index) => (
                            <div key={index} className="p-3 border rounded-lg">
                              <div className="flex items-start gap-2">
                                <Badge className={getSeverityColor(issue.severity)}>
                                  {issue.severity}
                                </Badge>
                                <div className="flex-1">
                                  <div className="font-medium">{issue.message}</div>
                                  {issue.location && (
                                    <div className="text-sm text-gray-600">Location: {issue.location}</div>
                                  )}
                                  {issue.suggestion && (
                                    <div className="text-sm text-blue-600 mt-1">
                                      💡 {issue.suggestion}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {validationResult.recommendations.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold">Recommendations</h3>
                        <ul className="space-y-1">
                          {validationResult.recommendations.map((rec, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-green-600">•</span>
                              <span className="text-sm">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </TabsContent>

              <TabsContent value="optimization" className="space-y-4">
                {optimizationResult && (
                  <>
                    {/* Optimization Summary */}
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          -{optimizationResult.size_reduction}
                        </div>
                        <div className="text-sm text-gray-600">Characters Reduced</div>
                      </div>
                      
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {optimizationResult.optimizations_applied.length}
                        </div>
                        <div className="text-sm text-gray-600">Optimizations Applied</div>
                      </div>
                      
                      <div className="text-center p-4 border rounded-lg">
                        <div className={`text-2xl font-bold ${getScoreColor(optimizationResult.validation_result.score)}`}>
                          {optimizationResult.validation_result.score}/100
                        </div>
                        <div className="text-sm text-gray-600">New Score</div>
                      </div>
                    </div>

                    {/* Optimizations Applied */}
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Optimizations Applied</h3>
                      <ul className="space-y-1">
                        {optimizationResult.optimizations_applied.map((opt, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-blue-600">✓</span>
                            <span className="text-sm">{opt}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Optimized Policy */}
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Optimized Policy</h3>
                      <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
                        {JSON.stringify(optimizationResult.optimized_policy, null, 2)}
                      </pre>
                    </div>
                  </>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PolicyValidator;
