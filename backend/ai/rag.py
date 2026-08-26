"""
Retrieval-augmented generation for the research pipeline.

Builds a grounded prompt from ranked evidence and asks the LLM to answer
the question with inline numeric citations like [1], [2]. Falls back to
an extractive summary (top claims stitched together) when no LLM is
configured, per the project's "don't depend entirely on an LLM" principle.
"""
from typing import List

from backend.ai.llm import LLMClient


class RAGSynthesizer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def synthesize(self, question: str, evidence: List[dict]) -> str:
        """
        `evidence` items are expected to have: "claim" (str) and
        "source_index" (1-based int, matching the numbered source list
        shown to the frontend).
        """
        if not evidence:
            return "No evidence was found to answer this question."
        if not self.llm_client.is_configured:
            return self._extractive_fallback(evidence)

        numbered_evidence = "\n".join(
            f"[{item['source_index']}] {item['claim']}" for item in evidence
        )
        prompt = (
            f"Answer the question using only the numbered evidence below. "
            f"Cite sources inline using their number in square brackets, e.g. [1]. "
            f"If evidence conflicts, say so explicitly.\n\n"
            f"Question: {question}\n\nEvidence:\n{numbered_evidence}\n\nAnswer:"
        )
        try:
            return self.llm_client.complete(prompt, max_tokens=700).strip()
        except Exception:
            return self._extractive_fallback(evidence)

    def _extractive_fallback(self, evidence: List[dict]) -> str:
        lines = [f"{item['claim']} [{item['source_index']}]" for item in evidence[:5]]
        return " ".join(lines)
