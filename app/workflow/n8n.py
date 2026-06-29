def trigger_n8n(webhook_url: str, payload: dict):
    return {"webhook": webhook_url, "status": "stub"}
