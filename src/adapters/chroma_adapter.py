import os
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
        query: Optional[str] = None,
        query_embeddings: Optional[List[List[float]]] = None,
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

        query_kwargs: Dict[str, Any] = {"n_results": limit}
        if where_filter:
            query_kwargs["where"] = where_filter

        if query_embeddings is not None:
            query_kwargs["query_embeddings"] = query_embeddings
        elif query is not None:
            query_kwargs["query_texts"] = [query]
        else:
            raise ValueError("Either query or query_embeddings must be provided")

        results = self.collection.query(**query_kwargs)

        items_found: List[Dict[str, Any]] = []
        if results and results.get("metadatas") and len(results["metadatas"]) > 0:
            items_found = [dict(meta) for meta in results["metadatas"][0] if meta]

        return items_found

    def count(self) -> int:
        return self.collection.count()
