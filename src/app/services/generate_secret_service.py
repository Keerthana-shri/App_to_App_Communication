import uuid

def generate_application_secret() -> str:
    """Generate a secure random secret for an application as a UUID4 string."""
    return str(uuid.uuid4())