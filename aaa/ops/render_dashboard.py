ALLOWED_STATUS = {"pass", "fail", "error", "skip"}


def compute_compliance(payload):
    rows = []
    eligible = 0
    compliant = 0
    for repo in payload.get("repos", []):
        statuses = [c.get("status") for c in repo.get("checks", [])]
        for status in statuses:
            if status not in ALLOWED_STATUS:
                raise ValueError(f"invalid check status: {status}")
        if repo.get("archived"):
            rows.append({**repo, "compliant": None})
            continue
        eligible += 1
        ok = all(status == "pass" for status in statuses)
        rows.append({**repo, "compliant": ok})
        if ok:
            compliant += 1
    rate = (compliant / eligible) if eligible else 1.0
    return rate, rows
