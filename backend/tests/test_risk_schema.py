from backend.app.schemas.risk import RiskLevel, RiskScore


def test_risk_score_schema() -> None:
    risk = RiskScore(
        signal="detection",
        rule="zone_entry",
        score=78,
        risk_level=RiskLevel.HIGH,
        rationale="High-confidence anomaly near restricted entry route.",
    )

    assert risk.risk_level == RiskLevel.HIGH
    assert risk.score == 78
