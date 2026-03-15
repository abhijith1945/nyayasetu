"""
Synthetic data generator for bail eligibility predictions.
Generates 10k balanced records for training ML models.
"""
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict


def generate_bail_dataset(num_records: int = 10000) -> List[Dict]:
    """
    Generate synthetic bail eligibility dataset.
    
    Args:
        num_records: Number of records to generate
    
    Returns:
        List of bail case dictionaries
    """
    
    # Bail-related offence categories
    offence_categories = [
        "theft", "assault", "fraud", "traffic_violation", "property_damage",
        "petty_crime", "white_collar", "drug_related", "violent_crime", "cyber_crime"
    ]
    
    # Prior history options
    prior_history = ["none", "minor", "moderate", "serious"]
    
    # Flight risk indicators
    flight_risk_options = ["low", "medium", "high", "very_high"]
    
    # Employment status
    employment_status = ["employed", "self_employed", "unemployed", "student"]
    
    # Residential stability
    residential_status = ["owned", "rented", "with_family", "homeless", "migrant"]
    
    dataset = []
    
    for _ in range(num_records):
        # Generate realistic bail eligibility patterns
        is_eligible_for_bail = random.random() > 0.3  # 70% eligible, 30% not eligible
        
        # Determine features based on eligibility
        if is_eligible_for_bail:
            # Features that make bail likely
            age = random.randint(18, 65)  # Mostly working age
            monthly_income = random.randint(15000, 150000)
            prior_hist = random.choices(prior_history, weights=[0.5, 0.3, 0.15, 0.05])[0]
            flight_risk_level = random.choices(flight_risk_options, weights=[0.6, 0.25, 0.1, 0.05])[0]
            employment = random.choices(employment_status, weights=[0.5, 0.2, 0.2, 0.1])[0]
            residential = random.choices(residential_status, weights=[0.4, 0.35, 0.15, 0.05, 0.05])[0]
            has_guarantor = random.random() > 0.3  # 70% have guarantor
            is_repeat_offender = random.random() > 0.7
            years_in_city = random.randint(0, 40)
            days_to_trial = random.randint(30, 365)
            offence_severity = random.randint(1, 5)  # 1-5 scale
        else:
            # Features that make bail unlikely
            age = random.randint(18, 80)
            monthly_income = random.randint(0, 50000)
            prior_hist = random.choices(prior_history, weights=[0.1, 0.2, 0.3, 0.4])[0]
            flight_risk_level = random.choices(flight_risk_options, weights=[0.05, 0.15, 0.3, 0.5])[0]
            employment = random.choices(employment_status, weights=[0.2, 0.1, 0.5, 0.2])[0]
            residential = random.choices(residential_status, weights=[0.05, 0.15, 0.2, 0.4, 0.2])[0]
            has_guarantor = random.random() > 0.6  # 40% have guarantor
            is_repeat_offender = random.random() > 0.4
            years_in_city = random.randint(0, 5)
            days_to_trial = random.randint(1, 100)
            offence_severity = random.randint(3, 5)  # More severe offences
        
        case_date = datetime.now() - timedelta(days=random.randint(1, 365))
        trial_date = case_date + timedelta(days=days_to_trial)
        
        record = {
            "case_id": f"CASE_{_:06d}",
            "age": age,
            "gender": random.choice(["male", "female", "other"]),
            "offence_category": random.choice(offence_categories),
            "offence_severity": offence_severity,  # 1-5 scale
            "prior_criminal_history": prior_hist,
            "employment_status": employment,
            "monthly_income": monthly_income,
            "residential_stability": residential,
            "years_in_current_city": years_in_city,
            "has_family_ties": random.random() > 0.3,
            "has_guarantor": has_guarantor,
            "guarantor_income": random.randint(20000, 300000) if has_guarantor else 0,
            "flight_risk": flight_risk_level,
            "is_repeat_offender": is_repeat_offender,
            "days_between_arrest_and_trial": days_to_trial,
            "health_conditions": random.random() > 0.7,  # 30% have health conditions
            "mental_health_issue": random.random() > 0.85,  # 15% have mental health issues
            "case_registration_date": case_date.isoformat(),
            "estimated_trial_date": trial_date.isoformat(),
            "bail_eligible": is_eligible_for_bail,
            "recommended_bail_amount": random.randint(10000, 500000) if is_eligible_for_bail else 0,
            "conditions_for_bail": generate_bail_conditions(is_eligible_for_bail, offence_severity),
            "credibility_score": round(random.uniform(30, 95) if is_eligible_for_bail else random.uniform(0, 40), 1),
        }
        
        dataset.append(record)
    
    return dataset


def generate_bail_conditions(is_eligible: bool, severity: int) -> List[str]:
    """Generate appropriate bail conditions based on eligibility and severity."""
    
    if not is_eligible:
        return []
    
    conditions = []
    
    # Standard conditions
    if random.random() > 0.3:
        conditions.append("Surrender passport")
    if random.random() > 0.2:
        conditions.append("Regular police reporting")
    if random.random() > 0.4:
        conditions.append("Reside at given address")
    
    # Severity-based conditions
    if severity >= 4:
        if random.random() > 0.3:
            conditions.append("Electronic monitoring")
        if random.random() > 0.5:
            conditions.append("Travel restrictions")
    
    if random.random() > 0.6:
        conditions.append("Avoid contact with complainant")
    
    return conditions if conditions else ["Standard conditions apply"]


def save_dataset(dataset: List[Dict], filename: str = "bail_training_data.json") -> str:
    """Save dataset to JSON file."""
    with open(filename, 'w') as f:
        json.dump(dataset, f, indent=2)
    return filename


def get_dataset_statistics(dataset: List[Dict]) -> Dict:
    """Get statistics about the generated dataset."""
    eligible_count = sum(1 for record in dataset if record["bail_eligible"])
    
    stats = {
        "total_records": len(dataset),
        "eligible_for_bail": eligible_count,
        "not_eligible_for_bail": len(dataset) - eligible_count,
        "eligibility_rate": round(eligible_count / len(dataset) * 100, 2),
        "avg_age": round(sum(r["age"] for r in dataset) / len(dataset), 1),
        "avg_monthly_income": round(sum(r["monthly_income"] for r in dataset) / len(dataset), 0),
        "avg_credibility_score": round(sum(r["credibility_score"] for r in dataset) / len(dataset), 2),
        "offence_distribution": {},
        "flight_risk_distribution": {},
    }
    
    # Calculate distributions
    for record in dataset:
        offence = record["offence_category"]
        flight_risk = record["flight_risk"]
        
        stats["offence_distribution"][offence] = stats["offence_distribution"].get(offence, 0) + 1
        stats["flight_risk_distribution"][flight_risk] = stats["flight_risk_distribution"].get(flight_risk, 0) + 1
    
    return stats


if __name__ == "__main__":
    print("Generating 10k synthetic bail dataset...")
    dataset = generate_bail_dataset(10000)
    
    stats = get_dataset_statistics(dataset)
    print(json.dumps(stats, indent=2))
    
    filename = save_dataset(dataset)
    print(f"\n✅ Dataset saved to {filename}")
