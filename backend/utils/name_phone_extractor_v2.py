"""
Name and Phone Number Auto-Extraction (Enhanced)
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
    Supports ALL Indian phone number formats:
    - 10 digits: 9876543210
    - +91 with formatting: +91 9876-543-210, +91 98765 43210
    - 91 prefix: 919876543210
    - Formatted: 98765 43210, 9876-543-210
    - In text: "my number is 9876543210", "contact: 9876543210"
    
    Args:
        text: Complaint text
    
    Returns:
        Phone number string (10 digits) or None
    """
    if not text:
        return None
    
    # Pattern 1: Standard 10-digit Indian number (starts with 6-9)
    match = re.search(r'\b[6-9]\d{9}\b', text)
    if match:
        return match.group(0)
    
    # Pattern 2: Number with +91 prefix (with various spacing/formatting)
    match = re.search(r'\+91[\s.-]?([6-9]\d{3})[\s.-]?(\d{3})[\s.-]?(\d{4})', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 3: Number with 91 prefix without + (boundary check)
    match = re.search(r'(?:^|\s|:)91\s?([6-9]\d{3})[\s.-]?(\d{3})[\s.-]?(\d{4})(?:\s|$|[,;.])', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 4: Formatted numbers with aggressive spacing/dashes
    match = re.search(r'(?:^|\s)([6-9]\d{3})[\s.-](\d{3})[\s.-]?(\d{4})(?:\s|$|[,;.])', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 5: Direct 10-digit with minimal spacing (e.g., "8765 432 109")
    match = re.search(r'(?:^|\s)([6-9])(\d{3})[\s.]?(\d{3})[\s.]?(\d{4})(?:\s|$|[,;.])', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3) + match.group(4)
    
    # Pattern 6: Keywords before number ("number is", "contact", "phone", "mobile")
    match = re.search(r'(?:number|contact|phone|mobile|phone number|mobile number)\s+(?:is|:|=)\s*[\(]?([6-9]\d{9})[\)]?', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 7: Keywords before number with +91 ("number is +91 9876543210")
    match = re.search(r'(?:number|contact|phone|mobile|phone number|mobile number)\s+(?:is|:|=)\s*\+91[\s.-]?([6-9]\d{9})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 8: "my number is X" or "my phone is X"
    match = re.search(r'(?:my\s+)?(?:number|mobile|phone|contact)\s+(?:is|:)\s+([6-9]\d{9})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 9: Number in parentheses like "(9876543210)"
    match = re.search(r'\(([6-9]\d{9})\)', text)
    if match:
        return match.group(1)
    
    # Pattern 10: Last resort - look for any 10-digit number starting 6-9
    match = re.search(r'[6-9]\d{9}', text)
    if match:
        return match.group(0)
    
    return None


def extract_name(text: str) -> Optional[str]:
    """
    Extract person name from complaint text.
    Uses patterns like "I am X", "My name is X", "This is X speaking", etc.
    
    Args:
        text: Complaint text
    
    Returns:
        Name string or None
    """
    if not text:
        return None
    
    # Pattern 1: "My name is [name]" or "I am [name]"
    match = re.search(r"(?:my name is|I am|I'm|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text, re.IGNORECASE)
    if match:
        name = match.group(1)
        if len(name.split()) <= 3:
            return name
    
    # Pattern 2: "[Name] speaking" or "[Name] calling"
    match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:speaking|calling|here)\b", text, re.IGNORECASE)
    if match:
        name = match.group(1)
        if len(name.split()) <= 3:
            return name
    
    # Pattern 3: "Name: [name]" or "Name - [name]"
    match = re.search(r"(?:name|from)\s*[:–-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text, re.IGNORECASE)
    if match:
        name = match.group(1)
        if len(name.split()) <= 3:
            return name
    
    # Pattern 4: "calling as [name]"
    match = re.search(r"calling\s+as\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text, re.IGNORECASE)
    if match:
        name = match.group(1)
        if len(name.split()) <= 3:
            return name
    
    return None


def extract_ward_location(text: str) -> Optional[str]:
    """
    Extract ward or location information from complaint text.
    
    Args:
        text: Complaint text
    
    Returns:
        Ward/location string or None
    """
    if not text:
        return None
    
    # Pattern 1: "Ward X" or "ward X"
    match = re.search(r'Ward\s+([0-9]+)', text, re.IGNORECASE)
    if match:
        return f"Ward {match.group(1)}"
    
    # Pattern 2: Location names (area, street, road, etc.)
    location_keywords = r'(?:area|street|road|lane|colony|sector|zone|block|housing|locality|main road|main street)\s+([A-Za-z0-9\s]+?)(?:[,;.]|$)'
    match = re.search(location_keywords, text, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        # Don't return if it's too long (likely not a location)
        if len(location) <= 50:
            return location
    
    return None


def auto_extract_info(text: str) -> Dict:
    """
    Auto-extract all available information from complaint text.
    
    Args:
        text: Raw complaint text from citizen
    
    Returns:
        Dictionary with extracted: name, phone, ward, confidence score, extraction methods
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
        
        logger.info(f"✅ Auto-extraction: Name={extracted['name']}, Phone={extracted['phone']}, Confidence={extracted['extraction_confidence']:.2f}")
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


# Test cases
if __name__ == "__main__":
    test_cases = [
        ("My name is Rajesh Kumar and my phone number is 9876543210. There's a pothole on main street", 
         "Should extract: Rajesh Kumar, 9876543210"),
        
        ("I am Priya Singh, my contact number is +919876543212, there is a water overflow in Ward 5", 
         "Should extract: Priya Singh, 9876543212, Ward 5"),
        
        ("This is Anil Kumar speaking, my number is 8765 432 109, road condition complaint in sector 7", 
         "Should extract: Anil Kumar, 8765432109, sector 7"),
        
        ("Hello calling as John, phone is 9876-543-210, electricity issue", 
         "Should extract: John, 9876543210"),
        
        ("Name: Meera Nair, my number: 91 9876543210, Ward 3 problem", 
         "Should extract: Meera Nair, 9876543210, Ward 3"),
    ]
    
    print("=" * 80)
    print("PHONE EXTRACTION TEST SUITE".center(80))
    print("=" * 80)
    
    for test_text, description in test_cases:
        print(f"\n📝 Input: {test_text[:70]}...")
        print(f"📌 {description}")
        result = auto_extract_info(test_text)
        print(f"✅ Extracted:")
        print(f"   - Name: {result['name']}")
        print(f"   - Phone: {result['phone']}")
        print(f"   - Ward: {result['ward']}")
        print(f"   - Confidence: {result['extraction_confidence']:.2f}")
        print(f"   - Methods: {', '.join(result['extraction_method'])}")
