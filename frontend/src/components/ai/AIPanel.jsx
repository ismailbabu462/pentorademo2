import React, { useState, useRef, useEffect } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '../ui/sheet';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Send, Bot, User, Loader2, FolderOpen } from 'lucide-react';
import api from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

const AIPanel = () => {
  const { isAIPanelOpen, setIsAIPanelOpen, aiContext, setAIContext } = useAuth();
  const [conversationHistory, setConversationHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const scrollAreaRef = useRef(null);

  // Auto scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [conversationHistory]);

  // Load projects when panel opens
  useEffect(() => {
    if (isAIPanelOpen) {
      fetchProjects();
    }
  }, [isAIPanelOpen]);

  // Handle AI context from other components
  useEffect(() => {
    if (aiContext && aiContext.defaultMessage) {
      setCurrentMessage(aiContext.defaultMessage);
      // Clear context after using it
      setAIContext(null);
    }
  }, [aiContext, setAIContext]);

  // Fetch user's projects
  const fetchProjects = async () => {
    setLoadingProjects(true);
    try {
      const response = await api.get('/projects');
      setProjects(response.data || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      setProjects([]);
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    
    // Add user message to conversation
    const newUserMessage = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    
    setConversationHistory(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Prepare request body with context
      const requestBody = {
        message: userMessage
      };

      // Add project context if selected
      if (selectedProjectId) {
        requestBody.project_id = selectedProjectId;
      }

      // Add tool output context if available
      if (aiContext && aiContext.tool_output) {
        // For now, we'll send the tool output as part of the message
        // In a real implementation, you'd save this to database and send tool_output_id
        requestBody.message = `${userMessage}\n\nTool Output Context:\n${aiContext.tool_output}`;
      }

      // Send message to backend with extended timeout for AI processing
      const response = await api.post('/ai/chat', requestBody, {
        timeout: 60000 // 60 seconds timeout for AI processing
      });

      // Add AI response to conversation
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.data.response,
        timestamp: new Date()
      };
      
      setConversationHistory(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('AI Chat Error:', error);
      
      // Add error message to conversation
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Sorry, an error occurred. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      
      setConversationHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setConversationHistory([]);
  };

  return (
    <Sheet open={isAIPanelOpen} onOpenChange={setIsAIPanelOpen}>
      <SheetContent side="right" className="w-[500px] sm:w-[700px] max-w-[85vw] p-0">
        <div className="flex flex-col h-full">
          {/* Header */}
          <SheetHeader className="p-6 pb-4 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-blue-600" />
                <SheetTitle className="text-lg font-semibold">Pentora AI</SheetTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearConversation}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                Clear
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              I can help you with cybersecurity topics
            </p>
            
            {/* Project Selection */}
            <div className="mt-4">
              <label className="text-xs font-medium text-muted-foreground mb-2 block">
                Active Project Context
              </label>
              <Select 
                value={selectedProjectId || ""} 
                onValueChange={(value) => {
                  setSelectedProjectId(value === "none" ? null : value);
                  // Clear tool output context when project is selected
                  if (value !== "none" && aiContext) {
                    setAIContext(null);
                  }
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select project (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No context</SelectItem>
                  {loadingProjects ? (
                    <SelectItem value="loading" disabled>
                      Loading projects...
                    </SelectItem>
                  ) : (
                    projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        <div className="flex items-center gap-2">
                          <FolderOpen className="h-4 w-4" />
                          {project.name}
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
          </SheetHeader>

          {/* Chat Messages */}
          <div className="flex-1 overflow-hidden">
            <ScrollArea className="h-full p-4" ref={scrollAreaRef}>
              <div className="space-y-4">
                {conversationHistory.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
                    <p className="text-sm">
                      Hello! I'm Pentora AI. How can I help you with cybersecurity topics?
                    </p>
                  </div>
                ) : (
                  conversationHistory.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.type === 'ai' && (
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                            <Bot className="h-4 w-4 text-blue-600" />
                          </div>
                        </div>
                      )}
                      
                      <div
                        className={`max-w-[85%] rounded-lg px-4 py-2 ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : message.isError
                            ? 'bg-red-50 text-red-800 border border-red-200'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString('tr-TR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      
                      {message.type === 'user' && (
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                            <User className="h-4 w-4 text-gray-600" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
                
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-blue-600" />
                      </div>
                    </div>
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <p className="text-sm text-muted-foreground">Pentora AI is thinking...</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </div>

          {/* Input Form */}
          <div className="p-4 border-t">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <Input
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                type="submit"
                disabled={!currentMessage.trim() || isLoading}
                size="icon"
                className="shrink-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default AIPanel;
