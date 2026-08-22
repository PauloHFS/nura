from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class NutritionalItem(BaseModel):
    food_id: str = Field(description="ID único do alimento (ex: usda-1001, tbca-002)")
    name: str = Field(description="Nome do alimento")
    category: str = Field(description="Categoria: protein, carb, fat, vegetable, fruit, dairy")
    calories_100g: float = Field(description="Calorias por 100g (kcal)")
    protein_100g: float = Field(description="Proteína por 100g (g)")
    carbs_100g: float = Field(description="Carboidratos por 100g (g)")
    fat_100g: float = Field(description="Gorduras por 100g (g)")
    fiber_100g: float = Field(default=0.0, description="Fibras por 100g (g)")
    source: str = Field(default="USDA/TBCA", description="Fonte dos dados")
    shelf_life_days: Optional[int] = Field(default=None, description="Estimativa de validade em dias")

    def to_metadata(self) -> Dict[str, Any]:
        """Converte atributos numéricos e categóricos para metadados indexáveis no Chroma DB."""
        meta: Dict[str, Any] = {
            "food_id": self.food_id,
            "name": self.name,
            "category": self.category,
            "calories_100g": float(self.calories_100g),
            "protein_100g": float(self.protein_100g),
            "carbs_100g": float(self.carbs_100g),
            "fat_100g": float(self.fat_100g),
            "fiber_100g": float(self.fiber_100g),
            "source": self.source,
        }
        if self.shelf_life_days is not None:
            meta["shelf_life_days"] = int(self.shelf_life_days)
        return meta
