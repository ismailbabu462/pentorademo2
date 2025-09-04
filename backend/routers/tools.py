from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from dependencies import get_current_active_user
from datetime import datetime

router = APIRouter(prefix="/api/tools", tags=["tools"])

# Pydantic models
class ToolOutputRequest(BaseModel):
    tool_name: str = Field(..., min_length=1, max_length=100, description="Name of the tool used")
    target: str = Field(..., min_length=1, max_length=500, description="Target of the scan")
    output: str = Field(..., min_length=1, max_length=100000, description="Tool output content")
    status: str = Field(default="completed", description="Status of the tool execution")
    project_id: Optional[str] = Field(None, description="Optional project ID to link to")
    
    @validator('tool_name')
    def validate_tool_name(cls, v):
        """Validate and sanitize tool name"""
        if not v or not v.strip():
            raise ValueError('Tool name cannot be empty')
        
        # Only allow alphanumeric characters, underscores, and hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', v.strip())
        if not sanitized:
            raise ValueError('Tool name contains invalid characters')
        
        return sanitized
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target input"""
        if not v or not v.strip():
            raise ValueError('Target cannot be empty')
        
        # Basic validation for common targets
        target = v.strip()
        if len(target) > 500:
            raise ValueError('Target too long')
        
        # Check for potentially dangerous content
        dangerous_patterns = [r'<script', r'javascript:', r'data:', r'vbscript:']
        for pattern in dangerous_patterns:
            if re.search(pattern, target, re.IGNORECASE):
                raise ValueError('Target contains potentially dangerous content')
        
        return target
    
    @validator('output')
    def validate_output(cls, v):
        """Validate output content"""
        if not v or not v.strip():
            raise ValueError('Output cannot be empty')
        
        # Limit output size
        if len(v) > 100000:
            raise ValueError('Output too large (max 100KB)')
        
        return v.strip()
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status value"""
        valid_statuses = ['completed', 'failed', 'running', 'pending']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
    
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

class ToolOutputResponse(BaseModel):
    id: str
    tool_name: str
    target: str
    output: str
    status: str
    project_id: Optional[str]
    created_at: str

class ToolOutputListResponse(BaseModel):
    outputs: List[ToolOutputResponse]

# Security helper functions
def validate_project_access(project_id: str, user_id: str, db: Session) -> bool:
    """Validate that user has access to the project"""
    try:
        # Validate UUID format
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

def sanitize_tool_output_id(tool_name: str) -> str:
    """Generate safe tool output ID"""
    # Sanitize tool name for ID generation
    safe_name = re.sub(r'[^a-z0-9_]', '', tool_name.lower())
    if not safe_name:
        safe_name = "unknown"
    
    # Limit length
    safe_name = safe_name[:20]
    
    return f"tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}"

@router.post("/output", response_model=ToolOutputResponse)
async def save_tool_output(
    request: ToolOutputRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Save tool output to database, optionally linked to a project
    """
    try:
        # If project_id is provided, verify user owns the project
        if request.project_id:
            if not validate_project_access(request.project_id, current_user.id, db):
                raise HTTPException(
                    status_code=403,
                    detail="Project not found or access denied"
                )

        # Generate safe tool output ID
        tool_output_id = sanitize_tool_output_id(request.tool_name)
        
        # Double-check project access (race condition protection)
        if request.project_id:
            project_check_query = text("""
                SELECT id FROM projects 
                WHERE id = :project_id AND user_id = :user_id
            """)
            project_result = db.execute(project_check_query, {
                "project_id": request.project_id,
                "user_id": current_user.id
            }).fetchone()
            
            if not project_result:
                raise HTTPException(
                    status_code=403,
                    detail="Project not found or access denied"
                )
        
        # Insert tool output with parameterized query
        insert_query = text("""
            INSERT INTO tool_outputs (id, tool_name, target, output, status, project_id, user_id, created_at)
            VALUES (:id, :tool_name, :target, :output, :status, :project_id, :user_id, :created_at)
        """)
        
        db.execute(insert_query, {
            "id": tool_output_id,
            "tool_name": request.tool_name,
            "target": request.target,
            "output": request.output,
            "status": request.status,
            "project_id": request.project_id,
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat()
        })
        
        # Commit transaction
        db.commit()
        
        return ToolOutputResponse(
            id=tool_output_id,
            tool_name=request.tool_name,
            target=request.target,
            output=request.output,
            status=request.status,
            project_id=request.project_id,
            created_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logging.error(f"Save Tool Output Error for user {current_user.id}: {str(e)}")
        try:
            db.rollback()
        except:
            pass  # Rollback may fail if no transaction is active
        raise HTTPException(
            status_code=500,
            detail="Failed to save tool output"
        )

@router.get("/outputs", response_model=ToolOutputListResponse)
async def get_tool_outputs(
    project_id: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get tool outputs, optionally filtered by project
    """
    try:
        if project_id:
            # Validate project access
            if not validate_project_access(project_id, current_user.id, db):
                raise HTTPException(
                    status_code=403,
                    detail="Project not found or access denied"
                )
            
            # Get tool outputs for specific project
            query = text("""
                SELECT id, tool_name, target, output, status, project_id, created_at
                FROM tool_outputs 
                WHERE project_id = :project_id AND user_id = :user_id
                ORDER BY created_at DESC
                LIMIT 100
            """)
            results = db.execute(query, {
                "project_id": project_id,
                "user_id": current_user.id
            }).fetchall()
        else:
            # Get all tool outputs for user (with limit)
            query = text("""
                SELECT id, tool_name, target, output, status, project_id, created_at
                FROM tool_outputs 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT 100
            """)
            results = db.execute(query, {"user_id": current_user.id}).fetchall()
        
        outputs = []
        for row in results:
            # Sanitize output for response
            sanitized_output = row.output
            if len(sanitized_output) > 1000:
                sanitized_output = sanitized_output[:1000] + "... [truncated]"
            
            # Convert datetime to string if needed
            created_at_str = row.created_at
            if hasattr(created_at_str, 'isoformat'):
                created_at_str = created_at_str.isoformat()
            elif isinstance(created_at_str, str):
                pass  # Already a string
            else:
                created_at_str = str(created_at_str)
            
            outputs.append(ToolOutputResponse(
                id=row.id,
                tool_name=row.tool_name,
                target=row.target,
                output=sanitized_output,
                status=row.status,
                project_id=row.project_id,
                created_at=created_at_str
            ))
        
        return ToolOutputListResponse(outputs=outputs)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logging.error(f"Get Tool Outputs Error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get tool outputs"
        )

@router.get("/output/{output_id}", response_model=ToolOutputResponse)
async def get_tool_output(
    output_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific tool output by ID
    """
    try:
        # Validate output_id format
        if not re.match(r'^tool_\d{8}_\d{6}_[a-z0-9_]+$', output_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid tool output ID format"
            )
        
        query = text("""
            SELECT id, tool_name, target, output, status, project_id, created_at
            FROM tool_outputs 
            WHERE id = :output_id AND user_id = :user_id
        """)
        
        result = db.execute(query, {
            "output_id": output_id,
            "user_id": current_user.id
        }).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Tool output not found"
            )
        
        # Convert datetime to string if needed
        created_at_str = result.created_at
        if hasattr(created_at_str, 'isoformat'):
            created_at_str = created_at_str.isoformat()
        elif isinstance(created_at_str, str):
            pass  # Already a string
        else:
            created_at_str = str(created_at_str)
        
        return ToolOutputResponse(
            id=result.id,
            tool_name=result.tool_name,
            target=result.target,
            output=result.output,
            status=result.status,
            project_id=result.project_id,
            created_at=created_at_str
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logging.error(f"Get Tool Output Error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get tool output"
        )
