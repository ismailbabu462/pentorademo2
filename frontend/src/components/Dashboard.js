import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Activity, 
  FolderOpen, 
  StickyNote, 
  Users, 
  Target,
  TrendingUp,
  Calendar,
  Clock,
  KeyRound
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import api from '../lib/api';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Input } from './ui/input';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { fetchUserData, forceRefreshUserData } = useAuth();
  const [stats, setStats] = useState({
    total_projects: 0,
    active_projects: 0,
    total_notes: 0,
    recent_projects: []
  });
  const [loading, setLoading] = useState(true);
  const [keyDialogOpen, setKeyDialogOpen] = useState(false);
  const [licenseKey, setLicenseKey] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      console.log('Fetching dashboard data...');
      
      // Try to fetch from API first
      try {
        const response = await api.get('/dashboard/stats');
        setStats(response.data);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // If API is not available, create mock data for development
      const mockStats = {
        total_projects: 2,
        active_projects: 1,
        total_notes: 3,
        recent_projects: [
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
        ]
      };
      
      setStats(mockStats);
      toast.info('Using mock data - Backend not available');
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard data');
      
      // Set default stats on error
      setStats({
        total_projects: 0,
        active_projects: 0,
        total_notes: 0,
        recent_projects: []
      });
    } finally {
      setLoading(false);
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
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to Emergent Pentest Suite - Your offensive security command center
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select 
            className="px-3 py-2 border rounded-md bg-background text-foreground"
            onChange={async (e) => {
              const tier = e.target.value;
              if (tier) {
                try {
                  const res = await api.post(`/keys/create-test-key?tier=${tier}`);
                  toast.success(`${tier.toUpperCase()} test key created: ${res.data.key}`);
                } catch (err) {
                  toast.error('Failed to create test key');
                }
                e.target.value = ''; // Reset selection
              }
            }}
          >
            <option value="">Create Test Key</option>
            <option value="professional">Professional</option>
            <option value="teams">Teams</option>
            <option value="enterprise">Enterprise</option>
            <option value="elite">Elite</option>
          </select>
          <Dialog open={keyDialogOpen} onOpenChange={setKeyDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <KeyRound className="w-4 h-4 mr-2" />
                Key Activation
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Activate Your Membership</DialogTitle>
                <DialogDescription>
                  Please enter your license key to upgrade your plan.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-2">
                <Input
                  placeholder="Enter your 50-digit key here..."
                  value={licenseKey}
                  onChange={(e) => setLicenseKey(e.target.value)}
                />
              </div>
              <DialogFooter>
                <Button
                  onClick={async (e) => {
                    const key = licenseKey.trim();
                    if (!key) {
                      toast.error('Please enter your license key');
                      return;
                    }
                    try {
                      const res = await api.post('/keys/activate', { key });
                      const tier = res.data?.tier || 'professional';
                      const newToken = res.data?.token;
                      
                      // Update JWT token if provided
                      if (newToken) {
                        localStorage.setItem('authToken', newToken);
                      }
                      
                      toast.success(`${tier} membership has been activated successfully!`);
                      setKeyDialogOpen(false);
                      setLicenseKey('');
                      // Force refresh user data to update tier
                      await forceRefreshUserData();
                    } catch (err) {
                      const message = err?.response?.data?.detail || 'Activation failed';
                      toast.error(message);
                    }
                  }}
                >
                  Activate
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Link to="/projects">
            <Button className="btn-primary">
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <FolderOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{stats.total_projects}</div>
            <p className="text-xs text-muted-foreground">
              All pentest projects
            </p>
          </CardContent>
        </Card>

        <Card className="glass hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
                            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">{stats.active_projects}</div>
            <p className="text-xs text-muted-foreground">
              Currently in progress
            </p>
          </CardContent>
        </Card>

        <Card className="glass hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Notes</CardTitle>
            <StickyNote className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
                            <div className="text-2xl font-bold text-gray-700 dark:text-gray-300">{stats.total_notes}</div>
            <p className="text-xs text-muted-foreground">
              Documentation entries
            </p>
          </CardContent>
        </Card>

        <Card className="glass hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
                            <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">87%</div>
            <p className="text-xs text-muted-foreground">
              Overall completion
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Projects */}
        <Card className="lg:col-span-2 glass">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="w-5 h-5" />
                <span>Recent Projects</span>
              </CardTitle>
              <CardDescription>
                Your latest pentest engagements
              </CardDescription>
            </div>
            <Link to="/projects">
              <Button variant="outline" size="sm">View All</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {!stats.recent_projects || stats.recent_projects.length === 0 ? (
              <div className="text-center py-8">
                <FolderOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">No projects yet</p>
                {stats.recent_projects && (
                  <Link to="/projects">
                    <Button className="btn-primary">
                      <Plus className="w-4 h-4 mr-2" />
                      Create First Project
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              stats.recent_projects && (
                <div className="space-y-4">
                  {stats.recent_projects?.map((project) => (
                    <div key={project.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h3 className="font-medium text-foreground">{project.name}</h3>
                          {getStatusBadge(project.status)}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {project.description || 'No description'}
                        </p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>Created: {formatDate(project.created_at)}</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <Target className="w-3 h-3" />
                            <span>{project.targets?.length || 0} targets</span>
                          </span>
                        </div>
                      </div>
                      <Link to={`/projects/${project.id}`}>
                        <Button variant="ghost" size="sm">
                          View →
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              )
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="glass">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Quick Actions</span>
            </CardTitle>
            <CardDescription>
              Common pentest activities
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/projects" className="block">
              <Button variant="outline" className="w-full justify-start">
                <Plus className="w-4 h-4 mr-2" />
                New Project
              </Button>
            </Link>
            
            <Link to="/notes" className="block">
              <Button variant="outline" className="w-full justify-start">
                <StickyNote className="w-4 h-4 mr-2" />
                Quick Note
              </Button>
            </Link>
            
            <Link to="/tools" className="block">
              <Button variant="outline" className="w-full justify-start">
                <Target className="w-4 h-4 mr-2" />
                Run Subdomain Scan
              </Button>
            </Link>
            
            <Button variant="outline" className="w-full justify-start" disabled>
              <Users className="w-4 h-4 mr-2" />
              Collaborate
              <Badge variant="secondary" className="ml-auto text-xs">Soon</Badge>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Security Alert */}
      <Card className="border-warning/50 bg-warning/5">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-warning">
            <Activity className="w-5 h-5" />
            <span>Security Notice</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground">
            This is a penetration testing platform. All activities should be conducted only on systems 
            you own or have explicit permission to test. Unauthorized testing is illegal and unethical.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;