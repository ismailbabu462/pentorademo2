import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  FileText, 
  Calendar,
  Tag,
  Edit,
  Trash2
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import api from '../lib/api';
import { toast } from 'sonner';

const NotesPage = () => {
  const [notes, setNotes] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedNote, setSelectedNote] = useState(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  
  const [formData, setFormData] = useState({
    project_id: '',
    title: '',
    content: '',
    tags: ''
  });

  useEffect(() => {
    fetchNotes();
    fetchProjects();
  }, []);

  const fetchNotes = async () => {
    try {
      console.log('Fetching notes...');
      
      // Try to fetch notes from API first
      try {
        const projectsResponse = await api.get('/projects');
        const allNotes = [];
        
        // For each project, fetch its notes
        for (const project of projectsResponse.data) {
          try {
            const notesResponse = await api.get(`/projects/${project.id}/notes`);
            if (notesResponse.data && Array.isArray(notesResponse.data)) {
              allNotes.push(...notesResponse.data.map(note => ({
                ...note,
                project_name: project.name
              })));
            }
          } catch (error) {
            console.log(`No notes for project ${project.id}`);
          }
        }
        
        setNotes(allNotes);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // If API is not available, create mock data for development
      const mockNotes = [
        {
          id: 1,
          project_id: 1,
          title: 'SQL Injection in Login Form',
          content: 'Found SQL injection vulnerability in the login form. The application is vulnerable to boolean-based blind SQL injection.',
          tags: ['sql-injection', 'web', 'critical'],
          created_at: '2024-01-20T10:30:00Z',
          updated_at: '2024-01-20T10:30:00Z'
        },
        {
          id: 2,
          project_id: 1,
          title: 'XSS in Search Function',
          content: 'Reflected XSS vulnerability found in the search functionality. User input is not properly sanitized.',
          tags: ['xss', 'web', 'medium'],
          created_at: '2024-01-21T14:15:00Z',
          updated_at: '2024-01-21T14:15:00Z'
        },
        {
          id: 3,
          project_id: 2,
          title: 'Directory Traversal',
          content: 'Path traversal vulnerability allows access to sensitive files outside web root.',
          tags: ['directory-traversal', 'web', 'high'],
          created_at: '2024-01-26T09:45:00Z',
          updated_at: '2024-01-26T09:45:00Z'
        }
      ];
      
      setNotes(mockNotes);
      toast.info('Using mock data - Backend not available');
      
    } catch (error) {
      console.error('Failed to fetch notes:', error);
      toast.error('Failed to load notes');
      setNotes([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    }
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!formData.project_id) {
      toast.error('Please select a project');
      return;
    }
    
    try {
      const noteData = {
        ...formData,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : []
      };
      
      await api.post('/notes', noteData);
      toast.success('Note created successfully');
      setShowCreateDialog(false);
      resetForm();
      fetchNotes();
    } catch (error) {
      console.error('Failed to create note:', error);
      toast.error('Failed to create note');
    }
  };

  const handleDeleteNote = async () => {
    if (!selectedNote) return;
    
    try {
      await api.delete(`/notes/${selectedNote.id}`);
      toast.success('Note deleted successfully');
      setShowDeleteDialog(false);
      setSelectedNote(null);
      fetchNotes();
    } catch (error) {
      console.error('Failed to delete note:', error);
      toast.error('Failed to delete note');
    }
  };

  const resetForm = () => {
    setFormData({
      project_id: '',
      title: '',
      content: '',
      tags: ''
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getProjectName = (projectId) => {
    if (!projects) return 'Unknown Project';
    const project = projects.find(p => p.id === projectId);
    return project ? project.name : 'Unknown Project';
  };

  const filteredNotes = notes?.filter(note =>
    note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    note.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    note.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

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
          <h1 className="text-3xl font-bold text-foreground">Notes</h1>
          <p className="text-muted-foreground">
            Document findings, methodologies, and observations
          </p>
        </div>
        <Button 
          className="btn-primary" 
          onClick={() => setShowCreateDialog(true)}
          disabled={!projects || projects.length === 0}
        >
          <Plus className="w-4 h-4 mr-2" />
          New Note
        </Button>
      </div>

      {!projects || projects.length === 0 ? (
        <Card className="glass">
          <CardContent className="text-center py-12">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No Projects Available</h3>
            <p className="text-muted-foreground mb-4">
              You need to create a project before you can add notes
            </p>
            <Button variant="outline">
              Create Project First
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Search */}
          {notes && (
            <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
            </div>
          )}

          {/* Notes Grid */}
          {(!notes || !filteredNotes || filteredNotes.length === 0) ? (
            <Card className="glass">
              <CardContent className="text-center py-12">
                <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">
                  {searchTerm ? 'No notes found' : 'No notes yet'}
                </h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm 
                    ? 'Try adjusting your search terms'
                    : 'Start documenting your penetration testing findings and methodologies'
                  }
                </p>
                {!searchTerm && notes && (
                  <Button className="btn-primary" onClick={() => setShowCreateDialog(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create First Note
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            notes && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredNotes?.map((note) => (
                  <Card key={note.id} className="glass hover:shadow-lg transition-all duration-300 group cursor-pointer" onClick={() => {
                    setSelectedNote(note);
                    setShowPreviewDialog(true);
                  }}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg line-clamp-2">{note.title}</CardTitle>
                          <CardDescription className="mt-1">
                            {getProjectName(note.project_id)}
                          </CardDescription>
                        </div>
                        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button variant="ghost" size="sm" onClick={(e) => {
                            e.stopPropagation();
                            // Edit functionality can be added here
                          }}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            className="text-destructive hover:text-destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedNote(note);
                              setShowDeleteDialog(true);
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground line-clamp-3">
                        {note.content}
                      </p>
                      
                      {note.tags?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {note.tags.slice(0, 3).map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              <Tag className="w-2 h-2 mr-1" />
                              {tag}
                            </Badge>
                          ))}
                          {note.tags.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{note.tags.length - 3} more
                            </Badge>
                          )}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(note.created_at)}</span>
                        </div>
                        {note.updated_at !== note.created_at && (
                          <span>Updated {formatDate(note.updated_at)}</span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )
          )}
        </>
      )}

      {/* Create Note Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Note</DialogTitle>
            <DialogDescription>
              Document findings, observations, or methodologies
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleCreateNote} className="space-y-4">
            <div>
              <Label htmlFor="project_id">Project *</Label>
              <Select 
                value={formData.project_id} 
                onValueChange={(value) => setFormData({...formData, project_id: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a project" />
                </SelectTrigger>
                <SelectContent>
                  {projects?.map((project) => (
                    <SelectItem key={project.id} value={project.id}>
                      {project.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="e.g., SQL Injection in Login Form"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="content">Content *</Label>
              <Textarea
                id="content"
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                placeholder="Document your findings, steps, and observations..."
                rows={10}
                required
                className="min-h-[200px]"
              />
            </div>
            
            <div>
              <Label htmlFor="tags">Tags</Label>
              <Input
                id="tags"
                value={formData.tags}
                onChange={(e) => setFormData({...formData, tags: e.target.value})}
                placeholder="vulnerability, web, database (comma-separated)"
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" className="btn-primary">
                Create Note
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Note Preview Dialog */}
      <Dialog open={showPreviewDialog} onOpenChange={setShowPreviewDialog}>
        <DialogContent className="sm:max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">{selectedNote?.title}</DialogTitle>
            <DialogDescription>
              {selectedNote && getProjectName(selectedNote.project_id)} • {selectedNote && formatDate(selectedNote.created_at)}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {selectedNote?.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {selectedNote.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-sm">
                    <Tag className="w-3 h-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
            
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {selectedNote?.content}
              </div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-muted-foreground pt-4 border-t">
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>Created: {selectedNote && formatDate(selectedNote.created_at)}</span>
              </div>
              {selectedNote?.updated_at !== selectedNote?.created_at && (
                <span>Updated: {selectedNote && formatDate(selectedNote.updated_at)}</span>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreviewDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Note</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{selectedNote?.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteNote}>
              Delete Note
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default NotesPage;