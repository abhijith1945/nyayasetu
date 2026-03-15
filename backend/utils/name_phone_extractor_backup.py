"""
Name and Phone Number Auto-Extraction
Uses NLP and regex patterns to extract citizen info from complaint text
"""

import re
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


def extract_phone_number(text: str) -> Optional[str]:
    """
    Extract phone number from text using multiple patterns.
    Supports Indian phone numbers (10 digits, with/without +91).
    
    Args:
        text: Complaint text
    
    Returns:
        Phone number string or None
    """
    if not text:
        return None
    
    # Pattern 1: Standard 10-digit Indian number
    match = re.search(r'\b[6-9]\d{9}\b', text)
    if match:
        return match.group(0)
    
    # Pattern 2: Number with +91
    match = re.search(r'\+91\s?[6-9]\d{9}\b', text)
    if match:
        phone = match.group(0).replace('+91', '').strip()
        return phone
    
    # Pattern 3: Number with country code
    match = re.search(r'91[6-9]\d{9}\b', text)
    if match:
        phone = match.group(0)[2:]  # Remove 91
        return phone
    
    # Pattern 4: Formatted numbers (with spaces or dashes)
    match = re.search(r'[6-9]\d{3}[\s-]?\d{3}[\s-]?\d{3}', text)
    if match:
        phone = re.sub(r'[\s-]', '', match.group(0))
        return phone
    
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
    
    # Pattern 1: "My name is [name]" - capture name until we hit a word that's not part of name
    match = re.search(r"(?:my name is|I am|I'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", text, re.IGNORECASE)
    if match:
        name = match.group(1)
        # Filter by word count (typically 1-3 parts)
        if len(name.split()) <= 3:
            return name
    
    # Pattern 2: "[Name] speaking" or "[Name] calling" or "[Name] here"
    match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:speaking|calling|here)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 3: "Name: [name]" or "Name - [name]"
    match = re.search(r"(?:name|from)\s*[:–-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 4: Names in quotes like "My name is 'Rajesh Kumar'"
    match = re.search(r"(?:my name is|I am|I'm)\s+['\"]?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)['\"]?", text, re.IGNORECASE)
    if match:
        return match.group(1)
    
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
    
    # Pattern 1: "Ward X"
    match = re.search(r'Ward\s+([0-9]+)', text, re.IGNORECASE)
    if match:
        return f"Ward {match.group(1)}"
    
    # Pattern 2: Location names (area, street, etc.)
    location_keywords = r'(?:area|street|road|lane|colony|sector|zone|block|housing)\s+([A-Za-z0-9\s]+?)(?:[.,;]|$)'
    match = re.search(location_keywords, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return None


def auto_extract_info(text: str) -> Dict:
    """
    Auto-extract all available information from complaint text.
    
    Args:
        text: Raw complaint text from citizen
    
    Returns:
        Dictionary with extracted: name, phone, ward, category hints
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
        
        logger.info(f"✅ Auto-extraction successful: {extracted}")
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


# Test examples
if __name__ == "__main__":
    test_cases = [
        "My name is Ramesh Kumar. My water pipe burst 5 days ago. My number is 9876543210. Urgent!",
        "I'm calling as Priya Nair. Street light broken in Ward 3. Contact: +91 98765 43211",
        "This is Arun here. Area near Market Street. Phone 9876543212. Sanitation issue.",
        "Pothole on road. No name. Call 8765432109",
        "Road blocked. 9123456789 is my number. I didn't mention name.",
    ]
    
    for test in test_cases:
        print(f"\n📝 Text: {test}")
        result = auto_extract_info(test)
        print(f"✅ Result: Name={result['name']}, Phone={result['phone']}, Confidence={result['extraction_confidence']}")
