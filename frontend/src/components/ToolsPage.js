import React, { useState } from 'react';
import { 
  Search, 
  Target, 
  Globe, 
  Shield, 
  Database,
  Code,
  Activity,
  Play,
  Settings,
  AlertTriangle
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

const ToolsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');

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
        status: 'coming-soon',
        command: 'amass enum -d target.com',
        features: ['Active/Passive', 'DNS Enumeration', 'Network Mapping']
      }
    ],
    scanning: [
      {
        name: 'Nmap',
        description: 'Network discovery and port scanning',
        icon: Shield,
        status: 'coming-soon',
        command: 'nmap -sV -sC target.com',
        features: ['Port Scanning', 'Service Detection', 'Script Engine']
      },
      {
        name: 'Nuclei',
        description: 'Fast vulnerability scanner',
        icon: AlertTriangle,
        status: 'coming-soon',
        command: 'nuclei -u https://target.com',
        features: ['CVE Detection', 'Custom Templates', 'Fast Scanning']
      }
    ],
    fuzzing: [
      {
        name: 'ffuf',
        description: 'Fast web fuzzer',
        icon: Code,
        status: 'coming-soon',
        command: 'ffuf -w wordlist.txt -u https://target.com/FUZZ',
        features: ['Directory Fuzzing', 'Parameter Discovery', 'High Performance']
      },
      {
        name: 'Gobuster',
        description: 'Directory and file brute-forcer',
        icon: Database,
        status: 'coming-soon',
        command: 'gobuster dir -u https://target.com -w wordlist.txt',
        features: ['Directory Brute Force', 'DNS Enumeration', 'Multiple Modes']
      }
    ]
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'ready': { label: 'Ready', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
      'coming-soon': { label: 'Coming Soon', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
      'maintenance': { label: 'Maintenance', className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' }
    };
    
    const config = statusConfig[status] || statusConfig['coming-soon'];
    return (
      <Badge className={`${config.className} text-xs font-medium`}>
        {config.label}
      </Badge>
    );
  };

  const handleRunTool = (toolName) => {
    if (toolName === 'Subfinder') {
      // This will be implemented in the next phase
      console.log('Running Subfinder...');
    }
  };

  const renderToolCard = (tool) => {
    const IconComponent = tool.icon;
    const isReady = tool.status === 'ready';
    
    return (
      <Card key={tool.name} className="glass hover:shadow-lg transition-all duration-300 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <IconComponent className="w-6 h-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">{tool.name}</CardTitle>
                <CardDescription className="mt-1">
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
              {tool.features.map((feature, index) => (
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
          
          <div className="flex items-center space-x-2">
            <Button 
              className="flex-1 btn-primary" 
              disabled={!isReady}
              onClick={() => handleRunTool(tool.name)}
            >
              <Play className="w-4 h-4 mr-2" />
              {isReady ? 'Run Tool' : 'Coming Soon'}
            </Button>
            <Button variant="outline" size="sm" disabled={!isReady}>
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Security Tools</h1>
          <p className="text-muted-foreground">
            Integrated penetration testing toolkit
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          placeholder="Search tools..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Tools by Category */}
      <Tabs defaultValue="reconnaissance" className="space-y-6">
        <TabsList className="grid grid-cols-3 w-full max-w-md">
          <TabsTrigger value="reconnaissance">Recon</TabsTrigger>
          <TabsTrigger value="scanning">Scanning</TabsTrigger>
          <TabsTrigger value="fuzzing">Fuzzing</TabsTrigger>
        </TabsList>

        <TabsContent value="reconnaissance" className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">Reconnaissance Tools</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Passive and active information gathering tools
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCategories.reconnaissance.map(renderToolCard)}
          </div>
        </TabsContent>

        <TabsContent value="scanning" className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">Scanning & Vulnerability Assessment</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Port scanning and vulnerability detection tools
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCategories.scanning.map(renderToolCard)}
          </div>
        </TabsContent>

        <TabsContent value="fuzzing" className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">Web Application Fuzzing</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Directory enumeration and content discovery tools
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCategories.fuzzing.map(renderToolCard)}
          </div>
        </TabsContent>
      </Tabs>

      {/* Coming Soon Notice */}
      <Card className="border-info/50 bg-info/5">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-info">
            <Activity className="w-5 h-5" />
            <span>Tool Integration Roadmap</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground mb-4">
            We're actively working on integrating more penetration testing tools. The Subfinder integration 
            is ready for testing, with more tools coming soon.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <h4 className="font-medium text-green-600 dark:text-green-400 mb-1">✅ Phase 1 (Current)</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Subfinder integration</li>
                <li>• Basic project management</li>
                <li>• Note-taking system</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-yellow-600 dark:text-yellow-400 mb-1">⏳ Phase 2 (Next)</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Nmap integration</li>
                <li>• Nuclei scanner</li>
                <li>• Result visualization</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-600 dark:text-blue-400 mb-1">🔮 Phase 3 (Future)</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• ffuf & Gobuster</li>
                <li>• Workflow automation</li>
                <li>• Custom scripts</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ToolsPage;