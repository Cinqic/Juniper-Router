from pathlib import Path

from juniper_router.runtime.audit import AuditLogger


def test_audit_redacts_secret_and_enforces_bound(tmp_path: Path):
    path = tmp_path / "audit.jsonl"
    AuditLogger(path, max_bytes=2000).append({"event": "x", "api_key": "secret-value"})
    text = path.read_text(encoding="utf-8")
    assert "secret-value" not in text
    assert "REDACTED" in text
