from .models import FacialExpression


BLINK_INTERVAL_DEFAULT = (4.0, 10.0)
BLINK_DURATION_FRAMES = (2, 4)


FACIAL_EXPRESSION_DESCRIPTIONS: dict[FacialExpression, dict] = {
    FacialExpression.NEUTRAL: {
        "eyes": "open, relaxed",
        "eyebrows": "neutral position",
        "mouth": "slight closed smile",
        "cheeks": "relaxed",
    },
    FacialExpression.HAPPY: {
        "eyes": "slightly squinted, creased at corners",
        "eyebrows": "slightly raised",
        "mouth": "wide smile, teeth may show",
        "cheeks": "lifted, round",
    },
    FacialExpression.EXCITED: {
        "eyes": "wide open, bright",
        "eyebrows": "raised high",
        "mouth": "open smile or 'O' shape",
        "cheeks": "lifted, rosy",
    },
    FacialExpression.CURIOUS: {
        "eyes": "slightly narrowed, focused",
        "eyebrows": "one raised slightly",
        "mouth": "slight pucker or tilted",
        "cheeks": "relaxed",
    },
    FacialExpression.SURPRISED: {
        "eyes": "wide open, round",
        "eyebrows": "raised high, arched",
        "mouth": "open oval shape",
        "cheeks": "pulled back slightly",
    },
    FacialExpression.CONFUSED: {
        "eyes": "one eye slightly squinted",
        "eyebrows": "furrowed, one lower",
        "mouth": "pursed or twisted to one side",
        "cheeks": "slightly tense",
    },
    FacialExpression.PROUD: {
        "eyes": "open, confident",
        "eyebrows": "raised slightly",
        "mouth": "broad smile, chin up",
        "cheeks": "lifted",
    },
    FacialExpression.THOUGHTFUL: {
        "eyes": "looking up or to side",
        "eyebrows": "slightly furrowed",
        "mouth": "pursed or slight frown",
        "cheeks": "relaxed",
    },
    FacialExpression.SLEEPY: {
        "eyes": "half-closed, heavy lids",
        "eyebrows": "relaxed, slightly lowered",
        "mouth": "slight relaxed smile or open",
        "cheeks": "relaxed, slightly droopy",
    },
    FacialExpression.LAUGHING: {
        "eyes": "tightly squinted, crinkled",
        "eyebrows": "raised",
        "mouth": "wide open, teeth visible",
        "cheeks": "very lifted, round",
    },
    FacialExpression.GENTLE_SADNESS: {
        "eyes": "slightly downcast, lower lids lifted",
        "eyebrows": "slight inner raise, outer lowered",
        "mouth": "slight downward curve or pout",
        "cheeks": "relaxed, slightly droopy",
    },
}


class FacialAnimationEngine:
    def describe_expression(self, expression: FacialExpression) -> dict:
        return FACIAL_EXPRESSION_DESCRIPTIONS.get(
            expression,
            FACIAL_EXPRESSION_DESCRIPTIONS[FacialExpression.NEUTRAL],
        )

    def list_expressions(self) -> list[FacialExpression]:
        return list(FacialExpression)

    def suggest_blink_interval(self, emotion: FacialExpression) -> tuple[float, float]:
        blink_rates = {
            FacialExpression.EXCITED: (6.0, 12.0),
            FacialExpression.SURPRISED: (8.0, 15.0),
            FacialExpression.SLEEPY: (2.0, 5.0),
            FacialExpression.LAUGHING: (5.0, 8.0),
            FacialExpression.GENTLE_SADNESS: (3.0, 6.0),
        }
        return blink_rates.get(emotion, BLINK_INTERVAL_DEFAULT)

    def blend_expressions(
        self, from_expr: FacialExpression, to_expr: FacialExpression, t: float
    ) -> dict:
        from_desc = self.describe_expression(from_expr)
        to_desc = self.describe_expression(to_expr)
        blend: dict[str, str] = {}
        for key in from_desc:
            if t < 0.5:
                blend[key] = from_desc[key]
            else:
                blend[key] = to_desc[key]
        return blend
