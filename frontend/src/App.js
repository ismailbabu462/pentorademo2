import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "./components/ui/sonner";
import { ThemeProvider } from "./contexts/ThemeContext";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import ProjectsPage from "./components/ProjectsPage";
import ProjectDetail from "./components/ProjectDetail";
import NotesPage from "./components/NotesPage";
import ToolsPage from "./components/ToolsPage";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
export const api = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <ThemeProvider>
      <div className="App">
        <BrowserRouter>
          <div className="flex h-screen bg-background">
            <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/projects/:projectId" element={<ProjectDetail />} />
                <Route path="/notes" element={<NotesPage />} />
                <Route path="/tools" element={<ToolsPage />} />
              </Routes>
            </main>
          </div>
          <Toaster />
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;