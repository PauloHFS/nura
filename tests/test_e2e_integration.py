import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver
from src.api.main import app, get_orchestrator, get_telegram_client
from src.graph.orchestrator import NuraOrchestrator
from src.adapters.aho_corasick_guardrail import AhoCorasickGuardrail
from src.adapters.grocy_adapter import GrocyAdapter
from src.domain.ports.pantry_port import GrocyItem, PantrySnapshot

client = TestClient(app)

def test_orchestrator_integrates_solver_and_grocy_and_guardrail():
    # Mock Grocy
    mock_grocy = MagicMock(spec=GrocyAdapter)
    mock_grocy.get_inventory_snapshot.return_value = PantrySnapshot(
        items=[GrocyItem(id="1", name="Peito de Frango", amount=2.0, best_before_date="2026-08-23")],
        appliances=[]
    )
    mock_grocy.deduct_item.return_value = True

    # Mock Solver
    mock_solver = MagicMock()
    mock_solver.solve.return_value = MagicMock(
        solved=True,
        selected_ingredients=[{"ingredient_name": "Peito de Frango", "weight_g": 200.0}],
        mape_error_percent=1.5
    )

    # Real Guardrail
    guardrail = AhoCorasickGuardrail()

    orchestrator = NuraOrchestrator(
        pantry_port=mock_grocy,
        optimizer_service=mock_solver,
        guardrail_port=guardrail,
        checkpointer=MemorySaver()
    )

    config = {"configurable": {"thread_id": "test-user-1"}}

    # Turn 1: User asks for meal plan
    state1 = {
        "patient_id": "test-user-1",
        "messages": [{"role": "user", "content": "Por favor, gerar cardápio semanal com foco em proteína."}],
        "step": "meal_planning",
        "meal_plan_pending": True,
        "last_meal_suggested": None,
        "inventory_confirmed": False,
        "guardrail_blocked": False,
        "response_text": None,
    }
    res1 = orchestrator.graph.invoke(state1, config=config)

    assert res1["guardrail_blocked"] is False
    assert res1["response_text"] is not None
    assert "Peito de Frango" in res1["response_text"]
    assert mock_solver.solve.called

    # Turn 2: User confirms meal consumption
    state2 = {
        "patient_id": "test-user-1",
        "messages": [{"role": "user", "content": "Sim, consumi a refeição de frango!"}],
        "step": "inventory_reconciliation",
        "meal_plan_pending": False,
        "last_meal_suggested": "Peito de Frango",
        "inventory_confirmed": True,
        "guardrail_blocked": False,
        "response_text": None,
    }
    res2 = orchestrator.graph.invoke(state2, config=config)
    assert mock_grocy.deduct_item.called

def test_orchestrator_guardrail_blocks_unsafe_coach_output():
    mock_guardrail = MagicMock()
    mock_guardrail.scan.return_value = MagicMock(is_safe=False, intercepted_term="jejum de 48h")

    orchestrator = NuraOrchestrator(
        guardrail_port=mock_guardrail,
        checkpointer=MemorySaver()
    )

    config = {"configurable": {"thread_id": "test-user-unsafe"}}
    state = {
        "patient_id": "test-user-unsafe",
        "messages": [{"role": "user", "content": "Como posso perded peso rápido?"}],
        "step": "oars_coaching",
        "meal_plan_pending": False,
        "last_meal_suggested": None,
        "inventory_confirmed": False,
        "guardrail_blocked": False,
        "response_text": None,
    }
    res = orchestrator.graph.invoke(state, config=config)

    assert res["guardrail_blocked"] is True
    assert "interceptada" in res["response_text"].lower() or "segurança" in res["response_text"].lower()

def test_telegram_webhook_e2e_flow():
    mock_telegram = MagicMock()
    mock_orchestrator = MagicMock()
    mock_orchestrator.graph.invoke.return_value = {
        "response_text": "Olá! Sou sua Coach Nura. Como posso ajudar?",
        "guardrail_blocked": False
    }

    app.dependency_overrides[get_telegram_client] = lambda: mock_telegram
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator

    try:
        payload = {
            "update_id": 9999,
            "message": {
                "message_id": 1,
                "chat": {"id": 8888, "type": "private"},
                "from": {"id": 8888, "first_name": "Paulo"},
                "text": "Olá Nura"
            }
        }
        res = client.post("/webhook/telegram", json=payload)
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert mock_orchestrator.graph.invoke.called
        assert mock_telegram.send_message.called
        mock_telegram.send_message.assert_called_once_with(
            chat_id=8888,
            text="Olá! Sou sua Coach Nura. Como posso ajudar?"
        )
    finally:
        app.dependency_overrides.clear()
