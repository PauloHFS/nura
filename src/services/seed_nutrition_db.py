from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.usda_tbca_dataset import SEED_NUTRITIONAL_DATA

def seed_database(repo: ChromaNutritionalRepository = None) -> int:
    if repo is None:
        repo = ChromaNutritionalRepository()
    count = repo.ingest_items(SEED_NUTRITIONAL_DATA)
    return count

if __name__ == "__main__":
    count = seed_database()
    print(f"Alimentos ingeridos com sucesso no Chroma DB: {count}")
