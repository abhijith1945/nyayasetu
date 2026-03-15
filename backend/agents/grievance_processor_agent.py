"""
Autonomous Grievance Processor Agent
Handles end-to-end grievance analysis, verification, and decision-making
Uses ReAct pattern with multi-turn reasoning
"""

import json
import logging
from typing import Dict, List, Any
from .base_agent import BaseAgent, ActionType

logger = logging.getLogger(__name__)


class GrievanceProcessorAgent(BaseAgent):
    """
    Multi-turn autonomous agent that processes grievances completely:
    1. Understands complaint context
    2. Verifies credibility
    3. Categorizes and assesses urgency
    4. Detects patterns (fake closures, duplicates)
    5. Generates action plan
    6. Makes autonomous recommendations
    """
    
    def __init__(self):
        super().__init__(
            name="GrievanceProcessor",
            role="Autonomous Governance Analyst",
            model_name="llama-3.1-8b"
        )
    
    async def act(self, action_type: ActionType, action_data: Dict) -> Dict:
        """Execute agent actions specific to grievance processing"""
        
        if action_type == ActionType.ANALYZE:
            return await self._analyze_grievance(action_data)
        
        elif action_type == ActionType.CHECK_RULES:
            return await self._check_compliance(action_data)
        
        elif action_type == ActionType.RETRIEVE_DATA:
            return await self._retrieve_context(action_data)
        
        return {"status": "unknown_action"}
    
    async def _analyze_grievance(self, grievance_data: Dict) -> Dict:
        """Multi-dimensional grievance analysis"""
        description = grievance_data.get("description", "")
        
        # Analyze with Groq
        from utils.groq_client import call_groq
        
        analysis_prompt = f"""
Analyze this citizen grievance with extreme rigor:

Complaint: {description}

DEEP ANALYSIS - Return JSON:
{{
  "surface_issue": "what citizen explicitly says",
  "root_cause": "what's actually causing this",
  "underlying_systemic_issue": "what policy failure enables this",
  "emotional_analysis": {{
    "anger_level": <1-5>,
    "urgency_indicators": ["indicator1", "indicator2"],
    "credibility_signals": ["signal1", "signal2"],
    "potential_fabrication_signs": ["sign1", "sign2"]
  }},
  "linguistic_markers": {{
    "specificity_score": <0-100>,
    "verifiable_details": ["detail1", "detail2"],
    "vague_generalities": ["vague1", "vague2"]
  }},
  "impact_scope": {{
    "individual_impact": "how it affects citizen",
    "community_impact": "does it affect others",
    "systemic_impact": "implications for governance"
  }}
}}
"""
        response = await call_groq(analysis_prompt)
        
        try:
            analysis = json.loads(response)
            self.thought_log.add_observation("grievance_analysis", analysis)
            return {
                "action": "grievance_analyzed",
                "analysis": analysis,
                "ready_to_decide": False
            }
        except:
            logger.error("Failed to parse grievance analysis")
            return {"action": "grievance_analyzed", "analysis": {}}
    
    async def _check_compliance(self, check_data: Dict) -> Dict:
        """Verify against rules, policies, and fraud indicators"""
        from utils.groq_client import call_groq
        
        grievance_text = check_data.get("description", "")
        previous_grievances = check_data.get("previous_grievances", [])
        
        # Check against policy/rules
        rules_check = f"""
Given this grievance: {grievance_text}

Check against these rules:
1. Is this within government's jurisdiction?
2. Is this a duplicate/harassment?
3. Does it violate any guidelines?
4. Is the citizen threatening?
5. Is it vague to be unactionable?
6. Fraud indicators present? (copy-paste, generic, too perfect)

Return JSON:
{{
  "jurisdiction_valid": true/false,
  "is_legitimate": true/false,
  "fraud_probability": <0-1>,
  "fraud_indicators": ["indicator1", "indicator2"],
  "policy_violations": ["violation1", "violation2"],
  "actionability_score": <0-100>
}}
"""
        response = await call_groq(rules_check)
        
        try:
            compliance = json.loads(response)
            self.thought_log.add_observation("compliance_check", compliance)
            return {
                "action": "compliance_checked",
                "compliance": compliance,
                "ready_to_decide": False
            }
        except:
            return {"action": "compliance_checked", "compliance": {}}
    
    async def _retrieve_context(self, retrieval_data: Dict) -> Dict:
        """Retrieve and analyze relevant context (patterns, similar cases, officer workload)"""
        from main import supabase
        
        if not supabase:
            return {"action": "context_retrieved", "context": {}}
        
        ward = retrieval_data.get("ward", "")
        category = retrieval_data.get("category", "other")
        
        try:
            # Get similar complaints in this ward
            similar = supabase.table("grievances").select("*").eq(
                "ward", ward
            ).eq("category", category).limit(10).execute()
            similar_cases = similar.data or []
            
            # Get stats for ward
            all_ward = supabase.table("grievances").select("*").eq("ward", ward).execute()
            ward_stats = {
                "total_complaints": len(all_ward.data or []),
                "open_count": len([g for g in (all_ward.data or []) if g.get("status") == "open"]),
                "resolution_rate": len([g for g in (all_ward.data or []) if g.get("status") == "resolved"]) / max(len(all_ward.data or []), 1)
            }
            
            self.thought_log.add_observation("ward_context", ward_stats)
            self.thought_log.add_observation("similar_cases", len(similar_cases))
            
            return {
                "action": "context_retrieved",
                "context": {
                    "similar_cases": len(similar_cases),
                    "ward_stats": ward_stats,
                    "recent_patterns": [
                        {
                            "category": g.get("category"),
                            "status": g.get("status"),
                            "created_at": g.get("created_at")
                        }
                        for g in similar_cases[:3]
                    ]
                },
                "ready_to_decide": True  # We have enough context
            }
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return {"action": "context_retrieved", "context": {}}
    
    async def process_grievance(self, grievance_data: Dict, supabase_client=None) -> Dict:
        """
        Main entry point: Full autonomous grievance processing
        
        Input:
        {
            "id": "grievance_id",
            "description": "complaint text",
            "ward": "Ward 5",
            "category": "water",
            "phone": "9999999999",  (auto-extracted if missing)
            "image_data": "base64_or_url"
        }
        
        Output:
        {
            "grievance_id": "id",
            "decision": "accept|reject|escalate|review_required",
            "urgency": 1-5,
            "recommended_actions": [...],
            "confidence": 0.85,
            "reasoning": "why this decision",
            "reasoning_trace": {...},
            "auto_extracted": {
                "name": "auto-detected name",
                "phone": "auto-detected phone",
                "ward": "auto-detected ward"
            }
        }
        """
        
        # ✅ AUTO-EXTRACT NAME AND PHONE FROM DESCRIPTION
        from utils.name_phone_extractor import auto_extract_info
        
        description = grievance_data.get("description", "")
        extracted_info = auto_extract_info(description)
        
        # Use extracted values if not provided
        citizen_name = grievance_data.get("citizen_name") or extracted_info.get("name") or "Unknown"
        phone = grievance_data.get("phone") or extracted_info.get("phone") or "N/A"
        ward = grievance_data.get("ward") or extracted_info.get("ward") or "Unknown Ward"
        
        # Update grievance data with extracted/filled values
        grievance_data_updated = {
            **grievance_data,
            "citizen_name": citizen_name,
            "phone": phone,
            "ward": ward,
        }
        
        self.thought_log.add_observation("auto_extraction", {
            "extracted_name": extracted_info.get("name"),
            "extracted_phone": extracted_info.get("phone"),
            "extraction_confidence": extracted_info.get("extraction_confidence"),
            "methods_used": extracted_info.get("extraction_method")
        })
        
        problem = f"""
Autonomously process this citizen grievance:
- Citizen Name: {citizen_name}
- Description: {description}
- Ward: {ward}
- Category: {grievance_data_updated.get('category', 'other')}
- Phone: {phone}
- Contact Info Confidence: {extracted_info.get('extraction_confidence', 0)}

Decide: Should we accept/escalate/reject this? What actions?
"""
        
        context = {
            "grievance": grievance_data_updated,
            "timestamp": grievance_data_updated.get("created_at"),
            "auto_extracted": extracted_info
        }
        
        # Run agent loop
        result = await self.run(problem, context)
        
        return {
            **result,
            "grievance_id": grievance_data_updated.get("id"),
            "agent_type": "GrievanceProcessor",
            "auto_extracted": {
                "name": extracted_info.get("name"),
                "phone": extracted_info.get("phone"),
                "ward": extracted_info.get("ward"),
                "extraction_confidence": extracted_info.get("extraction_confidence"),
                "extraction_methods": extracted_info.get("extraction_method")
            }
        }
