from ..models import EmissionsProducedModel, ReducedPotentialModel
from .interfaces import SerializerInterface
from typing import Union


class CalculatorSerializer(SerializerInterface):
    def serialize(
        self,
        data_calculator: Union[EmissionsProducedModel, ReducedPotentialModel],
        emission_ton_is_null: bool = False,
        mass_ton_is_null: bool = False,
        method_is_null: bool = False,
    ) -> dict:
        data = {}
        if not emission_ton_is_null:
            data["emission_ton"] = data_calculator.emission_ton
        if not mass_ton_is_null:
            data["mass_ton"] = data_calculator.mass_ton
        if not method_is_null:
            data["method"] = data_calculator.method
        return data
