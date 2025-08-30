from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Emergent Pentest Suite API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    PLANNING = "planning"

class TargetType(str, Enum):
    DOMAIN = "domain"
    IP = "ip" 
    CIDR = "cidr"
    URL = "url"

class VulnerabilitySeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

# Models
class Target(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_type: TargetType
    value: str
    description: Optional[str] = None
    is_in_scope: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TargetCreate(BaseModel):
    target_type: TargetType
    value: str
    description: Optional[str] = None
    is_in_scope: bool = True

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_members: List[str] = []
    targets: List[Target] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_members: List[str] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_members: Optional[List[str]] = None

class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    content: str
    tags: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NoteCreate(BaseModel):
    project_id: str
    title: str
    content: str
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key.endswith('_at'):
                try:
                    item[key] = datetime.fromisoformat(value)
                except:
                    pass
    return item

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate):
    project_dict = project_data.dict()
    project_obj = Project(**project_dict)
    project_dict = prepare_for_mongo(project_obj.dict())
    await db.projects.insert_one(project_dict)
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    return [Project(**parse_from_mongo(project)) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**parse_from_mongo(project))

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    update_data = prepare_for_mongo(update_data)
    await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**parse_from_mongo(updated_project))

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Target Routes
@api_router.post("/projects/{project_id}/targets", response_model=Target)
async def add_target_to_project(project_id: str, target_data: TargetCreate):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    target_obj = Target(**target_data.dict())
    target_dict = prepare_for_mongo(target_obj.dict())
    
    await db.projects.update_one(
        {"id": project_id},
        {"$push": {"targets": target_dict}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return target_obj

@api_router.get("/projects/{project_id}/targets", response_model=List[Target])
async def get_project_targets(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    targets = project.get("targets", [])
    return [Target(**parse_from_mongo(target)) for target in targets]

@api_router.delete("/projects/{project_id}/targets/{target_id}")
async def remove_target_from_project(project_id: str, target_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.projects.update_one(
        {"id": project_id},
        {"$pull": {"targets": {"id": target_id}}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Target removed successfully"}

# Notes Routes
@api_router.post("/notes", response_model=Note)
async def create_note(note_data: NoteCreate):
    # Verify project exists
    project = await db.projects.find_one({"id": note_data.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    note_obj = Note(**note_data.dict())
    note_dict = prepare_for_mongo(note_obj.dict())
    await db.notes.insert_one(note_dict)
    return note_obj

@api_router.get("/projects/{project_id}/notes", response_model=List[Note])
async def get_project_notes(project_id: str):
    notes = await db.notes.find({"project_id": project_id}).to_list(1000)
    return [Note(**parse_from_mongo(note)) for note in notes]

@api_router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    note = await db.notes.find_one({"id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return Note(**parse_from_mongo(note))

@api_router.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, note_update: NoteUpdate):
    note = await db.notes.find_one({"id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    update_data = prepare_for_mongo(update_data)
    await db.notes.update_one({"id": note_id}, {"$set": update_data})
    
    updated_note = await db.notes.find_one({"id": note_id})
    return Note(**parse_from_mongo(updated_note))

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    result = await db.notes.delete_one({"id": note_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    total_projects = await db.projects.count_documents({})
    active_projects = await db.projects.count_documents({"status": "active"})
    total_notes = await db.notes.count_documents({})
    
    # Get recent projects
    recent_projects = await db.projects.find().sort("updated_at", -1).limit(5).to_list(5)
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_notes": total_notes,
        "recent_projects": [Project(**parse_from_mongo(project)) for project in recent_projects]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()