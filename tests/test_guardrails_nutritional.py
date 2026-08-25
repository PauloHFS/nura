import pytest
from src.domain.services.guardrails import (
    DietTarget,
    GuardrailResult,
    validate_nutrition_targets,
)
from src.services.meal_optimizer import OptimizationRequest, MealOptimizerService

def test_guardrail_calories_min_daily():
    target = DietTarget(target_calories=1100.0, target_protein_g=80.0, is_single_meal=False)
    res = validate_nutrition_targets(target)
    assert isinstance(res, GuardrailResult)
    assert res.guardrail_blocked is True
    assert res.is_safe is False
    assert "Meta calórica perigosamente baixa" in res.message

def test_guardrail_calories_min_single_meal():
    target = DietTarget(target_calories=300.0, target_protein_g=25.0, is_single_meal=True)
    res = validate_nutrition_targets(target)
    assert res.guardrail_blocked is True
    assert res.is_safe is False
    assert "Meta calórica perigosamente baixa" in res.message

def test_guardrail_calories_safe():
    target_meal = DietTarget(target_calories=400.0, target_protein_g=30.0, is_single_meal=True)
    res_meal = validate_nutrition_targets(target_meal)
    assert res_meal.guardrail_blocked is False
    assert res_meal.is_safe is True

    target_daily = DietTarget(target_calories=1500.0, target_protein_g=100.0, is_single_meal=False)
    res_daily = validate_nutrition_targets(target_daily)
    assert res_daily.guardrail_blocked is False
    assert res_daily.is_safe is True

def test_guardrail_protein_max():
    target = DietTarget(target_calories=2000.0, target_protein_g=260.0, is_single_meal=False)
    res = validate_nutrition_targets(target)
    assert res.guardrail_blocked is True
    assert res.is_safe is False
    assert "excessivamente alta" in res.message or "> 250g/dia" in res.message

def test_guardrail_dict_input():
    target_dict = {
        "target_calories": 200.0,
        "target_protein_g": 20.0,
        "is_single_meal": True,
    }
    res = validate_nutrition_targets(target_dict)
    assert res.guardrail_blocked is True
    assert res.is_safe is False

def test_meal_optimizer_blocked_by_guardrails():
    optimizer = MealOptimizerService()
    req = OptimizationRequest(
        target_calories=250.0,  # Below 350.0 for single meal
        target_protein_g=20.0,
        target_carbs_g=30.0,
        target_fat_g=5.0,
    )
    result = optimizer.solve(req)
    assert result.success is False
    assert result.fallback_stage_used == "guardrail_blocked"
    assert "Meta calórica perigosamente baixa" in result.message
