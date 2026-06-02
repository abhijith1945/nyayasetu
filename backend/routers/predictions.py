"""
Predictions router: ML endpoints for forecasting, trends, and risk analysis.
"""
import logging
from fastapi import APIRouter, Depends
from typing import Optional
from datetime import datetime, timezone, timedelta

from utils.auth import get_current_user, require_roles
from utils.db_helpers import is_table_missing
from utils.ml_models import (
    predict_resolution_time,
    calculate_sla_breach_risk,
    analyze_trends,
    calculate_cluster_quality,
    predict_cluster_resolution_time,
    get_high_risk_grievances,
    generate_ml_report,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.get("")
async def get_predictions(
    limit: int = 20,
):
    """Get prediction summary (high-risk grievances and trends)."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": [], "error": "Database not configured"}
    
    try:
        # Get high-risk grievances
        result = supabase.table("grievances").select("*").eq("status", "open").execute()
        grievances = result.data or []
        
        high_risk = get_high_risk_grievances(grievances, threshold=0.7)
        high_risk = high_risk[:limit]
        
        # Transform to prediction format for frontend
        predictions = []
        for g in high_risk:
            pred = predict_resolution_time(g)
            risk = calculate_sla_breach_risk(g)
            
            # Determine trend (this is simplified - in real scenario would analyze historical data)
            trend = "rising" if risk.get("risk_score", 0) > 0.8 else "falling" if risk.get("risk_score", 0) < 0.5 else "stable"
            
            predictions.append({
                "id": g.get("id"),
                "grievance_id": g.get("id"),
                "category": g.get("category"),
                "ward": g.get("ward"),
                "trend": trend,
                "predicted_count": 1,
                "confidence": risk.get("risk_score", 0.5),
                "description": g.get("description"),
                "urgency": g.get("urgency"),
                "prediction": pred,
                "risk_assessment": risk,
            })
        
        return {
            "success": True,
            "data": predictions,
            "error": None,
        }
    except Exception as e:
        logger.error("Get predictions error: %s", str(e))
        return {"success": True, "data": [], "error": None}


@router.get("/grievance/{grievance_id}/resolution-time")
async def get_grievance_resolution_time(
    grievance_id: str,
    user: dict = Depends(get_current_user),
):
    """Predict resolution time for a specific grievance."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        result = supabase.table("grievances").select("*").eq("id", grievance_id).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Grievance not found"}
        
        grievance = result.data[0]
        prediction = predict_resolution_time(grievance)
        
        return {
            "success": True,
            "data": {
                "grievance_id": grievance_id,
                "prediction": prediction,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Resolution time prediction error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/grievance/{grievance_id}/sla-risk")
async def get_grievance_sla_risk(
    grievance_id: str,
    user: dict = Depends(get_current_user),
):
    """Calculate SLA breach risk for a grievance."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        result = supabase.table("grievances").select("*").eq("id", grievance_id).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Grievance not found"}
        
        grievance = result.data[0]
        
        try:
            created = datetime.fromisoformat(grievance["created_at"].replace("Z", "+00:00"))
            hours_since = (datetime.now(timezone.utc) - created).total_seconds() / 3600
        except:
            hours_since = 0
        
        risk_data = calculate_sla_breach_risk(grievance, hours_since)
        
        return {
            "success": True,
            "data": {
                "grievance_id": grievance_id,
                "hours_since_submission": round(hours_since, 1),
                "risk_assessment": risk_data,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("SLA risk calculation error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/trends")
async def get_grievance_trends(
    days: int = 30,
    user: dict = Depends(require_roles("officer", "admin", "auditor")),
):
    """Analyze grievance trends over specified days."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        result = supabase.table("grievances").select("*").gte("created_at", cutoff_date).execute()
        
        grievances = result.data or []
        trends = analyze_trends(grievances, days=days)
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "analysis": trends,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Trends analysis error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/high-risk")
async def get_high_risk_grievances_endpoint(
    threshold: float = 0.7,
    user: dict = Depends(require_roles("officer", "admin", "auditor")),
):
    """Get all grievances at high risk of SLA breach."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        result = supabase.table("grievances").select("*").eq("status", "open").execute()
        grievances = result.data or []
        
        high_risk = get_high_risk_grievances(grievances, threshold)
        high_risk = high_risk[:20]  # Top 20
        
        return {
            "success": True,
            "data": {
                "threshold": threshold,
                "high_risk_count": len(high_risk),
                "grievances": high_risk,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("High-risk grievances error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/cluster/{cluster_id}/quality")
async def get_cluster_quality(
    cluster_id: str,
    user: dict = Depends(get_current_user),
):
    """Calculate quality score for a cluster."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        result = supabase.table("clusters").select("*").eq("id", cluster_id).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Cluster not found"}
        
        cluster = result.data[0]
        
        grievances_result = supabase.table("grievances").select("*").eq("cluster_id", cluster_id).execute()
        grievances = grievances_result.data or []
        
        quality = calculate_cluster_quality(cluster, grievances)
        
        return {
            "success": True,
            "data": {
                "cluster_id": cluster_id,
                "quality_metrics": quality,
                "grievance_count": len(grievances),
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Cluster quality calculation error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/cluster/{cluster_id}/resolution-time")
async def get_cluster_resolution_time(
    cluster_id: str,
    user: dict = Depends(get_current_user),
):
    """Predict resolution time for all grievances in a cluster."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        result = supabase.table("grievances").select("*").eq("cluster_id", cluster_id).execute()
        grievances = result.data or []
        
        if not grievances:
            return {"success": False, "data": None, "error": "No grievances in cluster"}
        
        cluster_result = supabase.table("clusters").select("*").eq("id", cluster_id).execute()
        cluster = cluster_result.data[0] if cluster_result.data else {}
        
        prediction = predict_cluster_resolution_time(cluster, grievances)
        
        return {
            "success": True,
            "data": {
                "cluster_id": cluster_id,
                "prediction": prediction,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Cluster resolution prediction error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/report")
async def get_comprehensive_ml_report(
    days: int = 30,
    user: dict = Depends(require_roles("admin", "auditor")),
):
    """Generate comprehensive ML insights and recommendations."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        grievances_result = supabase.table("grievances").select("*").gte("created_at", cutoff_date).execute()
        grievances = grievances_result.data or []
        
        clusters_result = supabase.table("clusters").select("*").gte("created_at", cutoff_date).execute()
        clusters = clusters_result.data or []
        
        report = generate_ml_report(grievances, clusters)
        
        return {
            "success": True,
            "data": report,
            "error": None,
        }
    except Exception as e:
        logger.error("ML report generation error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.post("/run")
async def trigger_predictions_refresh(
    user: dict = Depends(require_roles("officer", "admin", "auditor")),
):
    """Manually trigger predictions refresh (normally runs on background schedule)."""
    from main import supabase
    
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    
    try:
        result = supabase.table("grievances").select("*").eq("status", "open").execute()
        open_grievances = result.data or []
        
        predictions = {}
        high_risk_count = 0
        
        for g in open_grievances:
            gid = g.get("id")
            pred = predict_resolution_time(g)
            risk = calculate_sla_breach_risk(g)
            
            predictions[gid] = {
                "resolution_prediction": pred,
                "sla_risk": risk,
            }
            
            if risk["risk_score"] >= 0.7:
                high_risk_count += 1
        
        return {
            "success": True,
            "data": {
                "grievances_processed": len(open_grievances),
                "high_risk_count": high_risk_count,
                "predictions_calculated": len(predictions),
                "sample_predictions": dict(list(predictions.items())[:3]),
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Predictions refresh error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}
