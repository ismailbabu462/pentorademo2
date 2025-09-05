import React, { useState, useEffect, useRef } from 'react';
import { 
  Target, 
  Globe, 
  Shield, 
  Database,
  Code,
  Activity,
  Play,
  Settings,
  AlertTriangle,
  Wifi,
  WifiOff,
  Download,
  ExternalLink,
  Sparkles,
  FolderOpen
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';

const ToolsPage = () => {
  const { user, setIsAIPanelOpen, setAIContext } = useAuth();

  const [targetInput, setTargetInput] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [runningTool, setRunningTool] = useState(null);
  const [toolResults, setToolResults] = useState({});

  
  // WebSocket state
  const [wsConnected, setWsConnected] = useState(false);
  const [wsOutput, setWsOutput] = useState('');
  const wsRef = useRef(null);

  // WebSocket connection
  const connectWebSocket = () => {
    try {
      // For production, WebSocket will be handled by Desktop Agent locally
      const wsUrl = process.env.NODE_ENV === 'production' 
        ? 'ws://localhost:13337'  // Desktop Agent runs locally
        : 'ws://localhost:13337';
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setWsConnected(true);
        toast.success('Desktop Agent connected');
        // WebSocket connected
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onclose = () => {
        setWsConnected(false);
        toast.error('Desktop Agent disconnected');
        // WebSocket disconnected
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Desktop Agent connection error');
      };
    } catch (error) {
      console.error('Failed to connect to Desktop Agent:', error);
      toast.error('Failed to connect to Desktop Agent');
    }
  };
  
  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'welcome':
        // Desktop Agent welcome message received
        break;
      case 'start':
        setRunningTool(data.tool);
        setWsOutput(`Starting ${data.tool} scan on ${data.target}...\n`);
        toast.info(`Starting ${data.tool} scan`);
        break;
      case 'output':
        setWsOutput(prev => prev + data.line + '\n');
        break;
      case 'complete':
        setRunningTool(null);
        setWsOutput(prev => prev + `\n${data.tool} scan completed (exit code: ${data.return_code})\n`);
        if (data.success) {
          toast.success(`${data.tool} scan completed successfully`);
          // Save tool output to project if selected
          saveToolOutputToProject(data.tool, data.target, wsOutput);
        } else {
          toast.error(`${data.tool} scan failed`);
        }
        break;
      case 'error':
        setRunningTool(null);
        setWsOutput(prev => prev + `\nError: ${data.message}\n`);
        toast.error(data.message);
        break;
      default:
        // Unknown WebSocket message type
    }
  };
  
  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  // Fetch projects
  const fetchProjects = async () => {
    setLoadingProjects(true);
    try {
      const response = await api.get('/projects');
      setProjects(response.data || []);
    } catch (error) {
      console.error('❌ ToolsPage: Failed to fetch projects:', error);
      toast.error('Failed to fetch projects');
      setProjects([]);
    } finally {
      setLoadingProjects(false);
    }
  };

  // Save tool output to project
  const saveToolOutputToProject = async (toolName, target, output) => {
    if (!selectedProjectId) {
      // No project selected, skipping save
      return;
    }

    try {
      const response = await api.post('/tools/output', {
        tool_name: toolName,
        target: target,
        output: output,
        status: 'completed',
        project_id: selectedProjectId
      });

      // Tool output saved to project
      toast.success(`Scan results saved to project`);
    } catch (error) {
      console.error('Failed to save tool output:', error);
      toast.error('Failed to save scan results to project');
    }
  };

  // Save current WebSocket output to selected project
  const saveCurrentOutputToProject = async () => {
    if (!selectedProjectId) {
      toast.error('Lütfen önce bir proje seçin');
      return;
    }

    if (!wsOutput || wsOutput.trim() === '') {
      toast.error('Kaydedilecek çıktı bulunamadı');
      return;
    }

    try {
      // Extract tool name from output (try to detect from common patterns)
      let toolName = 'Unknown Tool';
      const outputLower = wsOutput.toLowerCase();
      
      if (outputLower.includes('nmap')) {
        toolName = 'Nmap';
      } else if (outputLower.includes('subfinder')) {
        toolName = 'Subfinder';
      } else if (outputLower.includes('nuclei')) {
        toolName = 'Nuclei';
      } else if (outputLower.includes('ffuf')) {
        toolName = 'ffuf';
      } else if (outputLower.includes('gobuster')) {
        toolName = 'Gobuster';
      } else if (outputLower.includes('amass')) {
        toolName = 'Amass';
      }

      // Extract target from output or use targetInput
      let target = targetInput || 'Unknown Target';
      
      // Try to extract target from output
      const targetMatch = wsOutput.match(/(?:target|scanning|testing):\s*([^\s\n]+)/i);
      if (targetMatch) {
        target = targetMatch[1];
      }

      const response = await api.post('/tools/output', {
        tool_name: toolName,
        target: target,
        output: wsOutput,
        status: 'completed',
        project_id: selectedProjectId
      });

      // Current output saved to project
      toast.success(`Tarama sonuçları projeye kaydedildi`);
      
      // Optionally clear the output after saving
      // setWsOutput('');
      
    } catch (error) {
      console.error('Failed to save current output:', error);
      toast.error('Tarama sonuçları kaydedilemedi');
    }
  };

  // Fetch projects on component mount
  useEffect(() => {
    fetchProjects();
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Cleanup on unmount
    return () => {
      disconnectWebSocket();
    };
  }, []);

  const toolCategories = {
    reconnaissance: [
      {
        name: 'Subfinder',
        description: 'Fast passive subdomain discovery tool',
        icon: Globe,
        status: 'ready',
        command: 'subfinder -d target.com',
        features: ['Passive Discovery', 'Multiple Sources', 'Fast Execution']
      },
      {
        name: 'Amass',
        description: 'In-depth attack surface mapping',
        icon: Target,
        status: 'ready',
        command: 'amass enum -d target.com',
        features: ['Active/Passive', 'DNS Enumeration', 'Network Mapping']
      }
    ],
    scanning: [
      {
        name: 'Nmap',
        description: 'Network discovery and port scanning',
        icon: Shield,
        status: 'ready',
        command: 'nmap -sV -sC target.com',
        features: ['Port Scanning', 'Service Detection', 'Script Engine']
      },
      {
        name: 'Nuclei',
        description: 'Fast vulnerability scanner',
        icon: AlertTriangle,
        status: 'ready',
        command: 'nuclei -u https://target.com',
        features: ['CVE Detection', 'Custom Templates', 'Fast Scanning']
      }
    ],
    fuzzing: [
      {
        name: 'ffuf',
        description: 'Fast web fuzzer',
        icon: Code,
        status: 'ready',
        command: 'ffuf -w wordlist.txt -u https://target.com/FUZZ',
        features: ['Directory Fuzzing', 'Parameter Discovery', 'High Performance']
      },
      {
        name: 'Gobuster',
        description: 'Directory and file brute-forcer',
        icon: Database,
        status: 'ready',
        command: 'gobuster dir -u https://target.com -w wordlist.txt',
        features: ['Directory Brute Force', 'DNS Enumeration', 'Multiple Modes']
      }
    ]
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'ready': { label: 'Ready', className: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200' },
      'coming-soon': { label: 'Coming Soon', className: 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200' },
      'maintenance': { label: 'Maintenance', className: 'bg-gray-300 text-gray-900 dark:bg-gray-600 dark:text-gray-100' }
    };
    
    const config = statusConfig[status] || statusConfig['coming-soon'];
    return (
      <Badge className={`${config.className} text-xs font-medium`}>
        {config.label}
      </Badge>
    );
  };

  const handleRunTool = async (toolName) => {
    if (!targetInput.trim()) {
      toast.error('Please enter a target first');
      return;
    }
    
    if (!wsConnected) {
      toast.error('Desktop Agent not connected. Please start the Desktop Agent first.');
      return;
    }
    
    // Map tool names to lowercase for WebSocket
    const toolMap = {
      'Subfinder': 'subfinder',
      'Amass': 'amass',
      'Nmap': 'nmap',
      'Nuclei': 'nuclei',
      'ffuf': 'ffuf',
      'Gobuster': 'gobuster'
    };
    
    const wsToolName = toolMap[toolName];
    if (!wsToolName) {
      toast.error('Tool not supported by Desktop Agent');
      return;
    }
    
    // Send command to Desktop Agent via WebSocket with user info
    const message = {
      type: 'execute_tool',
      tool: wsToolName,
      target: targetInput.trim(),
      user_id: user?.id || 'anonymous',
      tier: user?.tier || 'essential'
    };
    
    try {
      wsRef.current.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      toast.error('Failed to send command to Desktop Agent');
    }
  };

  // Tool execution functions
  const runSubfinder = async (target) => {
    toast.info('Running Subfinder scan...');
    
    try {
      const response = await api.post('/tools/subfinder', { target });
      if (response.success) {
        return {
          tool: 'Subfinder',
          target: target,
          results: response.results.subdomains,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(response.error || 'Subfinder scan failed');
      }
    } catch (error) {
      console.error('Subfinder error:', error);
      toast.error(`Subfinder scan failed: ${error.message}`);
      throw error;
    }
  };

  const runNmap = async (target) => {
    toast.info('Running Nmap scan...');
    
    try {
      const response = await api.post('/tools/nmap', { target });
      if (response.success) {
        return {
          tool: 'Nmap',
          target: target,
          results: response.results,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(response.error || 'Nmap scan failed');
      }
    } catch (error) {
      console.error('Nmap error:', error);
      toast.error(`Nmap scan failed: ${error.message}`);
      throw error;
    }
  };

  const runNuclei = async (target) => {
    toast.info('Running Nuclei scan...');
    
    try {
      const response = await api.post('/tools/nuclei', { target });
      if (response.success) {
        return {
          tool: 'Nuclei',
          target: target,
          results: response.results.vulnerabilities,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(response.error || 'Nuclei scan failed');
      }
    } catch (error) {
      console.error('Nuclei error:', error);
      toast.error(`Nuclei scan failed: ${error.message}`);
      throw error;
    }
  };

  const runFfuf = async (target) => {
    toast.info('Running ffuf scan...');
    
    try {
      const response = await api.post('/tools/ffuf', { target });
      if (response.success) {
        return {
          tool: 'ffuf',
          target: target,
          results: response.results.directories,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(response.error || 'ffuf scan failed');
      }
    } catch (error) {
      console.error('ffuf error:', error);
      toast.error(`ffuf scan failed: ${error.message}`);
      throw error;
    }
  };

  const runGobuster = async (target) => {
    toast.info('Running Gobuster scan...');
    
    try {
      const response = await api.post('/tools/gobuster', { target });
      if (response.success) {
        return {
          tool: 'Gobuster',
          target: target,
          results: response.results.directories,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(response.error || 'Gobuster scan failed');
      }
    } catch (error) {
      console.error('Gobuster error:', error);
      toast.error(`Gobuster scan failed: ${error.message}`);
      throw error;
      throw error;
    }
  };

  const runAmass = async (target) => {
    toast.info('Running Amass scan...');
    
    try {
      const response = await api.post('/tools/amass', { target });
      if (response.success) {
        return {
          tool: 'Amass',
          target: target,
          results: response.results.subdomains,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(response.error || 'Amass scan failed');
      }
    } catch (error) {
      console.error('Amass error:', error);
      toast.error(`Amass scan failed: ${error.message}`);
      throw error;
    }
  };

  const renderToolCard = (tool) => {
    const IconComponent = tool.icon;
    const isReady = tool.status === 'ready';
    
    return (
      <Card key={tool.name} className="bg-card border border-border shadow-md hover:shadow-lg transition-all duration-300 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center shadow-md">
                <IconComponent className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold text-card-foreground">
                  {tool.name}
                </CardTitle>
                <CardDescription className="mt-1 text-muted-foreground">
                  {tool.description}
                </CardDescription>
              </div>
            </div>
            {getStatusBadge(tool.status)}
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Features</h4>
            <div className="flex flex-wrap gap-1">
              {tool.features?.map((feature, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {feature}
                </Badge>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium mb-2">Command</h4>
            <code className="text-xs bg-muted p-2 rounded block font-mono">
              {tool.command}
            </code>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button 
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-2 rounded-lg shadow-md hover:shadow-lg transition-all duration-300" 
              disabled={!isReady || runningTool === tool.name}
              onClick={() => handleRunTool(tool.name)}
            >
              {runningTool === tool.name ? (
                <>
                  <div className="animate-spin w-5 h-5 border-3 border-white border-t-transparent rounded-full mr-2"></div>
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  {isReady ? 'Run Tool' : 'Coming Soon'}
                </>
              )}
            </Button>
            <Button variant="outline" size="sm" disabled={!isReady} className="border border-border hover:border-primary hover:bg-primary/5 transition-all duration-300 rounded-lg">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
          <div className="p-6 space-y-6 animate-fade-in bg-background min-h-screen">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-foreground">
              Security Tools
            </h1>
            <p className="text-muted-foreground text-lg mt-2">
              Integrated penetration testing toolkit
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              className="flex items-center space-x-2 hover:bg-primary hover:text-primary-foreground transition-colors duration-200"
              onClick={() => window.open('https://github.com/ismailbabu462/pentora-desktop-agents', '_blank')}
            >
              <Download className="w-4 h-4" />
              <span>Agent Download</span>
              <ExternalLink className="w-3 h-3" />
            </Button>
          </div>
        </div>

      {/* Desktop Agent Status */}
      <Card className="border-border bg-card">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {wsConnected ? (
                <Wifi className="w-5 h-5 text-green-500" />
              ) : (
                <WifiOff className="w-5 h-5 text-red-500" />
              )}
              <div>
                <h3 className="font-medium text-foreground">Desktop Agent</h3>
                <p className="text-sm text-muted-foreground">
                  {wsConnected ? 'Connected to localhost:13337' : 'Not connected'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  <strong>Secure:</strong> Agent runs locally on your machine, your data is never sent externally
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={wsConnected ? 'default' : 'secondary'}>
                {wsConnected ? 'Online' : 'Offline'}
              </Badge>
              {!wsConnected && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={connectWebSocket}
                >
                  Reconnect
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Target Input, Project Selection and Search */}
      <div className="flex items-center space-x-6">
        <div className="flex-1 max-w-md">
          <Label htmlFor="target" className="text-sm font-semibold mb-3 block text-foreground">
            Target
          </Label>
          <Input
            id="target"
            placeholder="Enter target (e.g., example.com, 192.168.1.1)"
            value={targetInput}
            onChange={(e) => setTargetInput(e.target.value)}
            className="h-12 px-4 rounded-lg border border-border focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-300 bg-background"
          />
        </div>
        <div className="flex-1 max-w-md">
          <Label className="text-sm font-semibold mb-3 block text-foreground">
            Project
          </Label>
          <Select 
            value={selectedProjectId || ""} 
            onValueChange={(value) => setSelectedProjectId(value === "none" ? null : value)}
          >
            <SelectTrigger className="h-12">
              <SelectValue placeholder="Select project for scan results" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">No project (local only)</SelectItem>
              {loadingProjects ? (
                <SelectItem value="loading" disabled>
                  Loading projects...
                </SelectItem>
              ) : (
                projects.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    <div className="flex items-center gap-2">
                      <FolderOpen className="h-4 w-4" />
                      {project.name}
                    </div>
                  </SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
        </div>

      </div>



      {/* Tools by Category */}
      <Tabs defaultValue="reconnaissance" className="space-y-6">
        <div className="flex justify-center">
          <TabsList className="grid grid-cols-3 w-full max-w-md bg-secondary p-1 rounded-lg shadow-md">
            <TabsTrigger value="reconnaissance" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-md transition-all duration-300">
              Recon
            </TabsTrigger>
            <TabsTrigger value="scanning" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-md transition-all duration-300">
              Scanning
            </TabsTrigger>
            <TabsTrigger value="fuzzing" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-md transition-all duration-300">
              Fuzzing
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="reconnaissance" className="space-y-4">
          <div className="text-center py-6">
            <h3 className="text-2xl font-bold text-foreground mb-2">
              Reconnaissance Tools
            </h3>
            <p className="text-muted-foreground text-lg">
              Passive and active information gathering tools
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCategories.reconnaissance?.map(renderToolCard)}
          </div>
        </TabsContent>

        <TabsContent value="scanning" className="space-y-4">
          <div className="text-center py-6">
            <h3 className="text-2xl font-bold text-foreground mb-2">
              Scanning & Vulnerability Assessment
            </h3>
            <p className="text-muted-foreground text-lg">
              Port scanning and vulnerability detection tools
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCategories.scanning?.map(renderToolCard)}
          </div>
        </TabsContent>

        <TabsContent value="fuzzing" className="space-y-4">
          <div className="text-center py-6">
            <h3 className="text-2xl font-bold text-foreground mb-2">
              Web Application Fuzzing
            </h3>
            <p className="text-muted-foreground text-lg">
              Directory enumeration and content discovery tools
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCategories.fuzzing?.map(renderToolCard)}
          </div>
        </TabsContent>
      </Tabs>

      {/* WebSocket Output */}
      {wsOutput && (
        <Card className="border-primary/50 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-primary">
              <Activity className="w-5 h-5" />
              <span>Tool Output</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-background border rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="text-sm font-mono whitespace-pre-wrap text-foreground">
                {wsOutput}
              </pre>
            </div>
            <div className="flex justify-between mt-2">
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => {
                    setIsAIPanelOpen(true);
                    setAIContext({
                      tool_output: wsOutput,
                      defaultMessage: "Please analyze this scan output and summarize the important findings."
                    });
                  }}
                  className="flex items-center space-x-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Ask AI</span>
                </Button>
                
                {selectedProjectId && wsOutput && (
                  <Button 
                    variant="default" 
                    size="sm" 
                    onClick={() => saveCurrentOutputToProject()}
                    className="flex items-center space-x-2 bg-green-600 hover:bg-green-700"
                  >
                    <Download className="w-4 h-4" />
                    <span>Projeye Aktar</span>
                  </Button>
                )}
              </div>
              
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setWsOutput('')}
              >
                Clear Output
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tool Results */}
      {Object.keys(toolResults).length > 0 && (
        <Card className="border-success/50 bg-success/5">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-success">
              <Activity className="w-5 h-5" />
              <span>Recent Tool Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(toolResults).map(([key, result]) => (
                <div key={key} className="border rounded-lg p-4 bg-background">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{result.tool} - {result.target}</h4>
                    <span className="text-xs text-muted-foreground">
                      {new Date(result.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="text-sm">
                    {(result.tool === 'Subfinder' || result.tool === 'Amass') && (
                      <div>
                        <p className="font-medium mb-1">
                          {result.tool === 'Subfinder' ? 'Subdomains found:' : 'Attack surface discovered:'}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {result.results.map((subdomain, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {subdomain}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {result.tool === 'Nmap' && (
                      <div>
                        <p className="font-medium mb-1">Open ports:</p>
                        <div className="flex flex-wrap gap-1">
                          {result.results.open_ports.map((port, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {port} ({result.results.services[port]})
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {result.tool === 'Nuclei' && (
                      <div>
                        <p className="font-medium mb-1">Vulnerabilities found:</p>
                        <div className="space-y-1">
                          {result.results.map((vuln, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <Badge variant={vuln.severity === 'high' ? 'destructive' : 'secondary'} className="text-xs">
                                {vuln.severity}
                              </Badge>
                              <span className="text-xs">{vuln.description}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {(result.tool === 'ffuf' || result.tool === 'Gobuster') && (
                      <div>
                        <p className="font-medium mb-1">Directories found:</p>
                        <div className="flex flex-wrap gap-1">
                          {result.results.map((dir, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {dir}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ToolsPage;