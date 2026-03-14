import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from utils.hashing import generate_hash, generate_action_hash
from utils.groq_client import analyse_grievance

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Grievances"])


class GrievanceCreate(BaseModel):
    citizen_name: str
    phone: Optional[str] = None
    ward: str
    description: str
    category: Optional[str] = None


def log_action(supabase, grievance_id: str, action_type: str, performed_by: str = "system", notes: str = ""):
    try:
        now = datetime.now(timezone.utc).isoformat()
        action_data = {
            "grievance_id": grievance_id,
            "action_type": action_type,
            "performed_by": performed_by,
            "notes": notes,
        }
        result = supabase.table("actions").insert(action_data).execute()
        if result.data:
            action = result.data[0]
            action_hash = generate_action_hash(
                action.get("id", ""),
                grievance_id,
                action_type,
                action.get("created_at", now),
            )
            supabase.table("actions").update({"hash": action_hash}).eq("id", action["id"]).execute()
    except Exception as e:
        logger.error("Failed to log action: %s", str(e))


@router.post("/grievances")
async def create_grievance(req: GrievanceCreate):
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        analysis = await analyse_grievance(req.description, req.ward)
        grievance_data = {
            "citizen_name": req.citizen_name,
            "phone": req.phone,
            "ward": req.ward,
            "description": req.description,
            "category": req.category or analysis.get("category", "other"),
            "urgency": analysis.get("urgency", 3),
            "credibility_score": analysis.get("credibility_score", 50),
            "ai_summary": analysis.get("summary", req.description[:50]),
            "status": "open",
        }
        result = supabase.table("grievances").insert(grievance_data).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Failed to insert grievance"}
        grievance = result.data[0]
        gid = grievance["id"]
        hash_val = generate_hash(gid, grievance.get("created_at", ""), req.description)
        supabase.table("grievances").update({"hash": hash_val}).eq("id", gid).execute()
        log_action(supabase, gid, "submitted", performed_by="citizen", notes=f"Complaint submitted by {req.citizen_name}")
        grievance["hash"] = hash_val
        return {
            "success": True,
            "data": {"grievance": grievance, "hash": hash_val, "ai_analysis": analysis},
            "error": None,
        }
    except Exception as e:
        logger.error("Create grievance error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/grievances")
async def get_grievances(
    status: Optional[str] = None,
    category: Optional[str] = None,
    ward: Optional[str] = None,
    limit: int = 50,
):
    from main import supabase
    if not supabase:
        return {"success": False, "data": [], "error": "Database not configured"}
    try:
        query = supabase.table("grievances").select("*")
        if status:
            query = query.eq("status", status)
        if category:
            query = query.eq("category", category)
        if ward:
            query = query.eq("ward", ward)
        result = query.order("created_at", desc=True).limit(limit).execute()
        return {"success": True, "data": result.data or [], "error": None}
    except Exception as e:
        logger.error("Get grievances error: %s", str(e))
        return {"success": False, "data": [], "error": str(e)}


@router.get("/grievances/{grievance_id}")
async def get_grievance(grievance_id: str):
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        g_result = supabase.table("grievances").select("*").eq("id", grievance_id).execute()
        if not g_result.data:
            return {"success": False, "data": None, "error": "Grievance not found"}
        a_result = supabase.table("actions").select("*").eq("grievance_id", grievance_id).order("created_at", desc=False).execute()
        return {
            "success": True,
            "data": {"grievance": g_result.data[0], "actions": a_result.data or []},
            "error": None,
        }
    except Exception as e:
        logger.error("Get grievance error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.patch("/grievances/{grievance_id}/resolve")
async def resolve_grievance(grievance_id: str):
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        now = datetime.now(timezone.utc).isoformat()
        supabase.table("grievances").update({"status": "resolved", "resolved_at": now}).eq("id", grievance_id).execute()
        g_result = supabase.table("grievances").select("phone, citizen_name").eq("id", grievance_id).execute()
        phone = g_result.data[0].get("phone") if g_result.data else None
        sms_sent = False
        if phone:
            try:
                import os
                from twilio.rest import Client as TwilioClient
                sid = os.getenv("TWILIO_ACCOUNT_SID", "")
                token = os.getenv("TWILIO_AUTH_TOKEN", "")
                from_number = os.getenv("TWILIO_FROM_NUMBER", "")
                if sid and token and from_number and sid != "your_twilio_sid":
                    twilio_client = TwilioClient(sid, token)
                    msg_body = f"Your complaint #{grievance_id[:8]} has been marked resolved. Reply YES to confirm or it will be reopened in 2 minutes."
                    twilio_client.messages.create(body=msg_body, from_=from_number, to=phone)
                    sms_sent = True
                else:
                    logger.info("Twilio not configured. SMS would be sent to %s for complaint %s", phone, grievance_id[:8])
            except Exception as sms_err:
                logger.error("Failed to send SMS: %s", str(sms_err))
        log_action(supabase, grievance_id, "resolved", performed_by="officer", notes="Marked resolved by officer")
        if sms_sent:
            log_action(supabase, grievance_id, "sms_sent", notes=f"SMS sent to {phone}")
        return {
            "success": True,
            "data": {"message": "SMS sent to citizen" if sms_sent else "Resolved (SMS not sent - check Twilio config)"},
            "error": None,
        }
    except Exception as e:
        logger.error("Resolve grievance error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.patch("/grievances/{grievance_id}/confirm")
async def confirm_resolution(grievance_id: str):
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        supabase.table("grievances").update({"resolution_confirmed": True, "status": "closed"}).eq("id", grievance_id).execute()
        log_action(supabase, grievance_id, "resolved", performed_by="citizen", notes="Resolution confirmed by citizen")
        return {"success": True, "data": {"message": "Resolution confirmed. Thank you!"}, "error": None}
    except Exception as e:
        logger.error("Confirm resolution error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}
