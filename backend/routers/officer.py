"""
Officer router: assignment management, status updates, officer-specific endpoints.
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from utils.auth import get_current_user, require_roles
from utils.validators import sanitize_string
from utils.sms_client import send_assignment_notification, send_status_update_notification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/officer", tags=["Officer"])


class AssignRequest(BaseModel):
    officer_id: str
    notes: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: str  # in_progress, resolved, rejected
    notes: Optional[str] = None


class SendEmailRequest(BaseModel):
    recipient_email: str
    subject: str
    message: str
    grievance_id: Optional[str] = None


class AssignmentResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


@router.get("/me")
async def get_officer_profile(user: dict = Depends(get_current_user)):
    """Get current officer's profile."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        # Fetch user details
        result = supabase.table("users").select("*").eq("id", user.get("user_id")).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Officer not found"}
        
        officer = result.data[0]
        return {
            "success": True,
            "data": {
                "user_id": officer.get("id"),
                "email": officer.get("email"),
                "full_name": officer.get("full_name"),
                "role": officer.get("role"),
                "ward": officer.get("ward"),
                "phone": officer.get("phone"),
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Get officer profile error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/assignments")
async def get_my_assignments(
    user: dict = Depends(require_roles("officer", "admin", "auditor")),
    status_filter: Optional[str] = None,
):
    """Get assignments for the current officer."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": [], "error": "Database not configured"}
    
    try:
        officer_id = user.get("user_id")
        
        # Get assignments for this officer
        query = supabase.table("assignments").select("*").eq("officer_id", officer_id)
        
        if status_filter and status_filter in ["assigned", "in_progress", "completed"]:
            query = query.eq("status", status_filter)
        else:
            # By default, exclude completed assignments
            query = query.neq("status", "completed")
        
        result = query.order("assigned_at", desc=True).execute()
        assignments = result.data or []
        
        # Enrich with grievance data
        enriched = []
        for assignment in assignments:
            grievance_id = assignment.get("grievance_id")
            grievance_result = supabase.table("grievances").select("*").eq("id", grievance_id).execute()
            
            if grievance_result.data:
                grievance = grievance_result.data[0]
                enriched.append({
                    "assignment_id": assignment.get("id"),
                    "grievance_id": grievance_id,
                    "assigned_at": assignment.get("assigned_at"),
                    "status": assignment.get("status"),
                    "notes": assignment.get("notes"),
                    "grievance": {
                        "id": grievance.get("id"),
                        "citizen_name": grievance.get("citizen_name"),
                        "phone": grievance.get("phone"),
                        "ward": grievance.get("ward"),
                        "category": grievance.get("category"),
                        "urgency": grievance.get("urgency"),
                        "description": grievance.get("description"),
                        "ai_summary": grievance.get("ai_summary"),
                        "status": grievance.get("status"),
                        "created_at": grievance.get("created_at"),
                        "cluster_id": grievance.get("cluster_id"),
                    },
                })
        
        return {
            "success": True,
            "data": enriched,
            "error": None,
        }
    except Exception as e:
        logger.error("Get assignments error: %s", str(e))
        return {"success": False, "data": [], "error": str(e)}


@router.post("/assignments/{grievance_id}/assign")
async def assign_grievance(
    grievance_id: str,
    req: AssignRequest,
    user: dict = Depends(require_roles("admin", "auditor")),
):
    """Assign a grievance to an officer (admin/auditor only)."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        officer_id = req.officer_id
        notes = sanitize_string(req.notes, max_length=500) if req.notes else ""
        
        # Verify grievance exists
        grievance_result = supabase.table("grievances").select("id").eq("id", grievance_id).execute()
        if not grievance_result.data:
            return {"success": False, "data": None, "error": "Grievance not found"}
        
        # Verify officer exists
        officer_result = supabase.table("users").select("id").eq("id", officer_id).eq("role", "officer").execute()
        if not officer_result.data:
            return {"success": False, "data": None, "error": "Officer not found or not active"}
        
        # Check if already assigned
        existing = supabase.table("assignments").select("id").eq("grievance_id", grievance_id).neq("status", "completed").execute()
        if existing.data:
            return {"success": False, "data": None, "error": "Grievance already assigned"}
        
        # Create assignment
        assignment_data = {
            "grievance_id": grievance_id,
            "officer_id": officer_id,
            "status": "assigned",
            "notes": notes,
        }
        
        result = supabase.table("assignments").insert(assignment_data).execute()
        
        if not result.data:
            return {"success": False, "data": None, "error": "Failed to create assignment"}
        
        assignment = result.data[0]
        
        # Log action
        log_action_data = {
            "grievance_id": grievance_id,
            "action_type": "assigned",
            "performed_by": user.get("user_id"),
            "notes": f"Assigned to officer {officer_id}: {notes}",
        }
        supabase.table("actions").insert(log_action_data).execute()
        
        logger.info(f"Assigned grievance {grievance_id} to officer {officer_id}")
        
        # Send SMS to officer about assignment
        grievance = grievance_result.data[0]
        officer_phone = officer_result.data[0].get("phone")
        if officer_phone:
            sms_success, sms_message = send_assignment_notification(
                officer_phone,
                grievance.get("category", "Issue"),
                grievance.get("citizen_name", "Citizen"),
                grievance.get("ward", "Unknown Ward")
            )
            logger.info(f"Officer SMS: {sms_message}")
        
        return {
            "success": True,
            "data": {
                "assignment_id": assignment.get("id"),
                "grievance_id": grievance_id,
                "officer_id": officer_id,
                "status": "assigned",
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Assign grievance error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.put("/grievances/{grievance_id}/status")
async def update_grievance_status(
    grievance_id: str,
    req: StatusUpdateRequest,
    user: dict = Depends(require_roles("officer", "admin", "auditor")),
):
    """Update grievance status (in_progress, resolved, rejected)."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        officer_id = user.get("user_id")
        new_status = req.status.lower()
        notes = sanitize_string(req.notes, max_length=500) if req.notes else ""
        
        # Validate status
        if new_status not in ["in_progress", "resolved", "rejected"]:
            return {"success": False, "data": None, "error": "Invalid status"}
        
        # Verify grievance exists
        grievance_result = supabase.table("grievances").select("*").eq("id", grievance_id).execute()
        if not grievance_result.data:
            return {"success": False, "data": None, "error": "Grievance not found"}
        
        grievance = grievance_result.data[0]
        
        # Update grievance status
        update_data = {"status": new_status}
        
        if new_status == "resolved":
            update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()
            # For demo: set resolution_confirmed to False (needs citizen confirmation)
            update_data["resolution_confirmed"] = False
        
        supabase.table("grievances").update(update_data).eq("id", grievance_id).execute()
        
        # Update assignment status if exists
        assignment_result = supabase.table("assignments").select("id").eq("grievance_id", grievance_id).neq("status", "completed").execute()
        if assignment_result.data:
            assignment = assignment_result.data[0]
            assignment_status = "in_progress" if new_status == "in_progress" else "completed"
            supabase.table("assignments").update({"status": assignment_status}).eq("id", assignment.get("id")).execute()
        
        # Log action
        log_action_data = {
            "grievance_id": grievance_id,
            "action_type": f"status_updated_{new_status}",
            "performed_by": officer_id,
            "notes": notes,
        }
        supabase.table("actions").insert(log_action_data).execute()
        
        logger.info(f"Updated grievance {grievance_id} status to {new_status} by officer {officer_id}")
        
        # Send SMS to citizen about status update
        citizen_phone = grievance.get("phone")
        if citizen_phone:
            tracking_url = f"https://nyayasetu.local/track/{grievance_id}"
            sms_success, sms_message = send_status_update_notification(
                citizen_phone,
                grievance_id,
                new_status,
                tracking_url
            )
            logger.info(f"Citizen SMS: {sms_message}")
        
        return {
            "success": True,
            "data": {
                "grievance_id": grievance_id,
                "status": new_status,
                "message": f"Grievance marked as {new_status}",
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Update grievance status error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/stats")
async def get_officer_stats(
    user: dict = Depends(require_roles("officer", "admin", "auditor")),
):
    """Get officer's personal stats."""
    from main import supabase
    if not supabase:
        return {
            "success": False,
            "data": {
                "total_assignments": 0,
                "active": 0,
                "resolved": 0,
                "pending_confirmation": 0,
            },
            "error": "Database not configured",
        }
    
    try:
        officer_id = user.get("user_id")
        
        # Get all assignments for this officer
        assignments_result = supabase.table("assignments").select("*").eq("officer_id", officer_id).execute()
        assignments = assignments_result.data or []
        
        total = len(assignments)
        active = sum(1 for a in assignments if a.get("status") in ["assigned", "in_progress"])
        completed = sum(1 for a in assignments if a.get("status") == "completed")
        
        # Get grievances with pending confirmation
        pending_result = supabase.table("grievances").select("id").eq("status", "resolved").eq("resolution_confirmed", False).eq("officer_id", officer_id).execute()
        pending = len(pending_result.data or [])
        
        return {
            "success": True,
            "data": {
                "total_assignments": total,
                "active": active,
                "resolved": completed,
                "pending_confirmation": pending,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Get officer stats error: %s", str(e))
        return {
            "success": False,
            "data": {
                "total_assignments": 0,
                "active": 0,
                "resolved": 0,
                "pending_confirmation": 0,
            },
            "error": str(e),
        }


@router.post("/send-email")
async def send_officer_email(req: SendEmailRequest):
    """Send email to citizen or prescribed person regarding grievance."""
    from utils.email_service import send_email_smtp
    
    try:
        # For demo: use default officer_id if no user
        officer_id = "demo_officer"
        recipient_email = req.recipient_email.strip()
        subject = sanitize_string(req.subject, max_length=200)
        message = sanitize_string(req.message, max_length=2000)
        
        # Validate email format (basic check)
        if "@" not in recipient_email or "." not in recipient_email:
            return {"success": False, "data": None, "error": "Invalid email format"}
        
        # Build email body
        email_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">Message from Grievance Officer</h2>
                    
                    <div style="margin: 20px 0;">
                        <p><strong>Subject:</strong> {subject}</p>
                        <hr/>
                        <p>{message}</p>
                    </div>
                    
                    {f'<p style="margin-top: 20px; font-size: 12px; color: #7f8c8d;"><strong>Grievance ID:</strong> {req.grievance_id}</p>' if req.grievance_id else ''}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; font-size: 12px; color: #7f8c8d;">
                        <p>This is an automated email from NyayaSetu - Grievance Management System</p>
                        <p>For further assistance, please contact the grievance department.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Send email via SMTP
        success = send_email_smtp(
            to_email=recipient_email,
            subject=subject,
            html_content=email_body,
        )
        
        if success:
            # Log the email action
            if req.grievance_id:
                log_action_data = {
                    "grievance_id": req.grievance_id,
                    "action_type": "email_sent",
                    "performed_by": officer_id,
                    "notes": f"Email sent to {recipient_email} with subject: {subject}",
                }
                try:
                    from main import supabase
                    if supabase:
                        supabase.table("actions").insert(log_action_data).execute()
                except Exception as e:
                    logger.warning("Failed to log email action: %s", str(e))
            
            logger.info(f"Email sent by officer {officer_id} to {recipient_email}")
            return {
                "success": True,
                "data": {
                    "recipient": recipient_email,
                    "subject": subject,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                },
                "error": None,
            }
        else:
            logger.error(f"Failed to send email to {recipient_email}")
            return {
                "success": False,
                "data": None,
                "error": "Failed to send email. Check server logs.",
            }
    except Exception as e:
        logger.error("Send email error: %s", str(e))
        return {
            "success": False,
            "data": None,
            "error": str(e),
        }
