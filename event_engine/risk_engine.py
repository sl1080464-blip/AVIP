from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskRule:
    name: str
    score: int
    description: str


class RiskEngine:
    """Abstract risk engine responsible for interpreting signal and rule inputs."""

    def evaluate(self, signal: str, rules: list[RiskRule]) -> int:
        if not rules:
            return 0
        return max(rule.score for rule in rules if rule.name or signal)
