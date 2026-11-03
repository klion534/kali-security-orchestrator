from collections import Counter
import html
import json
from pathlib import Path

from .evidence import Finding
from .runner import redact_text


def build_report(run: dict, findings: list[Finding]) -> dict:
    safe_run = _sanitize(run)
    serialized = [finding.as_dict() for finding in findings]
    severity_counts = Counter(finding.severity for finding in findings)
    status_counts = Counter(finding.status for finding in findings)
    run_status = safe_run.get("status")
    tool_status = safe_run.get("tool_status")
    coverage_status = (
        "tool-unavailable"
        if tool_status == "not-installed"
        else "verified"
        if run_status == "completed"
        else "not-verified"
    )
    return {
        "run": safe_run,
        "summary": {
            "total_findings": len(findings),
            "by_severity": dict(sorted(severity_counts.items())),
            "by_status": dict(sorted(status_counts.items())),
        },
        "coverage": [{"tool": safe_run.get("tool", "unknown"), "status": coverage_status}],
        "findings": serialized,
        "limitations": [] if coverage_status == "verified" else [f"Coverage status: {coverage_status}"],
        "pending": [],
    }


def write_reports(directory: str | Path, report: dict) -> dict[str, Path]:
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination.chmod(0o700)
    safe_report = _sanitize(report)
    json_path = destination / "report.json"
    markdown_path = destination / "report.md"
    html_path = destination / "report.html"
    sarif_path = destination / "report.sarif.json"

    json_path.write_text(json.dumps(safe_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(safe_report), encoding="utf-8")
    html_path.write_text(_html(safe_report), encoding="utf-8")
    sarif_path.write_text(json.dumps(_sarif(safe_report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path in (json_path, markdown_path, html_path, sarif_path):
        path.chmod(0o600)
    return {"json": json_path, "markdown": markdown_path, "html": html_path, "sarif": sarif_path}


def _markdown(report: dict) -> str:
    summary = report["summary"]
    coverage = ", ".join(f"{item['tool']}: {item['status']}" for item in report["coverage"])
    lines = [
        "# Security Audit Report",
        "",
        f"Total findings: {summary['total_findings']}",
        f"Coverage: {coverage}",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"## [{finding['severity'].upper()}] {finding['title']}",
                f"- Tool: `{finding['tool']}`",
                f"- Target: `{finding['target']}`",
                f"- Location: `{finding['location']}`",
                f"- Confidence: `{finding['confidence']}`",
                f"- Evidence: `{finding['evidence']}`",
                "",
            ]
        )
    return "\n".join(lines)


def _html(report: dict) -> str:
    body = ["<h1>Security Audit Report</h1>", f"<p>Total findings: {report['summary']['total_findings']}</p>"]
    for finding in report["findings"]:
        body.append(
            "<article>"
            f"<h2>{html.escape(finding['severity'].upper())}: {html.escape(finding['title'])}</h2>"
            f"<p>Tool: <code>{html.escape(finding['tool'])}</code> · Target: <code>{html.escape(finding['target'])}</code></p>"
            f"<p>Evidence: <code>{html.escape(finding['evidence'])}</code></p>"
            "</article>"
        )
    return "<!doctype html><html><body>" + "".join(body) + "</body></html>\n"


def _sarif(report: dict) -> dict:
    results = []
    for finding in report["findings"]:
        level = "error" if finding["severity"] in {"critical", "high"} else "warning" if finding["severity"] in {"medium", "low"} else "note"
        results.append(
            {
                "ruleId": finding["id"],
                "level": level,
                "message": {"text": finding["title"]},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": finding["location"]}}}],
            }
        )
    return {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "runs": [{"tool": {"driver": {"name": "kali-security-orchestrator"}}, "results": results}]}


def _sanitize(value):
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value
