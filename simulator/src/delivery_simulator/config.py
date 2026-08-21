from dataclasses import dataclass

@dataclass(frozen=True)
class SimulatorProfile:
    name: str
    customer_count: int
    restaurant_count: int
    courier_count: int
    orders_count: int

PROFILES: dict[str, SimulatorProfile] = {
    "tiny": SimulatorProfile(
        name="tiny",
        customer_count=100,
        restaurant_count=20,
        courier_count=25,
        orders_count=500,
    ),

    "dev": SimulatorProfile(
        name="dev",
        customer_count=1_000,
        restaurant_count=100,
        courier_count=150,
        orders_count=5_000
    ),

    "demo": SimulatorProfile(
        name="demo",
        customer_count=10_000,
        restaurant_count=500,
        courier_count=750,
        orders_count=50_000,
    ),
}

def get_profile(name: str) -> SimulatorProfile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        valid_profiles = ", ".join(sorted(PROFILES))
        raise ValueError(
            f"Unknown profile '{name}'. Valid profiles: {valid_profiles}"
        ) from exc