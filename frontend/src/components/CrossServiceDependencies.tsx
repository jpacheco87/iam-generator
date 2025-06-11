import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { analyzeCrossServiceDependencies } from '../lib/api';

interface DependencyAnalysisResult {
  dependencies: Record<string, string[]>;
  additional_permissions: Array<{
    Effect: string;
    Action: string;
    Resource: string;
    Dependency?: string;
  }>;
  enhanced_policy: {
    Version: string;
    Statement: any[];
  };
  dependency_graph: {
    nodes: Array<{ id: string; label: string; type: string }>;
    edges: Array<{ from: string; to: string; type: string }>;
  };
}

const CrossServiceDependencies: React.FC = () => {
  const [commands, setCommands] = useState('lambda invoke --function-name my-function\necs run-task --cluster my-cluster\ns3 put-object --bucket my-bucket --key file.txt');
  const [includeImplicit, setIncludeImplicit] = useState(true);
  const [result, setResult] = useState<DependencyAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
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
      
      const analysisResult = await analyzeCrossServiceDependencies({
        commands: commandList,
        include_implicit: includeImplicit,
        debug: false
      });
      
      setResult(analysisResult);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze dependencies');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const ServiceNode: React.FC<{ service: string; dependencies: string[] }> = ({ service, dependencies }) => (
    <div className="p-4 border rounded-lg bg-blue-50">
      <div className="font-semibold text-blue-800 mb-2">{service.toUpperCase()}</div>
      <div className="space-y-1">
        {dependencies.map((dep, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <span className="text-gray-400">→</span>
            <span className="text-gray-700">{dep}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const DependencyGraph: React.FC<{ dependencies: Record<string, string[]> }> = ({ dependencies }) => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Service Dependencies</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(dependencies).map(([service, deps]) => (
          <ServiceNode key={service} service={service} dependencies={deps} />
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔗 Cross-Service Dependencies Analyzer
          </CardTitle>
          <CardDescription>
            Analyze AWS CLI commands to identify cross-service dependencies and generate enhanced permissions with all required access.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Commands Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">AWS CLI Commands (one per line)</label>
            <Textarea
              value={commands}
              onChange={(e) => setCommands(e.target.value)}
              className="font-mono text-sm min-h-[150px]"
              placeholder="Enter AWS CLI commands (without 'aws' prefix)&#10;Example:&#10;lambda invoke --function-name my-function&#10;ecs run-task --cluster my-cluster&#10;s3 put-object --bucket my-bucket --key file.txt"
            />
          </div>

          {/* Configuration */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="includeImplicit"
              checked={includeImplicit}
              onChange={(e) => setIncludeImplicit(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="includeImplicit" className="text-sm font-medium">
              Include implicit dependencies (recommended)
            </label>
          </div>

          {/* Action Button */}
          <Button onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? 'Analyzing Dependencies...' : 'Analyze Dependencies'}
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
            <CardTitle>Dependency Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="dependencies" className="w-full">
              <TabsList>
                <TabsTrigger value="dependencies">Dependencies</TabsTrigger>
                <TabsTrigger value="permissions">Additional Permissions</TabsTrigger>
                <TabsTrigger value="policy">Enhanced Policy</TabsTrigger>
              </TabsList>

              <TabsContent value="dependencies" className="space-y-4">
                {/* Summary Stats */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {Object.keys(result.dependencies).length}
                    </div>
                    <div className="text-sm text-gray-600">Services Found</div>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {Object.values(result.dependencies).flat().length}
                    </div>
                    <div className="text-sm text-gray-600">Dependencies</div>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {result.additional_permissions.length}
                    </div>
                    <div className="text-sm text-gray-600">Extra Permissions</div>
                  </div>
                </div>

                {/* Dependencies Graph */}
                {Object.keys(result.dependencies).length > 0 ? (
                  <DependencyGraph dependencies={result.dependencies} />
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No cross-service dependencies found for the provided commands.
                  </div>
                )}
              </TabsContent>

              <TabsContent value="permissions" className="space-y-4">
                {result.additional_permissions.length > 0 ? (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Additional Permissions Required</h3>
                    <div className="space-y-2">
                      {result.additional_permissions.map((perm, index) => (
                        <div key={index} className="p-3 border rounded-lg">
                          <div className="flex items-start gap-2">
                            <Badge variant="outline">{perm.Effect}</Badge>
                            <div className="flex-1">
                              <div className="font-mono text-sm font-medium">{perm.Action}</div>
                              <div className="text-sm text-gray-600">Resource: {perm.Resource}</div>
                              {perm.Dependency && (
                                <div className="text-sm text-blue-600">
                                  Dependency: {perm.Dependency}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No additional permissions required beyond base command permissions.
                  </div>
                )}
              </TabsContent>

              <TabsContent value="policy" className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Enhanced Policy Document</h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(JSON.stringify(result.enhanced_policy, null, 2));
                      }}
                    >
                      Copy JSON
                    </Button>
                  </div>
                  
                  <div className="bg-gray-50 border rounded-lg">
                    <pre className="p-4 text-sm overflow-x-auto">
                      {JSON.stringify(result.enhanced_policy, null, 2)}
                    </pre>
                  </div>

                  {/* Policy Summary */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {result.enhanced_policy.Statement?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Statements</div>
                    </div>
                    
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {JSON.stringify(result.enhanced_policy).length}
                      </div>
                      <div className="text-sm text-gray-600">Policy Size (chars)</div>
                    </div>
                    
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {result.enhanced_policy.Version}
                      </div>
                      <div className="text-sm text-gray-600">Policy Version</div>
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
                          const blob = new Blob([JSON.stringify(result.enhanced_policy, null, 2)], {
                            type: 'application/json'
                          });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = 'enhanced-iam-policy.json';
                          a.click();
                          URL.revokeObjectURL(url);
                        }}
                      >
                        JSON Policy
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          // Generate Terraform format
                          const terraformConfig = `resource "aws_iam_policy" "enhanced_policy" {
  name        = "EnhancedPolicy"
  description = "Auto-generated policy with cross-service dependencies"
  
  policy = jsonencode(${JSON.stringify(result.enhanced_policy, null, 2)})
}`;
                          const blob = new Blob([terraformConfig], { type: 'text/plain' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = 'enhanced-policy.tf';
                          a.click();
                          URL.revokeObjectURL(url);
                        }}
                      >
                        Terraform
                      </Button>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CrossServiceDependencies;
