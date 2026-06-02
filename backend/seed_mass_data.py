"""Bulk seed generator for NyayaSetu.

Usage:
    py seed_mass_data.py [grievances=1200] [railway_grievances=250] [legal_cases=150]

This script adds a much larger dataset across the main app tables:
- grievances and actions
- clusters
- users and assignments
- legal_cases
- railway_grievances, railway_clusters, railway_actions
- budget_allocations
- predictions
"""

import hashlib
import os
import random
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from supabase import create_client, Client

from utils.auth import hash_password

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Set SUPABASE_URL and SUPABASE_KEY in .env first.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

SEED_TAG = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
random.seed(2026)

WARDS = [
    "Ward 1 (Kazhakoottam)",
    "Ward 2 (Technopark)",
    "Ward 3 (Pattom)",
    "Ward 4 (Vanchiyoor)",
    "Ward 5 (Palayam)",
    "Ward 6 (Karamana)",
    "Ward 7 (Nemom)",
    "Ward 8 (Kovalam)",
]

WARD_LOCALITIES = {
    "Ward 1 (Kazhakoottam)": ["Kazhakoottam junction", "Chanthavila", "Smart City layout", "Muttathara", "IT corridor"],
    "Ward 2 (Technopark)": ["Technopark Phase 1", "Technopark Phase 3", "Infopark road", "TCS building road", "residential block"],
    "Ward 3 (Pattom)": ["Marappalam", "Palace Road", "Government Secretariat quarters", "Pattom junction", "staff quarters"],
    "Ward 4 (Vanchiyoor)": ["Vanchiyoor court junction", "MG Road", "Overbridge", "market area", "residential colony"],
    "Ward 5 (Palayam)": ["Palayam market", "PMG junction", "bus stand", "Connemara market", "Canakakkunnu side"],
    "Ward 6 (Karamana)": ["Karamana bridge", "riverside colony", "medical road", "housing colony", "temple road"],
    "Ward 7 (Nemom)": ["Nemom junction", "temple road", "school route", "railway crossing", "UP school side"],
    "Ward 8 (Kovalam)": ["Kovalam beach road", "lighthouse area", "beach entry", "tourist lane", "coastal road"],
}

FIRST_NAMES = [
    "Arun", "Priya", "Rajesh", "Lakshmi", "Suresh", "Anitha", "Vijay", "Deepa",
    "Manoj", "Suja", "Rajan", "Kavitha", "Dileep", "Meera", "Biju", "Asha",
    "Sandeep", "Geetha", "Ajith", "Reshma", "Sreekumar", "Divya", "Harikrishnan",
    "Bindu", "Unnikrishnan", "Jyothi", "Gopakumar", "Parvathy", "Shibu", "Saritha",
    "Jayakumar", "Soumya", "Babu", "Thulasi", "Sajeev", "Ammu", "Muraleedharan",
    "Indira", "Shaji", "Remya", "Anil", "Veena", "Prasad", "Manju", "Sunil",
    "Sreelatha", "Pramod", "Swathi", "Madhavan", "Beena", "Nikhil", "Radhika",
    "Naveen", "Roopa", "Akhil", "Nisha", "Mohan", "Karthika", "Ravi", "Neethu",
]

LAST_NAMES = [
    "Kumar", "Nair", "Menon", "Devi", "Pillai", "George", "Krishnan", "Mohan",
    "Varma", "Thomas", "Nambiar", "Rajan", "Kumar", "Sasidharan", "Abdul",
    "K.", "Raj", "Das", "Lal", "Menon", "Pillai", "Joseph", "Krishnan", "Nair",
]

RAILWAY_ZONES = ["Southern", "Central", "North", "East Coast", "Western"]
RAILWAY_STATIONS = [
    "Thiruvananthapuram Central", "Kochuveli", "Nemom", "Varkala", "Kollam",
    "Ernakulam", "Palakkad", "Kozhikode", "Kazhakoottam", "Pattom Halt",
]

RAILWAY_ISSUES = {
    "delay": [
        "train delayed by several hours",
        "platform change announced at the last minute",
        "signal failure causing repeated stoppages",
        "coach coupled late and passengers stranded",
    ],
    "cleanliness": [
        "coach is filthy and has overflowing trash",
        "toilets are unusable and foul smelling",
        "water is unavailable in multiple coaches",
        "cleaning staff have not visited since departure",
    ],
    "crowding": [
        "severe overcrowding and people standing in the aisle",
        "passengers unable to board due to excess crowd",
        "reserved coach filled with unreserved travellers",
        "elderly passengers left without seats for hours",
    ],
    "ticketing": [
        "ticketing machine is not working at the station",
        "confirmed ticket was downgraded without notice",
        "counter staff are refusing to issue proper receipts",
        "app booking failed but amount was deducted",
    ],
    "safety": [
        "coach door is malfunctioning and opens while moving",
        "emergency light is not working in the compartment",
        "platform edge is unsafe and not barricaded",
        "passengers reported suspicious activity near the berth",
    ],
    "technical": [
        "engine kept stopping due to technical fault",
        "air conditioning failed in multiple coaches",
        "power supply to the coach keeps tripping",
        "announcement system is not working on board",
    ],
}

CATEGORIES = ["water", "road", "electricity", "health", "sanitation", "legal", "general"]
CATEGORY_DEPARTMENTS = {
    "water": "Water Authority",
    "road": "PWD Roads",
    "electricity": "KSEB",
    "health": "Health Department",
    "sanitation": "Sanitation Wing",
    "legal": "Legal Aid Cell",
    "general": "Municipal Administration",
}

PASSWORD_HASH = hash_password("password123")


def chunked(items, size=100):
    for index in range(0, len(items), size):
        yield items[index : index + size]


def random_phone():
    return f"+919{random.randint(100000000, 999999999)}"


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}".replace("  ", " ").strip()


def rand_created_at(months_back=18):
    now = datetime.now(timezone.utc)
    days_back = random.randint(0, months_back * 30)
    hours_back = random.randint(0, 23)
    return (now - timedelta(days=days_back, hours=hours_back)).isoformat()


def month_key(iso_string):
    return iso_string[:7]


def add_days(iso_string, days):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return (dt + timedelta(days=days)).isoformat()


def make_hash(record_id, created_at, description):
    raw = f"{record_id}{created_at}{description}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_grievance(category, ward, index):
    locality = random.choice(WARD_LOCALITIES[ward])
    created_at = rand_created_at(18)

    if category == "water":
        days = random.randint(1, 14)
        households = random.randint(80, 600)
        issue = random.choice([
            "Water pipeline burst",
            "No drinking water supply",
            "Contaminated tap water",
            "Low water pressure",
            "Broken water meter",
        ])
        description = (
            f"{issue} near {locality} in {ward} for {days} days. "
            f"Around {households} households are affected and tanker supply is irregular. "
            f"Residents demand immediate repair from the Water Authority."
        )
        summary = f"{issue} in {ward}; {days} days affected and {households} households impacted."
        urgency = random.randint(3, 5)
        credibility = random.randint(65, 100)

    elif category == "road":
        days = random.randint(2, 45)
        accidents = random.randint(1, 7)
        issue = random.choice([
            "A large pothole has opened",
            "Road surface is washed away",
            "Streetlights are not working",
            "Drainage work has left the road open",
            "Pedestrian crossing signal is down",
        ])
        description = (
            f"{issue} at {locality} in {ward}. {accidents} accidents or near-miss reports were filed over {days} days. "
            f"Traffic is forced to divert through narrow lanes and the repair work is still pending."
        )
        summary = f"Road safety issue in {ward}; {accidents} incidents reported over {days} days."
        urgency = random.randint(3, 5)
        credibility = random.randint(55, 100)

    elif category == "electricity":
        hours = random.randint(4, 20)
        homes = random.randint(60, 500)
        issue = random.choice([
            "Frequent power cuts",
            "Transformer sparking at night",
            "Voltage fluctuation is damaging appliances",
            "Electric wire is sagging dangerously low",
            "Electric pole is leaning after a storm",
        ])
        description = (
            f"{issue} near {locality} in {ward}. {homes} homes and small businesses are affected every day for about {hours} hours. "
            f"Residents say KSEB has not shared any repair timeline."
        )
        summary = f"Electricity disruption in {ward}; {homes} households affected with no repair timeline."
        urgency = random.randint(3, 5)
        credibility = random.randint(55, 100)

    elif category == "health":
        patients = random.randint(12, 250)
        issue = random.choice([
            "Hospital medicine stock is exhausted",
            "Stray dog attacks are increasing",
            "Dengue cases are rising",
            "PHC is understaffed",
            "Ambulance service is unreachable",
        ])
        description = (
            f"{issue} at {locality} in {ward}. Around {patients} residents or patients are affected and the local health office has not responded. "
            f"Urgent intervention is required from the health department."
        )
        summary = f"Health service issue in {ward}; about {patients} people affected."
        urgency = random.randint(3, 5)
        credibility = random.randint(60, 100)

    elif category == "sanitation":
        days = random.randint(3, 18)
        households = random.randint(60, 400)
        issue = random.choice([
            "Garbage has not been collected",
            "Drainage is blocked and sewage is overflowing",
            "A public toilet is unusable",
            "Construction waste is dumped illegally",
            "Plastic waste is being burned every night",
        ])
        description = (
            f"{issue} near {locality} in {ward} for {days} days. {households} households are facing bad smell, pests, or flooding. "
            f"Corporation cleanup work is still pending."
        )
        summary = f"Sanitation issue in {ward}; waste or sewage affecting {households} households."
        urgency = random.randint(3, 5)
        credibility = random.randint(60, 100)

    elif category == "legal":
        months = random.randint(3, 36)
        issue = random.choice([
            "RTI application has not been answered",
            "An undertrial prisoner has been in jail too long",
            "Police are refusing to register an FIR",
            "A court order is not being enforced",
            "A domestic violence complaint is pending without chargesheet",
        ])
        description = (
            f"{issue} in {ward}. The matter has been pending for {months} months and the family says legal aid has not been effective. "
            f"Immediate review by the legal aid cell is requested."
        )
        summary = f"Legal complaint in {ward}; pending for {months} months."
        urgency = random.randint(2, 5)
        credibility = random.randint(55, 100)

    else:
        issue = random.choice([
            "Ration distribution is delayed",
            "Bus frequency has dropped sharply",
            "Pension payment is pending",
            "School building needs repairs",
            "Noise pollution is disturbing residents",
        ])
        description = (
            f"{issue} near {locality} in {ward}. The issue has affected daily life for several weeks and residents have already raised multiple complaints. "
            f"They are asking for a quick administrative response."
        )
        summary = f"General public service issue in {ward}; residents need quick action."
        urgency = random.randint(2, 5)
        credibility = random.randint(50, 100)

    status_roll = random.random()
    if status_roll < 0.68:
        status = "open"
    elif status_roll < 0.80:
        status = "resolved"
    elif status_roll < 0.90:
        status = "reopened"
    else:
        status = "breached"

    resolved_at = None
    resolution_confirmed = False
    if status in {"resolved", "reopened"}:
        resolved_at = add_days(created_at, random.randint(1, 14))
        resolution_confirmed = random.random() < 0.55

    grievance_id = str(uuid.uuid4())
    row = {
        "id": grievance_id,
        "citizen_name": random_name(),
        "phone": random_phone(),
        "ward": ward,
        "district": "Thiruvananthapuram",
        "description": description,
        "category": category,
        "urgency": urgency,
        "credibility_score": credibility,
        "ai_summary": summary,
        "status": status,
        "resolved_at": resolved_at,
        "resolution_confirmed": resolution_confirmed,
        "support_count": random.randint(0, 250),
        "image_url": None,
        "image_verified": None,
        "at_risk_of_sla_breach": status == "open" and urgency >= 4 and random.random() < 0.6,
        "created_at": created_at,
    }
    row["hash"] = make_hash(grievance_id, created_at, description)
    return row


def build_legal_case(grievance_id=None):
    ward = random.choice(WARDS)
    months = random.randint(2, 54)
    max_years = random.choice([2, 3, 4, 5, 7, 10])
    half_max = (max_years * 12) // 2
    eligible = months >= half_max
    start_date = (datetime.now(timezone.utc) - timedelta(days=months * 30)).date().isoformat()
    name = random_name()
    section = random.choice([
        "IPC 379 (Theft)", "IPC 420 (Cheating)", "IPC 324 (Hurt)",
        "IPC 304A (Negligence)", "IPC 457 (Trespass)", "IPC 506 (Threats)",
    ])
    return {
        "id": str(uuid.uuid4()),
        "prisoner_name": name,
        "ward": ward,
        "ipc_section": section,
        "max_sentence_years": max_years,
        "detention_start": start_date,
        "eligible_436a": eligible,
        "months_detained": months,
        "dlsa_contact": "DLSA Thiruvananthapuram: 0471-2334455",
        "grievance_id": grievance_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_user(role, ward=None):
    name = random_name()
    user_id = str(uuid.uuid4())
    email = f"{role}.{SEED_TAG}.{user_id[:8]}@nyayasetu.local"
    row = {
        "id": user_id,
        "email": email,
        "password_hash": PASSWORD_HASH,
        "role": role,
        "full_name": name,
        "phone": random_phone(),
        "ward": ward,
        "sms_notifications_enabled": role in {"citizen", "officer"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    }
    return row


def build_railway_grievance(group_index, member_index, train_number, zone, station, cluster_id):
    category = random.choice(list(RAILWAY_ISSUES.keys()))
    issue = random.choice(RAILWAY_ISSUES[category])
    coach = random.choice(["S1", "S2", "S3", "B1", "B2", "A1", "General", "GS"])
    created_at = rand_created_at(12)
    description = (
        f"{issue} on train {train_number} near {station} in {zone} zone. "
        f"Coach {coach} is overcrowded and about {random.randint(40, 280)} passengers are affected. "
        f"Railway staff have not provided a clear response."
    )
    return {
        "id": str(uuid.uuid4()),
        "passenger_name": random_name(),
        "phone": random_phone(),
        "train_number": train_number,
        "railway_zone": zone,
        "station": station,
        "coach_number": coach,
        "description": description,
        "category": category,
        "urgency": random.randint(2, 5),
        "credibility_score": random.randint(50, 100),
        "ai_summary": f"Railway {category} issue on {train_number} near {station}; staff response pending.",
        "status": "open" if random.random() < 0.75 else random.choice(["resolved", "reopened"]),
        "hash": None,
        "cluster_id": cluster_id,
        "image_url": None,
        "image_verified": None,
        "created_at": created_at,
        "resolved_at": None,
        "resolution_confirmed": False,
    }


def build_prediction_rows(grievances):
    counts = defaultdict(lambda: defaultdict(int))
    for item in grievances:
        counts[(item["ward"], item["category"])][month_key(item["created_at"])] += 1

    rows = []
    for (ward, category), monthly in counts.items():
        months = sorted(monthly.keys())
        if len(months) < 3:
            continue

        values = [monthly[m] for m in months]

        def exp_smooth(seq, alpha=0.6):
            result = seq[0]
            for value in seq[1:]:
                result = alpha * value + (1 - alpha) * result
            return result

        forecast = exp_smooth(values)
        predicted = max(1, int(round(forecast)))
        if values[-1] > values[-2]:
            trend = "rising"
        elif values[-1] < values[-2]:
            trend = "falling"
        else:
            trend = "stable"

        last_month = months[-1]
        year, month_num = int(last_month[:4]), int(last_month[5:7])
        if month_num == 12:
            next_month = f"{year + 1}-01"
        else:
            next_month = f"{year}-{month_num + 1:02d}"

        rows.append({
            "id": str(uuid.uuid4()),
            "ward": ward,
            "category": category,
            "month": next_month,
            "predicted_count": predicted,
            "confidence": round(min(0.95, 0.55 + len(values) * 0.03), 2),
            "trend": trend,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })

    return rows


def batch_insert(table, rows, label, batch_size=100):
    if not rows:
        print(f"  [SKIP] {label}: no rows")
        return 0

    total = len(rows)
    inserted = 0
    print(f"\n  Seeding {label}: {total} rows")
    for index, batch in enumerate(chunked(rows, batch_size), start=1):
        try:
            supabase.table(table).insert(batch).execute()
            inserted += len(batch)
            print(f"    batch {index:>3}: inserted {inserted}/{total}")
        except Exception as e:
            print(f"    batch {index:>3}: ERROR -> {e}")
    return inserted


def create_user_pool():
    users = []
    officers = []
    auditors = []
    admins = []
    citizens = []

    for idx, ward in enumerate(WARDS * 2):
        row = build_user("officer", ward)
        row["full_name"] = f"Officer {idx + 1} {ward.split('(')[1].split(')')[0]}"
        users.append(row)
        officers.append(row)

    for idx in range(8):
        row = build_user("auditor")
        row["full_name"] = f"Auditor {idx + 1}"
        users.append(row)
        auditors.append(row)

    for idx in range(6):
        row = build_user("admin")
        row["full_name"] = f"Admin {idx + 1}"
        users.append(row)
        admins.append(row)

    for idx in range(36):
        ward = random.choice(WARDS)
        row = build_user("citizen", ward)
        row["full_name"] = f"Citizen {idx + 1}"
        users.append(row)
        citizens.append(row)

    return users, officers, auditors, admins, citizens


def build_grievance_pool(count, officers, auditors):
    grievances = []
    categories_cycle = (CATEGORIES * ((count // len(CATEGORIES)) + 1))[:count]
    for index, category in enumerate(categories_cycle):
        ward = random.choice(WARDS)
        row = build_grievance(category, ward, index)
        grievances.append(row)

    # Assign officers and auditors in-memory before insert.
    officers_by_ward = defaultdict(list)
    for officer in officers:
        officers_by_ward[officer["ward"]].append(officer)

    auditor_ids = [auditor["id"] for auditor in auditors]

    for row in grievances:
        ward_officers = officers_by_ward.get(row["ward"], officers)
        if ward_officers and random.random() < 0.8:
            row["officer_id"] = random.choice(ward_officers)["id"]
        else:
            row["officer_id"] = random.choice(officers)["id"]

        row["auditor_id"] = random.choice(auditor_ids) if random.random() < 0.25 else None

    return grievances


def build_clusters_for_grievances(grievances):
    grouped = defaultdict(list)
    for item in grievances:
        grouped[(item["category"], item["ward"])].append(item)

    clusters = []
    for (category, ward), group_items in grouped.items():
        if len(group_items) < 8:
            continue

        cluster_id = str(uuid.uuid4())
        member_ids = [item["id"] for item in group_items]
        for item in group_items:
            item["cluster_id"] = cluster_id

        clusters.append({
            "id": cluster_id,
            "category": category,
            "ward": ward,
            "member_ids": member_ids,
            "summary": f"{category.title()} complaints concentrated in {ward}; {len(member_ids)} related reports.",
            "ai_brief": f"{len(member_ids)} {category} complaints in {ward} indicate a recurring local issue.",
            "count": len(member_ids),
            "alert_sent": random.random() < 0.35,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return clusters


def build_actions_for_grievances(grievances):
    actions = []
    for item in grievances:
        actions.append({
            "id": str(uuid.uuid4()),
            "grievance_id": item["id"],
            "action_type": "submitted",
            "performed_by": item["citizen_name"],
            "notes": f"Bulk seeded complaint in {item['ward']} ({item['category']}).",
            "hash": hashlib.sha256(f"{item['id']}submitted{item['created_at']}".encode("utf-8")).hexdigest(),
            "created_at": item["created_at"],
        })
    return actions


def build_budget_rows(clusters):
    rows = []
    for cluster in clusters:
        allocated = random.randint(120000, 950000)
        spent = random.randint(int(allocated * 0.35), allocated)
        flagged = random.random() < 0.2
        grievance_id = cluster["member_ids"][0] if cluster["member_ids"] else None
        rows.append({
            "id": str(uuid.uuid4()),
            "grievance_id": grievance_id,
            "cluster_id": cluster["id"],
            "department": CATEGORY_DEPARTMENTS.get(cluster["category"], "Municipal Administration"),
            "amount_allocated": allocated,
            "amount_spent": spent,
            "description": cluster["summary"],
            "auditor_flagged": flagged,
            "flag_reason": "Auto-flagged during bulk seed for audit review" if flagged else None,
            "flagged_at": datetime.now(timezone.utc).isoformat() if flagged else None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    return rows


def build_assignments(grievances, officers):
    rows = []
    grievances_by_ward = defaultdict(list)
    for item in grievances:
        grievances_by_ward[item["ward"]].append(item)

    for officer in officers:
        ward_items = grievances_by_ward.get(officer["ward"], grievances)
        sample = random.sample(ward_items, k=min(8, len(ward_items)))
        for item in sample:
            status = random.choice(["assigned", "in_progress", "completed"])
            rows.append({
                "id": str(uuid.uuid4()),
                "grievance_id": item["id"],
                "officer_id": officer["id"],
                "assigned_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "notes": f"Assigned automatically to {officer['full_name']} for bulk dataset.",
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "completed" else None,
            })
    return rows


def build_legal_cases(count, grievance_ids):
    cases = []
    for index in range(count):
        grievance_id = random.choice(grievance_ids) if grievance_ids and random.random() < 0.2 else None
        cases.append(build_legal_case(grievance_id))
    return cases


def build_railway_pool(count):
    groups = max(25, count // 10)
    zone_cycle = (RAILWAY_ZONES * ((groups // len(RAILWAY_ZONES)) + 1))[:groups]
    railway_grievances = []
    railway_clusters = []

    for group_index in range(groups):
        zone = zone_cycle[group_index]
        train_number = f"12{600 + group_index:03d}"
        station = random.choice(RAILWAY_STATIONS)
        cluster_id = str(uuid.uuid4())
        member_ids = []

        for member_index in range(10):
            if len(railway_grievances) >= count:
                break
            row = build_railway_grievance(group_index, member_index, train_number, zone, station, cluster_id)
            member_ids.append(row["id"])
            railway_grievances.append(row)

        railway_clusters.append({
            "id": cluster_id,
            "category": random.choice(list(RAILWAY_ISSUES.keys())),
            "train_number": train_number,
            "railway_zone": zone,
            "station": station,
            "member_ids": member_ids,
            "summary": f"Railway issues concentrated on {train_number} in {zone} zone.",
            "ai_brief": f"{len(member_ids)} railway grievances on {train_number} show recurring service disruption.",
            "count": len(member_ids),
            "alert_sent": random.random() < 0.35,
            "next_station": random.choice(RAILWAY_STATIONS),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return railway_grievances, railway_clusters


def build_railway_actions(railway_grievances):
    rows = []
    for item in railway_grievances:
        rows.append({
            "id": str(uuid.uuid4()),
            "grievance_id": item["id"],
            "action_type": "submitted",
            "performed_by": item["passenger_name"],
            "notes": f"Bulk seeded railway complaint on {item['train_number']}.",
            "hash": hashlib.sha256(f"{item['id']}submitted{item['created_at']}".encode("utf-8")).hexdigest(),
            "created_at": item["created_at"],
        })
    return rows


def print_header(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def main():
    grievance_count = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    railway_count = int(sys.argv[2]) if len(sys.argv) > 2 else 250
    legal_case_count = int(sys.argv[3]) if len(sys.argv) > 3 else 150

    print("\n" + "=" * 72)
    print("  NyayaSetu Bulk Seeder")
    print(f"  Supabase URL : {SUPABASE_URL}")
    print(f"  Seed tag     : {SEED_TAG}")
    print(f"  Grievances   : {grievance_count}")
    print(f"  Railway rows  : {railway_count}")
    print(f"  Legal cases   : {legal_case_count}")
    print("=" * 72)

    print_header("Building users")
    users, officers, auditors, admins, citizens = create_user_pool()
    print(f"  Users built: {len(users)} (officers={len(officers)}, auditors={len(auditors)}, admins={len(admins)}, citizens={len(citizens)})")

    print_header("Building grievances")
    grievances = build_grievance_pool(grievance_count, officers, auditors)
    clusters = build_clusters_for_grievances(grievances)
    actions = build_actions_for_grievances(grievances)
    print(f"  Grievances built: {len(grievances)}")
    print(f"  Clusters built   : {len(clusters)}")
    print(f"  Actions built    : {len(actions)}")

    print_header("Building legal cases")
    grievance_ids = [item["id"] for item in grievances]
    legal_cases = build_legal_cases(legal_case_count, grievance_ids)
    print(f"  Legal cases built: {len(legal_cases)}")

    print_header("Building railway dataset")
    railway_grievances, railway_clusters = build_railway_pool(railway_count)
    railway_actions = build_railway_actions(railway_grievances)
    print(f"  Railway grievances built: {len(railway_grievances)}")
    print(f"  Railway clusters built   : {len(railway_clusters)}")
    print(f"  Railway actions built    : {len(railway_actions)}")

    print_header("Building audit + predictions")
    budget_rows = build_budget_rows(clusters[: min(len(clusters), 120)])
    prediction_rows = build_prediction_rows(grievances)
    assignments = build_assignments(grievances, officers)
    print(f"  Budget rows    : {len(budget_rows)}")
    print(f"  Predictions    : {len(prediction_rows)}")
    print(f"  Assignments    : {len(assignments)}")

    print_header("Seeding users")
    batch_insert("users", users, "users")

    print_header("Seeding clusters")
    batch_insert("clusters", clusters, "clusters")

    print_header("Seeding grievances")
    batch_insert("grievances", grievances, "grievances")

    print_header("Seeding actions")
    batch_insert("actions", actions, "actions")

    print_header("Seeding legal cases")
    batch_insert("legal_cases", legal_cases, "legal_cases")

    print_header("Seeding railway clusters")
    batch_insert("railway_clusters", railway_clusters, "railway_clusters")

    print_header("Seeding railway grievances")
    batch_insert("railway_grievances", railway_grievances, "railway_grievances")

    print_header("Seeding railway actions")
    batch_insert("railway_actions", railway_actions, "railway_actions")

    print_header("Seeding budget allocations")
    batch_insert("budget_allocations", budget_rows, "budget_allocations")

    print_header("Seeding assignments")
    batch_insert("assignments", assignments, "assignments")

    print_header("Seeding predictions")
    batch_insert("predictions", prediction_rows, "predictions")

    print("\n" + "=" * 72)
    print("  Bulk seeding complete")
    print(f"  Total grievance rows   : {len(grievances)}")
    print(f"  Total railway rows     : {len(railway_grievances)}")
    print(f"  Total legal cases      : {len(legal_cases)}")
    print(f"  Total users            : {len(users)}")
    print(f"  Total clusters         : {len(clusters)}")
    print(f"  Total budget rows      : {len(budget_rows)}")
    print(f"  Total assignments      : {len(assignments)}")
    print(f"  Total predictions rows : {len(prediction_rows)}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
