import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal,
  Calendar,
  Target,
  Users,
  Edit,
  Trash2,
  Activity,
  Eye,
  Download
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import api from '../lib/api';
import { toast } from 'sonner';

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [toolOutputs, setToolOutputs] = useState({});
  const [showToolOutputs, setShowToolOutputs] = useState({});
  const [refreshingOutputs, setRefreshingOutputs] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'planning',
    start_date: '',
    end_date: '',
    team_members: ''
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      console.log('Fetching projects...');
      const response = await api.get('/projects');
      console.log('Projects response:', response.data);
      setProjects(response.data || []);
      
      // Fetch tool outputs for each project
      const projectsData = response.data || [];
      console.log('🔍 ProjectsPage: Fetching tool outputs for', projectsData.length, 'projects');
      const outputsData = {};
      for (const project of projectsData) {
        try {
          console.log(`🔍 ProjectsPage: Fetching outputs for project ${project.id} (${project.name})`);
          const outputsResponse = await api.get(`/tools/outputs?project_id=${project.id}`);
          console.log(`🔍 ProjectsPage: Outputs for project ${project.id}:`, outputsResponse.outputs?.length || 0);
          outputsData[project.id] = outputsResponse.outputs || [];
        } catch (error) {
          console.error(`❌ ProjectsPage: Failed to fetch tool outputs for project ${project.id}:`, error);
          outputsData[project.id] = [];
        }
      }
      console.log('🔍 ProjectsPage: Final outputs data:', outputsData);
      setToolOutputs(outputsData);
    } catch (error) {
      console.error('❌ ProjectsPage: Failed to fetch projects:', error);
      
      // If API is not available, create mock data for development
      if (error.code === 'ERR_NETWORK' || error.response?.status === 404) {
        console.log('Creating mock projects data...');
        const mockProjects = [
          {
            id: 1,
            name: 'ACME Corp Security Assessment',
            description: 'Comprehensive penetration testing for ACME Corporation',
            status: 'active',
            start_date: '2024-01-15',
            end_date: '2024-02-15',
            team_members: ['john@example.com', 'jane@example.com'],
            targets: ['acme.com', 'api.acme.com'],
            created_at: '2024-01-10',
            updated_at: '2024-01-20'
          },
          {
            id: 2,
            name: 'TechStart Web App Test',
            description: 'Web application security testing for TechStart',
            status: 'planning',
            start_date: '2024-02-01',
            end_date: '2024-03-01',
            team_members: ['john@example.com'],
            targets: ['techstart.io'],
            created_at: '2024-01-25',
            updated_at: '2024-01-25'
          }
        ];
        setProjects(mockProjects);
        setToolOutputs({}); // Mock data için boş tool outputs
        toast.info('Using mock data - Backend not available');
      } else {
        toast.error('Failed to load projects');
        setProjects([]);
        setToolOutputs({});
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      const projectData = {
        ...formData,
        team_members: formData.team_members ? formData.team_members.split(',').map(m => m.trim()) : [],
        start_date: formData.start_date || null,
        end_date: formData.end_date || null
      };
      
      await api.post('/projects', projectData);
      toast.success('Project created successfully');
      setShowCreateDialog(false);
      resetForm();
      fetchProjects();
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project');
    }
  };

  const handleDeleteProject = async () => {
    if (!selectedProject) return;
    
    try {
      await api.delete(`/projects/${selectedProject.id}`);
      toast.success('Project deleted successfully');
      setShowDeleteDialog(false);
      setSelectedProject(null);
      fetchProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      toast.error('Failed to delete project');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      status: 'planning',
      start_date: '',
      end_date: '',
      team_members: ''
    });
  };

  // Refresh tool outputs for all projects
  const refreshToolOutputs = async () => {
    if (projects.length === 0) return;
    
    setRefreshingOutputs(true);
    try {
      console.log('🔄 ProjectsPage: Refreshing tool outputs...');
      const outputsData = {};
      for (const project of projects) {
        try {
          console.log(`🔄 ProjectsPage: Refreshing outputs for project ${project.id} (${project.name})`);
          const outputsResponse = await api.get(`/tools/outputs?project_id=${project.id}`);
          console.log(`🔄 ProjectsPage: Outputs for project ${project.id}:`, outputsResponse.outputs?.length || 0);
          outputsData[project.id] = outputsResponse.outputs || [];
        } catch (error) {
          console.error(`❌ ProjectsPage: Failed to refresh tool outputs for project ${project.id}:`, error);
          outputsData[project.id] = [];
        }
      }
      console.log('🔄 ProjectsPage: Refreshed outputs data:', outputsData);
      setToolOutputs(outputsData);
      toast.success('Tool outputs refreshed');
    } catch (error) {
      console.error('❌ ProjectsPage: Failed to refresh tool outputs:', error);
      toast.error('Failed to refresh tool outputs');
    } finally {
      setRefreshingOutputs(false);
    }
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
      month: 'short',
      day: 'numeric'
    });
  };

  const filteredProjects = projects?.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (project.description && project.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Projects</h1>
          <p className="text-muted-foreground">
            Manage your penetration testing projects
          </p>
        </div>
        <div className="flex space-x-3">
          <Button
            onClick={refreshToolOutputs}
            disabled={refreshingOutputs || projects.length === 0}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Activity className="w-4 h-4" />
            <span>{refreshingOutputs ? 'Refreshing...' : 'Refresh Tools'}</span>
          </Button>
          <Button 
            className="btn-primary" 
            onClick={() => setShowCreateDialog(true)}
            disabled={!projects}
          >
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </div>
      </div>

      {/* Filters */}
      {projects && (
        <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="planning">Planning</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
        </div>
      )}

      {/* Projects Grid */}
      {projects && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects?.map((project) => (
          <Card key={project.id} className="glass hover:shadow-lg transition-all duration-300 group">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <span className="truncate">{project.name}</span>
                    {getStatusBadge(project.status)}
                  </CardTitle>
                  <CardDescription className="mt-1">
                    {project.description || 'No description provided'}
                  </CardDescription>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link to={`/projects/${project.id}`}>
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      className="text-destructive"
                      onClick={() => {
                        setSelectedProject(project);
                        setShowDeleteDialog(true);
                      }}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="flex items-center text-muted-foreground mb-1">
                    <Calendar className="w-3 h-3 mr-1" />
                    <span>Start Date</span>
                  </div>
                  <p className="font-medium">{formatDate(project.start_date)}</p>
                </div>
                <div>
                  <div className="flex items-center text-muted-foreground mb-1">
                    <Calendar className="w-3 h-3 mr-1" />
                    <span>End Date</span>
                  </div>
                  <p className="font-medium">{formatDate(project.end_date)}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center text-muted-foreground">
                  <Target className="w-3 h-3 mr-1" />
                  <span>{project.targets?.length || 0} targets</span>
                </div>
                <div className="flex items-center text-muted-foreground">
                  <Users className="w-3 h-3 mr-1" />
                  <span>{project.team_members?.length || 0} members</span>
                </div>
              </div>
              
              {/* Tool Outputs Section */}
              {toolOutputs[project.id] && toolOutputs[project.id].length > 0 && (
                <div className="border-t pt-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center text-muted-foreground">
                      <Activity className="w-3 h-3 mr-1" />
                      <span className="text-xs font-medium">Scan Results</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowToolOutputs(prev => ({
                        ...prev,
                        [project.id]: !prev[project.id]
                      }))}
                      className="text-xs h-6 px-2"
                    >
                      {showToolOutputs[project.id] ? 'Hide' : 'Show'} ({toolOutputs[project.id].length})
                    </Button>
                  </div>
                  
                  {showToolOutputs[project.id] && (
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {toolOutputs[project.id].slice(0, 3).map((output) => (
                        <div key={output.id} className="bg-muted/50 rounded p-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{output.tool_name}</span>
                            <span className="text-muted-foreground">
                              {new Date(output.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="text-muted-foreground truncate">
                            Target: {output.target}
                          </div>
                        </div>
                      ))}
                      {toolOutputs[project.id].length > 3 && (
                        <div className="text-xs text-muted-foreground text-center">
                          +{toolOutputs[project.id].length - 3} more scans
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              <Link to={`/projects/${project.id}`} className="block">
                <Button variant="outline" className="w-full mt-3">
                  View Project →
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
        </div>
      )}

      {/* Empty State */}
      {(!projects || !filteredProjects || filteredProjects.length === 0) && !loading && (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
            <Target className="w-12 h-12 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium text-foreground mb-2">
            {searchTerm || statusFilter !== 'all' ? 'No projects found' : 'No projects yet'}
          </h3>
          <p className="text-muted-foreground mb-4">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Create your first penetration testing project to get started'
            }
          </p>
          {!searchTerm && statusFilter === 'all' && projects && (
            <Button className="btn-primary" onClick={() => setShowCreateDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create First Project
            </Button>
          )}
        </div>
      )}

      {/* Create Project Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
            <DialogDescription>
              Set up a new penetration testing project
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleCreateProject} className="space-y-4">
            <div>
              <Label htmlFor="name">Project Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g., ACME Corp Security Assessment"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Brief description of the project scope..."
                rows={3}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="team_members">Team Members</Label>
              <Input
                id="team_members"
                value={formData.team_members}
                onChange={(e) => setFormData({...formData, team_members: e.target.value})}
                placeholder="john@example.com, jane@example.com"
              />
            </div>
            
            <div>
              <Label htmlFor="status">Initial Status</Label>
              <Select value={formData.status} onValueChange={(value) => setFormData({...formData, status: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="planning">Planning</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" className="btn-primary">
                Create Project
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Project</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{selectedProject?.name}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteProject}>
              Delete Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProjectsPage;