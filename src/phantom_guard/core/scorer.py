"""Risk scoring engine for package validation.

Calculates risk scores based on package metadata signals.
Scoring algorithm validated in research-output/TECHNICAL_VALIDATION.md
"""

from __future__ import annotations

from phantom_guard.core.types import (
    PackageMetadata,
    PackageRisk,
    RiskLevel,
    RiskSignal,
    SignalType,
)

# Scoring weights (validated against real packages)
SCORE_WEIGHTS = {
    "releases_10_plus": 30,
    "releases_3_to_9": 15,
    "has_repository": 30,
    "has_author": 20,
    "has_description": 20,
}

# Thresholds for risk classification
THRESHOLDS = {
    "safe": 60,
    "suspicious": 30,
}

# Recommendations for each risk level
RECOMMENDATIONS = {
    RiskLevel.SAFE: "Package appears legitimate.",
    RiskLevel.SUSPICIOUS: (
        "CAUTION: Package has suspicious characteristics. Verify before installing."
    ),
    RiskLevel.HIGH_RISK: ("WARNING: High risk package. Do not install without thorough review."),
    RiskLevel.NOT_FOUND: ("BLOCK: Package not found in registry. Likely hallucinated by AI."),
}


class RiskScorer:
    """Calculate risk scores for packages based on metadata signals.

    The scoring algorithm awards points for positive signals:
    - 30 points: 10+ releases (established package)
    - 15 points: 3-9 releases (some history)
    - 30 points: Has repository URL
    - 20 points: Has author information
    - 20 points: Has meaningful description

    Risk levels:
    - SAFE: Score >= 60
    - SUSPICIOUS: Score 30-59
    - HIGH_RISK: Score < 30
    - NOT_FOUND: Package doesn't exist

    Usage:
        scorer = RiskScorer()
        risk = scorer.score(metadata)
        print(f"{risk.package_name}: {risk.risk_level.value}")
    """

    def score(self, metadata: PackageMetadata) -> PackageRisk:
        """Calculate risk score from package metadata.

        Args:
            metadata: Package metadata from registry.

        Returns:
            Complete risk assessment.
        """
        if not metadata.exists:
            return self._not_found_result(metadata)

        signals: list[RiskSignal] = []
        score = 0

        # Release count signal
        score += self._score_releases(metadata, signals)

        # Repository signal
        score += self._score_repository(metadata, signals)

        # Author signal
        score += self._score_author(metadata, signals)

        # Description signal
        score += self._score_description(metadata, signals)

        # Clamp score to valid range
        score = min(100, max(0, score))

        # Determine risk level
        risk_level = self._score_to_level(score)

        return PackageRisk(
            package_name=metadata.name,
            registry=metadata.registry,
            risk_level=risk_level,
            risk_score=score,
            signals=tuple(signals),
            recommendation=RECOMMENDATIONS[risk_level],
            metadata=metadata,
        )

    def _score_releases(
        self,
        metadata: PackageMetadata,
        signals: list[RiskSignal],
    ) -> int:
        """Score based on release count.

        More releases indicate a more established package.
        """
        if metadata.release_count >= 10:
            return SCORE_WEIGHTS["releases_10_plus"]
        elif metadata.release_count >= 3:
            signals.append(
                RiskSignal(
                    signal_type=SignalType.FEW_RELEASES,
                    weight=-15,
                    details=f"Only {metadata.release_count} releases",
                )
            )
            return SCORE_WEIGHTS["releases_3_to_9"]
        else:
            signals.append(
                RiskSignal(
                    signal_type=SignalType.FEW_RELEASES,
                    weight=-30,
                    details=f"Only {metadata.release_count} release(s)",
                )
            )
            return 0

    def _score_repository(
        self,
        metadata: PackageMetadata,
        signals: list[RiskSignal],
    ) -> int:
        """Score based on repository presence.

        Packages without public source code are suspicious.
        """
        if metadata.has_repository:
            return SCORE_WEIGHTS["has_repository"]
        else:
            signals.append(
                RiskSignal(
                    signal_type=SignalType.NO_REPOSITORY,
                    weight=-30,
                    details="No repository URL found",
                )
            )
            return 0

    def _score_author(
        self,
        metadata: PackageMetadata,
        signals: list[RiskSignal],
    ) -> int:
        """Score based on author information.

        Anonymous packages are slightly suspicious.
        """
        if metadata.has_author:
            return SCORE_WEIGHTS["has_author"]
        else:
            signals.append(
                RiskSignal(
                    signal_type=SignalType.NO_AUTHOR,
                    weight=-20,
                    details="No author information",
                )
            )
            return 0

    def _score_description(
        self,
        metadata: PackageMetadata,
        signals: list[RiskSignal],
    ) -> int:
        """Score based on description quality.

        Packages without descriptions may be low-effort malware.
        """
        if metadata.has_description:
            return SCORE_WEIGHTS["has_description"]
        else:
            signals.append(
                RiskSignal(
                    signal_type=SignalType.NO_DESCRIPTION,
                    weight=-20,
                    details="No or minimal description",
                )
            )
            return 0

    def _score_to_level(self, score: int) -> RiskLevel:
        """Convert numeric score to risk level.

        Args:
            score: Numeric score from 0-100.

        Returns:
            Corresponding risk level.
        """
        if score >= THRESHOLDS["safe"]:
            return RiskLevel.SAFE
        elif score >= THRESHOLDS["suspicious"]:
            return RiskLevel.SUSPICIOUS
        else:
            return RiskLevel.HIGH_RISK

    def _not_found_result(self, metadata: PackageMetadata) -> PackageRisk:
        """Create result for non-existent package.

        Non-existent packages are the primary slopsquatting indicator.
        """
        return PackageRisk(
            package_name=metadata.name,
            registry=metadata.registry,
            risk_level=RiskLevel.NOT_FOUND,
            risk_score=0,
            signals=(
                RiskSignal(
                    signal_type=SignalType.NOT_FOUND,
                    weight=-100,
                    details="Package does not exist in registry",
                ),
            ),
            recommendation=RECOMMENDATIONS[RiskLevel.NOT_FOUND],
            metadata=metadata,
        )
