"""
seed_data.py — Seed test data into Supabase for NyayaSetu
Run:  py seed_data.py   (from the backend/ directory)

Seeds:
  - 60 grievances (water, road, electricity, health, sanitation, legal, general)
  - 5 undertrial legal cases (2 are 436A eligible)
"""

import os
import sys
import hashlib
import random
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Set SUPABASE_URL and SUPABASE_KEY in .env first.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Connected to Supabase")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
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

NAMES = [
    "Arun Kumar", "Priya Nair", "Rajesh Menon", "Lakshmi Devi", "Suresh Pillai",
    "Anitha George", "Vijay Krishnan", "Deepa Mohan", "Manoj Varma", "Suja Thomas",
    "Rajan Nambiar", "Kavitha Rajan", "Dileep Kumar", "Meera Suresh", "Biju Mathew",
    "Asha Kumari", "Sandeep Nair", "Geetha Pillai", "Ajith Prasad", "Reshma Abdul",
    "Sreekumar K.", "Divya Raj", "Harikrishnan M.", "Bindu Sasidharan", "Unnikrishnan P.",
    "Jyothi Lal", "Gopakumar S.", "Parvathy Menon", "Shibu Das", "Saritha Devi",
    "Jayakumar V.", "Soumya Krishnan", "Babu Raj", "Thulasi Nair", "Sajeev Kumar",
    "Ammu Lakshmi", "Muraleedharan K.", "Indira Varma", "Shaji George", "Remya Mohan",
    "Anil Krishnan", "Veena Nair", "Prasad Pillai", "Manju Thomas", "Sunil Kumar R.",
    "Sreelatha K.", "Pramod Nambiar", "Swathi Menon", "Madhavan Pillai", "Beena Joseph",
]


def random_phone() -> str:
    """Indian mobile number in +91 format."""
    return f"+919{random.randint(100000000, 999999999)}"


def gen_hash(gid: str, created_at: str, desc: str) -> str:
    raw = f"{gid}{created_at}{desc}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# WATER complaints — 10 total: 5 in Ward 1, 5 in Ward 3  (must cluster)
# ---------------------------------------------------------------------------
WATER_WARD1 = [
    {
        "description": (
            "Water pipeline burst near Kazhakoottam junction causing flooding "
            "on main road since 3 days. Dirty water mixing with drinking supply. "
            "Multiple houses affected in Chanthavila area."
        ),
        "ai_summary": "Pipeline burst at Kazhakoottam junction; flooding for 3 days with contamination risk in Chanthavila.",
    },
    {
        "description": (
            "No water supply in Kazhakoottam colony for the last 5 days. "
            "Tanker lorry also not coming. Senior citizens and children suffering "
            "badly. Kerala Water Authority helpline always busy."
        ),
        "ai_summary": "Complete water outage in Kazhakoottam colony for 5 days; vulnerable residents affected, KWA unreachable.",
    },
    {
        "description": (
            "Sewage water leaking into drinking water pipe near Kazhakoottam "
            "bus stop. Multiple families reporting stomach illness and diarrhoea. "
            "Health inspector visited but no repair initiated."
        ),
        "ai_summary": "Sewage-drinking water cross-contamination near Kazhakoottam bus stop causing gastrointestinal illness.",
    },
    {
        "description": (
            "Open water tank in Kazhakoottam ward overflowing daily, wasting "
            "thousands of litres. Mosquito breeding ground formed around it. "
            "Dengue risk increasing in nearby residential area."
        ),
        "ai_summary": "Overflowing water tank in Kazhakoottam causing wastage and mosquito breeding; dengue risk.",
    },
    {
        "description": (
            "Brown-coloured water coming from taps in Chanthavila area near "
            "Kazhakoottam since one week. Water Authority not responding to "
            "complaints. We are buying bottled water for cooking and drinking."
        ),
        "ai_summary": "Discoloured tap water in Chanthavila near Kazhakoottam for a week; KWA unresponsive.",
    },
]

WATER_WARD3 = [
    {
        "description": (
            "Major water main leak on Pattom-Kesavadasapuram road. Road "
            "completely flooded and traffic disrupted for 2 days. KSRTC buses "
            "diverted. Urgent repair needed before monsoon worsens situation."
        ),
        "ai_summary": "Water main leak on Pattom-Kesavadasapuram road causing flooding and traffic disruption for 2 days.",
    },
    {
        "description": (
            "Pattom Marappalam area residents not getting water since last "
            "4 days. Kerala Water Authority office giving no proper response. "
            "Housewives queuing at public tap from 4 AM every morning."
        ),
        "ai_summary": "4-day water outage in Pattom Marappalam; KWA office unresponsive, residents queuing from 4 AM.",
    },
    {
        "description": (
            "Contaminated water supply in Pattom ward near Government "
            "Secretariat quarters. Water has foul smell and yellowish colour. "
            "Children in nearby LP school falling sick with vomiting."
        ),
        "ai_summary": "Foul-smelling contaminated water in Pattom near Secretariat quarters; school children falling ill.",
    },
    {
        "description": (
            "Broken water meter in Pattom Palace Road area overcharging "
            "residents. Bills showing Rs.4000 instead of usual Rs.600. "
            "Multiple complaints filed with KWA but no action for 3 months."
        ),
        "ai_summary": "Faulty water meters in Pattom overcharging residents; unresolved for 3 months despite complaints.",
    },
    {
        "description": (
            "Low water pressure in Pattom desom area. Water only trickles "
            "for 10 minutes in the morning. Very difficult for daily cooking, "
            "washing, and bathing. Requesting additional pump installation."
        ),
        "ai_summary": "Severely low water pressure in Pattom desom; only 10 minutes of trickle supply daily.",
    },
]

# ---------------------------------------------------------------------------
# ROAD complaints — 10, spread across wards
# ---------------------------------------------------------------------------
ROAD_COMPLAINTS = [
    {
        "description": (
            "Massive pothole on NH-66 bypass near Technopark Phase 3 entrance. "
            "Multiple two-wheeler accidents reported in last 2 weeks. A delivery "
            "boy broke his leg falling into it yesterday evening."
        ),
        "ai_summary": "Dangerous pothole on NH-66 near Technopark Phase 3 causing two-wheeler accidents.",
        "ward": "Ward 2 (Technopark)",
    },
    {
        "description": (
            "Street lights not working on entire stretch from Vanchiyoor court "
            "junction to Overbridge for past 3 weeks. Very dangerous for "
            "pedestrians at night. Women afraid to walk alone after 7 PM."
        ),
        "ai_summary": "Complete streetlight failure from Vanchiyoor court to Overbridge for 3 weeks; pedestrian safety risk.",
        "ward": "Ward 4 (Vanchiyoor)",
    },
    {
        "description": (
            "Road completely washed out near Palayam market after last week "
            "heavy rains. Auto-rickshaws and buses refusing to go there. "
            "Shop owners losing 50% business. Needs immediate re-tarring."
        ),
        "ai_summary": "Rain-damaged road near Palayam market disrupting transport and local businesses.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Dangerous open manhole on Karamana bridge approach road. A child "
            "fell in yesterday evening and got leg injury. No barricade or "
            "warning sign placed by Corporation. Extremely negligent."
        ),
        "ai_summary": "Uncovered manhole on Karamana bridge road; child injured, no safety barriers placed.",
        "ward": "Ward 6 (Karamana)",
    },
    {
        "description": (
            "Road divider broken at Nemom junction causing wrong-side driving. "
            "Traffic police ignoring the issue completely. Three accidents in "
            "last 10 days. One person in ICU at Medical College Hospital."
        ),
        "ai_summary": "Broken divider at Nemom junction enabling wrong-side driving; 3 accidents in 10 days.",
        "ward": "Ward 7 (Nemom)",
    },
    {
        "description": (
            "Waterlogged road near Kovalam beach entry point since last monsoon. "
            "Tourists and locals unable to reach beach safely. Drainage completely "
            "blocked with plastic waste. Tourism revenue affected badly."
        ),
        "ai_summary": "Waterlogged road at Kovalam beach entry due to blocked drainage; tourism revenue impacted.",
        "ward": "Ward 8 (Kovalam)",
    },
    {
        "description": (
            "Unfinished road work near Kazhakoottam IT corridor left open for "
            "2 months by contractor. Gravel and mud making commute extremely "
            "difficult for thousands of IT employees daily. No timeline given."
        ),
        "ai_summary": "Abandoned road work near Kazhakoottam IT corridor for 2 months; daily commuter hardship.",
        "ward": "Ward 1 (Kazhakoottam)",
    },
    {
        "description": (
            "Heavy truck traffic damaging internal roads in Pattom residential "
            "area. Roads not designed for heavy vehicles. Deep cracks appearing "
            "everywhere. Multiple representations to Corporation went unanswered."
        ),
        "ai_summary": "Heavy truck traffic destroying residential roads in Pattom; cracking widespread.",
        "ward": "Ward 3 (Pattom)",
    },
    {
        "description": (
            "Pedestrian crossing signal not working at Palayam-PMG junction "
            "for the past month. Elderly people and school children unable to "
            "cross safely. Traffic constable posted only during morning hours."
        ),
        "ai_summary": "Non-functional pedestrian signal at Palayam-PMG junction for a month; elderly and children at risk.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Tar road completely peeled off in Technopark internal road near "
            "TCS building. Dusty conditions causing respiratory issues for IT "
            "workers. Campus management says PWD responsibility, PWD says campus."
        ),
        "ai_summary": "Deteriorated tar road inside Technopark near TCS; dust causing respiratory complaints, blame-shifting.",
        "ward": "Ward 2 (Technopark)",
    },
]

# ---------------------------------------------------------------------------
# ELECTRICITY complaints — 10, spread across wards
# ---------------------------------------------------------------------------
ELECTRICITY_COMPLAINTS = [
    {
        "description": (
            "Frequent power cuts in Technopark Phase 1 area, 4 to 5 times daily "
            "since last week. UPS systems in offices failing. IT companies losing "
            "productivity and threatening to relocate to Kochi InfoPark."
        ),
        "ai_summary": "Repeated daily power cuts in Technopark Phase 1 impacting IT company operations.",
        "ward": "Ward 2 (Technopark)",
    },
    {
        "description": (
            "Transformer near Vanchiyoor market making loud humming noise and "
            "sparking at night. Residents fear electrocution or fire hazard. "
            "KSEB lineman visited but said parts not available for repair."
        ),
        "ai_summary": "Sparking transformer near Vanchiyoor market posing fire and electrocution risk; parts unavailable.",
        "ward": "Ward 4 (Vanchiyoor)",
    },
    {
        "description": (
            "Fallen electric pole leaning on compound wall in Nemom ward after "
            "last week cyclone. KSEB not attended in 5 days. Live wire hanging "
            "dangerously close to footpath where school children walk daily."
        ),
        "ai_summary": "Fallen electric pole with live wire in Nemom unattended for 5 days post-cyclone; school-route hazard.",
        "ward": "Ward 7 (Nemom)",
    },
    {
        "description": (
            "Billing error from KSEB — charged Rs.18,000 for a single month for "
            "a small 2-BHK house in Karamana. Normal monthly bill is Rs.800. "
            "Online portal not accepting dispute. Office asks to pay first."
        ),
        "ai_summary": "KSEB billing error in Karamana: Rs 18,000 charge vs normal Rs 800; dispute process broken.",
        "ward": "Ward 6 (Karamana)",
    },
    {
        "description": (
            "Street lights in Kovalam beach road area not working for past 3 "
            "weeks. Tourist area becoming unsafe after dark. Foreign tourists "
            "complaining on travel forums. Damaging Kerala tourism reputation."
        ),
        "ai_summary": "3-week streetlight outage on Kovalam beach road; tourist safety compromised, reputation damage.",
        "ward": "Ward 8 (Kovalam)",
    },
    {
        "description": (
            "Electric wire sagging very low over the road near Palayam bus "
            "stand. Top of KSRTC buses almost touching the wire during rush "
            "hour. Major accident waiting to happen. Reported to KSEB thrice."
        ),
        "ai_summary": "Dangerously sagging electric wire over Palayam bus stand road; buses nearly touching it.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "No electricity connection provided to newly constructed houses in "
            "Kazhakoottam Smart City layout. Applied 6 months ago with all "
            "documents but no response from KSEB. Families living with generator."
        ),
        "ai_summary": "6-month delay in electricity connection for new houses in Kazhakoottam Smart City layout.",
        "ward": "Ward 1 (Kazhakoottam)",
    },
    {
        "description": (
            "Recurring voltage fluctuation in Pattom causing damage to "
            "electronic appliances. My refrigerator and washing machine both "
            "damaged last week. KSEB says stabilizer is our responsibility."
        ),
        "ai_summary": "Voltage fluctuations in Pattom damaging household appliances; KSEB deflecting responsibility.",
        "ward": "Ward 3 (Pattom)",
    },
    {
        "description": (
            "Illegal electricity tapping by a large construction site near "
            "Nemom temple. Causing frequent tripping for the whole neighbourhood "
            "of 150 houses. KSEB should investigate and take action immediately."
        ),
        "ai_summary": "Suspected illegal electricity tapping by construction site in Nemom affecting 150 households.",
        "ward": "Ward 7 (Nemom)",
    },
    {
        "description": (
            "Broken electric meter box on public road near Vanchiyoor junction "
            "exposing live wires. School children from Government LPS walk past "
            "daily. Extremely dangerous. Cover was broken by a truck 2 weeks ago."
        ),
        "ai_summary": "Exposed live wires from broken meter box near Vanchiyoor junction; school-route hazard.",
        "ward": "Ward 4 (Vanchiyoor)",
    },
]

# ---------------------------------------------------------------------------
# HEALTH complaints — 10, spread across wards
# ---------------------------------------------------------------------------
HEALTH_COMPLAINTS = [
    {
        "description": (
            "Government General Hospital in Palayam running out of basic "
            "medicines including paracetamol and ORS packets. Patients turned "
            "away and told to buy from private medical shop. Staff says no "
            "stock received from DHS for 2 weeks."
        ),
        "ai_summary": "Palayam govt hospital out of basic medicines for 2 weeks; patients turned away.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Stray dog menace in Karamana residential area. Five people bitten "
            "in last 10 days including two children under age 8. Anti-rabies "
            "vaccine not available at the PHC. Corporation not conducting ABC drive."
        ),
        "ai_summary": "Stray dog attacks in Karamana; 5 bitten including 2 children. PHC lacks rabies vaccine.",
        "ward": "Ward 6 (Karamana)",
    },
    {
        "description": (
            "Dengue cases increasing rapidly in Technopark campus area. Stagnant "
            "water in abandoned construction sites not cleared despite complaints. "
            "Need fumigation drive urgently. Three IT employees hospitalised."
        ),
        "ai_summary": "Rising dengue near Technopark due to stagnant water; 3 IT employees hospitalised.",
        "ward": "Ward 2 (Technopark)",
    },
    {
        "description": (
            "Primary Health Centre in Nemom ward has only one doctor for 15,000 "
            "population. Average waiting time exceeds 4 hours. Patients giving "
            "up and going to expensive private hospitals losing their savings."
        ),
        "ai_summary": "Nemom PHC critically understaffed: 1 doctor for 15K population; 4-hour wait times.",
        "ward": "Ward 7 (Nemom)",
    },
    {
        "description": (
            "Food poisoning outbreak in Kovalam tourist area. At least 12 people "
            "hospitalised after eating from roadside stall near lighthouse. "
            "Health inspector informed but not taking any action against vendors."
        ),
        "ai_summary": "Food poisoning outbreak in Kovalam: 12 hospitalised from roadside stall; inspector inactive.",
        "ward": "Ward 8 (Kovalam)",
    },
    {
        "description": (
            "Open garbage dump near Vanchiyoor residential colony causing "
            "respiratory diseases. Children suffering from chronic asthma and "
            "allergies. Multiple petitions to Corporation and MLA office filed "
            "with zero response over 6 months."
        ),
        "ai_summary": "Open dump near Vanchiyoor colony causing respiratory issues in children; petitions ignored 6 months.",
        "ward": "Ward 4 (Vanchiyoor)",
    },
    {
        "description": (
            "Ambulance service number 108 not reachable in Kazhakoottam area. "
            "My father had severe chest pain at midnight and we could not get "
            "ambulance for 45 minutes. Had to use private vehicle. Very dangerous."
        ),
        "ai_summary": "108 ambulance unreachable in Kazhakoottam; cardiac patient waited 45 minutes at midnight.",
        "ward": "Ward 1 (Kazhakoottam)",
    },
    {
        "description": (
            "Expired medicines being sold at a pharmacy near Pattom junction. "
            "I purchased cough syrup that expired 6 months ago. Another customer "
            "got expired antibiotics. Drug inspector should raid and take action."
        ),
        "ai_summary": "Pharmacy near Pattom selling expired medicines; multiple customers affected, inspection needed.",
        "ward": "Ward 3 (Pattom)",
    },
    {
        "description": (
            "Rat infestation in Palayam Connemara Market area spreading "
            "leptospirosis risk. Market association formally requested fumigation "
            "and pest control but municipality has not responded in 3 weeks."
        ),
        "ai_summary": "Rat infestation in Palayam market creating leptospirosis risk; fumigation request pending 3 weeks.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Mental health counselling centre run by Corporation in Karamana "
            "closed for 3 months without notice. Patients with depression and "
            "anxiety left without support. Nearest alternative is 15 km away."
        ),
        "ai_summary": "Karamana mental health centre closed 3 months without notice; patients unsupported.",
        "ward": "Ward 6 (Karamana)",
    },
]

# ---------------------------------------------------------------------------
# SANITATION complaints — 10, spread across wards
# ---------------------------------------------------------------------------
SANITATION_COMPLAINTS = [
    {
        "description": (
            "Garbage not collected in Technopark residential area for 10 days "
            "running. Waste piling up on streets attracting rats and crows. "
            "Foul smell making it impossible to open windows. Corporation truck "
            "driver says vehicle is broken."
        ),
        "ai_summary": "10-day garbage collection lapse in Technopark residential area; waste piling up, vehicle broken.",
        "ward": "Ward 2 (Technopark)",
    },
    {
        "description": (
            "Public toilet near Palayam KSRTC bus stand in extremely unhygienic "
            "condition. No water supply, no daily cleaning, broken door latches. "
            "Women and elderly completely avoiding it. Tourists disgusted."
        ),
        "ai_summary": "Palayam bus stand public toilet unclean and waterless; unusable for women and elderly.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Blocked drainage on MG Road in Vanchiyoor causing raw sewage "
            "overflow onto main road. Sewage flowing into residential area "
            "affecting more than 200 families. Corporation says contractor "
            "dispute delaying work."
        ),
        "ai_summary": "Sewage overflow from blocked drain in Vanchiyoor MG Road affecting 200+ families.",
        "ward": "Ward 4 (Vanchiyoor)",
    },
    {
        "description": (
            "Illegal dumping of construction debris near Nemom Government "
            "Upper Primary School compound wall. Children exposed to dust and "
            "sharp materials during interval time. PTA complained but no action."
        ),
        "ai_summary": "Construction debris illegally dumped near Nemom school; children at risk during playtime.",
        "ward": "Ward 7 (Nemom)",
    },
    {
        "description": (
            "Dead animal carcass lying on Kovalam-Vizhinjam coastal road for "
            "4 days. Corporation not removing despite multiple phone calls. "
            "Vultures gathering and terrible stench reaching nearby hotels."
        ),
        "ai_summary": "Animal carcass on Kovalam-Vizhinjam road unremoved 4 days; stench reaching tourist hotels.",
        "ward": "Ward 8 (Kovalam)",
    },
    {
        "description": (
            "Waste treatment plant in Karamana malfunctioning since 2 weeks. "
            "Untreated sewage being directly discharged into Karamana river. "
            "Fish dying downstream. Environmental activist group filed complaint."
        ),
        "ai_summary": "Karamana waste plant malfunction: untreated sewage discharged into river for 2 weeks; fish dying.",
        "ward": "Ward 6 (Karamana)",
    },
    {
        "description": (
            "Plastic waste burning happening every night near Kazhakoottam "
            "bypass by unknown persons. Toxic black smoke entering residential "
            "flats in Muttathara area. Asthma patients suffering badly."
        ),
        "ai_summary": "Nightly illegal plastic burning near Kazhakoottam bypass; toxic smoke reaching Muttathara residences.",
        "ward": "Ward 1 (Kazhakoottam)",
    },
    {
        "description": (
            "Overflowing septic tank in Pattom government staff quarters "
            "contaminating surrounding ground for weeks. Residents complaining "
            "of severe skin rashes and itching after ground water contact."
        ),
        "ai_summary": "Overflowing septic tank in Pattom govt quarters causing skin rashes from groundwater contamination.",
        "ward": "Ward 3 (Pattom)",
    },
    {
        "description": (
            "No dustbins provided in Palayam commercial area despite Smart "
            "City project promise made 2 years ago. Shopkeepers dumping waste "
            "on road. Area looks terrible for tourists visiting Kanakakunnu Palace."
        ),
        "ai_summary": "No dustbins in Palayam commercial area despite Smart City promise; waste on roads near tourist spots.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Clogged storm-water drain in Technopark campus flooding basement "
            "parking during every rain. Employees vehicles getting water damage. "
            "Management and Corporation both not clearing the drain. Insurance "
            "not covering repeated claims."
        ),
        "ai_summary": "Clogged storm drain floods Technopark basement parking each rain; vehicle damage, insurance refused.",
        "ward": "Ward 2 (Technopark)",
    },
]

# ---------------------------------------------------------------------------
# LEGAL complaints — 5
# ---------------------------------------------------------------------------
LEGAL_COMPLAINTS = [
    {
        "description": (
            "My brother is an undertrial prisoner in Poojappura Central Jail "
            "for 18 months on a petty theft charge under IPC 379. Maximum "
            "sentence is only 3 years. No legal aid lawyer assigned despite "
            "DLSA application. Bail hearing postponed 6 times by court."
        ),
        "ai_summary": "Undertrial in Poojappura jail 18 months for petty theft; no legal aid, bail postponed 6 times.",
        "ward": "Ward 4 (Vanchiyoor)",
    },
    {
        "description": (
            "Illegal land encroachment by local builder on government poramboke "
            "land near Nemom lake. Panchayat survey records appear to be "
            "tampered. Filed complaint with Nemom police but they say it is "
            "civil matter and refuse to register FIR."
        ),
        "ai_summary": "Land encroachment by builder in Nemom; survey records possibly tampered; police refusing FIR.",
        "ward": "Ward 7 (Nemom)",
    },
    {
        "description": (
            "RTI application filed 4 months ago with Corporation Engineering "
            "section for road construction tender details and contractor "
            "payments. No reply received under Section 7. First appeal to "
            "Appellate Authority also completely ignored."
        ),
        "ai_summary": "RTI for road tender details unanswered 4 months; first appeal also ignored by Corporation.",
        "ward": "Ward 5 (Palayam)",
    },
    {
        "description": (
            "Domestic violence case registered at Karamana Women's Police "
            "Station 8 months ago but police not filing chargesheet. Accused "
            "husband roaming freely and openly threatening the victim. Kerala "
            "Women's Commission complaint also pending without action."
        ),
        "ai_summary": "DV case chargesheet pending 8 months; accused free and threatening; Women's Commission inactive.",
        "ward": "Ward 6 (Karamana)",
    },
    {
        "description": (
            "My 82-year-old father-in-law forcibly evicted from own ancestral "
            "property in Pattom by his nephew. Revenue Department not enforcing "
            "Munsiff Court order to restore possession. He is now living with "
            "us in a single room. Very distressing situation."
        ),
        "ai_summary": "82-year-old evicted from Pattom property; court order unenforced by revenue dept; displaced.",
        "ward": "Ward 3 (Pattom)",
    },
]

# ---------------------------------------------------------------------------
# GENERAL / OTHER complaints — 5
# ---------------------------------------------------------------------------
GENERAL_COMPLAINTS = [
    {
        "description": (
            "Ration shop in Kazhakoottam not distributing rice quota for BPL "
            "families since 2 months. Shop owner claims stock not received from "
            "Civil Supplies Department. 300 families dependent on this shop. "
            "Children going hungry."
        ),
        "ai_summary": "Kazhakoottam ration shop not distributing BPL rice 2 months; 300 families affected.",
        "ward": "Ward 1 (Kazhakoottam)",
    },
    {
        "description": (
            "Government LP school building in Kovalam leaking badly during "
            "every rain. Ceiling plaster falling on students in Class 2 room. "
            "PTA funds exhausted and no help from Education Department despite "
            "written requests with photographs."
        ),
        "ai_summary": "Kovalam govt school building leaking with falling plaster on students; no repair funds.",
        "ward": "Ward 8 (Kovalam)",
    },
    {
        "description": (
            "KSRTC bus service to Technopark reduced from every 10 minutes to "
            "every 40 minutes without any notice. Thousands of IT employees "
            "struggling with daily commute. No alternative public transport. "
            "Auto-rickshaws charging Rs.300 for short distance."
        ),
        "ai_summary": "KSRTC bus frequency to Technopark cut from 10 to 40 min; IT employees stranded, autos overcharging.",
        "ward": "Ward 2 (Technopark)",
    },
    {
        "description": (
            "Old age pension payment pending for 6 months for my 78-year-old "
            "bedridden mother in Karamana. Village office keeps asking for "
            "different documents on each visit. She cannot travel to the office. "
            "Only source of income for medicine."
        ),
        "ai_summary": "78-year-old bedridden woman's pension pending 6 months; village office demanding repeat documents.",
        "ward": "Ward 6 (Karamana)",
    },
    {
        "description": (
            "Severe noise pollution from late-night events at convention centre "
            "near Pattom. Events with DJ music going past midnight with massive "
            "loudspeakers. Clearly violating Supreme Court noise guidelines. "
            "Affecting sleep and health of entire neighbourhood."
        ),
        "ai_summary": "Late-night noise from Pattom convention centre violating SC guidelines; neighbourhood sleep disrupted.",
        "ward": "Ward 3 (Pattom)",
    },
]

# ---------------------------------------------------------------------------
# LEGAL CASES — 5 undertrial prisoners (2 are 436A eligible)
# ---------------------------------------------------------------------------
#
# 436A eligibility: months_detained >= (max_sentence_years * 12) / 2
#
LEGAL_CASES = [
    {
        # 436A ELIGIBLE: detained 21 months, max 3 years => half = 18 months => 21 >= 18
        "prisoner_name": "Murugan Krishnan",
        "ward": "Ward 4 (Vanchiyoor)",
        "ipc_section": "IPC 379 (Theft)",
        "max_sentence_years": 3,
        "detention_start": "2024-06-15",
        "months_detained": 21,
        "dlsa_contact": "DLSA Thiruvananthapuram: 0471-2334455",
    },
    {
        # 436A ELIGIBLE: detained 42 months, max 7 years => half = 42 months => 42 >= 42
        "prisoner_name": "Sunil Babu",
        "ward": "Ward 2 (Technopark)",
        "ipc_section": "IPC 420 (Cheating)",
        "max_sentence_years": 7,
        "detention_start": "2022-09-01",
        "months_detained": 42,
        "dlsa_contact": "DLSA Thiruvananthapuram: 0471-2334455",
    },
    {
        # NOT eligible: detained 14 months, max 3 years => half = 18 => 14 < 18
        "prisoner_name": "Anwar Hussain",
        "ward": "Ward 6 (Karamana)",
        "ipc_section": "IPC 324 (Voluntarily causing hurt)",
        "max_sentence_years": 3,
        "detention_start": "2025-01-10",
        "months_detained": 14,
        "dlsa_contact": "DLSA Thiruvananthapuram: 0471-2334455",
    },
    {
        # NOT eligible: detained 7 months, max 2 years => half = 12 => 7 < 12
        "prisoner_name": "Pradeep Varma",
        "ward": "Ward 1 (Kazhakoottam)",
        "ipc_section": "IPC 304A (Death by negligence)",
        "max_sentence_years": 2,
        "detention_start": "2025-08-20",
        "months_detained": 7,
        "dlsa_contact": "DLSA Thiruvananthapuram: 0471-2334455",
    },
    {
        # NOT eligible: detained 10 months, max 5 years => half = 30 => 10 < 30
        "prisoner_name": "James Kurien",
        "ward": "Ward 5 (Palayam)",
        "ipc_section": "IPC 457 (Lurking house-trespass by night)",
        "max_sentence_years": 5,
        "detention_start": "2025-05-10",
        "months_detained": 10,
        "dlsa_contact": "DLSA Thiruvananthapuram: 0471-2334455",
    },
]


# ===================================================================
# Seed functions
# ===================================================================

def seed_grievances():
    """Build all 60 grievances and insert one-by-one, printing progress."""
    print("\n" + "=" * 65)
    print("  Seeding 60 grievances into 'grievances' table")
    print("=" * 65)

    all_complaints: list[dict] = []

    # --- 10 water (5 x Ward 1, 5 x Ward 3 — clustered) ---
    for item in WATER_WARD1:
        all_complaints.append({**item, "ward": "Ward 1 (Kazhakoottam)", "category": "water"})
    for item in WATER_WARD3:
        all_complaints.append({**item, "ward": "Ward 3 (Pattom)", "category": "water"})

    # --- 10 road ---
    for item in ROAD_COMPLAINTS:
        all_complaints.append({**item, "category": "road"})

    # --- 10 electricity ---
    for item in ELECTRICITY_COMPLAINTS:
        all_complaints.append({**item, "category": "electricity"})

    # --- 10 health ---
    for item in HEALTH_COMPLAINTS:
        all_complaints.append({**item, "category": "health"})

    # --- 10 sanitation ---
    for item in SANITATION_COMPLAINTS:
        all_complaints.append({**item, "category": "sanitation"})

    # --- 5 legal ---
    for item in LEGAL_COMPLAINTS:
        all_complaints.append({**item, "category": "legal"})

    # --- 5 general ---
    for item in GENERAL_COMPLAINTS:
        all_complaints.append({**item, "category": "general"})

    # Pre-generate statuses: mostly open, a few resolved
    statuses = ["open"] * 50 + ["resolved"] * 10
    random.shuffle(statuses)

    success = 0
    total = len(all_complaints)

    for i, complaint in enumerate(all_complaints):
        name = random.choice(NAMES)
        phone = random_phone()
        status = statuses[i] if i < len(statuses) else "open"
        urgency = random.randint(1, 5)
        credibility = random.randint(40, 100)

        row = {
            "citizen_name": name,
            "phone": phone,
            "ward": complaint["ward"],
            "district": "Thiruvananthapuram",
            "description": complaint["description"],
            "category": complaint["category"],
            "urgency": urgency,
            "credibility_score": credibility,
            "ai_summary": complaint["ai_summary"],
            "status": status,
        }

        # Add resolved_at for resolved grievances
        if status == "resolved":
            row["resolved_at"] = (
                datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
            ).isoformat()
            if random.random() < 0.5:
                row["resolution_confirmed"] = True

        try:
            result = supabase.table("grievances").insert(row).execute()

            # Generate and set tamper-proof hash if insert succeeded
            if result.data:
                g = result.data[0]
                h = gen_hash(g["id"], g.get("created_at", ""), complaint["description"])
                supabase.table("grievances").update({"hash": h}).eq("id", g["id"]).execute()

                # Also create an initial "submitted" action log entry
                supabase.table("actions").insert({
                    "grievance_id": g["id"],
                    "action_type": "submitted",
                    "performed_by": name,
                    "notes": f"Seeded: {complaint['category']} complaint from {complaint['ward']}",
                }).execute()

            success += 1
            print(
                f"  [{success:>2}/{total}]  {complaint['category']:<12}  "
                f"{complaint['ward']:<28}  urgency={urgency}  "
                f"cred={credibility:<3}  {status:<8}  {name}"
            )
        except Exception as e:
            print(
                f"  [FAIL]  {complaint['category']:<12}  "
                f"{complaint['ward']:<28}  ERROR: {e}"
            )

    print(f"\n  Grievances inserted: {success}/{total}")
    return success


def seed_legal_cases():
    """Insert 5 undertrial legal cases, printing progress."""
    print("\n" + "=" * 65)
    print("  Seeding 5 legal cases into 'legal_cases' table")
    print("=" * 65)

    success = 0
    total = len(LEGAL_CASES)

    for i, case in enumerate(LEGAL_CASES):
        max_y = case["max_sentence_years"]
        months = case["months_detained"]
        half_max = (max_y * 12) // 2
        eligible = months >= half_max

        row = {
            "prisoner_name": case["prisoner_name"],
            "ward": case["ward"],
            "ipc_section": case["ipc_section"],
            "max_sentence_years": max_y,
            "detention_start": case["detention_start"],
            "months_detained": months,
            "eligible_436a": eligible,
            "dlsa_contact": case["dlsa_contact"],
        }

        tag = "436A-ELIGIBLE" if eligible else "not yet eligible"

        try:
            supabase.table("legal_cases").insert(row).execute()
            success += 1
            print(
                f"  [{success}/{total}]  {case['prisoner_name']:<22}  "
                f"{case['ipc_section']:<42}  {months:>2} months detained  "
                f"half-max={half_max:>2}m  -> {tag}"
            )
        except Exception as e:
            print(
                f"  [FAIL]  {case['prisoner_name']:<22}  ERROR: {e}"
            )

    print(f"\n  Legal cases inserted: {success}/{total}")
    return success


# ===================================================================
# Main
# ===================================================================

def main():
    print("\n" + "=" * 65)
    print("  NyayaSetu  --  Seed Data Script")
    print(f"  Supabase URL : {SUPABASE_URL}")
    print(f"  Timestamp    : {datetime.now().isoformat()}")
    print("=" * 65)

    g_ok = seed_grievances()
    l_ok = seed_legal_cases()

    print("\n" + "=" * 65)
    print(f"  DONE")
    print(f"  Grievances inserted : {g_ok} / 60")
    print(f"  Legal cases inserted: {l_ok} / 5")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
