import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FolderOpen, 
  StickyNote, 
  Wrench, 
  ChevronLeft,
  Gem,
  Star,
  Sparkles,
  FileText,
  Sun,
  Moon,
  Heart
} from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import PentoraLogo from './PentoraLogo';
import UserStatusBar from './UserStatusBar';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

const Sidebar = ({ isOpen, onToggle }) => {
  const location = useLocation();
  const { tier, refreshTrigger, forceUpdate, user, isAIPanelOpen, setIsAIPanelOpen } = useAuth();
  const { theme, toggleTheme, isDark, isElite } = useTheme();
  
  // Force re-render when tier changes
  useEffect(() => {
    console.log('Sidebar: Tier changed to:', tier, 'forceUpdate:', forceUpdate, 'user:', user?.tier);
    console.log('Sidebar: getTierBadge will render with tier:', tier);
  }, [tier, refreshTrigger, forceUpdate, user]);

  const navigation = [
    { name: 'Welcome', href: '/welcome', icon: Heart },
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Projects', href: '/projects', icon: FolderOpen },
    { name: 'Notes', href: '/notes', icon: StickyNote },
    { name: 'Tools', href: '/tools', icon: Wrench },
    { name: 'Upgrade Plan', href: '/pricing', icon: Gem },
    { name: 'Policy', href: '/policy', icon: FileText },
  ];

  const isActive = (href) => location.pathname === href;

  const getTierBadge = () => {
    // Use user.tier if available, fallback to tier from context
    const currentTier = user?.tier || tier || 'essential';
    console.log('Sidebar: getTierBadge called with tier:', currentTier, 'user.tier:', user?.tier, 'context.tier:', tier);
    
    const tierConfig = {
      'essential': { 
        label: 'ESSENTIAL', 
        className: 'bg-slate-600 text-white border-slate-500' 
      },
      'professional': { 
        label: 'PROFESSIONAL', 
        className: 'bg-blue-600 text-white border-blue-500' 
      },
      'teams': { 
        label: 'TEAMS', 
        className: 'bg-purple-600 text-white border-purple-500' 
      },
      'enterprise': { 
        label: 'ENTERPRISE', 
        className: 'bg-emerald-600 text-white border-emerald-500' 
      },
      'elite': { 
        label: 'ELITE', 
        className: 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black border-yellow-400' 
      }
    };
    
    const config = tierConfig[currentTier] || tierConfig['essential'];
    console.log('Sidebar: getTierBadge returning config for tier:', currentTier, 'config:', config);
    return (
      <Badge className={`${config.className} text-xs font-bold tracking-wide px-2 py-1`}>
        {config.label}
      </Badge>
    );
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden" 
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-card border-r border-border
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        ${!isOpen ? 'lg:w-16' : 'lg:w-64'}
        flex flex-col
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className={`flex items-center space-x-3 ${!isOpen ? 'lg:justify-center' : ''}`}>
            <div className="w-8 h-8 flex items-center justify-center">
              <PentoraLogo className="w-8 h-8" />
            </div>
            {isOpen && (
              <div>
                <h1 className="text-lg font-bold text-foreground">
                  Pentora
                </h1>
                <p className="text-xs text-muted-foreground">Security Suite</p>
              </div>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="hidden lg:flex"
          >
            <ChevronLeft className={`w-4 h-4 transition-transform ${!isOpen ? 'rotate-180' : ''}`} />
          </Button>
        </div>

        {/* User Status Bar */}
        {isOpen && (
          <div className="px-4 pb-2">
            <UserStatusBar />
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center space-x-3 px-3 py-2 rounded-lg
                  transition-colors duration-200
                  ${isActive(item.href) 
                    ? 'bg-primary text-primary-foreground shadow-lg' 
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }
                  ${!isOpen ? 'lg:justify-center lg:px-2' : ''}
                `}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {isOpen && <span className="font-medium">{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* AI Assistant Button */}
        <div className="p-4">
          <Button
            onClick={() => setIsAIPanelOpen(!isAIPanelOpen)}
            className={`w-full justify-start gap-3 ${
              isAIPanelOpen 
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' 
                : 'bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 hover:from-blue-100 hover:to-purple-100'
            }`}
            variant={isAIPanelOpen ? "default" : "outline"}
          >
            <Sparkles className="w-5 h-5 flex-shrink-0" />
            {isOpen && <span className="font-medium">Pentora AI</span>}
          </Button>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <div className={`text-center ${!isOpen ? 'lg:hidden' : ''}`}>
            <div className="flex items-center justify-center mb-2">
              {getTierBadge()}
            </div>
            
            {/* Theme Toggle */}
            <div className="flex items-center justify-center mb-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className={`flex items-center space-x-2 text-xs text-muted-foreground hover:text-foreground transition-colors ${
                  isElite && !isDark ? 'bg-gradient-to-r from-red-100 to-pink-100 dark:from-red-900/20 dark:to-pink-900/20 border border-red-200 dark:border-red-800' : ''
                }`}
              >
                {isDark ? (
                  <>
                    <Sun className="h-3 w-3" />
                    <span>{isElite ? 'Elite Light' : 'Light Mode'}</span>
                  </>
                ) : (
                  <>
                    <Moon className="h-3 w-3" />
                    <span>Dark Mode</span>
                  </>
                )}
              </Button>
            </div>
            
            {/* Elite Theme Indicator */}
            {isElite && !isDark && (
              <div className="flex items-center justify-center mb-1">
                <Badge 
                  variant="outline" 
                  className="text-xs bg-gradient-to-r from-red-500 to-orange-500 text-white border-red-400"
                >
                  <Gem className="h-3 w-3 mr-1" />
                  Elite Theme Active
                </Badge>
              </div>
            )}
            
            <p className="text-xs text-muted-foreground">
              Professional Security Suite
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;