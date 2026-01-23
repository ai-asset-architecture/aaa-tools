from __future__ import annotations

from pathlib import Path


ALLOWED_STATUS = {"pass", "fail", "error", "skip"}
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


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


def _format_compliance(value: bool | None) -> str:
    if value is None:
        return "N/A"
    return "PASS" if value else "FAIL"


def _failing_checks(checks: list[dict]) -> str:
    failed = [c.get("id") for c in checks if c.get("status") != "pass"]
    return ", ".join([c for c in failed if c]) or "-"


def _render_template(template_name: str, **values: str) -> str:
    template = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template


def render_markdown(date_str: str, compliance_rate: float, rows: list[dict]) -> str:
    row_lines = []
    for repo in rows:
        row_lines.append(
            "| {name} | {repo_type} | {compliance} | {failing} |".format(
                name=repo.get("name", "-"),
                repo_type=repo.get("repo_type", "-"),
                compliance=_format_compliance(repo.get("compliant")),
                failing=_failing_checks(repo.get("checks", [])),
            )
        )
    return _render_template(
        "dashboard.md.tmpl",
        date=date_str,
        rate_pct=f"{compliance_rate:.0%}",
        rows="\n".join(row_lines),
    )


def render_html(date_str: str, compliance_rate: float, rows: list[dict]) -> str:
    row_lines = []
    for repo in rows:
        row_lines.append(
            "<tr><td>{name}</td><td>{repo_type}</td><td>{compliance}</td><td>{failing}</td></tr>".format(
                name=repo.get("name", "-"),
                repo_type=repo.get("repo_type", "-"),
                compliance=_format_compliance(repo.get("compliant")),
                failing=_failing_checks(repo.get("checks", [])),
            )
        )
    return _render_template(
        "dashboard.html.tmpl",
        date=date_str,
        rate_pct=f"{compliance_rate:.0%}",
        rows="\n".join(row_lines),
    )
