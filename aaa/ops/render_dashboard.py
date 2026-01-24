from __future__ import annotations

import json
from pathlib import Path


ALLOWED_STATUS = {"pass", "fail", "error", "skip"}
DRIFT_CHECKS = {"orphaned_assets", "checks_manifest_alignment"}
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


def compute_compliance(payload):
    rows = []
    eligible = 0
    compliant = 0
    archived_count = 0
    for repo in payload.get("repos", []):
        statuses = [c.get("status") for c in repo.get("checks", [])]
        for status in statuses:
            if status not in ALLOWED_STATUS:
                raise ValueError(f"invalid check status: {status}")
        if repo.get("archived"):
            archived_count += 1
            rows.append({**repo, "compliant": None})
            continue
        eligible += 1
        ok = all(status == "pass" for status in statuses)
        rows.append({**repo, "compliant": ok})
        if ok:
            compliant += 1
    rate = (compliant / eligible) if eligible else 1.0
    total = len(payload.get("repos", []))
    failing = sum(1 for repo in rows if repo.get("compliant") is False)
    summary = {
        "total_repos": total,
        "eligible_repos": eligible,
        "compliant_repos": compliant,
        "failing_repos": failing,
        "archived_repos": archived_count,
    }
    return rate, rows, summary


def compute_metrics(payload: dict) -> dict[str, float]:
    eligible = 0
    drift_repos = 0
    health_scores = []
    for repo in payload.get("repos", []):
        if repo.get("archived"):
            continue
        eligible += 1
        checks = repo.get("checks", [])
        statuses = [check.get("status") for check in checks]
        total_checks = len(statuses)
        pass_count = sum(1 for status in statuses if status == "pass")
        health_scores.append((pass_count / total_checks) if total_checks else 1.0)
        drift_checks = [check for check in checks if check.get("id") in DRIFT_CHECKS]
        if drift_checks and any(check.get("status") != "pass" for check in drift_checks):
            drift_repos += 1
    drift_rate = (drift_repos / eligible) if eligible else 0.0
    repo_health = (sum(health_scores) / eligible) if eligible else 1.0
    return {
        "drift_rate": drift_rate,
        "repo_health": repo_health,
    }


def _format_compliance(value: bool | None) -> str:
    if value is None:
        return "N/A"
    return "PASS" if value else "FAIL"


def _format_status_key(value: bool | None) -> str:
    if value is None:
        return "archived"
    return "pass" if value else "fail"


def _compliance_class(value: bool | None) -> str:
    if value is None:
        return "status-na"
    return "status-pass" if value else "status-fail"


def _failing_checks(checks: list[dict]) -> str:
    failed = [c.get("id") for c in checks if c.get("status") != "pass"]
    return ", ".join([c for c in failed if c]) or "-"


def _render_template(template_name: str, **values: str) -> str:
    template = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template


def _build_failing_list(rows: list[dict]) -> list[dict]:
    failing = []
    for repo in rows:
        if repo.get("compliant") is False:
            failing.append(
                {
                    "name": repo.get("name", "-"),
                    "repo_type": repo.get("repo_type", "-"),
                    "failing": _failing_checks(repo.get("checks", [])),
                }
            )
    return failing


def _update_trends(path: Path, date_str: str, compliance_rate: float, total_repos: int) -> None:
    entries = []
    if path.exists():
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
    entries.append(
        {
            "date": date_str,
            "compliance_rate": round(compliance_rate, 4),
            "total_repos": total_repos,
        }
    )
    if len(entries) > 90:
        entries = entries[-90:]
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _update_metrics(path: Path, date_str: str, compliance_rate: float, metrics: dict[str, float]) -> None:
    entries = []
    if path.exists():
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
    entries.append(
        {
            "date": date_str,
            "compliance_rate": round(compliance_rate, 4),
            "drift_rate": round(metrics.get("drift_rate", 0.0), 4),
            "repo_health": round(metrics.get("repo_health", 0.0), 4),
        }
    )
    if len(entries) > 90:
        entries = entries[-90:]
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def render_markdown(
    date_str: str,
    compliance_rate: float,
    rows: list[dict],
    summary: dict,
    metrics: dict[str, float],
) -> str:
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
    failing_rows = _build_failing_list(rows)
    if failing_rows:
        failing_md = "\n".join(
            "- {name} ({repo_type}) - {failing}".format(**row)
            for row in failing_rows
        )
    else:
        failing_md = "- None / 無"
    return _render_template(
        "dashboard.md.tmpl",
        date=date_str,
        rate_pct=f"{compliance_rate:.0%}",
        drift_rate_pct=f"{metrics.get('drift_rate', 0.0):.0%}",
        repo_health_pct=f"{metrics.get('repo_health', 0.0):.0%}",
        total_repos=str(summary.get("total_repos", 0)),
        eligible_repos=str(summary.get("eligible_repos", 0)),
        failing_repos=str(summary.get("failing_repos", 0)),
        archived_repos=str(summary.get("archived_repos", 0)),
        failing_list=failing_md,
        rows="\n".join(row_lines),
    )


def render_html(
    date_str: str,
    compliance_rate: float,
    rows: list[dict],
    summary: dict,
    metrics: dict[str, float],
    thresholds: dict[str, float],
) -> str:
    row_lines = []
    for repo in rows:
        status_key = _format_status_key(repo.get("compliant"))
        status_label = _format_compliance(repo.get("compliant"))
        status_class = _compliance_class(repo.get("compliant"))
        row_lines.append(
            "<tr>"
            "<td class=\"repo-name\">{name}</td>"
            "<td class=\"repo-type\">{repo_type}</td>"
            "<td><span class=\"status {status_class}\" data-status=\"{status_key}\">{status_label}</span></td>"
            "<td class=\"failing\">{failing}</td>"
            "</tr>".format(
                name=repo.get("name", "-"),
                repo_type=repo.get("repo_type", "-"),
                status_class=status_class,
                status_key=status_key,
                status_label=status_label,
                failing=_failing_checks(repo.get("checks", [])),
            )
        )
    failing_rows = _build_failing_list(rows)
    if failing_rows:
        failing_list = "\n".join(
            "<li><div class=\"fail-name\">{name}</div>"
            "<div class=\"fail-meta\">{repo_type}</div>"
            "<div class=\"fail-checks\">{failing}</div></li>".format(**row)
            for row in failing_rows
        )
    else:
        failing_list = "<li class=\"empty\" data-i18n=\"panel.failing_empty\">All repos compliant</li>"
    return _render_template(
        "dashboard.html.tmpl",
        date=date_str,
        rate_pct=f"{compliance_rate:.0%}",
        drift_rate_pct=f"{metrics.get('drift_rate', 0.0):.0%}",
        repo_health_pct=f"{metrics.get('repo_health', 0.0):.0%}",
        total_repos=str(summary.get("total_repos", 0)),
        eligible_repos=str(summary.get("eligible_repos", 0)),
        failing_repos=str(summary.get("failing_repos", 0)),
        archived_repos=str(summary.get("archived_repos", 0)),
        failing_list=failing_list,
        rows="\n".join(row_lines),
        threshold=f"{thresholds.get('compliance', 0.8):.2f}",
        drift_threshold=f"{thresholds.get('drift', 0.05):.2f}",
        health_threshold=f"{thresholds.get('health', 0.9):.2f}",
    )


def render_dashboard(
    input_path: str,
    md_out: str,
    html_out: str,
    thresholds: dict[str, float] | None = None,
) -> tuple[float, dict[str, float]]:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    compliance_rate, rows, summary = compute_compliance(payload)
    metrics = compute_metrics(payload)
    date_str = payload.get("generated_at") or "-"
    thresholds = thresholds or {"compliance": 0.8, "drift": 0.05, "health": 0.9}
    md = render_markdown(date_str, compliance_rate, rows, summary, metrics)
    html = render_html(date_str, compliance_rate, rows, summary, metrics, thresholds)
    md_path = Path(md_out)
    html_path = Path(html_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    css = _render_template("dashboard.css.tmpl")
    js = _render_template("dashboard.js.tmpl")
    (html_path.parent / "dashboard.css").write_text(css, encoding="utf-8")
    (html_path.parent / "dashboard.js").write_text(js, encoding="utf-8")
    _update_trends(
        html_path.parent / "trends.json",
        date_str,
        compliance_rate,
        summary.get("total_repos", 0),
    )
    _update_metrics(
        html_path.parent / "metrics.json",
        date_str,
        compliance_rate,
        metrics,
    )
    return compliance_rate, metrics
