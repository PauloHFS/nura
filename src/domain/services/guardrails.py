from typing import Optional, Union, Any
from pydantic import BaseModel, Field

class DietTarget(BaseModel):
    target_calories: float = Field(description="Meta calórica em kcal")
    target_protein_g: float = Field(description="Meta de proteína em g")
    target_carbs_g: float = Field(default=0.0, description="Meta de carboidratos em g")
    target_fat_g: float = Field(default=0.0, description="Meta de gorduras em g")
    is_single_meal: bool = Field(default=True, description="Indica se é uma refeição isolada")

class GuardrailResult(BaseModel):
    guardrail_blocked: bool = False
    is_safe: bool = True
    message: str = "Metas nutricionais dentro dos parâmetros de segurança."
    rule_intercepted: Optional[str] = None

def validate_nutrition_targets(targets: Union[DietTarget, dict, Any]) -> GuardrailResult:
    if isinstance(targets, DietTarget):
        dt = targets
    elif isinstance(targets, dict):
        dt = DietTarget.model_validate(targets)
    elif hasattr(targets, "model_dump"):
        dt = DietTarget.model_validate(targets.model_dump())
    else:
        dt = DietTarget.model_validate(targets)

    min_cal = 350.0 if dt.is_single_meal else 1200.0
    if dt.target_calories < min_cal:
        return GuardrailResult(
            guardrail_blocked=True,
            is_safe=False,
            message="Meta calórica perigosamente baixa. Requer validação de nutricionista.",
            rule_intercepted="min_calories",
        )

    max_prot = 100.0 if dt.is_single_meal else 250.0
    if dt.target_protein_g > max_prot:
        msg = (
            "Meta de proteína excessivamente alta (> 100g/refeição). Requer validação de nutricionista."
            if dt.is_single_meal
            else "Meta de proteína excessivamente alta (> 250g/dia). Requer validação de nutricionista."
        )
        return GuardrailResult(
            guardrail_blocked=True,
            is_safe=False,
            message=msg,
            rule_intercepted="max_protein",
        )

    return GuardrailResult(
        guardrail_blocked=False,
        is_safe=True,
        message="Metas nutricionais validadas com sucesso.",
        rule_intercepted=None,
    )
