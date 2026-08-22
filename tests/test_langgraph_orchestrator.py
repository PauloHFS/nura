import pytest
from langgraph.checkpoint.memory import MemorySaver
from src.graph.orchestrator import NuraOrchestrator, PatientState
from src.graph.prompts import OARS_SYSTEM_PROMPT

def test_oars_system_prompt_contains_core_principles():
    assert "Perguntas Abertas" in OARS_SYSTEM_PROMPT or "OARS" in OARS_SYSTEM_PROMPT
    assert "Reflexão" in OARS_SYSTEM_PROMPT or "Afirmação" in OARS_SYSTEM_PROMPT

def test_orchestrator_initial_state_onboarding_transition():
    orchestrator = NuraOrchestrator(checkpointer=MemorySaver())
    initial_state = {
        "patient_id": "p123",
        "messages": [{"role": "user", "content": "Olá, quero começar minha jornada de perda de peso"}],
        "step": "onboarding",
        "meal_plan_pending": False,
        "last_meal_suggested": None,
        "inventory_confirmed": False,
        "guardrail_blocked": False,
        "response_text": None,
    }

    config = {"configurable": {"thread_id": "p123"}}
    final_state = orchestrator.graph.invoke(initial_state, config=config)

    assert final_state["patient_id"] == "p123"
    assert final_state["response_text"] is not None
    assert final_state["step"] in ["onboarding", "oars_coaching"]

def test_orchestrator_checkpoint_persistence():
    checkpointer = MemorySaver()
    orchestrator = NuraOrchestrator(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "patient-42"}}

    # Turn 1
    state_turn1 = {
        "patient_id": "patient-42",
        "messages": [{"role": "user", "content": "Peso 80kg e quero chegar a 72kg."}],
        "step": "onboarding",
        "meal_plan_pending": False,
        "last_meal_suggested": None,
        "inventory_confirmed": False,
        "guardrail_blocked": False,
        "response_text": None,
    }
    orchestrator.graph.invoke(state_turn1, config=config)

    # Inspect checkpointed state
    checkpointed = checkpointer.get(config)
    assert checkpointed is not None
    assert checkpointed["channel_values"]["patient_id"] == "patient-42"
