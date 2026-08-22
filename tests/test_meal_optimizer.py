import pytest
import shutil
import tempfile
from src.services.meal_optimizer import MealOptimizerService, OptimizationRequest
from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.usda_tbca_dataset import SEED_NUTRITIONAL_DATA

@pytest.fixture
def test_repo():
    temp_dir = tempfile.mkdtemp()
    repo = ChromaNutritionalRepository(persist_path=temp_dir)
    repo.ingest_items(SEED_NUTRITIONAL_DATA)
    yield repo
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.mark.parametrize("calories,protein,carbs,fat", [
    (500.0, 40.0, 50.0, 15.0),
    (650.0, 45.0, 65.0, 20.0),
    (400.0, 35.0, 40.0, 10.0),
    (750.0, 50.0, 80.0, 25.0),
    (550.0, 38.0, 55.0, 18.0),
])
def test_linear_solver_mape_under_five_percent(test_repo: ChromaNutritionalRepository, calories: float, protein: float, carbs: float, fat: float):
    optimizer = MealOptimizerService(repo=test_repo)
    request = OptimizationRequest(
        target_calories=calories,
        target_protein_g=protein,
        target_carbs_g=carbs,
        target_fat_g=fat,
    )
    result = optimizer.solve(request)

    assert result.success is True
    assert result.mape_error_percent < 5.0  # Invariante estrita: MAPE < 5%
    assert len(result.ingredients) > 0
    assert result.total_calories > 0

def test_solver_vector_expansion_fallback(test_repo: ChromaNutritionalRepository):
    # Passar lista inicial restrita (apenas arroz e alface - impossível bater proteína)
    restricted_candidates = [
        SEED_NUTRITIONAL_DATA[6].to_metadata(),  # Arroz
        SEED_NUTRITIONAL_DATA[18].to_metadata(), # Alface
    ]

    optimizer = MealOptimizerService(repo=test_repo)
    request = OptimizationRequest(
        target_calories=450.0,
        target_protein_g=40.0,
        target_carbs_g=50.0,
        target_fat_g=10.0,
        candidate_foods=restricted_candidates,
    )

    result = optimizer.solve(request)
    assert result.success is True
    assert result.mape_error_percent < 5.0
    assert result.fallback_stage_used == "vector_expansion"

def test_solver_slack_variables_fallback():
    # Sem repositório e com candidatos onde é matematicamente inviável o ajuste exato
    tight_candidates = [
        SEED_NUTRITIONAL_DATA[12].to_metadata(), # Azeite (100% gordura)
    ]
    optimizer = MealOptimizerService(repo=None)
    request = OptimizationRequest(
        target_calories=500.0,
        target_protein_g=50.0, # Impossível com azeite
        target_carbs_g=50.0,
        target_fat_g=10.0,
        candidate_foods=tight_candidates,
    )

    result = optimizer.solve(request)
    assert result.success is True
    assert result.fallback_stage_used == "slack_variables"
    assert len(result.ingredients) > 0
