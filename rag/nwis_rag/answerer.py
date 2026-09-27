"""Evidence-grounded answer generation for historical drilling questions."""

from __future__ import annotations

from collections.abc import Callable

from .schemas import AnswerResponse, EvidenceItem

INSUFFICIENT = "Insufficient historical evidence."


class EvidenceAnswerer:
    """Generate an answer from retrieved evidence without inventing events.

    A custom LLM callable can be supplied. The callable must return text and
    receives a prompt containing only the user question and retrieved evidence.
    Without an LLM, this class returns a deterministic evidence summary.
    """

    def __init__(self, llm: Callable[[str], str] | None = None, min_evidence: int = 1):
        self.llm = llm
        self.min_evidence = max(1, min_evidence)

    def answer(self, question: str, evidence: list[EvidenceItem]) -> AnswerResponse:
        """Return FACT/SOURCE/INFERENCE sections backed by retrieved evidence."""
        if len(evidence) < self.min_evidence:
            return AnswerResponse(
                question=question,
                sufficient_evidence=False,
                message=INSUFFICIENT,
            )

        if self.llm is None:
            return self._deterministic(question, evidence)

        generated = self.llm(self.build_prompt(question, evidence))
        return self._parse_llm_output(question, generated, evidence)

    @staticmethod
    def build_prompt(question: str, evidence: list[EvidenceItem]) -> str:
        """Build a strict prompt that prevents unsupported historical claims."""
        evidence_text = "\n\n".join(
            f"[{item.evidence_id}] {item.text}\nSOURCE: {item.source_reference}"
            for item in evidence
        )
        return f"""You are an evidence-only historical drilling knowledge assistant.
Answer the question only from the supplied evidence. Never invent a well,
event, depth, date, formation, mitigation, or lesson. If the evidence does
not establish an answer, say exactly: {INSUFFICIENT}

Return exactly these sections:
FACT:
- factual statements directly supported by evidence
SOURCE:
- source references for the facts
INFERENCE:
- only clearly marked, conservative inferences; write 'None supported.' if none

QUESTION:
{question}

EVIDENCE:
{evidence_text}
"""

    def _deterministic(self, question: str, evidence: list[EvidenceItem]) -> AnswerResponse:
        facts = [item.text.strip() for item in evidence if item.text.strip()]
        sources = [f"[{item.evidence_id}] {item.source_reference}" for item in evidence]
        return AnswerResponse(
            question=question,
            fact=facts,
            source=sources,
            inference=[],
            sufficient_evidence=bool(facts),
        )

    def _parse_llm_output(
        self,
        question: str,
        generated: str,
        evidence: list[EvidenceItem],
    ) -> AnswerResponse:
        """Parse the required sections while retaining source traceability."""
        sections = {"FACT": [], "SOURCE": [], "INFERENCE": []}
        current: str | None = None
        for raw in generated.splitlines():
            line = raw.strip()
            upper = line.rstrip(":").upper()
            if upper in sections:
                current = upper
                continue
            if current and line:
                clean = line[1:].strip() if line.startswith(("-", "*")) else line
                sections[current].append(clean)

        # Never allow the LLM to omit source references. Attach the actual
        # retrieved source list independently of generated text.
        sources = [f"[{item.evidence_id}] {item.source_reference}" for item in evidence]
        if not sections["FACT"]:
            sections["FACT"] = [INSUFFICIENT]
        if not sections["INFERENCE"]:
            sections["INFERENCE"] = ["None supported."]

        insufficient = sections["FACT"] == [INSUFFICIENT]
        return AnswerResponse(
            question=question,
            fact=sections["FACT"],
            source=sources,
            inference=sections["INFERENCE"],
            sufficient_evidence=not insufficient,
            message=INSUFFICIENT if insufficient else None,
        )
