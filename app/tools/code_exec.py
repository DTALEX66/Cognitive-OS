def code_exec(code: str, dry_run: bool = True):
    return {"dry_run": dry_run, "code_preview": code[:200]}
