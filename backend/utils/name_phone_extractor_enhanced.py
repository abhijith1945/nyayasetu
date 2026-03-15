"""
Name and Phone Number Auto-Extraction (Enhanced v2)
Uses NLP and regex patterns to extract citizen info from complaint text
Supports all Indian phone number formats
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def extract_phone_number(text: str) -> Optional[str]:
    """
    Extract phone number from text using multiple patterns.
    Supports ALL Indian phone number formats
    """
    if not text:
        return None
    
    # Pattern 1: Keywords before number with flexible spacing ("number is 9876 543 210")
    match = re.search(r'(?:number|contact|phone|mobile|phone number|mobile number)\s+(?:is|:|=)\s*\(*\s*([6-9]\d{3})\s+(\d{3})\s+(\d{4})\s*\)*', text, re.IGNORECASE)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 2: Standard 10-digit Indian number
    match = re.search(r'\b[6-9]\d{9}\b', text)
    if match:
        return match.group(0)
    
    # Pattern 3: Number with +91 prefix (with various spacing/formatting)
    match = re.search(r'\+91[\s.-]?([6-9]\d{3})[\s.-]?(\d{3})[\s.-]?(\d{4})', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 4: 91 prefix without + 
    match = re.search(r'(?:^|[\s:,])91[\s.-]?([6-9]\d{3})[\s.-]?(\d{3})[\s.-]?(\d{4})', text, re.MULTILINE)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 5: Formatted numbers XXX XXX XXXX
    match = re.search(r'(?:^|[\s:,])([6-9]\d{3})\s+(\d{3})\s+(\d{4})(?:\s|$|[,;.])', text, re.MULTILINE)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 6: Formatted numbers with dashes XXX-XXX-XXXX
    match = re.search(r'([6-9]\d{2})-(\d{3})-(\d{4})', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 7: In parentheses "(9876543210)" or "(+91 9876543210)"
    match = re.search(r'\(\s*\+?91?\s*[\s.-]?([6-9]\d{9})\s*\)', text)
    if match:
        phone = match.group(1)
        if len(phone) >= 10:
            return phone[-10:]
    
    return None


def extract_name(text: str) -> Optional[str]:
    """
    Extract person name from complaint text.
    """
    if not text:
        return None
    
    # Pattern 1: "My name is [FirstName LastName]" - most common
    match = re.search(r'(?:my\s+name\s+is|I\s+am|I\'m|this\s+is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3 and not any(kw in name.lower() for kw in ['water', 'road', 'street', 'complaint', 'issue']):
            return name
    
    # Pattern 2: "[Name] speaking" or "[Name] calling"
    match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:speaking|calling)\b', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    # Pattern 3: "Name: [name]"
    match = re.search(r'name\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    # Pattern 4: "calling as [name]"
    match = re.search(r'calling\s+as\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if len(name.split()) <= 3:
            return name
    
    return None


def extract_ward_location(text: str) -> Optional[str]:
    """
    Extract ward or location information from complaint text.
    """
    if not text:
        return None
    
    # Pattern 1: "Ward X"
    match = re.search(r'Ward\s+([0-9]+)', text, re.IGNORECASE)
    if match:
        return f"Ward {match.group(1)}"
    
    # Pattern 2: Location patterns (sector, area, street, etc.)
    location_keywords = r'(?:sector|area|street|road|lane|colony|zone|block|locality)\s+([A-Za-z0-9\s]+?)(?:\s+(?:problem|issue|complaint)|[,;.]|$)'
    match = re.search(location_keywords, text, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        if 0 < len(location) <= 50:
            return location
    
    return None


def auto_extract_info(text: str) -> Dict:
    """
    Auto-extract all available information from complaint text.
    """
    try:
        extracted = {
            "name": extract_name(text),
            "phone": extract_phone_number(text),
            "ward": extract_ward_location(text),
            "extraction_confidence": 0.0,
            "extraction_method": []
        }
        
        # Calculate confidence
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
        
        logger.info(f"✅ Extracted: Name={extracted['name']}, Phone={extracted['phone']}, Confidence={extracted['extraction_confidence']:.2f}")
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
