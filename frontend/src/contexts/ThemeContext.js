import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const { tier } = useAuth();
  const [theme, setTheme] = useState(() => {
    // Check localStorage for saved theme
    const savedTheme = localStorage.getItem('pentorasec-theme');
    return savedTheme || 'dark';
  });
  
  const isElite = tier === 'elite';

  const applyTheme = (currentTheme) => {
    if (currentTheme === 'light') {
      // Apply light mode
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      
      // Add or remove elite class based on tier
      if (isElite) {
        document.documentElement.classList.add('elite');
      } else {
        document.documentElement.classList.remove('elite');
      }
      
      if (isElite) {
        // Elite light mode colors: Deep red (#8E0D3C), blackcurrant (#1D1842), orange (#EF3B33), rose pink (#FDA1A2)
        document.documentElement.style.setProperty('--background', '346 89% 85%'); // Light rose pink background
        document.documentElement.style.setProperty('--foreground', '250 55% 15%'); // Dark blackcurrant
        document.documentElement.style.setProperty('--card', '346 89% 90%');
        document.documentElement.style.setProperty('--card-foreground', '250 55% 15%');
        document.documentElement.style.setProperty('--popover', '346 89% 90%');
        document.documentElement.style.setProperty('--popover-foreground', '250 55% 15%');
        document.documentElement.style.setProperty('--primary', '346 89% 30%'); // Deep red #8E0D3C
        document.documentElement.style.setProperty('--primary-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--secondary', '250 55% 15%'); // Blackcurrant #1D1842
        document.documentElement.style.setProperty('--secondary-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--muted', '346 89% 87%');
        document.documentElement.style.setProperty('--muted-foreground', '250 55% 25%');
        document.documentElement.style.setProperty('--accent', '6 87% 57%'); // Orange #EF3B33
        document.documentElement.style.setProperty('--accent-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--destructive', '0 84% 60%');
        document.documentElement.style.setProperty('--destructive-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--border', '346 89% 82%');
        document.documentElement.style.setProperty('--input', '346 89% 82%');
        document.documentElement.style.setProperty('--ring', '346 89% 30%');
        
        document.documentElement.style.setProperty('--success', '142 76% 36%');
        document.documentElement.style.setProperty('--success-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--warning', '6 87% 57%');
        document.documentElement.style.setProperty('--warning-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--info', '346 89% 30%');
        document.documentElement.style.setProperty('--info-foreground', '0 0% 98%');
      } else {
        // Standard light mode colors: Pale blue (#EFFAFD), royal blue (#4A8BDF), eggplant (#A0006D)
        document.documentElement.style.setProperty('--background', '204 100% 97%'); // #EFFAFD
        document.documentElement.style.setProperty('--foreground', '0 0% 9%');
        document.documentElement.style.setProperty('--card', '204 100% 97%');
        document.documentElement.style.setProperty('--card-foreground', '0 0% 9%');
        document.documentElement.style.setProperty('--popover', '204 100% 97%');
        document.documentElement.style.setProperty('--popover-foreground', '0 0% 9%');
        document.documentElement.style.setProperty('--primary', '218 69% 57%'); // #4A8BDF
        document.documentElement.style.setProperty('--primary-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--secondary', '204 100% 94%');
        document.documentElement.style.setProperty('--secondary-foreground', '0 0% 9%');
        document.documentElement.style.setProperty('--muted', '204 100% 94%');
        document.documentElement.style.setProperty('--muted-foreground', '0 0% 45%');
        document.documentElement.style.setProperty('--accent', '322 100% 31%'); // #A0006D
        document.documentElement.style.setProperty('--accent-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--destructive', '0 84% 60%');
        document.documentElement.style.setProperty('--destructive-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--border', '204 100% 90%');
        document.documentElement.style.setProperty('--input', '204 100% 90%');
        document.documentElement.style.setProperty('--ring', '218 69% 57%');
        
        document.documentElement.style.setProperty('--success', '142 76% 36%');
        document.documentElement.style.setProperty('--success-foreground', '0 0% 98%');
        document.documentElement.style.setProperty('--warning', '38 92% 50%');
        document.documentElement.style.setProperty('--warning-foreground', '0 0% 9%');
        document.documentElement.style.setProperty('--info', '218 69% 57%');
        document.documentElement.style.setProperty('--info-foreground', '0 0% 98%');
      }
    } else {
      // Apply dark mode
      document.documentElement.classList.remove('light', 'elite');
      document.documentElement.classList.add('dark');
      
      // Dark theme colors
      document.documentElement.style.setProperty('--background', '0 0% 9%');
      document.documentElement.style.setProperty('--foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--card', '0 0% 9%');
      document.documentElement.style.setProperty('--card-foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--popover', '0 0% 9%');
      document.documentElement.style.setProperty('--popover-foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--primary', '0 0% 98%');
      document.documentElement.style.setProperty('--primary-foreground', '0 0% 9%');
      document.documentElement.style.setProperty('--secondary', '0 0% 15%');
      document.documentElement.style.setProperty('--secondary-foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--muted', '0 0% 15%');
      document.documentElement.style.setProperty('--muted-foreground', '0 0% 65%');
      document.documentElement.style.setProperty('--accent', '0 0% 15%');
      document.documentElement.style.setProperty('--accent-foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--destructive', '0 84% 60%');
      document.documentElement.style.setProperty('--destructive-foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--border', '0 0% 20%');
      document.documentElement.style.setProperty('--input', '0 0% 20%');
      document.documentElement.style.setProperty('--ring', '0 0% 98%');

      document.documentElement.style.setProperty('--success', '142 76% 36%');
      document.documentElement.style.setProperty('--success-foreground', '0 0% 98%');
      document.documentElement.style.setProperty('--warning', '0 0% 85%');
      document.documentElement.style.setProperty('--warning-foreground', '0 0% 9%');
      document.documentElement.style.setProperty('--info', '0 0% 65%');
      document.documentElement.style.setProperty('--info-foreground', '0 0% 98%');
    }
    
    // Common properties
    document.documentElement.style.setProperty('--chart-1', '218 69% 57%');
    document.documentElement.style.setProperty('--chart-2', '322 100% 31%');
    document.documentElement.style.setProperty('--chart-3', '204 100% 85%');
    document.documentElement.style.setProperty('--chart-4', '0 0% 35%');
    document.documentElement.style.setProperty('--chart-5', '0 0% 15%');
    document.documentElement.style.setProperty('--radius', '0.5rem');
  };

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem('pentorasec-theme', theme);
  }, [theme, tier]); // tier değişikliklerini de dinle

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  const value = {
    theme,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    isElite
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};