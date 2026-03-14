import logging
from fastapi import APIRouter
from utils.groq_client import generate_brief

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# Hardcoded Kerala ward coordinates
WARD_COORDS = {
    "Ward 1 (Kazhakoottam)": {"lat": 8.5667, "lng": 76.8721},
    "Ward 2 (Technopark)": {"lat": 8.5500, "lng": 76.8800},
    "Ward 3 (Pattom)": {"lat": 8.5241, "lng": 76.9366},
    "Ward 4 (Vanchiyoor)": {"lat": 8.4875, "lng": 76.9525},
    "Ward 5 (Palayam)": {"lat": 8.5005, "lng": 76.9536},
    "Ward 6 (Karamana)": {"lat": 8.4700, "lng": 76.9700},
    "Ward 7 (Nemom)": {"lat": 8.4500, "lng": 76.9600},
    "Ward 8 (Kovalam)": {"lat": 8.3988, "lng": 76.9820},
}


@router.get("/stats")
async def get_stats():
    """Get main dashboard statistics."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": {"total": 0, "open": 0, "resolved": 0, "critical": 0, "clusters_active": 0, "sla_breaches": 0}, "error": "Database not configured"}
    try:
        all_result = supabase.table("grievances").select("id, status, urgency").execute()
        grievances = all_result.data or []

        total = len(grievances)
        open_count = sum(1 for g in grievances if g.get("status") == "open")
        resolved = sum(1 for g in grievances if g.get("status") in ("resolved", "closed"))
        critical = sum(1 for g in grievances if (g.get("urgency") or 0) >= 4)
        breached = sum(1 for g in grievances if g.get("status") == "breached")

        clusters_result = supabase.table("clusters").select("id").execute()
        clusters_active = len(clusters_result.data or [])

        return {
            "success": True,
            "data": {
                "total": total,
                "open": open_count,
                "resolved": resolved,
                "critical": critical,
                "clusters_active": clusters_active,
                "sla_breaches": breached,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Dashboard stats error: %s", str(e))
        return {"success": False, "data": {"total": 0, "open": 0, "resolved": 0, "critical": 0, "clusters_active": 0, "sla_breaches": 0}, "error": str(e)}


@router.get("/clusters")
async def get_clusters():
    """Get all active clusters with member grievances."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": [], "error": "Database not configured"}
    try:
        result = supabase.table("clusters").select("*").order("created_at", desc=True).execute()
        clusters = result.data or []

        for cluster in clusters:
            member_ids = cluster.get("member_ids") or []
            if member_ids:
                members_result = supabase.table("grievances").select("id, citizen_name, description, ai_summary, urgency, status").in_("id", member_ids).execute()
                cluster["members"] = members_result.data or []
            else:
                cluster["members"] = []

        return {"success": True, "data": clusters, "error": None}
    except Exception as e:
        logger.error("Dashboard clusters error: %s", str(e))
        return {"success": False, "data": [], "error": str(e)}


@router.get("/map")
async def get_map_data():
    """Get ward-level complaint counts for map visualization."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": [], "error": "Database not configured"}
    try:
        result = supabase.table("grievances").select("ward, urgency").execute()
        grievances = result.data or []

        ward_data = {}
        for g in grievances:
            ward = g.get("ward", "Unknown")
            if ward not in ward_data:
                ward_data[ward] = {"count": 0, "critical_count": 0}
            ward_data[ward]["count"] += 1
            if (g.get("urgency") or 0) >= 4:
                ward_data[ward]["critical_count"] += 1

        map_points = []
        for ward_name, coords in WARD_COORDS.items():
            data = ward_data.get(ward_name, {"count": 0, "critical_count": 0})
            map_points.append({
                "ward": ward_name,
                "count": data["count"],
                "critical_count": data["critical_count"],
                "lat": coords["lat"],
                "lng": coords["lng"],
            })

        return {"success": True, "data": map_points, "error": None}
    except Exception as e:
        logger.error("Dashboard map error: %s", str(e))
        return {"success": False, "data": [], "error": str(e)}


@router.get("/brief")
async def get_brief():
    """Generate and return current week's governance brief."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        clusters_result = supabase.table("clusters").select("*").execute()
        clusters = clusters_result.data or []

        if not clusters:
            return {
                "success": True,
                "data": {"brief": "No active clusters. The system will generate a brief when complaint patterns are detected."},
                "error": None,
            }

        clusters_data = []
        for c in clusters:
            clusters_data.append({
                "category": c.get("category"),
                "ward": c.get("ward"),
                "count": c.get("count"),
                "summary": c.get("summary"),
            })

        brief = await generate_brief(clusters_data)
        return {"success": True, "data": {"brief": brief}, "error": None}
    except Exception as e:
        logger.error("Dashboard brief error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}
