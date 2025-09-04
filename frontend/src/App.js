import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import api, { setAuthToken } from "./lib/api";
import { Toaster } from "./components/ui/sonner";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import ProjectsPage from "./components/ProjectsPage";
import ProjectDetail from "./components/ProjectDetail";
import NotesPage from "./components/NotesPage";
import ToolsPage from "./components/ToolsPage";
import PolicyPage from "./components/PolicyPage";
import WelcomePage from "./components/WelcomePage";
import PricingPage from "./pages/PricingPage";
import PaymentSuccessPage from "./pages/PaymentSuccessPage";
import MockCheckoutPage from "./pages/MockCheckoutPage";
import AIPanel from "./components/ai/AIPanel";

// Token management is now handled in lib/api.js

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authToken, setAuthTokenState] = useState(null);

  // Auto-login on app start
  useEffect(() => {
    const autoLogin = async () => {
      try {
        console.log('App: Starting auto-login...');
        const response = await api.post('/auth/auto-login');
        console.log('App: Auto-login response:', response.data);
        
        const token = response.data.access_token;
        console.log('App: Setting auth token:', token ? 'Present' : 'Missing');
        setAuthToken(token);
        setAuthTokenState(token);
        setIsAuthenticated(true);
        console.log('App: Auto-login successful');
      } catch (error) {
        console.error('App: Auto-login failed:', error);
        // Still allow access for development
        setIsAuthenticated(true);
      } finally {
        setIsLoading(false);
      }
    };

    autoLogin();
  }, []);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, show a simple login bypass
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Authentication Required</h1>
          <p className="mb-4">Please log in to continue</p>
          <button 
            onClick={() => setIsAuthenticated(true)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
          >
            Continue to App
          </button>
        </div>
      </div>
    );
  }

  return (
    <AuthProvider initialToken={authToken}>
      <ThemeProvider>
        <div className="App">
          <BrowserRouter>
          <div className="flex h-screen bg-background">
            <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<Navigate to="/welcome" replace />} />
                <Route path="/welcome" element={<WelcomePage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/projects/:projectId" element={<ProjectDetail />} />
                <Route path="/notes" element={<NotesPage />} />
                <Route path="/tools" element={<ToolsPage />} />
                <Route path="/policy" element={<PolicyPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/payment/mock-checkout" element={<MockCheckoutPage />} />
                <Route path="/payment/success" element={<PaymentSuccessPage />} />
              </Routes>
            </main>
            <AIPanel />
          </div>
          <Toaster />
        </BrowserRouter>
      </div>
    </ThemeProvider>
    </AuthProvider>
  );
}

export default App;