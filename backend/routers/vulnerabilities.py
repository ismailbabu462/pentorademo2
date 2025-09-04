"""
Vulnerability Management Router

This router handles vulnerability-related operations including
AI-powered vulnerability enrichment and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db, Vulnerability as DBVulnerability, Project as DBProject
from dependencies import get_current_active_user
from tasks import enrich_vulnerability
import logging

router = APIRouter(prefix="/api/vulnerabilities", tags=["vulnerabilities"])
logger = logging.getLogger(__name__)

class VulnerabilityAnalysisResponse(BaseModel):
    message: str
    task_id: str
    vulnerability_id: str

class VulnerabilityResponse(BaseModel):
    id: str
    title: str
    payload: str
    how_it_works: str
    severity: str
    ai_analysis: Optional[str] = None
    project_id: str
    user_id: str
    created_at: str
    updated_at: str

@router.post("/{vulnerability_id}/analyze", response_model=VulnerabilityAnalysisResponse)
async def analyze_vulnerability(
    vulnerability_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start AI-powered vulnerability analysis in the background.
    
    This endpoint triggers a Celery task that will:
    1. Search the web for vulnerability information
    2. Scrape relevant content
    3. Analyze with AI
    4. Save results to database
    """
    try:
        # SECURITY: Verify vulnerability exists and belongs to current user
        vulnerability = db.query(DBVulnerability).join(DBProject).filter(
            DBVulnerability.id == vulnerability_id,
            DBProject.user_id == current_user.id
        ).first()
        
        if not vulnerability:
            raise HTTPException(
                status_code=404,
                detail="Vulnerability not found or access denied"
            )
        
        # Check if analysis is already in progress or completed
        if vulnerability.ai_analysis:
            raise HTTPException(
                status_code=400,
                detail="Vulnerability analysis already completed"
            )
        
        # Start background task
        task = enrich_vulnerability.delay(vulnerability_id)
        
        logger.info(f"Started AI analysis for vulnerability {vulnerability_id}, task ID: {task.id}")
        
        return VulnerabilityAnalysisResponse(
            message="AI analysis has started in the background. Results will be available shortly.",
            task_id=task.id,
            vulnerability_id=vulnerability_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start vulnerability analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to start vulnerability analysis"
        )

@router.get("/{vulnerability_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vulnerability_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get vulnerability details including AI analysis if available.
    """
    try:
        # SECURITY: Verify vulnerability exists and belongs to current user
        vulnerability = db.query(DBVulnerability).join(DBProject).filter(
            DBVulnerability.id == vulnerability_id,
            DBProject.user_id == current_user.id
        ).first()
        
        if not vulnerability:
            raise HTTPException(
                status_code=404,
                detail="Vulnerability not found or access denied"
            )
        
        return VulnerabilityResponse(
            id=vulnerability.id,
            title=vulnerability.title,
            payload=vulnerability.payload,
            how_it_works=vulnerability.how_it_works,
            severity=vulnerability.severity,
            ai_analysis=vulnerability.ai_analysis,
            project_id=vulnerability.project_id,
            user_id=vulnerability.user_id,
            created_at=vulnerability.created_at.isoformat(),
            updated_at=vulnerability.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vulnerability: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve vulnerability"
        )

@router.get("/{vulnerability_id}/analysis-status")
async def get_analysis_status(
    vulnerability_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current status of vulnerability analysis.
    """
    try:
        # SECURITY: Verify vulnerability exists and belongs to current user
        vulnerability = db.query(DBVulnerability).join(DBProject).filter(
            DBVulnerability.id == vulnerability_id,
            DBProject.user_id == current_user.id
        ).first()
        
        if not vulnerability:
            raise HTTPException(
                status_code=404,
                detail="Vulnerability not found or access denied"
            )
        
        # Check if analysis is completed
        if vulnerability.ai_analysis:
            return {
                "status": "completed",
                "has_analysis": True,
                "analysis_length": len(vulnerability.ai_analysis)
            }
        else:
            return {
                "status": "pending",
                "has_analysis": False,
                "analysis_length": 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analysis status"
        )