"""Brand Score — weighted composite scoring per D-05.

Aggregates multiple scoring dimensions into a single 0-1 Brand Score
with per-component breakdown for auditability.
"""


class BrandScore:
    """Weighted composite score for brand consistency evaluation.

    WEIGHTS per D-05:
        prompt_accuracy:          0.20
        character_consistency:    0.20
        technical_quality:        0.15
        facial_appeal:            0.15
        child_friendliness:       0.10
        color_harmony:            0.10
        silhouette_recognizability: 0.05
        style_consistency:        0.05
    """

    WEIGHTS: dict[str, float] = {
        "prompt_accuracy": 0.20,
        "character_consistency": 0.20,
        "technical_quality": 0.15,
        "facial_appeal": 0.15,
        "child_friendliness": 0.10,
        "color_harmony": 0.10,
        "silhouette_recognizability": 0.05,
        "style_consistency": 0.05,
    }

    @classmethod
    def compute(cls, scores: dict[str, float]) -> dict:
        """Compute weighted Brand Score and return full breakdown.

        Args:
            scores: Dict of {dimension_name: raw_score} where raw_score is 0-1.

        Returns:
            Dict with:
                - total: weighted composite score
                - max: 1.0 (theoretical maximum)
                - components: per-dimension breakdown with raw/weighted/weight
        """
        total = sum(
            scores.get(key, 0.0) * weight for key, weight in cls.WEIGHTS.items()
        )
        return {
            "total": round(total, 4),
            "max": 1.0,
            "components": {
                key: {
                    "raw": scores.get(key, 0.0),
                    "weighted": round(scores.get(key, 0.0) * weight, 4),
                    "weight": weight,
                }
                for key, weight in cls.WEIGHTS.items()
            },
        }
