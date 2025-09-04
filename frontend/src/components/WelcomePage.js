import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Home, 
  FolderOpen, 
  StickyNote, 
  Wrench, 
  Sparkles,
  Shield,
  Target,
  ChevronRight,
  Play,
  BookOpen,
  Zap,
  Users,
  Lock,
  Gem
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

const WelcomePage = () => {
  const { user, tier, setIsAIPanelOpen } = useAuth();
  const { isElite, isDark } = useTheme();

  const features = [
    {
      icon: Home,
      title: "Dashboard",
      description: "Get a comprehensive overview of your security projects, recent activities, and quick stats.",
      color: "from-blue-500 to-cyan-500",
      link: "/dashboard"
    },
    {
      icon: FolderOpen,
      title: "Projects",
      description: "Organize your penetration testing projects. Create, manage, and track security assessments.",
      color: "from-purple-500 to-pink-500",
      link: "/projects"
    },
    {
      icon: StickyNote,
      title: "Notes",
      description: "Document findings, observations, and important security insights throughout your tests.",
      color: "from-green-500 to-emerald-500",
      link: "/notes"
    },
    {
      icon: Wrench,
      title: "Security Tools",
      description: "Access powerful penetration testing tools like Nmap, Nuclei, Subfinder, and more.",
      color: "from-orange-500 to-red-500",
      link: "/tools"
    },
    {
      icon: Sparkles,
      title: "Pentora AI",
      description: "Get AI-powered vulnerability analysis, security guidance, and intelligent reporting assistance.",
      color: "from-indigo-500 to-purple-500",
      link: "#",
      isAI: true
    }
  ];

  const quickActions = [
    {
      title: "Start Your First Project",
      description: "Create a new penetration testing project and begin your security assessment",
      icon: Play,
      link: "/projects",
      color: "bg-gradient-to-r from-blue-600 to-purple-600"
    },
    {
      title: "Explore Security Tools",
      description: "Discover our integrated security testing tools and scanners",
      icon: Zap,
      link: "/tools",
      color: "bg-gradient-to-r from-orange-600 to-red-600"
    },
    {
      title: "Chat with AI Assistant",
      description: "Get intelligent security insights and vulnerability analysis",
      icon: Sparkles,
      link: "#",
      color: "bg-gradient-to-r from-indigo-600 to-purple-600",
      isAI: true
    }
  ];

  const handleAIClick = () => {
    setIsAIPanelOpen(true);
  };

  return (
    <div className={`min-h-screen bg-background ${isElite && !isDark ? 'bg-gradient-to-br from-red-50 via-white to-pink-50' : ''}`}>
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className={`absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10 ${isElite && !isDark ? 'from-red-600/10 via-orange-600/10 to-pink-600/10' : ''}`} />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20">
          {/* Welcome Header */}
          <div className="text-center mb-16">
            <div className="flex justify-center mb-6">
              <div className={`p-4 rounded-full ${isElite && !isDark ? 'bg-gradient-to-r from-red-500 to-orange-500' : 'bg-gradient-to-r from-blue-600 to-purple-600'} shadow-lg`}>
                <Shield className="w-12 h-12 text-white" />
              </div>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-4">
              Welcome to{' '}
              <span className={`bg-gradient-to-r ${isElite && !isDark ? 'from-red-600 to-orange-600' : 'from-blue-600 to-purple-600'} bg-clip-text text-transparent`}>
                Pentora
              </span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
              Your comprehensive cybersecurity and penetration testing management platform. 
              Streamline your security assessments with powerful tools, AI assistance, and professional reporting.
            </p>

            {/* User Welcome */}
            {user && (
              <div className="flex items-center justify-center gap-4 mb-8">
                <Badge variant="outline" className="text-sm px-4 py-2">
                  Welcome back, {user.username || user.email}!
                </Badge>
                <Badge className={`text-sm px-4 py-2 ${
                  tier === 'elite' ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black' :
                  tier === 'enterprise' ? 'bg-emerald-600' :
                  tier === 'teams' ? 'bg-purple-600' :
                  tier === 'professional' ? 'bg-blue-600' : 'bg-slate-600'
                }`}>
                  <Gem className="w-3 h-3 mr-1" />
                  {tier?.toUpperCase() || 'ESSENTIAL'} PLAN
                </Badge>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {quickActions.map((action, index) => (
              <Card key={index} className="group hover:shadow-lg transition-all duration-300 border-0 bg-card/80 backdrop-blur-sm">
                <CardContent className="p-6">
                  <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <action.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">{action.title}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{action.description}</p>
                  {action.isAI ? (
                    <Button onClick={handleAIClick} variant="outline" size="sm" className="group-hover:bg-primary group-hover:text-primary-foreground">
                      Get Started
                      <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  ) : (
                    <Button asChild variant="outline" size="sm" className="group-hover:bg-primary group-hover:text-primary-foreground">
                      <Link to={action.link}>
                        Get Started
                        <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </Link>
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">Platform Features</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need for professional penetration testing and security assessments
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="group hover:shadow-xl transition-all duration-300 border-0 bg-card/50 backdrop-blur-sm overflow-hidden">
              <CardHeader>
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${feature.color} shadow-lg group-hover:scale-110 transition-transform`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm leading-relaxed mb-4">
                  {feature.description}
                </CardDescription>
                {feature.isAI ? (
                  <Button onClick={handleAIClick} variant="ghost" size="sm" className="text-primary hover:text-primary-foreground hover:bg-primary">
                    Learn More
                    <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                ) : (
                  <Button asChild variant="ghost" size="sm" className="text-primary hover:text-primary-foreground hover:bg-primary">
                    <Link to={feature.link}>
                      Learn More
                      <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Getting Started Section */}
      <div className={`border-t border-border ${isElite && !isDark ? 'bg-gradient-to-r from-red-50/50 to-orange-50/50' : 'bg-muted/30'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-foreground mb-4">Ready to Get Started?</h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Begin your security testing journey with Pentora's powerful suite of tools and AI assistance.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className={`${isElite && !isDark ? 'bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700' : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'} text-white shadow-lg`}>
                <Link to="/projects">
                  <FolderOpen className="w-5 h-5 mr-2" />
                  Create Your First Project
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/dashboard">
                  <Home className="w-5 h-5 mr-2" />
                  Go to Dashboard
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
