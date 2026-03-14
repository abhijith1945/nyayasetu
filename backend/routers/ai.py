import os
import json
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import numpy as np

from utils.groq_client import analyse_grievance, generate_brief, translate_to_malayalam, explain_436a
from utils.gemini_client import get_embedding

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["AI"])


# --- Request/Response models ---

class AnalyseRequest(BaseModel):
    text: str
    ward: str = "Unknown"

class BriefRequest(BaseModel):
    clusters: list

class EmbedRequest(BaseModel):
    text: str


# --- Endpoints ---

@router.post("/analyse")
async def analyse_endpoint(req: AnalyseRequest):
    """Analyse a grievance with Groq AI."""
    try:
        result = await analyse_grievance(req.text, req.ward)
        return {"success": True, "data": result, "error": None}
    except Exception as e:
        logger.error("Analyse endpoint error: %s", str(e))
        return {
            "success": False,
            "data": {
                "category": "other",
                "urgency": 3,
                "credibility_score": 50,
                "summary": req.text[:50] if req.text else "No description",
                "department": "General Administration",
            },
            "error": str(e),
        }


@router.post("/brief")
async def brief_endpoint(req: BriefRequest):
    """Generate governance intelligence brief."""
    try:
        result = await generate_brief(req.clusters)
        return {"success": True, "data": {"brief": result}, "error": None}
    except Exception as e:
        logger.error("Brief endpoint error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.post("/embed")
async def embed_endpoint(req: EmbedRequest):
    """Get embedding for text (internal use)."""
    try:
        embedding = await get_embedding(req.text)
        if embedding is None:
            return {"success": False, "data": None, "error": "Failed to get embedding"}
        return {"success": True, "data": {"embedding": embedding}, "error": None}
    except Exception as e:
        logger.error("Embed endpoint error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two vectors."""
    try:
        a_arr = np.array(a, dtype=np.float64)
        b_arr = np.array(b, dtype=np.float64)
        dot = np.dot(a_arr, b_arr)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))
    except Exception:
        return 0.0


@router.post("/cluster")
async def cluster_endpoint():
    """Run cluster detection on unclustered open grievances."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        # Fetch open grievances without cluster_id
        result = supabase.table("grievances").select("*").eq("status", "open").is_("cluster_id", "null").execute()
        grievances = result.data or []

        if len(grievances) < 2:
            return {"success": True, "data": {"clusters_created": 0, "message": "Not enough unclustered grievances"}, "error": None}

        # Get embeddings for each grievance
        embeddings = {}
        for g in grievances:
            gid = g.get("id")
            text = g.get("description", "")
            emb = await get_embedding(text)
            if emb is not None:
                embeddings[gid] = {"embedding": emb, "grievance": g}

        if len(embeddings) < 2:
            return {"success": True, "data": {"clusters_created": 0, "message": "Could not get enough embeddings"}, "error": None}

        # Compute pairwise similarities and group
        ids = list(embeddings.keys())
        visited = set()
        clusters_created = 0

        for i, id_a in enumerate(ids):
            if id_a in visited:
                continue
            cluster_members = [id_a]
            visited.add(id_a)

            for j in range(i + 1, len(ids)):
                id_b = ids[j]
                if id_b in visited:
                    continue
                sim = cosine_similarity(embeddings[id_a]["embedding"], embeddings[id_b]["embedding"])
                if sim > 0.75:
                    # Also check same ward or same category
                    g_a = embeddings[id_a]["grievance"]
                    g_b = embeddings[id_b]["grievance"]
                    if g_a.get("ward") == g_b.get("ward") or g_a.get("category") == g_b.get("category"):
                        cluster_members.append(id_b)
                        visited.add(id_b)

            if len(cluster_members) >= 2:
                # Create cluster
                first = embeddings[cluster_members[0]]["grievance"]
                category = first.get("category", "other")
                ward = first.get("ward", "Unknown")
                summaries = [embeddings[m]["grievance"].get("ai_summary", "") or embeddings[m]["grievance"].get("description", "")[:50] for m in cluster_members]
                summary = f"{len(cluster_members)} {category} complaints in {ward}: " + "; ".join(summaries[:3])

                cluster_data = {
                    "category": category,
                    "ward": ward,
                    "member_ids": cluster_members,
                    "summary": summary[:500],
                    "count": len(cluster_members),
                }
                cluster_result = supabase.table("clusters").insert(cluster_data).execute()
                if cluster_result.data:
                    cluster_id = cluster_result.data[0]["id"]
                    for mid in cluster_members:
                        supabase.table("grievances").update({"cluster_id": cluster_id}).eq("id", mid).execute()
                    clusters_created += 1

        return {"success": True, "data": {"clusters_created": clusters_created}, "error": None}
    except Exception as e:
        logger.error("Cluster endpoint error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}


@router.get("/translate/{grievance_id}")
async def translate_endpoint(grievance_id: str):
    """Translate grievance summary to Malayalam."""
    from main import supabase
    if not supabase:
        return {"success": False, "data": None, "error": "Database not configured"}
    try:
        result = supabase.table("grievances").select("ai_summary, description").eq("id", grievance_id).execute()
        if not result.data:
            return {"success": False, "data": None, "error": "Grievance not found"}

        grievance = result.data[0]
        text = grievance.get("ai_summary") or grievance.get("description", "")
        if not text:
            return {"success": False, "data": None, "error": "No text to translate"}

        translated = await translate_to_malayalam(text)
        return {"success": True, "data": {"original": text, "malayalam": translated}, "error": None}
    except Exception as e:
        logger.error("Translate endpoint error: %s", str(e))
        return {"success": False, "data": None, "error": str(e)}
