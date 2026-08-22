import os
import time
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
from src.domain.vector_models import NutritionalItem

DEFAULT_CHROMA_PATH = os.getenv("CHROMA_PERSIST_PATH", "./chroma_data")
COLLECTION_NAME = "nutritional_items"

class ChromaNutritionalRepository:
    def __init__(self, persist_path: str = DEFAULT_CHROMA_PATH):
        self.persist_path = persist_path
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Nutritional database with USDA/TBCA food records"},
        )

    def ingest_items(self, items: List[NutritionalItem]) -> int:
        """
        Ingere ou atualiza uma lista de alimentos no repositório vetorial do Chroma DB.
        Retorna a quantidade de itens processados.
        """
        if not items:
            return 0

        ids = [item.food_id for item in items]
        documents = [f"{item.name} - Categoria: {item.category}. Fonte: {item.source}" for item in items]
        metadatas = [item.to_metadata() for item in items]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return len(items)

    def search_items(
        self,
        query: str,
        category: Optional[str] = None,
        max_calories_100g: Optional[float] = None,
        min_protein_100g: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Realiza busca semântica vetorial com suporte a filtros de metadados.
        """
        where_conditions: List[Dict[str, Any]] = []

        if category:
            where_conditions.append({"category": category})

        if max_calories_100g is not None:
            where_conditions.append({"calories_100g": {"$lte": max_calories_100g}})

        if min_protein_100g is not None:
            where_conditions.append({"protein_100g": {"$gte": min_protein_100g}})

        where_filter: Optional[Dict[str, Any]] = None
        if len(where_conditions) == 1:
            where_filter = where_conditions[0]
        elif len(where_conditions) > 1:
            where_filter = {"$and": where_conditions}

        start_time = time.perf_counter()
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where_filter,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        items_found: List[Dict[str, Any]] = []
        if results and results.get("metadatas") and len(results["metadatas"]) > 0:
            for idx, meta in enumerate(results["metadatas"][0]):
                meta_copy = dict(meta)
                meta_copy["search_latency_ms"] = round(elapsed_ms, 2)
                items_found.append(meta_copy)

        return items_found

    def count(self) -> int:
        return self.collection.count()
