from .models import PhysicsMaterial


PHYSICS_PROPERTIES: dict[PhysicsMaterial, dict] = {
    PhysicsMaterial.BOUNCY: {
        "bounce_factor": 0.8,
        "gravity_scale": 1.0,
        "friction": 0.3,
        "description": "Objects bounce softly with energy preservation",
        "examples": ["balloons", "rubber balls", "jumping characters"],
    },
    PhysicsMaterial.SOFT: {
        "bounce_factor": 0.3,
        "gravity_scale": 0.8,
        "friction": 0.6,
        "description": "Gentle, dampened motion with soft landings",
        "examples": ["fabric", "hair", "stuffed animals", "character bodies"],
    },
    PhysicsMaterial.FLOATING: {
        "bounce_factor": 0.5,
        "gravity_scale": 0.3,
        "friction": 0.2,
        "description": "Slow, gentle floating with minimal gravity influence",
        "examples": ["leaves", "feathers", "bubbles", "balloons in air"],
    },
    PhysicsMaterial.HEAVY: {
        "bounce_factor": 0.1,
        "gravity_scale": 2.0,
        "friction": 0.8,
        "description": "Slow, weighty motion with minimal bounce",
        "examples": ["rocks", "furniture", "large objects"],
    },
    PhysicsMaterial.LIGHT: {
        "bounce_factor": 0.6,
        "gravity_scale": 0.6,
        "friction": 0.4,
        "description": "Quick, responsive motion with moderate bounce",
        "examples": ["paper", "small toys", "light props"],
    },
}


class PhysicsEngine:
    def describe(self, material: PhysicsMaterial) -> dict:
        return PHYSICS_PROPERTIES.get(
            material,
            PHYSICS_PROPERTIES[PhysicsMaterial.SOFT],
        )

    def list_materials(self) -> list[PhysicsMaterial]:
        return list(PhysicsMaterial)

    def simulate_impact(self, material: PhysicsMaterial, height: float = 1.0) -> dict:
        props = self.describe(material)
        bounce_height = height * props["bounce_factor"]
        time_to_ground = (2 * height / max(props["gravity_scale"], 0.1)) ** 0.5
        return {
            "material": material.value,
            "drop_height": height,
            "bounce_height": round(bounce_height, 3),
            "time_to_ground": round(time_to_ground, 3),
            "bounces_to_rest": self._bounces_to_rest(material, bounce_height),
        }

    def _bounces_to_rest(self, material: PhysicsMaterial, start_height: float) -> int:
        props = self.describe(material)
        threshold = 0.01
        bounces = 0
        height = start_height
        while height > threshold and bounces < 20:
            height *= props["bounce_factor"]
            bounces += 1
        return bounces
