from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .runner import redact_text


SEVERITIES = frozenset({"critical", "high", "medium", "low", "info", "unknown"})


@dataclass(frozen=True)
class Finding:
    id: str
    tool: str
    target: str
    title: str
    severity: str
    confidence: str
    category: str
    location: str
    evidence: str
    references: tuple[str, ...]
    status: str = "finding"
    recommendation: str = "Review and validate this finding before remediation."

    def as_dict(self) -> dict:
        return asdict(self) | {"references": list(self.references)}


class EvidenceStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

    def write_run(self, evidence: dict) -> Path:
        if not isinstance(evidence, dict):
            raise ValueError("evidence must be an object")
        sanitized = _sanitize(evidence)
        sanitized.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
        payload = json.dumps(sanitized, ensure_ascii=False, indent=2, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.directory.chmod(0o700)
        path = self.directory / f"run-{digest}.json"
        path.write_text(payload + "\n", encoding="utf-8")
        path.chmod(0o600)
        return path


def parse_findings(tool: str, target: str, output: str) -> list[Finding]:
    records = _json_records(output)
    findings = []
    for record in records:
        if tool == "nuclei":
            findings.extend(_parse_nuclei(record, target))
        elif tool == "gitleaks":
            findings.extend(_parse_gitleaks(record, target))
        elif tool == "trivy":
            findings.extend(_parse_trivy(record, target))
        else:
            finding = _parse_generic(tool, target, record)
            if finding:
                findings.append(finding)
    return findings


def _parse_nuclei(record: dict, target: str) -> list[Finding]:
    info = record.get("info") or {}
    title = str(info.get("name") or record.get("template-id") or "Nuclei finding")
    evidence = json.dumps(record.get("extracted-results") or record, ensure_ascii=False)
    return [_finding(tool="nuclei", target=target, title=title, severity=info.get("severity"), category="web", location=record.get("matched-at", target), evidence=evidence, references=info.get("reference", ()))]


def _parse_gitleaks(record: dict, target: str) -> list[Finding]:
    title = str(record.get("Description") or record.get("RuleID") or "Secret detected")
    location = f"{record.get('File', target)}:{record.get('StartLine', '?')}"
    evidence = json.dumps({"rule": record.get("RuleID"), "file": location}, ensure_ascii=False)
    return [_finding(tool="gitleaks", target=target, title=title, severity="high", category="secrets", location=location, evidence=evidence, references=())]


def _parse_trivy(record: dict, target: str) -> list[Finding]:
    findings = []
    for result in record.get("Results", ()) or ():
        for item in (result.get("Vulnerabilities", ()) or ()) + (result.get("Misconfigurations", ()) or ()) + (result.get("Secrets", ()) or ()):
            title = str(item.get("Title") or item.get("VulnerabilityID") or item.get("ID") or "Trivy finding")
            location = str(result.get("Target") or target)
            evidence = json.dumps({"id": item.get("VulnerabilityID") or item.get("ID"), "package": item.get("PkgName")}, ensure_ascii=False)
            findings.append(_finding(tool="trivy", target=target, title=title, severity=item.get("Severity"), category="dependencies", location=location, evidence=evidence, references=(item.get("PrimaryURL"),)))
    return findings


def _parse_generic(tool: str, target: str, record: dict) -> Finding | None:
    title = record.get("title") or record.get("name") or record.get("message")
    if not title:
        return None
    return _finding(tool=tool, target=target, title=str(title), severity=record.get("severity"), category="unknown", location=str(record.get("location") or target), evidence=json.dumps(record, ensure_ascii=False), references=record.get("references", ()))


def _finding(*, tool, target, title, severity, category, location, evidence, references) -> Finding:
    normalized_severity = str(severity or "unknown").lower()
    if normalized_severity not in SEVERITIES:
        normalized_severity = "unknown"
    safe_references = tuple(str(reference) for reference in references or () if reference)
    safe_evidence = redact_text(str(evidence))
    identity = "|".join((tool, target, str(title), str(location)))
    finding_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return Finding(
        id=finding_id,
        tool=tool,
        target=redact_text(target),
        title=redact_text(str(title)),
        severity=normalized_severity,
        confidence="confirmed",
        category=category,
        location=redact_text(str(location)),
        evidence=safe_evidence,
        references=safe_references,
    )


def _json_records(output: str) -> list[dict]:
    records = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, list):
            records.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            records.append(value)
    return records


def _sanitize(value):
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value
