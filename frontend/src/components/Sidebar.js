import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FolderOpen, 
  StickyNote, 
  Wrench, 
  Shield, 
  ChevronLeft,
  Moon,
  Sun
} from 'lucide-react';
import { Button } from './ui/button';
import { useTheme } from '../contexts/ThemeContext';

const Sidebar = ({ isOpen, onToggle }) => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Projects', href: '/projects', icon: FolderOpen },
    { name: 'Notes', href: '/notes', icon: StickyNote },
    { name: 'Tools', href: '/tools', icon: Wrench },
  ];

  const isActive = (href) => location.pathname === href;

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
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-primary-foreground" />
            </div>
            {isOpen && (
              <div>
                <h1 className="text-lg font-bold text-foreground">
                  Emergent Pentest
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

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className={`w-full ${!isOpen ? 'lg:px-2' : ''}`}
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
            {isOpen && (
              <span className="ml-3">
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </span>
            )}
          </Button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;