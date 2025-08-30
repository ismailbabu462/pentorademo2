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
  Activity
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { api } from '../App';
import { toast } from 'sonner';

const ProjectDetail = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddTargetDialog, setShowAddTargetDialog] = useState(false);
  const [targetForm, setTargetForm] = useState({
    target_type: 'domain',
    value: '',
    description: '',
    is_in_scope: true
  });

  useEffect(() => {
    if (projectId) {
      fetchProject();
      fetchTargets();
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await api.get(`/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to fetch project:', error);
      toast.error('Failed to load project');
    }
  };

  const fetchTargets = async () => {
    try {
      const response = await api.get(`/projects/${projectId}/targets`);
      setTargets(response.data);
    } catch (error) {
      console.error('Failed to fetch targets:', error);
      toast.error('Failed to load targets');
    } finally {
      setLoading(false);
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

  const getTargetIcon = (type) => {
    const icons = {
      domain: Globe,
      ip: Server,
      cidr: Server,
      url: LinkIcon
    };
    return icons[type] || Globe;
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
        <TabsList className="grid grid-cols-4 w-full max-w-md">
          <TabsTrigger value="targets">Targets</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
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

          {targets.length === 0 ? (
            <Card className="glass">
              <CardContent className="text-center py-12">
                <Target className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No targets defined</h3>
                <p className="text-muted-foreground mb-4">
                  Add domains, IPs, or URLs to define your testing scope
                </p>
                <Button className="btn-primary" onClick={() => setShowAddTargetDialog(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Target
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {targets.map((target) => {
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
          )}
        </TabsContent>

        <TabsContent value="notes">
          <Card className="glass">
            <CardContent className="text-center py-12">
              <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Notes Coming Soon</h3>
              <p className="text-muted-foreground">
                Rich text editor for project documentation
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tools">
          <Card className="glass">
            <CardContent className="text-center py-12">
              <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Tools Coming Soon</h3>
              <p className="text-muted-foreground">
                Integrated penetration testing tools
              </p>
            </CardContent>
          </Card>
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
    </div>
  );
};

export default ProjectDetail;