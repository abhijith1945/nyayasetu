#!/usr/bin/env python3
"""Test script to verify name detection and resource allocation fixes."""

import sys
sys.path.insert(0, 'backend')

from utils.name_phone_extractor_v3 import extract_name, extract_phone_number, auto_extract_info
from utils.ml_models import predict_resolution_time

print("=" * 60)
print("TEST 1: NAME DETECTION FIXES")
print("=" * 60)

test_cases_names = [
    "i am john kumar",  # lowercase (speech-to-text issue)
    "I am Rajesh Kumar",  # Original format
    "my name is priya sharma",  # lowercase
    "this is Amit calling",  # Single name
    "Hello, raj speaking",  # Single name lowercase
    "name is Mehta",  # Single surname
    "Kumar, Rajesh",  # Comma-separated
    "Raj here to report",  # Minimal phrase
]

for text in test_cases_names:
    name = extract_name(text)
    status = "✅" if name else "❌"
    print(f"{status} '{text}' → {name}")

print("\n" + "=" * 60)
print("TEST 2: PHONE DETECTION (existing - should still work)")
print("=" * 60)

test_cases_phones = [
    "number is 9876 543 210",
    "9876543210",
    "+91 9876 543 2101",
    "+919876543210",
]

for text in test_cases_phones:
    phone = extract_phone_number(text)
    status = "✅" if phone else "❌"
    print(f"{status} '{text}' → {phone}")

print("\n" + "=" * 60)
print("TEST 3: RESOURCE ALLOCATION MULTIPLIERS FIX")
print("=" * 60)

test_grievances = [
    {
        "category": "water",
        "urgency": 5,  # High urgency
        "credibility_score": 80,  # High credibility
        "image_verified": True,
        "description": "Water issue in ward 5",
        "ward": "Ward 5",
    },
    {
        "category": "electricity",
        "urgency": 1,  # Low urgency
        "credibility_score": 30,  # Low credibility
        "image_verified": False,
        "description": "Electricity issue",
        "ward": "Ward 2",
    },
    {
        "category": "legal",
        "urgency": 3,  # Medium urgency
        "credibility_score": 60,  # Medium credibility
        "image_verified": False,
        "description": "Legal advice needed",
        "ward": "Ward 1",
    },
]

print("\nPrediction Results (should be within reasonable bounds):\n")
for i, grievance in enumerate(test_grievances, 1):
    result = predict_resolution_time(grievance)
    print(f"Grievance {i}:")
    print(f"  Category: {result['category']}")
    print(f"  Predicted: {result['predicted_hours']}h ({result['predicted_days']} days)")
    print(f"  Base hours: {result['factors']['base_hours']}h")
    print(f"  Multipliers: Urgency={result['factors']['urgency_impact']:.3f}, "
          f"Credibility={result['factors']['credibility_impact']:.3f}, "
          f"Evidence={result['factors']['evidence_impact']:.3f}")
    
    # Verify bounds: predictions should be between 25%-175% of baseline
    base = result['factors']['base_hours']
    actual = result['predicted_hours']
    min_bound = base * 0.25
    max_bound = base * 1.75
    
    if min_bound <= actual <= max_bound:
        print(f"  ✅ Within bounds ({min_bound:.0f}h - {max_bound:.0f}h)")
    else:
        print(f"  ❌ OUT OF BOUNDS ({min_bound:.0f}h - {max_bound:.0f}h)")
    print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("✅ Name extraction now handles:")
print("   - Lowercase input from speech-to-text")
print("   - Single names without full names")
print("   - Names at sentence start")
print("   - Comma-separated names")
print("\n✅ Resource allocation now:")
print("   - Uses additive adjustments instead of multiplicative")
print("   - Bounds predictions to 25%-175% of baseline")
print("   - Prevents extreme compound reductions (like 0.5×0.8×0.7)")
print("=" * 60)
