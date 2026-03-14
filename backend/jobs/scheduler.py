import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


async def run_cluster_detection():
    """Run cluster detection on unclustered grievances."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8000/api/cluster")
            if response.status_code == 200:
                data = response.json()
                created = data.get("data", {}).get("clusters_created", 0)
                if created > 0:
                    logger.info("Cluster detection: %d clusters created", created)
            else:
                logger.error("Cluster detection failed: %s", response.status_code)
    except Exception as e:
        logger.error("Cluster detection job error: %s", str(e))


def check_sla_breaches():
    """Find grievances open > 48hrs and mark as breached."""
    try:
        from main import supabase
        threshold = datetime.now(timezone.utc) - timedelta(hours=48)
        threshold_str = threshold.isoformat()

        result = supabase.table("grievances").select("id, created_at").eq("status", "open").lt("created_at", threshold_str).execute()
        grievances = result.data or []

        for g in grievances:
            gid = g.get("id")
            try:
                supabase.table("grievances").update({"status": "breached"}).eq("id", gid).execute()
                supabase.table("actions").insert({
                    "grievance_id": gid,
                    "action_type": "breach_detected",
                    "performed_by": "system",
                    "notes": "SLA breach: complaint open for more than 48 hours",
                }).execute()
                logger.info("SLA breach detected for grievance %s", gid)
            except Exception as inner_e:
                logger.error("Failed to mark breach for %s: %s", gid, str(inner_e))

    except Exception as e:
        logger.error("SLA breach check job error: %s", str(e))


def check_fake_closures():
    """Find resolved grievances where citizen hasn't confirmed within 2 minutes. Auto-reopen."""
    try:
        from main import supabase
        # 2-minute timeout for demo (would be 48hrs in production)
        threshold = datetime.now(timezone.utc) - timedelta(minutes=2)
        threshold_str = threshold.isoformat()

        result = (
            supabase.table("grievances")
            .select("id, resolved_at, citizen_name")
            .eq("status", "resolved")
            .eq("resolution_confirmed", False)
            .lt("resolved_at", threshold_str)
            .execute()
        )
        grievances = result.data or []

        for g in grievances:
            gid = g.get("id")
            try:
                supabase.table("grievances").update({
                    "status": "reopened",
                    "resolved_at": None,
                }).eq("id", gid).execute()
                supabase.table("actions").insert({
                    "grievance_id": gid,
                    "action_type": "reopened",
                    "performed_by": "system",
                    "notes": "Auto-reopened: citizen did not confirm resolution within 2 minutes",
                }).execute()
                logger.info("Fake closure detected, reopened grievance %s", gid)
            except Exception as inner_e:
                logger.error("Failed to reopen %s: %s", gid, str(inner_e))

    except Exception as e:
        logger.error("Fake closure check job error: %s", str(e))
