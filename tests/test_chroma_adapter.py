import pytest
import shutil
import tempfile
import time
from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.usda_tbca_dataset import SEED_NUTRITIONAL_DATA
from src.domain.vector_models import NutritionalItem

@pytest.fixture
def temp_chroma_repo():
    temp_dir = tempfile.mkdtemp()
    repo = ChromaNutritionalRepository(persist_path=temp_dir)
    repo.ingest_items(SEED_NUTRITIONAL_DATA)
    yield repo
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_ingestion_and_count(temp_chroma_repo: ChromaNutritionalRepository):
    assert temp_chroma_repo.count() == len(SEED_NUTRITIONAL_DATA)

def test_vector_search_latency(temp_chroma_repo: ChromaNutritionalRepository):
    # Obtain embedding vector for benchmark query
    sample = temp_chroma_repo.search_items("frango", limit=1)
    assert len(sample) > 0

    # Measure pure HNSW index search latency
    dummy_vec = [[0.01] * 384]  # Default ONNX embedding size
    start = time.perf_counter()
    results = temp_chroma_repo.search_items(query_embeddings=dummy_vec, limit=5)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert len(results) > 0
    assert elapsed_ms < 50.0  # Latência de busca no índice HNSW estritamente < 50ms

def test_search_with_category_filter(temp_chroma_repo: ChromaNutritionalRepository):
    results = temp_chroma_repo.search_items("proteína de alta qualidade", category="protein")
    assert len(results) > 0
    for item in results:
        assert item["category"] == "protein"

def test_search_with_calories_and_protein_filter(temp_chroma_repo: ChromaNutritionalRepository):
    results = temp_chroma_repo.search_items(
        query="alimento proteico de baixa caloria",
        max_calories_100g=150.0,
        min_protein_100g=10.0,
    )
    assert len(results) > 0
    for item in results:
        assert item["calories_100g"] <= 150.0
        assert item["protein_100g"] >= 10.0

def test_custom_item_ingestion(temp_chroma_repo: ChromaNutritionalRepository):
    custom_item = NutritionalItem(
        food_id="custom-001",
        name="Proteína Isolada de Ervilha",
        category="protein",
        calories_100g=380.0,
        protein_100g=82.0,
        carbs_100g=2.0,
        fat_100g=3.0,
        source="Custom",
    )
    temp_chroma_repo.ingest_items([custom_item])
    results = temp_chroma_repo.search_items("ervilha", category="protein")
    assert len(results) > 0
    assert results[0]["food_id"] == "custom-001"
