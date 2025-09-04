import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Plus, 
  Target, 
  Globe, 
  Server, 
  Link as LinkIcon,
  Trash2,
  Edit,
  Calendar,
  Users,
  Activity,
  Tag,
  Shield,
  AlertTriangle,
  Brain,
  Loader2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import api from '../lib/api';
import { toast } from 'sonner';

const ProjectDetail = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [targets, setTargets] = useState([]);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddTargetDialog, setShowAddTargetDialog] = useState(false);
  const [showCreateNoteDialog, setShowCreateNoteDialog] = useState(false);
  const [showNotePreviewDialog, setShowNotePreviewDialog] = useState(false);
  const [selectedNote, setSelectedNote] = useState(null);
  const [showAddVulnDialog, setShowAddVulnDialog] = useState(false);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [toolOutputs, setToolOutputs] = useState([]);
  const [targetForm, setTargetForm] = useState({
    target_type: 'domain',
    value: '',
    description: '',
    is_in_scope: true
  });
  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    tags: ''
  });
  const [vulnForm, setVulnForm] = useState({
    title: '',
    payload: '',
    how_it_works: '',
    severity: 'medium'
  });
  const [analyzingVulns, setAnalyzingVulns] = useState(new Set());

  useEffect(() => {
    if (projectId) {
      fetchProject();
      fetchTargets();
      fetchNotes();
      fetchVulnerabilities();
      fetchToolOutputs();
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      console.log('Fetching project:', projectId);
      
      // Try to fetch from API first
      try {
        const response = await api.get(`/projects/${projectId}`);
        setProject(response.data);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // If API is not available, create mock data for development
      const mockProject = {
        id: parseInt(projectId),
        name: `Project ${projectId}`,
        description: 'Mock project for development purposes',
        status: 'active',
        start_date: '2024-01-15',
        end_date: '2024-02-15',
        team_members: ['john@example.com', 'jane@example.com'],
        created_at: '2024-01-10',
        updated_at: '2024-01-20'
      };
      
      setProject(mockProject);
      toast.info('Using mock data - Backend not available');
      
    } catch (error) {
      console.error('Failed to fetch project:', error);
      toast.error('Failed to load project');
    }
  };

  const fetchTargets = async () => {
    try {
      console.log('Fetching targets for project:', projectId);
      
      // Try to fetch from API first
      try {
        const response = await api.get(`/projects/${projectId}/targets`);
        setTargets(response.data);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // If API is not available, create mock data for development
      const mockTargets = [
        {
          id: 1,
          target_type: 'domain',
          value: 'example.com',
          description: 'Main website domain',
          is_in_scope: true
        },
        {
          id: 2,
          target_type: 'ip',
          value: '192.168.1.100',
          description: 'Internal server',
          is_in_scope: true
        },
        {
          id: 3,
          target_type: 'url',
          value: 'https://api.example.com',
          description: 'API endpoint',
          is_in_scope: false
        }
      ];
      
      setTargets(mockTargets);
      toast.info('Using mock data - Backend not available');
      
    } catch (error) {
      console.error('Failed to fetch targets:', error);
      toast.error('Failed to load targets');
      setTargets([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotes = async () => {
    try {
      console.log('Fetching notes for project:', projectId);
      
      // Try to fetch from API first
      try {
        const response = await api.get(`/projects/${projectId}/notes`);
        setNotes(response.data);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // If API is not available, create mock data for development
      const mockNotes = [
        {
          id: 1,
          title: 'SQL Injection in Login Form',
          content: 'Found SQL injection vulnerability in the login form. The application is vulnerable to boolean-based blind SQL injection.',
          tags: ['sql-injection', 'web', 'critical'],
          created_at: '2024-01-20T10:30:00Z',
          updated_at: '2024-01-20T10:30:00Z'
        },
        {
          id: 2,
          title: 'XSS in Search Function',
          content: 'Reflected XSS vulnerability found in the search functionality. User input is not properly sanitized.',
          tags: ['xss', 'web', 'medium'],
          created_at: '2024-01-21T14:15:00Z',
          updated_at: '2024-01-21T14:15:00Z'
        }
      ];
      
      setNotes(mockNotes);
      toast.info('Using mock data - Backend not available');
      
    } catch (error) {
      console.error('Failed to fetch notes:', error);
      toast.error('Failed to load notes');
      setNotes([]);
    }
  };

  const handleAddTarget = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/projects/${projectId}/targets`, targetForm);
      toast.success('Target added successfully');
      setShowAddTargetDialog(false);
      setTargetForm({
        target_type: 'domain',
        value: '',
        description: '',
        is_in_scope: true
      });
      fetchTargets();
      fetchProject(); // Refresh project to update target count
    } catch (error) {
      console.error('Failed to add target:', error);
      toast.error('Failed to add target');
    }
  };

  const handleDeleteTarget = async (targetId) => {
    try {
      await api.delete(`/projects/${projectId}/targets/${targetId}`);
      toast.success('Target removed successfully');
      fetchTargets();
      fetchProject();
    } catch (error) {
      console.error('Failed to remove target:', error);
      toast.error('Failed to remove target');
    }
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    try {
      const noteData = {
        ...noteForm,
        project_id: projectId,
        tags: noteForm.tags ? noteForm.tags.split(',').map(t => t.trim()) : []
      };
      
      await api.post('/notes', noteData);
      toast.success('Note created successfully');
      setShowCreateNoteDialog(false);
      setNoteForm({
        title: '',
        content: '',
        tags: ''
      });
      fetchNotes();
    } catch (error) {
      console.error('Failed to create note:', error);
      toast.error('Failed to create note');
    }
  };

  const fetchVulnerabilities = async () => {
    try {
      console.log('Fetching vulnerabilities for project:', projectId);
      
      // Try to fetch from API first
      try {
        const response = await api.get(`/projects/${projectId}/vulnerabilities`);
        setVulnerabilities(response.data);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // If API is not available, create mock data for development
      const mockVulns = [
        {
          id: 1,
          title: 'SQL Injection in Login Form',
          payload: "' OR '1'='1",
          how_it_works: 'The application does not properly sanitize user input in the login form, allowing SQL injection attacks.',
          severity: 'critical',
          created_at: '2024-01-20T10:30:00Z'
        },
        {
          id: 2,
          title: 'XSS in Search Parameter',
          payload: '<script>alert("XSS")</script>',
          how_it_works: 'The search functionality reflects user input without proper encoding, leading to stored XSS.',
          severity: 'high',
          created_at: '2024-01-19T14:20:00Z'
        }
      ];
      
      setVulnerabilities(mockVulns);
      toast.info('Using mock data - Backend not available');
      
    } catch (error) {
      console.error('Failed to fetch vulnerabilities:', error);
      toast.error('Failed to load vulnerabilities');
    }
  };

  const fetchToolOutputs = async () => {
    try {
      console.log('Fetching tool outputs for project:', projectId);
      
      // Fetch tool outputs from API
      const response = await api.get(`/tools/outputs?project_id=${projectId}`);
      setToolOutputs(response.data.outputs || []);
      console.log('Tool outputs fetched:', response.data.outputs);
      
    } catch (error) {
      console.error('Failed to fetch tool outputs:', error);
      // Don't show error toast for missing tool outputs, it's optional
      setToolOutputs([]);
    }
  };

  const handleCreateVulnerability = async (e) => {
    e.preventDefault();
    try {
      // SECURITY: Validate and sanitize inputs
      validateInput(vulnForm.title, 'Title', 200);
      validateInput(vulnForm.payload, 'Payload', 5000);
      validateInput(vulnForm.how_it_works, 'Description', 10000);
      
      // Validate severity
      const validSeverities = ['critical', 'high', 'medium', 'low'];
      if (!validSeverities.includes(vulnForm.severity)) {
        throw new Error('Invalid severity level');
      }
      
      // SECURITY: Sanitize inputs before sending
      const sanitizedVulnData = {
        title: sanitizeInput(vulnForm.title),
        payload: vulnForm.payload, // Keep payload as-is for security research
        how_it_works: sanitizeInput(vulnForm.how_it_works),
        severity: vulnForm.severity,
        project_id: projectId
      };
      
      await api.post(`/projects/${projectId}/vulnerabilities`, sanitizedVulnData);
      toast.success('Vulnerability added successfully');
      setShowAddVulnDialog(false);
      setVulnForm({
        title: '',
        payload: '',
        how_it_works: '',
        severity: 'medium'
      });
      fetchVulnerabilities();
    } catch (error) {
      console.error('Failed to create vulnerability:', error);
      if (error.message) {
        toast.error(error.message);
      } else {
        toast.error('Failed to create vulnerability');
      }
    }
  };

  const getTargetIcon = (type) => {
    const icons = {
      domain: Globe,
      ip: Server,
      cidr: Server,
      url: LinkIcon
    };
    return icons[type] || Globe;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[severity] || colors.medium;
  };

  // AI Analysis Functions
  const startAIAnalysis = async (vulnerabilityId) => {
    try {
      setAnalyzingVulns(prev => new Set([...prev, vulnerabilityId]));
      
      const response = await api.post(`/vulnerabilities/${vulnerabilityId}/analyze`);
      
      if (response.data.message) {
        toast.success('AI analysis started! Results will appear shortly.');
        
        // Start polling for results
        pollForAnalysisResults(vulnerabilityId);
      }
    } catch (error) {
      console.error('Failed to start AI analysis:', error);
      toast.error('Failed to start AI analysis');
      setAnalyzingVulns(prev => {
        const newSet = new Set(prev);
        newSet.delete(vulnerabilityId);
        return newSet;
      });
    }
  };

  const pollForAnalysisResults = (vulnerabilityId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/vulnerabilities/${vulnerabilityId}`);
        
        if (response.data.ai_analysis) {
          // Analysis completed
          clearInterval(pollInterval);
          setAnalyzingVulns(prev => {
            const newSet = new Set(prev);
            newSet.delete(vulnerabilityId);
            return newSet;
          });
          
          // Update vulnerabilities state
          setVulnerabilities(prev => 
            prev.map(vuln => 
              vuln.id === vulnerabilityId 
                ? { ...vuln, ai_analysis: response.data.ai_analysis }
                : vuln
            )
          );
          
          toast.success('AI analysis completed!');
        }
      } catch (error) {
        console.error('Failed to poll analysis results:', error);
        clearInterval(pollInterval);
        setAnalyzingVulns(prev => {
          const newSet = new Set(prev);
          newSet.delete(vulnerabilityId);
          return newSet;
        });
      }
    }, 3000); // Poll every 3 seconds

    // Stop polling after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      setAnalyzingVulns(prev => {
        const newSet = new Set(prev);
        newSet.delete(vulnerabilityId);
        return newSet;
      });
    }, 300000);
  };

  // SECURITY: Input sanitization functions
  const sanitizeInput = (input) => {
    if (!input) return '';
    
    // Remove potentially dangerous characters and patterns
    return input
      .replace(/[<>"']/g, '') // Remove dangerous characters
      .replace(/javascript:/gi, '') // Remove javascript protocol
      .replace(/on\w+\s*=/gi, '') // Remove event handlers
      .replace(/data:text\/html/gi, '') // Remove data URLs
      .replace(/vbscript:/gi, '') // Remove vbscript
      .replace(/expression\s*\(/gi, '') // Remove CSS expressions
      .trim();
  };

  const validateInput = (input, fieldName, maxLength = 1000) => {
    if (!input || !input.trim()) {
      throw new Error(`${fieldName} cannot be empty`);
    }
    
    if (input.length > maxLength) {
      throw new Error(`${fieldName} is too long (max ${maxLength} characters)`);
    }
    
    // Check for XSS patterns
    const dangerousPatterns = [
      /<script[^>]*>/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /data:text\/html/i,
      /vbscript:/i,
      /expression\s*\(/i
    ];
    
    for (const pattern of dangerousPatterns) {
      if (pattern.test(input)) {
        throw new Error(`${fieldName} contains potentially dangerous content`);
      }
    }
    
    return true;
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      active: 'status-active',
      completed: 'status-completed',
      paused: 'status-paused',
      planning: 'status-planning'
    };
    return (
      <Badge className={`${statusClasses[status]} text-xs font-medium`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatNoteDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-foreground mb-2">Project not found</h3>
          <Link to="/projects">
            <Button variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Projects
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/projects">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-foreground">{project.name}</h1>
              {getStatusBadge(project.status)}
            </div>
            <p className="text-muted-foreground mt-1">
              {project.description || 'No description provided'}
            </p>
          </div>
        </div>
        <Button variant="outline">
          <Edit className="w-4 h-4 mr-2" />
          Edit Project
        </Button>
      </div>

      {/* Project Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Start Date</p>
                <p className="text-xs text-muted-foreground">{formatDate(project.start_date)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">End Date</p>
                <p className="text-xs text-muted-foreground">{formatDate(project.end_date)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Targets</p>
                <p className="text-xs text-muted-foreground">{targets.length} total</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Team</p>
                <p className="text-xs text-muted-foreground">{project.team_members?.length || 0} members</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="targets" className="space-y-4">
        <TabsList className="grid grid-cols-5 w-full max-w-lg">
          <TabsTrigger value="targets">Targets</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
          <TabsTrigger value="vulnerabilities">Vulnerabilities</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="targets" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">Target Management</h3>
              <p className="text-sm text-muted-foreground">
                Define the scope of your penetration test
              </p>
            </div>
            <Button className="btn-primary" onClick={() => setShowAddTargetDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Target
            </Button>
          </div>

          {!targets || targets.length === 0 ? (
            <Card className="glass">
              <CardContent className="text-center py-12">
                <Target className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No targets defined</h3>
                <p className="text-muted-foreground mb-4">
                  Add domains, IPs, or URLs to define your testing scope
                </p>
                {targets && (
                  <Button className="btn-primary" onClick={() => setShowAddTargetDialog(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add First Target
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            targets && (
              <div className="grid grid-cols-1 gap-4">
                {targets?.map((target) => {
                  const TargetIcon = getTargetIcon(target.target_type);
                  return (
                    <Card key={target.id} className="glass hover:shadow-lg transition-all duration-300 group">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                              <TargetIcon className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="flex items-center space-x-2">
                                <h4 className="font-medium font-mono">{target.value}</h4>
                                <Badge variant={target.is_in_scope ? "default" : "destructive"} className="text-xs">
                                  {target.is_in_scope ? 'In Scope' : 'Out of Scope'}
                                </Badge>
                                <Badge variant="outline" className="text-xs">
                                  {target.target_type.toUpperCase()}
                                </Badge>
                              </div>
                              {target.description && (
                                <p className="text-sm text-muted-foreground mt-1">
                                  {target.description}
                                </p>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive"
                            onClick={() => handleDeleteTarget(target.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )
          )}
        </TabsContent>

        <TabsContent value="notes" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">Project Notes</h3>
              <p className="text-sm text-muted-foreground">
                Document findings, observations, and methodologies for this project
              </p>
            </div>
            <Button className="btn-primary" onClick={() => setShowCreateNoteDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Note
            </Button>
          </div>

          {!notes || notes.length === 0 ? (
            <Card className="glass">
              <CardContent className="text-center py-12">
                <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No notes yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start documenting your penetration testing findings and observations
                </p>
                <Button className="btn-primary" onClick={() => setShowCreateNoteDialog(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Note
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {notes.map((note) => (
                <Card 
                  key={note.id} 
                  className="glass hover:shadow-lg transition-all duration-300 group cursor-pointer" 
                  onClick={() => {
                    setSelectedNote(note);
                    setShowNotePreviewDialog(true);
                  }}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg line-clamp-2">{note.title}</CardTitle>
                    <CardDescription className="text-xs">
                      {formatNoteDate(note.created_at)}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-3">
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {note.content}
                    </p>
                    
                    {note.tags?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {note.tags.slice(0, 3).map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {note.tags.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{note.tags.length - 3} more
                          </Badge>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="vulnerabilities" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">Vulnerability Management</h3>
              <p className="text-sm text-muted-foreground">
                Document and track security vulnerabilities found during testing
              </p>
            </div>
            <Button 
              className="btn-primary bg-red-600 hover:bg-red-700 border-red-600 hover:border-red-700" 
              onClick={() => setShowAddVulnDialog(true)}
            >
              <Shield className="w-4 h-4 mr-2" />
              Add Vulnerability
            </Button>
          </div>

          {!vulnerabilities || vulnerabilities.length === 0 ? (
            <Card className="glass">
              <CardContent className="text-center py-12">
                <AlertTriangle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No vulnerabilities documented yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start documenting security vulnerabilities found during your penetration testing
                </p>
                <Button 
                  className="btn-primary bg-red-600 hover:bg-red-700 border-red-600 hover:border-red-700" 
                  onClick={() => setShowAddVulnDialog(true)}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Add First Vulnerability
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {vulnerabilities.map((vuln) => (
                <Card 
                  key={vuln.id} 
                  className="glass hover:shadow-lg transition-all duration-300 border-l-4 border-l-red-500"
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-2">{vuln.title}</CardTitle>
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getSeverityColor(vuln.severity)} border`}>
                            {vuln.severity.toUpperCase()}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(vuln.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {!vuln.ai_analysis && !analyzingVulns.has(vuln.id) && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => startAIAnalysis(vuln.id)}
                            className="flex items-center space-x-1"
                          >
                            <Brain className="h-4 w-4" />
                            <span>Analyze with AI</span>
                          </Button>
                        )}
                        {analyzingVulns.has(vuln.id) && (
                          <div className="flex items-center space-x-2 text-blue-600">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">AI is thinking...</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm mb-2 text-red-600">Payload:</h4>
                      <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg font-mono text-sm">
                        {/* SECURITY: Escape HTML to prevent XSS */}
                        {vuln.payload.replace(/[<>]/g, (match) => {
                          return match === '<' ? '&lt;' : '&gt;';
                        })}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm mb-2 text-blue-600">How it works:</h4>
                      <p className="text-sm text-muted-foreground">
                        {vuln.how_it_works}
                      </p>
                    </div>

                    {/* AI Analysis Results */}
                    {vuln.ai_analysis && (
                      <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="flex items-center space-x-2 mb-3">
                          <Brain className="h-5 w-5 text-blue-600" />
                          <h4 className="font-medium text-blue-800 dark:text-blue-200">AI Analysis</h4>
                        </div>
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <ReactMarkdown>{vuln.ai_analysis}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="tools" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">Tool Outputs</h3>
              <p className="text-muted-foreground text-sm">Scan results and tool outputs for this project</p>
            </div>
            <Badge variant="outline" className="text-sm">
              {toolOutputs.length} outputs
            </Badge>
          </div>

          {toolOutputs.length > 0 ? (
            <div className="grid grid-cols-1 gap-4">
              {toolOutputs.map((output) => (
                <Card key={output.id} className="glass hover:shadow-lg transition-all duration-300 group">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                          <Activity className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium">{output.tool_name}</h4>
                            <Badge variant={output.status === 'completed' ? 'default' : 'secondary'} className="text-xs">
                              {output.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{output.target}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(output.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-4">
                      <pre className="text-xs font-mono whitespace-pre-wrap text-foreground overflow-x-auto max-h-32 overflow-y-auto">
                        {output.output.length > 500 
                          ? output.output.substring(0, 500) + '... [truncated]' 
                          : output.output
                        }
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="glass">
              <CardContent className="text-center py-12">
                <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h4 className="text-lg font-medium mb-2">No Tool Outputs</h4>
                <p className="text-muted-foreground">
                  No scan results have been imported to this project yet. Run scans from the Tools page and use "Projeye Aktar" to import them here.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="results">
          <Card className="glass">
            <CardContent className="text-center py-12">
              <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Results Coming Soon</h3>
              <p className="text-muted-foreground">
                Scan results and vulnerability reports
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add Target Dialog */}
      <Dialog open={showAddTargetDialog} onOpenChange={setShowAddTargetDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add Target</DialogTitle>
            <DialogDescription>
              Add a new target to your project scope
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleAddTarget} className="space-y-4">
            <div>
              <Label htmlFor="target_type">Target Type</Label>
              <Select 
                value={targetForm.target_type} 
                onValueChange={(value) => setTargetForm({...targetForm, target_type: value})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="domain">Domain</SelectItem>
                  <SelectItem value="ip">IP Address</SelectItem>
                  <SelectItem value="cidr">CIDR Range</SelectItem>
                  <SelectItem value="url">URL</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="value">Target Value *</Label>
              <Input
                id="value"
                value={targetForm.value}
                onChange={(e) => setTargetForm({...targetForm, value: e.target.value})}
                placeholder="e.g., example.com, 192.168.1.1, 10.0.0.0/24"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={targetForm.description}
                onChange={(e) => setTargetForm({...targetForm, description: e.target.value})}
                placeholder="Optional description or notes"
              />
            </div>
            
            <div>
              <Label htmlFor="scope">Scope</Label>
              <Select 
                value={targetForm.is_in_scope.toString()} 
                onValueChange={(value) => setTargetForm({...targetForm, is_in_scope: value === 'true'})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">In Scope</SelectItem>
                  <SelectItem value="false">Out of Scope</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowAddTargetDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" className="btn-primary">
                Add Target
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Create Note Dialog */}
      <Dialog open={showCreateNoteDialog} onOpenChange={setShowCreateNoteDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Note</DialogTitle>
            <DialogDescription>
              Document findings, observations, or methodologies for this project
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleCreateNote} className="space-y-4">
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={noteForm.title}
                onChange={(e) => setNoteForm({...noteForm, title: e.target.value})}
                placeholder="e.g., SQL Injection in Login Form"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="content">Content *</Label>
              <Textarea
                id="content"
                value={noteForm.content}
                onChange={(e) => setNoteForm({...noteForm, content: e.target.value})}
                placeholder="Document your findings, steps, and observations..."
                rows={10}
                required
                className="min-h-[200px]"
              />
            </div>
            
            <div>
              <Label htmlFor="tags">Tags</Label>
              <Input
                id="tags"
                value={noteForm.tags}
                onChange={(e) => setNoteForm({...noteForm, tags: e.target.value})}
                placeholder="vulnerability, web, database (comma-separated)"
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateNoteDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" className="btn-primary">
                Create Note
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Note Preview Dialog */}
      <Dialog open={showNotePreviewDialog} onOpenChange={setShowNotePreviewDialog}>
        <DialogContent className="sm:max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">{selectedNote?.title}</DialogTitle>
            <DialogDescription>
              {project?.name} • {selectedNote && formatNoteDate(selectedNote.created_at)}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {selectedNote?.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {selectedNote.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-sm">
                    <Tag className="w-3 h-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
            
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {selectedNote?.content}
              </div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-muted-foreground pt-4 border-t">
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>Created: {selectedNote && formatNoteDate(selectedNote.created_at)}</span>
              </div>
              {selectedNote?.updated_at !== selectedNote?.created_at && (
                <span>Updated: {selectedNote && formatNoteDate(selectedNote.updated_at)}</span>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNotePreviewDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Vulnerability Dialog */}
      <Dialog open={showAddVulnDialog} onOpenChange={setShowAddVulnDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-red-600" />
              <span>Add Vulnerability</span>
            </DialogTitle>
            <DialogDescription>
              Document a security vulnerability found during penetration testing
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleCreateVulnerability} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="vuln-title">Vulnerability Title</Label>
              <Input
                id="vuln-title"
                placeholder="e.g., SQL Injection in Login Form"
                value={vulnForm.title}
                onChange={(e) => {
                  // SECURITY: Real-time sanitization
                  const sanitized = sanitizeInput(e.target.value);
                  setVulnForm({...vulnForm, title: sanitized});
                }}
                maxLength={200}
                required
              />
              <p className="text-xs text-muted-foreground">
                {vulnForm.title.length}/200 characters
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="vuln-payload">Payload</Label>
              <Textarea
                id="vuln-payload"
                placeholder="Enter the payload or exploit code used..."
                value={vulnForm.payload}
                onChange={(e) => setVulnForm({...vulnForm, payload: e.target.value})}
                className="font-mono text-sm"
                rows={3}
                maxLength={5000}
                required
              />
              <p className="text-xs text-muted-foreground">
                {vulnForm.payload.length}/5000 characters
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="vuln-how-it-works">How it works</Label>
              <Textarea
                id="vuln-how-it-works"
                placeholder="Explain how this vulnerability works and its impact..."
                value={vulnForm.how_it_works}
                onChange={(e) => {
                  // SECURITY: Real-time sanitization
                  const sanitized = sanitizeInput(e.target.value);
                  setVulnForm({...vulnForm, how_it_works: sanitized});
                }}
                rows={4}
                maxLength={10000}
                required
              />
              <p className="text-xs text-muted-foreground">
                {vulnForm.how_it_works.length}/10000 characters
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="vuln-severity">Vulnerability Type</Label>
              <Select 
                value={vulnForm.severity} 
                onValueChange={(value) => setVulnForm({...vulnForm, severity: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select severity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <span>Critical</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="high">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                      <span>High</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="medium">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span>Medium</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="low">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span>Low</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowAddVulnDialog(false)}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                className="bg-red-600 hover:bg-red-700 border-red-600 hover:border-red-700"
              >
                <Shield className="w-4 h-4 mr-2" />
                Add Vulnerability
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProjectDetail;