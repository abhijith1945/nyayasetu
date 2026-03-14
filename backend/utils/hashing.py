import hashlib


def generate_hash(grievance_id: str, created_at: str, description: str) -> str:
    """Generate SHA-256 hash for tamper-proof grievance receipt."""
    try:
        raw = f"{grievance_id}{created_at}{description}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
    except Exception:
        return hashlib.sha256(str(grievance_id).encode("utf-8")).hexdigest()


def generate_action_hash(action_id: str, grievance_id: str, action_type: str, created_at: str) -> str:
    """Generate SHA-256 hash for tamper-proof action log."""
    try:
        raw = f"{action_id}{grievance_id}{action_type}{created_at}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
    except Exception:
        return hashlib.sha256(str(action_id).encode("utf-8")).hexdigest()
