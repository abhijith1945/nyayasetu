import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from utils.groq_client import explain_436a

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/legal", tags=["Legal"])


class LegalCaseCreate(BaseModel):
    prisoner_name: str
    ward: Optional[str] = None
    ipc_section: Optional[str] = None
    max_sentence_years: Optional[int] = None
    detention_start: Optional[str] = None
    months_detained: Optional[int] = None
    dlsa_contact: Optional[str] = None
    grievance_id: Optional[str] = None


@router.get("")
async def get_legal_cases():
    """Get all legal cases with 436A eligibility computed in-memory."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": [], "error": "Database not configured"}
    try:
        result = supabase.table("legal_cases").select("*").order("created_at", desc=True).execute()
        cases = result.data or []

        # Compute 436A eligibility in-memory only (no DB writes)
        for case in cases:
            max_years = case.get("max_sentence_years") or 0
            months = case.get("months_detained") or 0
            half_max_months = (max_years * 12) // 2
            eligible = months >= half_max_months if half_max_months > 0 else False
            case["eligible_436a"] = eligible
            case["half_max_months"] = half_max_months

        return {"success": True, "data": cases, "error": None}
    except Exception as e:
        logger.error("Get legal cases error: %s", str(e))
        return {"success": False, "data": [], "error": str(e)}


@router.post("")
async def create_legal_case(req: LegalCaseCreate):
    """Add a new legal case."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        case_data = {
            "prisoner_name": req.prisoner_name,
            "ward": req.ward,
            "ipc_section": req.ipc_section,
            "max_sentence_years": req.max_sentence_years,
            "detention_start": req.detention_start,
            "months_detained": req.months_detained,
            "dlsa_contact": req.dlsa_contact,
            "grievance_id": req.grievance_id,
        }

        max_years = req.max_sentence_years or 0
        months = req.months_detained or 0
        half_max_months = (max_years * 12) // 2
        case_data["eligible_436a"] = months >= half_max_months if half_max_months > 0 else False

        result = supabase.table("legal_cases").insert(case_data).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Failed to create legal case"}

        return {"success": True, "data": result.data[0], "error": None}
    except Exception as e:
        logger.error("Create legal case error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/check/{case_id}")
async def check_eligibility(case_id: str):
    """Get 436A explanation for a case."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        result = supabase.table("legal_cases").select("*").eq("id", case_id).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Case not found"}

        case = result.data[0]
        max_years = case.get("max_sentence_years") or 0
        months = case.get("months_detained") or 0
        half_max_months = (max_years * 12) // 2
        eligible = months >= half_max_months if half_max_months > 0 else False

        explanation = await explain_436a(
            prisoner_name=case.get("prisoner_name", "Unknown"),
            ipc_section=case.get("ipc_section", "Unknown"),
            max_years=max_years,
            months_detained=months,
            eligible=eligible,
        )

        return {
            "success": True,
            "data": {
                "case": case,
                "eligible": eligible,
                "half_max_months": half_max_months,
                "explanation": explanation,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Check eligibility error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}
