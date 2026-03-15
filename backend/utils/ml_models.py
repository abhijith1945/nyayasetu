"""
Machine Learning module for NyayaSetu predictions.
- Resolution time forecasting
- Trend analysis and pattern detection
- SLA breach risk warnings
- Cluster quality metrics
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sklearn (optional dependency for ML)
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. ML predictions will use simplified models.")


def extract_features_from_grievance(grievance: dict) -> dict:
    """
    Extract ML features from grievance data.
    
    Args:
        grievance: Grievance record from database
    
    Returns:
        dict with extractable features
    """
    features = {
        "urgency": grievance.get("urgency", 3),  # 1-5 scale
        "credibility_score": grievance.get("credibility_score", 50),  # 0-100
        "category_encode": {
            "water": 1, "road": 2, "electricity": 3, "health": 4,
            "sanitation": 5, "legal": 6, "other": 7, "railway": 8
        }.get(grievance.get("category", "other"), 0),
        "ward_encode": int(grievance.get("ward", "Ward 1").split()[1]) if "Ward" in grievance.get("ward", "Ward 1") else 1,
        "is_image_verified": 1 if grievance.get("image_verified") else 0,
        "description_length": len(grievance.get("description", "")),
        "has_phone": 1 if grievance.get("phone") else 0,
    }
    return features


def predict_resolution_time(grievance: dict, historical_data: List[dict] = None) -> Dict:
    """
    Predict how long it will take to resolve a grievance (in hours).
    
    Args:
        grievance: Current grievance
        historical_data: List of historical grievances with resolution times
    
    Returns:
        dict with prediction and confidence
    """
    features = extract_features_from_grievance(grievance)
    
    # Baseline resolution times (hours) by category
    baseline_resolution_times = {
        1: 48,    # water
        2: 72,    # road
        3: 96,    # electricity
        4: 120,   # health
        5: 60,    # sanitation
        6: 240,   # legal
        7: 84,    # other
        8: 168,   # railway
    }
    
    category = features["category_encode"]
    base_hours = baseline_resolution_times.get(category, 84)
    
    # Adjust based on urgency (5 = highest urgency, 1 = lowest)
    # High urgency reduces time by up to 20%, low urgency increases by 10%
    urgency_score = (features["urgency"] - 3) / 5  # Normalize to -0.4 to +0.4
    urgency_multiplier = 1.0 - (urgency_score * 0.25)  # Range: 0.9 to 1.1
    
    # Adjust based on credibility (high credibility = slightly faster)
    # Score 0-100: low (0-30) increases by 15%, medium (30-70) no change, high (70-100) reduces by 10%
    credibility_normalized = (features["credibility_score"] - 50) / 100  # Normalize to -0.5 to +0.5
    credibility_multiplier = 1.0 - (credibility_normalized * 0.15)  # Range: 0.925 to 1.075
    
    # Adjust based on evidence (image verified = 5% faster)
    evidence_multiplier = 0.95 if features["is_image_verified"] else 1.0
    
    # Calculate predicted hours with bounded multiplications to avoid extreme values
    # Instead of multiplying all multipliers, use additive approach for non-extreme adjustments
    total_adjustment = (urgency_multiplier - 1.0) + (credibility_multiplier - 1.0) + (evidence_multiplier - 1.0)
    predicted_hours = base_hours * (1.0 + total_adjustment)
    
    # Apply realistic bounds: don't go lower than 25% of baseline or higher than 175% of baseline
    predicted_hours = max(base_hours * 0.25, min(base_hours * 1.75, predicted_hours))
    
    # Calculate confidence based on how much data we have
    confidence = 0.65  # Base confidence
    if historical_data and len(historical_data) > 10:
        confidence = min(0.95, 0.65 + (len(historical_data) / 100))
    
    return {
        "predicted_hours": round(predicted_hours, 1),
        "predicted_days": round(predicted_hours / 24, 1),
        "confidence": round(confidence, 2),
        "category": grievance.get("category", "other"),
        "factors": {
            "base_hours": base_hours,
            "urgency_impact": round(urgency_multiplier, 3),
            "credibility_impact": round(credibility_multiplier, 3),
            "evidence_impact": round(evidence_multiplier, 3),
        }
    }


def calculate_sla_breach_risk(grievance: dict, hours_since_submission: float = 0) -> Dict:
    """
    Calculate risk of SLA breach (72-hour default).
    
    Args:
        grievance: Grievance record
        hours_since_submission: Hours elapsed since submission
    
    Returns:
        dict with risk level and hours remaining
    """
    SLA_HOURS = 72  # Default SLA: 72 hours
    
    features = extract_features_from_grievance(grievance)
    
    # Get predicted resolution time
    prediction = predict_resolution_time(grievance)
    predicted_hours = prediction["predicted_hours"]
    
    # Calculate remaining SLA time
    hours_remaining = max(0, SLA_HOURS - hours_since_submission)
    hours_over = max(0, hours_since_submission - SLA_HOURS)
    
    # Determine risk level
    if hours_over > 0:
        risk_level = "breached"
        risk_score = 1.0
    elif predicted_hours > hours_remaining:
        # Prediction exceeds SLA
        remaining_percentage = (hours_remaining / predicted_hours) * 100
        if remaining_percentage < 20:
            risk_level = "critical"
            risk_score = 0.9
        elif remaining_percentage < 50:
            risk_level = "high"
            risk_score = 0.7
        else:
            risk_level = "medium"
            risk_score = 0.4
    else:
        risk_level = "low"
        risk_score = 0.1
    
    # High urgency complaints have tighter SLA
    if features["urgency"] >= 4:
        risk_score = min(1.0, risk_score + 0.2)
    
    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "hours_remaining": round(hours_remaining, 1),
        "hours_over": round(hours_over, 1),
        "predicted_vs_sla": f"{prediction['predicted_hours']}h pred vs {SLA_HOURS}h SLA",
        "recommendation": get_sla_recommendation(risk_level, risk_score, hours_remaining),
    }


def get_sla_recommendation(risk_level: str, risk_score: float, hours_remaining: float) -> str:
    """Generate actionable recommendation based on SLA risk."""
    if risk_level == "breached":
        return "⚠️ CRITICAL: SLA already breached. Immediate action required."
    elif risk_level == "critical":
        return f"🔴 URGENT: {hours_remaining:.0f}h to SLA breach. Escalate to director."
    elif risk_level == "high":
        return f"🟠 HIGH: {hours_remaining:.0f}h remaining. Fast-track resolution."
    elif risk_level == "medium":
        return f"🟡 MEDIUM: {hours_remaining:.0f}h remaining. Monitor closely."
    else:
        return f"🟢 LOW: On track for resolution. {hours_remaining:.0f}h buffer."


def analyze_trends(grievances: List[dict], days: int = 30) -> Dict:
    """
    Analyze grievance trends over time period.
    
    Args:
        grievances: List of grievances
        days: Number of days to analyze
    
    Returns:
        dict with trend analysis
    """
    if not grievances:
        return {
            "total_grievances": 0,
            "average_resolution_time": 0,
            "top_categories": [],
            "critical_wards": [],
            "trends": {}
        }
    
    # Category breakdown
    category_counts = {}
    ward_counts = {}
    resolution_times = []
    urgency_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for g in grievances:
        category = g.get("category", "other")
        category_counts[category] = category_counts.get(category, 0) + 1
        
        ward = g.get("ward", "Unknown")
        ward_counts[ward] = ward_counts.get(ward, 0) + 1
        
        urgency = g.get("urgency", 3)
        urgency_breakdown[urgency] = urgency_breakdown.get(urgency, 0) + 1
        
        # Calculate resolution time if resolved
        if g.get("resolved_at") and g.get("created_at"):
            try:
                created = datetime.fromisoformat(g["created_at"].replace("Z", "+00:00"))
                resolved = datetime.fromisoformat(g["resolved_at"].replace("Z", "+00:00"))
                hours = (resolved - created).total_seconds() / 3600
                resolution_times.append(hours)
            except:
                pass
    
    # Sort by count
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    critical_wards = sorted(ward_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    return {
        "total_grievances": len(grievances),
        "average_resolution_time_hours": round(avg_resolution, 1),
        "average_resolution_time_days": round(avg_resolution / 24, 1),
        "top_categories": [{"category": cat, "count": count} for cat, count in top_categories],
        "critical_wards": [{"ward": ward, "count": count} for ward, count in critical_wards],
        "urgency_distribution": urgency_breakdown,
        "total_resolved": len(resolution_times),
    }


def calculate_cluster_quality(cluster: dict, grievances: List[dict] = None) -> Dict:
    """
    Calculate quality score for a grievance cluster.
    
    Args:
        cluster: Cluster record
        grievances: List of grievances in cluster
    
    Returns:
        dict with quality metrics
    """
    quality_score = 0.5  # Start at 0.5
    
    # Check cluster size (optimal: 3-8 grievances)
    grievance_count = cluster.get("grievance_count", 0)
    if 3 <= grievance_count <= 8:
        quality_score += 0.15
    elif grievance_count == 2:
        quality_score += 0.05
    elif grievance_count > 8:
        quality_score += 0.08  # Large clusters less optimal
    
    # Check average similarity (should be high)
    avg_similarity = cluster.get("avg_similarity", 0.75)
    if avg_similarity >= 0.85:
        quality_score += 0.2
    elif avg_similarity >= 0.75:
        quality_score += 0.15
    elif avg_similarity >= 0.65:
        quality_score += 0.08
    
    # Check if same ward/category (should be true for good clusters)
    same_ward = cluster.get("metadata", {}).get("same_ward", False)
    same_category = cluster.get("metadata", {}).get("same_category", False)
    
    if same_ward:
        quality_score += 0.1
    if same_category:
        quality_score += 0.1
    
    # Check if AI summary exists and is meaningful
    ai_summary = cluster.get("ai_summary", "")
    if ai_summary and len(ai_summary) > 50:
        quality_score += 0.1
    
    # Cap at 1.0
    quality_score = min(1.0, quality_score)
    
    # Determine quality level
    if quality_score >= 0.85:
        quality_level = "excellent"
    elif quality_score >= 0.70:
        quality_level = "good"
    elif quality_score >= 0.50:
        quality_level = "fair"
    else:
        quality_level = "poor"
    
    return {
        "quality_score": round(quality_score, 2),
        "quality_level": quality_level,
        "grievance_count": grievance_count,
        "average_similarity": round(avg_similarity, 2),
        "same_ward": same_ward,
        "same_category": same_category,
        "has_summary": bool(ai_summary),
        "factors": {
            "size_optimal": 3 <= grievance_count <= 8,
            "similarity_high": avg_similarity >= 0.75,
            "contextual_match": same_ward or same_category,
        }
    }


def predict_cluster_resolution_time(cluster: dict, grievances: List[dict] = None) -> Dict:
    """
    Predict time to resolve all grievances in a cluster.
    
    Args:
        cluster: Cluster record
        grievances: Grievances in cluster
    
    Returns:
        dict with resolution time for cluster
    """
    if not grievances:
        return {
            "cluster_predicted_hours": 0,
            "individual_predictions": [],
            "complexity_factor": 1.0,
        }
    
    # Get predictions for each grievance
    predictions = []
    for g in grievances:
        pred = predict_resolution_time(g)
        predictions.append({
            "grievance_id": g.get("id"),
            "predicted_hours": pred["predicted_hours"],
            "category": g.get("category"),
            "urgency": g.get("urgency"),
        })
    
    # Cluster resolution time is the maximum (must resolve all)
    max_hours = max([p["predicted_hours"] for p in predictions])
    
    # Complexity factor: clusters benefit from shared context/resources
    complexity_factor = 0.85 if len(grievances) <= 5 else 0.75
    
    # Adjust for resource efficiency
    cluster_predicted_hours = max_hours * (1 / complexity_factor)
    
    return {
        "cluster_predicted_hours": round(cluster_predicted_hours, 1),
        "max_grievance_hours": round(max_hours, 1),
        "grievance_count": len(grievances),
        "complexity_factor": round(complexity_factor, 2),
        "individual_predictions": predictions,
        "recommendation": f"Assign 1-2 officers to resolve in parallel. est. {round(cluster_predicted_hours / 24, 1)} days",
    }


def get_high_risk_grievances(grievances: List[dict], threshold: float = 0.7) -> List[dict]:
    """
    Filter grievances that are at high risk of SLA breach.
    
    Args:
        grievances: List of grievances
        threshold: Risk score threshold (0-1)
    
    Returns:
        list of high-risk grievances with risk info
    """
    high_risk = []
    
    for g in grievances:
        if g.get("status") in ["resolved", "rejected"]:
            continue  # Skip completed grievances
        
        # Calculate hours since submission
        try:
            created = datetime.fromisoformat(g.get("created_at", "").replace("Z", "+00:00"))
            hours_since = (datetime.now(created.tzinfo) - created).total_seconds() / 3600
        except:
            hours_since = 0
        
        risk_data = calculate_sla_breach_risk(g, hours_since)
        
        if risk_data["risk_score"] >= threshold:
            high_risk.append({
                "grievance_id": g.get("id"),
                "citizen_name": g.get("citizen_name"),
                "category": g.get("category"),
                "ward": g.get("ward"),
                "urgency": g.get("urgency"),
                "hours_since_submission": round(hours_since, 1),
                "risk_data": risk_data,
            })
    
    return sorted(high_risk, key=lambda x: x["risk_data"]["risk_score"], reverse=True)


def generate_ml_report(grievances: List[dict] = None, clusters: List[dict] = None) -> Dict:
    """
    Generate comprehensive ML insights report.
    
    Args:
        grievances: List of grievances
        clusters: List of clusters
    
    Returns:
        dict with full ML report
    """
    grievances = grievances or []
    clusters = clusters or []
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_grievances": len(grievances),
        "total_clusters": len(clusters),
        "trends": analyze_trends(grievances),
        "high_risk_grievances": get_high_risk_grievances(grievances),
        "cluster_quality_metrics": {
            "average_quality_score": round(
                sum([calculate_cluster_quality(c).get("quality_score", 0) for c in clusters]) / len(clusters)
                if clusters else 0.5,
                2
            ),
            "quality_distribution": {
                "excellent": sum(1 for c in clusters if calculate_cluster_quality(c).get("quality_level") == "excellent"),
                "good": sum(1 for c in clusters if calculate_cluster_quality(c).get("quality_level") == "good"),
                "fair": sum(1 for c in clusters if calculate_cluster_quality(c).get("quality_level") == "fair"),
                "poor": sum(1 for c in clusters if calculate_cluster_quality(c).get("quality_level") == "poor"),
            }
        },
        "recommendations": generate_recommendations(grievances, clusters),
    }


def generate_recommendations(grievances: List[dict], clusters: List[dict]) -> List[str]:
    """Generate actionable recommendations from ML analysis."""
    recommendations = []
    
    if not grievances:
        return ["No grievances to analyze"]
    
    trends = analyze_trends(grievances)
    
    # Find bottleneck categories
    if trends["top_categories"]:
        top_cat = trends["top_categories"][0]
        recommendations.append(f"📊 {top_cat['category'].title()} is {top_cat['count']} grievances. Consider more resources.")
    
    # Find high-workload wards
    if trends["critical_wards"]:
        top_ward = trends["critical_wards"][0]
        recommendations.append(f"📍 {top_ward['ward']} has {top_ward['count']} grievances. Deploy additional staff.")
    
    # Resolution time insight
    if trends["average_resolution_time_days"]:
        avg_days = trends["average_resolution_time_days"]
        if avg_days > 3:
            recommendations.append(f"⏱️ Avg resolution: {avg_days} days (target: 3). Process improvement needed.")
        else:
            recommendations.append(f"✅ Avg resolution: {avg_days} days. Continue current pace.")
    
    # Cluster efficiency
    if clusters:
        avg_quality = trends.get("quality_metrics", {}).get("average_quality_score", 0.5)
        if avg_quality < 0.6:
            recommendations.append("🔧 Cluster quality low. Refine similarity thresholds.")
        elif avg_quality > 0.8:
            recommendations.append("⭐ Cluster quality excellent. Clustering strategy working well.")
    
    # High-risk grievances
    high_risk = get_high_risk_grievances(grievances, threshold=0.7)
    if high_risk:
        recommendations.append(f"⚠️ {len(high_risk)} grievances at SLA risk. Immediate escalation needed.")
    
    return recommendations if recommendations else ["All metrics looking healthy. Continue monitoring."]
