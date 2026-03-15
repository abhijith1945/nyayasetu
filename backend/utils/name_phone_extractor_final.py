"""
Name and Phone Number Auto-Extraction (Final Enhanced)
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def extract_phone_number(text: str) -> Optional[str]:
    """Extract phone number from text"""
    if not text:
        return None
    
    # Pattern: "my number is 9876 543 210" (with spaces)
    match = re.search(r'(?:my\s+)?number\s+is\s+(\d{4})\s+(\d{3})\s+(\d{4})', text, re.IGNORECASE)
    if match:
        phone = match.group(1) + match.group(2) + match.group(3)
        if phone[0] in '6789':
            return phone
    
    # Pattern: Standard 10-digit
    match = re.search(r'\b[6-9]\d{9}\b', text)
    if match:
        return match.group(0)
    
    # Pattern: +91 format
    match = re.search(r'\+91\s*[\s.-]?([6-9]\d{3})[\s.-]*(\d{3})[\s.-]*(\d{4})', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern: "number is 9876543210"
    match = re.search(r'(?:number|contact|phone)\s+(?:is|:)\s*\(?([6-9]\d{9})\)?', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None


def extract_name(text: str) -> Optional[str]:
    """Extract person name from text"""
    if not text:
        return None
    
    # Pattern 1: "I am Rajesh Kumar"
    match = re.search(r'\bi\s+am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    # Pattern 2: "My name is Rajesh Kumar"
    match = re.search(r'my\s+name\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    # Pattern 3: "This is Rajesh Kumar speaking"
    match = re.search(r'this\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:speaking|calling)', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    # Pattern 4: "Rajesh Kumar speaking"
    match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:speaking|calling|here)\b', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    # Pattern 5: "Name: Rajesh Kumar"
    match = re.search(r'name\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    return None


def extract_ward_location(text: str) -> Optional[str]:
    """Extract ward or location from text"""
    if not text:
        return None
    
    # Pattern 1: "Ward 5" or "ward 5"
    match = re.search(r'Ward\s+([0-9]+)', text, re.IGNORECASE)
    if match:
        return f"Ward {match.group(1)}"
    
    # Pattern 2: "sector 7" or "sector 7"
    match = re.search(r'(?:sector|area|main\s+road|main\s+street)\s+([A-Za-z0-9]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return None


def auto_extract_info(text: str) -> Dict:
    """Auto-extract all information from complaint text"""
    try:
        extracted = {
            "name": extract_name(text),
            "phone": extract_phone_number(text),
            "ward": extract_ward_location(text),
            "extraction_confidence": 0.0,
            "extraction_method": []
        }
        
        confidence_score = 0.0
        if extracted["name"]:
            confidence_score += 0.4
            extracted["extraction_method"].append("name_extraction")
        
        if extracted["phone"]:
            confidence_score += 0.4
            extracted["extraction_method"].append("phone_extraction")
        
        if extracted["ward"]:
            confidence_score += 0.2
            extracted["extraction_method"].append("location_extraction")
        
        extracted["extraction_confidence"] = min(1.0, confidence_score)
        
        logger.info(f"✅ Extracted: Name={extracted['name']}, Phone={extracted['phone']}")
        return extracted
    
    except Exception as e:
        logger.error(f"Auto-extraction failed: {e}")
        return {
            "name": None,
            "phone": None,
            "ward": None,
            "extraction_confidence": 0.0,
            "extraction_method": [],
            "error": str(e)
        }
