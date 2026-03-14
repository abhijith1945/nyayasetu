import os
import json
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TIMEOUT = 15.0


async def call_groq(prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    """Call Groq API with timeout and fallback. Returns raw text response."""
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key":
        logger.warning("Groq API key not configured, returning empty response")
        return ""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    try:
        async with httpx.AsyncClient(timeout=GROQ_TIMEOUT) as client:
            response = await client.post(GROQ_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except httpx.TimeoutException:
        logger.error("Groq API timeout after %.1fs", GROQ_TIMEOUT)
        return ""
    except httpx.HTTPStatusError as e:
        logger.error("Groq API HTTP error: %s %s", e.response.status_code, e.response.text[:200])
        return ""
    except Exception as e:
        logger.error("Groq API unexpected error: %s", str(e))
        return ""


async def analyse_grievance(text: str, ward: str) -> dict:
    """Analyse a grievance using Groq. Returns structured analysis with safe defaults."""
    safe_defaults = {
        "category": "other",
        "urgency": 3,
        "credibility_score": 50,
        "summary": text[:50] if text else "No description provided",
        "department": "General Administration",
    }

    prompt = (
        "You are a governance AI for India. Analyse this public grievance and return ONLY valid JSON "
        "with no explanation or markdown:\n"
        "{\n"
        '  "category": "one of: water, road, electricity, health, sanitation, legal, other",\n'
        '  "urgency": <integer 1-5 where 5 is most critical>,\n'
        '  "credibility_score": <integer 0-100 based on specificity>,\n'
        '  "summary": "<one sentence under 15 words>",\n'
        '  "department": "<responsible Indian government department>"\n'
        "}\n"
        f"Grievance text: {text}\n"
        f"Ward: {ward}"
    )

    raw = await call_groq(prompt)
    if not raw:
        return safe_defaults

    try:
        # Try to extract JSON from response (handle markdown code blocks)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        result = json.loads(cleaned)
        # Validate and fill missing fields
        return {
            "category": result.get("category", safe_defaults["category"]),
            "urgency": int(result.get("urgency", safe_defaults["urgency"])),
            "credibility_score": int(result.get("credibility_score", safe_defaults["credibility_score"])),
            "summary": result.get("summary", safe_defaults["summary"]),
            "department": result.get("department", safe_defaults["department"]),
        }
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.error("Failed to parse Groq analysis response: %s", str(e))
        return safe_defaults


async def generate_brief(clusters_data: list) -> str:
    """Generate a governance intelligence brief from cluster data."""
    if not clusters_data:
        return "No active clusters to generate a brief from."

    prompt = (
        "You are a governance intelligence analyst for India. Based on the following complaint clusters, "
        "generate a structured governance brief with these sections:\n"
        "1. EXECUTIVE SUMMARY (2-3 sentences)\n"
        "2. TOP ISSUES (bulleted list with ward and severity)\n"
        "3. ROOT CAUSE ANALYSIS (brief analysis)\n"
        "4. RECOMMENDATIONS (actionable steps for authorities)\n\n"
        f"Cluster data: {json.dumps(clusters_data, default=str)}"
    )

    result = await call_groq(prompt)
    if not result:
        # Template fallback
        lines = ["# Governance Intelligence Brief\n", "## Executive Summary"]
        lines.append(f"There are {len(clusters_data)} active complaint clusters requiring attention.\n")
        lines.append("## Top Issues")
        for c in clusters_data[:5]:
            ward = c.get("ward", "Unknown")
            cat = c.get("category", "general")
            count = c.get("count", 0)
            lines.append(f"- **{cat.title()}** in {ward}: {count} complaints")
        lines.append("\n## Recommendations")
        lines.append("- Prioritize clusters with highest complaint counts")
        lines.append("- Deploy field officers to affected wards")
        lines.append("- Schedule review meeting within 48 hours")
        return "\n".join(lines)

    return result


async def translate_to_malayalam(text: str) -> str:
    """Translate text to Malayalam using Groq."""
    prompt = f"Translate the following English text to Malayalam. Return only the Malayalam translation, nothing else:\n\n{text}"
    result = await call_groq(prompt)
    return result if result else text


async def explain_436a(prisoner_name: str, ipc_section: str, max_years: int, months_detained: int, eligible: bool) -> str:
    """Get 436A explanation in English and Malayalam."""
    prompt = (
        f"Explain Section 436A of CrPC for this case in simple language, first in English then in Malayalam:\n"
        f"Prisoner: {prisoner_name}\n"
        f"IPC Section: {ipc_section}\n"
        f"Maximum sentence: {max_years} years\n"
        f"Months detained: {months_detained}\n"
        f"Eligible for 436A bail: {'Yes' if eligible else 'No'}\n"
        f"Half of max sentence: {max_years * 12 // 2} months\n\n"
        "Explain what 436A means, whether this person qualifies, and what steps to take. "
        "Format: English explanation first, then '---' separator, then Malayalam translation."
    )
    result = await call_groq(prompt)
    if not result:
        eng = (
            f"Section 436A CrPC: An undertrial prisoner who has been detained for a period extending "
            f"up to half of the maximum sentence cannot be detained further. "
            f"{prisoner_name} has been detained for {months_detained} months. "
            f"Half of the maximum sentence ({max_years} years) is {max_years * 12 // 2} months. "
            f"{'This person IS eligible for release under Section 436A.' if eligible else 'This person is NOT yet eligible under Section 436A.'}"
        )
        return eng
    return result
