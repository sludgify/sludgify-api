from flask import jsonify
from ..utils import calculate_emisi
from ..serializers import CalculatorSerializer
from ..models import EmissionsProducedModel, ReducedPotentialModel


class CalculatorController:
    def __init__(self):
        self.calculator_serializer = CalculatorSerializer()

    async def calculator(self, method, massa, user_input):
        result = calculate_emisi(method, massa, user_input)
        coprocessing = calculate_emisi("coprocessing", massa, user_input)
        emissions_produced = EmissionsProducedModel(
            emission_ton=result["emission_ton"],
            mass_ton=result["mass_ton"],
            method=result["method"],
        )
        reduced_potential = ReducedPotentialModel(
            emission_ton=coprocessing["emission_ton"],
            mass_ton=coprocessing["mass_ton"],
            method=coprocessing["method"],
        )
        emissions_produced_serializer = self.calculator_serializer.serialize(
            emissions_produced
        )
        reduced_potential_serializer = self.calculator_serializer.serialize(
            reduced_potential
        )
        result = {
            "emissions_produced": emissions_produced_serializer,
            "reduced_potential": reduced_potential_serializer,
        }
        result["method"] = method
        return jsonify({"message": "successfully calculate", "data": result}), 200
