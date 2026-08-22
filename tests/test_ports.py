import pytest
from src.domain.ports.meal_optimizer_port import MealOptimizerPort
from src.domain.ports.pantry_port import PantryPort
from src.domain.ports.guardrail_port import GuardrailPort

def test_ports_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        MealOptimizerPort()  # type: ignore

    with pytest.raises(TypeError):
        PantryPort()  # type: ignore

    with pytest.raises(TypeError):
        GuardrailPort()  # type: ignore

class DummyOptimizer(MealOptimizerPort):
    def solve(self, request):
        return {"solved": True}

class DummyPantry(PantryPort):
    def get_inventory_snapshot(self):
        return []

    def deduct_item(self, item_id: str, quantity: float):
        return True

class DummyGuardrail(GuardrailPort):
    def scan(self, content: str):
        return {"is_safe": True}

def test_dummy_ports_implementation():
    optimizer = DummyOptimizer()
    assert optimizer.solve({}) == {"solved": True}

    pantry = DummyPantry()
    assert pantry.get_inventory_snapshot() == []
    assert pantry.deduct_item("item-1", 2.0) is True

    guardrail = DummyGuardrail()
    assert guardrail.scan("test") == {"is_safe": True}
