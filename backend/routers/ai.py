from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional
import os
import requests
import json
import re
import uuid
import logging
from dependencies import get_current_active_user
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message to AI")
    project_id: str | None = Field(None, description="Optional project ID for context")
    tool_output_id: str | None = Field(None, description="Optional tool output ID for context")
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message content for security"""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',     # JavaScript protocol
            r'on\w+\s*=',      # Event handlers
            r'data:text/html', # Data URLs
            r'vbscript:',      # VBScript
            r'expression\s*\(', # CSS expressions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Message contains potentially dangerous content')
        
        return v.strip()
    
    @validator('project_id')
    def validate_project_id(cls, v):
        """Validate project ID format"""
        if v is None:
            return v
        
        try:
            # Validate UUID format
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid project ID format')
    
    @validator('tool_output_id')
    def validate_tool_output_id(cls, v):
        """Validate tool output ID format"""
        if v is None:
            return v
        
        # Tool output ID format: tool_YYYYMMDD_HHMMSS_toolname
        if not re.match(r'^tool_\d{8}_\d{6}_[a-z0-9_]+$', v):
            raise ValueError('Invalid tool output ID format')
        
        return v

class ChatResponse(BaseModel):
    response: str

# Ollama configuration
from config import OLLAMA_URL, OLLAMA_MODEL, AI_CONFIG
MODEL_NAME = OLLAMA_MODEL

# Security helper functions
def validate_project_access(project_id: str, user_id: str, db: Session) -> bool:
    """Validate that user has access to the project"""
    try:
        # Double-check UUID format
        uuid.UUID(project_id)
        
        # Check project ownership
        project_query = text("""
            SELECT id FROM projects 
            WHERE id = :project_id AND user_id = :user_id
        """)
        
        result = db.execute(project_query, {
            "project_id": project_id,
            "user_id": user_id
        }).fetchone()
        
        return result is not None
    except (ValueError, Exception):
        return False

def validate_tool_output_access(tool_output_id: str, user_id: str, db: Session) -> bool:
    """Validate that user has access to the tool output"""
    try:
        # Validate tool output ID format
        if not re.match(r'^tool_\d{8}_\d{6}_[a-z0-9_]+$', tool_output_id):
            return False
        
        # Check tool output ownership through project
        tool_query = text("""
            SELECT t.id FROM tool_outputs t
            JOIN projects p ON t.project_id = p.id
            WHERE t.id = :tool_output_id AND p.user_id = :user_id
        """)
        
        result = db.execute(tool_query, {
            "tool_output_id": tool_output_id,
            "user_id": user_id
        }).fetchone()
        
        return result is not None
    except Exception:
        return False

# System prompt for Pentora AI
SYSTEM_PROMPT = """You are the AI assistant of PentoraSec, a cybersecurity and penetration testing management platform. Your name is 'Pentora AI'. 

Your task is to help cybersecurity professionals with testing processes, analyze scan outputs, provide information about vulnerabilities, and accelerate reporting processes. 

Your responses should be clear, technically accurate, and professional. Always maintain the role of a helpful assistant.

In cybersecurity topics, you can help with:
- Vulnerability analysis and assessment
- Penetration testing methodologies
- Security tools usage
- Reporting and documentation
- Security standards and best practices
- Project analysis and comprehensive security assessment

When analyzing project context:
- Review all targets and their scope to understand the attack surface
- Analyze notes for important findings and observations
- Examine vulnerabilities by severity and provide remediation advice
- Review tool outputs for patterns and additional insights
- Provide actionable recommendations based on the complete project picture
- Identify potential security gaps or areas for further testing
- Suggest next steps for penetration testing based on current findings

Always respond in English and maintain a professional, helpful tone. When provided with project context, use it to give more specific and relevant advice."""



@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Chat with Pentora AI assistant using Ollama Llama 3.1 with contextual analysis
    """
    try:
        # Rate limiting check (basic implementation)
        # In production, use Redis or similar for proper rate limiting
        import time
        current_time = time.time()
        
        # Initialize context block
        context_block = ""
        
        # Process project context if project_id is provided
        if request.project_id:
            # Security: Validate project access first
            if not validate_project_access(request.project_id, current_user.id, db):
                raise HTTPException(
                    status_code=403,
                    detail="Project not found or access denied"
                )
            
            try:
                # Get comprehensive project details with all related data
                project_query = text("""
                    SELECT p.name, p.description, p.status, p.created_at, p.updated_at
                    FROM projects p
                    WHERE p.id = :project_id AND p.user_id = :user_id
                """)
                
                project_result = db.execute(project_query, {
                    "project_id": request.project_id,
                    "user_id": current_user.id
                }).fetchone()
                
                if project_result:
                    # Sanitize project details
                    project_name = re.sub(r'[<>"\']', '', str(project_result.name or ''))
                    project_desc = re.sub(r'[<>"\']', '', str(project_result.description or ''))
                    project_status = re.sub(r'[<>"\']', '', str(project_result.status or ''))
                    
                    context_block += f"""
--- CONTEXT: PROJECT OVERVIEW ---
Project Name: {project_name}
Description: {project_desc or 'No description'}
Status: {project_status}
Created: {project_result.created_at}
Last Updated: {project_result.updated_at}
--- END PROJECT OVERVIEW ---

"""
                    
                    # Get project targets
                    targets_query = text("""
                        SELECT target_type, value, description, is_in_scope, created_at
                        FROM targets
                        WHERE project_id = :project_id
                        ORDER BY created_at DESC
                    """)
                    
                    targets_result = db.execute(targets_query, {
                        "project_id": request.project_id
                    }).fetchall()
                    
                    if targets_result:
                        context_block += "--- CONTEXT: PROJECT TARGETS ---\n"
                        for target in targets_result:
                            target_type = re.sub(r'[<>"\']', '', str(target.target_type or ''))
                            target_value = re.sub(r'[<>"\']', '', str(target.value or ''))
                            target_desc = re.sub(r'[<>"\']', '', str(target.description or ''))
                            in_scope = "Yes" if target.is_in_scope else "No"
                            
                            context_block += f"""
Target: {target_value}
Type: {target_type}
Description: {target_desc or 'No description'}
In Scope: {in_scope}
Added: {target.created_at}
---
"""
                        context_block += "--- END PROJECT TARGETS ---\n\n"
                    
                    # Get project notes
                    notes_query = text("""
                        SELECT title, content, tags, created_at, updated_at
                        FROM notes
                        WHERE project_id = :project_id
                        ORDER BY created_at DESC
                    """)
                    
                    notes_result = db.execute(notes_query, {
                        "project_id": request.project_id
                    }).fetchall()
                    
                    if notes_result:
                        context_block += "--- CONTEXT: PROJECT NOTES ---\n"
                        for note in notes_result:
                            note_title = re.sub(r'[<>"\']', '', str(note.title or ''))
                            note_content = re.sub(r'[<>"\']', '', str(note.content or ''))
                            note_tags = re.sub(r'[<>"\']', '', str(note.tags or ''))
                            
                            context_block += f"""
Note: {note_title}
Content: {note_content[:300]}{'...' if len(note_content) > 300 else ''}
Tags: {note_tags or 'No tags'}
Created: {note.created_at}
---
"""
                        context_block += "--- END PROJECT NOTES ---\n\n"
                    
                    # Get project vulnerabilities
                    vulns_query = text("""
                        SELECT title, payload, how_it_works, severity, created_at
                        FROM vulnerabilities
                        WHERE project_id = :project_id
                        ORDER BY 
                            CASE severity 
                                WHEN 'critical' THEN 1 
                                WHEN 'high' THEN 2 
                                WHEN 'medium' THEN 3 
                                WHEN 'low' THEN 4 
                            END,
                            created_at DESC
                    """)
                    
                    vulns_result = db.execute(vulns_query, {
                        "project_id": request.project_id
                    }).fetchall()
                    
                    if vulns_result:
                        context_block += "--- CONTEXT: PROJECT VULNERABILITIES ---\n"
                        for vuln in vulns_result:
                            vuln_title = re.sub(r'[<>"\']', '', str(vuln.title or ''))
                            vuln_payload = str(vuln.payload or '')
                            vuln_how = re.sub(r'[<>"\']', '', str(vuln.how_it_works or ''))
                            vuln_severity = re.sub(r'[<>"\']', '', str(vuln.severity or ''))
                            
                            context_block += f"""
Vulnerability: {vuln_title}
Severity: {vuln_severity.upper()}
Payload: {vuln_payload[:150]}{'...' if len(vuln_payload) > 150 else ''}
How it works: {vuln_how[:200]}{'...' if len(vuln_how) > 200 else ''}
Found: {vuln.created_at}
---
"""
                        context_block += "--- END PROJECT VULNERABILITIES ---\n\n"
                    
                    # Get project tool outputs (limited for performance)
                    tools_query = text("""
                        SELECT tool_name, target, output, status, created_at
                        FROM tool_outputs
                        WHERE project_id = :project_id
                        ORDER BY created_at DESC
                        LIMIT 5
                    """)
                    
                    tools_result = db.execute(tools_query, {
                        "project_id": request.project_id
                    }).fetchall()
                    
                    if tools_result:
                        context_block += "--- CONTEXT: PROJECT TOOL OUTPUTS ---\n"
                        for tool in tools_result:
                            tool_name = re.sub(r'[<>"\']', '', str(tool.tool_name or ''))
                            tool_target = re.sub(r'[<>"\']', '', str(tool.target or ''))
                            tool_output = str(tool.output or '')
                            tool_status = re.sub(r'[<>"\']', '', str(tool.status or ''))
                            
                            context_block += f"""
Tool: {tool_name}
Target: {tool_target}
Status: {tool_status}
Output: {tool_output[:200]}{'...' if len(tool_output) > 200 else ''}
Executed: {tool.created_at}
---
"""
                        context_block += "--- END PROJECT TOOL OUTPUTS ---\n\n"
            except Exception as e:
                # Log error internally, don't expose details
                logging.error(f"Project context error for user {current_user.id}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to load project context"
                )
        
        # Process tool output context if tool_output_id is provided
        if request.tool_output_id:
            # Security: Validate tool output access first
            if not validate_tool_output_access(request.tool_output_id, current_user.id, db):
                raise HTTPException(
                    status_code=403,
                    detail="Tool output not found or access denied"
                )
            
            try:
                # Get tool output details with proper access control
                tool_query = text("""
                    SELECT t.tool_name, t.status, t.output, t.created_at, p.name as project_name
                    FROM tool_outputs t
                    JOIN projects p ON t.project_id = p.id
                    WHERE t.id = :tool_output_id AND p.user_id = :user_id
                """)
                
                result = db.execute(tool_query, {
                    "tool_output_id": request.tool_output_id,
                    "user_id": current_user.id
                }).fetchone()
                
                if result:
                    # Sanitize output to prevent injection
                    tool_name = re.sub(r'[<>"\']', '', str(result.tool_name or ''))
                    project_name = re.sub(r'[<>"\']', '', str(result.project_name or ''))
                    tool_output = str(result.output or '')
                    
                    # Limit output size to prevent prompt injection
                    if len(tool_output) > 5000:
                        tool_output = tool_output[:5000] + "... [truncated]"
                    
                    context_block += f"""
--- CONTEXT: TOOL OUTPUT ({tool_name}) ---
Tool: {tool_name}
Status: {result.status}
Project: {project_name}
Created: {result.created_at}
Output:
{tool_output}
--- END CONTEXT ---

"""
            except Exception as e:
                # Log error internally, don't expose details
                logging.error(f"Tool output context error for user {current_user.id}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to load tool output context"
                )
        
        # Sanitize user message to prevent prompt injection
        sanitized_message = re.sub(r'[<>"\']', '', request.message)
        
        # Combine system prompt, context, and user message
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context_block}User: {sanitized_message}\n\nPentora AI:"
        
        # Prepare request for Ollama
        ollama_request = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        }
        
        # Send request to Ollama with configurable timeout
        # SECURITY: Use Docker service name instead of localhost
        ollama_service_url = "http://pentest_ollama:11434"
        response = requests.post(
            f"{ollama_service_url}/api/generate",
            json=ollama_request,
            timeout=AI_CONFIG["timeout_seconds"]
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama service error: {response.status_code}"
            )
        
        result = response.json()
        
        if not result.get("response"):
            raise HTTPException(
                status_code=500,
                detail="AI service returned empty response"
            )
        
        return ChatResponse(response=result["response"].strip())
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=500,
            detail="AI service is not available. Please check if Ollama is running."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=500,
            detail="AI service timeout. Please try again."
        )
    except Exception as e:
        # Log error internally, don't expose details
        logging.error(f"AI Chat Error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="AI service error occurred"
        )

@router.get("/status")
async def get_ai_status():
    """
    Check if AI service is available
    """
    try:
        # Check if Ollama is running
        # SECURITY: Use Docker service name instead of localhost
        ollama_service_url = "http://pentest_ollama:11434"
        response = requests.get(f"{ollama_service_url}/api/tags", timeout=5)
        ollama_available = response.status_code == 200
        
        return {
            "available": ollama_available,
            "service": "Ollama",
            "model": MODEL_NAME,
            "url": ollama_service_url,
            "status": "running" if ollama_available else "not_available"
        }
    except:
        return {
            "available": False,
            "service": "Ollama",
            "model": MODEL_NAME,
            "url": "http://pentest_ollama:11434",
            "status": "not_available"
        }
