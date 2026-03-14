import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
GEMINI_TIMEOUT = 15.0


async def get_embedding(text: str) -> list | None:
    """Get 768-dimension embedding from Gemini text-embedding-004. Returns None on failure."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key":
        logger.warning("Gemini API key not configured, skipping embedding")
        return None

    if not text or not text.strip():
        return None

    url = f"{GEMINI_EMBED_URL}?key={GEMINI_API_KEY}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{"text": text[:2048]}]
        },
    }

    try:
        async with httpx.AsyncClient(timeout=GEMINI_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            embedding = data.get("embedding", {}).get("values", None)
            if embedding and len(embedding) > 0:
                return embedding
            logger.error("Gemini returned empty embedding")
            return None
    except httpx.TimeoutException:
        logger.error("Gemini embedding API timeout after %.1fs", GEMINI_TIMEOUT)
        return None
    except httpx.HTTPStatusError as e:
        logger.error("Gemini embedding HTTP error: %s %s", e.response.status_code, e.response.text[:200])
        return None
    except Exception as e:
        logger.error("Gemini embedding unexpected error: %s", str(e))
        return None
