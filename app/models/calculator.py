from dataclasses import dataclass


@dataclass
class EmissionsProducedModel:
    emission_ton: int
    mass_ton: int
    method: str


@dataclass
class ReducedPotentialModel:
    emission_ton: int
    mass_ton: int
    method: str
