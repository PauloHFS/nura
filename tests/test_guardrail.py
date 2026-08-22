import time
import pytest
from src.domain.ports.guardrail_port import GuardrailResult
from src.adapters.aho_corasick_guardrail import AhoCorasickGuardrail

def test_aho_corasick_safe_content():
    guardrail = AhoCorasickGuardrail()
    result = guardrail.scan("Uma dieta equilibrada com arroz, feijão, frango e legumes é muito saudável.")
    assert isinstance(result, GuardrailResult)
    assert result.is_safe is True
    assert result.intercepted_term is None
    assert result.latency_ms < 5.0

@pytest.mark.parametrize("unsafe_text, expected_term", [
    ("Recomendo fortemente um jejum de 48h para perder peso.", "jejum de 48h"),
    ("A partir de amanhã você deve consumir 0 carboidratos.", "0 carboidratos"),
    ("Alimentos com calorias negativas ajudam a queimar gordura.", "calorias negativas"),
    ("Faça um JEJUM DE 48H imediatamente.", "jejum de 48h"),
])
def test_aho_corasick_unsafe_content_detection(unsafe_text, expected_term):
    guardrail = AhoCorasickGuardrail()
    result = guardrail.scan(unsafe_text)
    assert result.is_safe is False
    assert result.intercepted_term == expected_term

def test_aho_corasick_custom_patterns():
    custom_patterns = ["dieta da lua", "reédio milagroso"]
    guardrail = AhoCorasickGuardrail(patterns=custom_patterns)
    
    safe_res = guardrail.scan("Coma salada e proteína.")
    assert safe_res.is_safe is True

    unsafe_res = guardrail.scan("Experimente a dieta da lua esta semana.")
    assert unsafe_res.is_safe is False
    assert unsafe_res.intercepted_term == "dieta da lua"

def test_aho_corasick_latency_under_5ms():
    guardrail = AhoCorasickGuardrail()
    large_payload = "Esta é uma refeição saudável rica em nutrientes e proteína magra. " * 200
    start = time.perf_counter()
    result = guardrail.scan(large_payload)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert result.is_safe is True
    assert result.latency_ms < 5.0
    assert elapsed_ms < 5.0
