import time
from collections import deque
from typing import Dict, List, Optional
from src.domain.ports.guardrail_port import GuardrailPort, GuardrailResult

class TrieNode:
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.fail: Optional[TrieNode] = None
        self.output: List[str] = []

class AhoCorasickGuardrail(GuardrailPort):
    DEFAULT_PATTERNS = [
        "jejum de 48h",
        "0 carboidratos",
        "calorias negativas",
        "jejum prolongado",
        "dieta de 500 kcal",
        "refeição zero caloria",
    ]

    def __init__(self, patterns: Optional[List[str]] = None):
        self.patterns = patterns if patterns is not None else self.DEFAULT_PATTERNS
        self.root = TrieNode()
        self._build_automaton()

    def _build_automaton(self) -> None:
        # Step 1: Build trie
        for pattern in self.patterns:
            node = self.root
            normalized = pattern.lower()
            for char in normalized:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.output.append(pattern)

        # Step 2: Build failure links using BFS
        queue: deque = deque()
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current = queue.popleft()
            for char, child_node in current.children.items():
                fail_node = current.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail

                if fail_node is not None and char in fail_node.children:
                    child_node.fail = fail_node.children[char]
                else:
                    child_node.fail = self.root

                if child_node.fail and child_node.fail.output:
                    child_node.output.extend(child_node.fail.output)

                queue.append(child_node)

    def scan(self, content: str) -> GuardrailResult:
        start_time = time.perf_counter()
        normalized = content.lower()
        current = self.root

        for char in normalized:
            while current is not None and char not in current.children:
                current = current.fail

            if current is None:
                current = self.root
                continue

            current = current.children[char]
            if current.output:
                latency = (time.perf_counter() - start_time) * 1000.0
                return GuardrailResult(
                    is_safe=False,
                    intercepted_term=current.output[0],
                    latency_ms=latency,
                )

        latency = (time.perf_counter() - start_time) * 1000.0
        return GuardrailResult(is_safe=True, intercepted_term=None, latency_ms=latency)
