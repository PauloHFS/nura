from typing import List
from src.domain.vector_models import NutritionalItem

SEED_NUTRITIONAL_DATA: List[NutritionalItem] = [
    # Proteínas
    NutritionalItem(food_id="tbca-001", name="Peito de Frango Grelhado", category="protein", calories_100g=165.0, protein_100g=31.0, carbs_100g=0.0, fat_100g=3.6, fiber_100g=0.0, source="TBCA", shelf_life_days=5),
    NutritionalItem(food_id="tbca-002", name="Ovo de Galinha Cozido", category="protein", calories_100g=155.0, protein_100g=13.0, carbs_100g=1.1, fat_100g=10.6, fiber_100g=0.0, source="TBCA", shelf_life_days=14),
    NutritionalItem(food_id="tbca-003", name="Carne Moída Patinho Grelhada", category="protein", calories_100g=219.0, protein_100g=35.9, carbs_100g=0.0, fat_100g=7.3, fiber_100g=0.0, source="TBCA", shelf_life_days=4),
    NutritionalItem(food_id="usda-101", name="Filé de Tilápia Assado", category="protein", calories_100g=128.0, protein_100g=26.0, carbs_100g=0.0, fat_100g=2.7, fiber_100g=0.0, source="USDA", shelf_life_days=3),
    NutritionalItem(food_id="usda-102", name="Whey Protein Concentrado 80%", category="protein", calories_100g=400.0, protein_100g=80.0, carbs_100g=6.0, fat_100g=6.0, fiber_100g=0.0, source="USDA", shelf_life_days=180),
    NutritionalItem(food_id="tbca-004", name="Atum em Lata em Água", category="protein", calories_100g=116.0, protein_100g=25.5, carbs_100g=0.0, fat_100g=1.0, fiber_100g=0.0, source="TBCA", shelf_life_days=365),

    # Carboidratos
    NutritionalItem(food_id="tbca-010", name="Arroz Branco Cozido", category="carb", calories_100g=128.0, protein_100g=2.5, carbs_100g=28.1, fat_100g=0.2, fiber_100g=1.6, source="TBCA", shelf_life_days=6),
    NutritionalItem(food_id="tbca-011", name="Batata Doce Cozida", category="carb", calories_100g=77.0, protein_100g=0.6, carbs_100g=18.4, fat_100g=0.1, fiber_100g=2.2, source="TBCA", shelf_life_days=7),
    NutritionalItem(food_id="tbca-012", name="Mandioca Cozida", category="carb", calories_100g=125.0, protein_100g=0.6, carbs_100g=30.1, fat_100g=0.3, fiber_100g=1.6, source="TBCA", shelf_life_days=5),
    NutritionalItem(food_id="usda-201", name="Aveia em Flocos", category="carb", calories_100g=389.0, protein_100g=16.9, carbs_100g=66.3, fat_100g=6.9, fiber_100g=10.6, source="USDA", shelf_life_days=120),
    NutritionalItem(food_id="tbca-013", name="Pão Integral", category="carb", calories_100g=247.0, protein_100g=9.4, carbs_100g=45.2, fat_100g=3.4, fiber_100g=6.9, source="TBCA", shelf_life_days=10),

    # Gorduras Saudáveis
    NutritionalItem(food_id="usda-301", name="Azeite de Oliva Extra Virgem", category="fat", calories_100g=884.0, protein_100g=0.0, carbs_100g=0.0, fat_100g=100.0, fiber_100g=0.0, source="USDA", shelf_life_days=180),
    NutritionalItem(food_id="tbca-020", name="Abacate Fresco", category="fat", calories_100g=96.0, protein_100g=1.2, carbs_100g=6.0, fat_100g=8.4, fiber_100g=6.3, source="TBCA", shelf_life_days=4),
    NutritionalItem(food_id="usda-302", name="Castanha do Pará", category="fat", calories_100g=656.0, protein_100g=14.3, carbs_100g=12.3, fat_100g=66.4, fiber_100g=7.5, source="USDA", shelf_life_days=90),
    NutritionalItem(food_id="usda-303", name="Pasta de Amendoim Integral", category="fat", calories_100g=588.0, protein_100g=25.0, carbs_100g=20.0, fat_100g=50.0, fiber_100g=6.0, source="USDA", shelf_life_days=120),

    # Vegetais & Folhosos
    NutritionalItem(food_id="tbca-030", name="Brócolis Cozido", category="vegetable", calories_100g=35.0, protein_100g=2.1, carbs_100g=4.4, fat_100g=0.5, fiber_100g=3.4, source="TBCA", shelf_life_days=5),
    NutritionalItem(food_id="tbca-031", name="Espinafre Refogado", category="vegetable", calories_100g=67.0, protein_100g=2.7, carbs_100g=4.2, fat_100g=4.8, fiber_100g=2.5, source="TBCA", shelf_life_days=3),
    NutritionalItem(food_id="tbca-032", name="Cenoura Cozida", category="vegetable", calories_100g=30.0, protein_100g=0.8, carbs_100g=6.7, fat_100g=0.2, fiber_100g=3.2, source="TBCA", shelf_life_days=7),
    NutritionalItem(food_id="tbca-033", name="Alface Crespa", category="vegetable", calories_100g=11.0, protein_100g=1.3, carbs_100g=1.7, fat_100g=0.2, fiber_100g=1.3, source="TBCA", shelf_life_days=4),

    # Laticínios
    NutritionalItem(food_id="tbca-040", name="Iogurte Natural Desnatado", category="dairy", calories_100g=41.0, protein_100g=3.8, carbs_100g=5.8, fat_100g=0.3, fiber_100g=0.0, source="TBCA", shelf_life_days=15),
    NutritionalItem(food_id="tbca-041", name="Queijo Cottage", category="dairy", calories_100g=98.0, protein_100g=11.1, carbs_100g=3.4, fat_100g=4.3, fiber_100g=0.0, source="TBCA", shelf_life_days=10),
    NutritionalItem(food_id="tbca-042", name="Leite Desnatado", category="dairy", calories_100g=35.0, protein_100g=3.4, carbs_100g=5.0, fat_100g=0.1, fiber_100g=0.0, source="TBCA", shelf_life_days=7),
]
