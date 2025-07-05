from flask import jsonify
from ..utils import calculate_emisi


class CalculatorController:
    def __init__(self):
        pass

    async def calculator(self, methode, massa, user_input):
        result = calculate_emisi(methode, massa, user_input)
        return jsonify({"message": "successfully calculate", "data": result}), 200
