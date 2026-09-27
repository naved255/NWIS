"""Deterministic, contextual extraction rules for drilling documents."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from ..models import (
    DocumentPage, DrillingEvent, EventType, ExtractedEntity,
    FormationObservation, LessonLearned, MitigationAction, Provenance, Severity,
)


@dataclass(frozen=True)
class TextUnit:
    text: str
    start: int
    end: int


class RuleBasedExtractor:
    """Extract drilling knowledge using contextual regex and lexical rules."""

    DEPTH_RE = re.compile(r"\b(?:at|@|depth(?:\s+of)?|from|to)\s*(\d{2,5}(?:\.\d+)?)\s*(?:m|meters?|metres?)\b", re.I)
    DEPTH_BARE_RE = re.compile(r"\b(\d{3,5}(?:\.\d+)?)\s*(?:m|meters?|metres?)\b", re.I)
    DATE_PATTERNS = [
        re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
        re.compile(r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"),
        re.compile(r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b", re.I),
    ]

    EVENT_RULES: Sequence[Tuple[EventType, re.Pattern[str]]] = [
        (EventType.MUD_LOSS, re.compile(r"\b(?:mud\s+loss(?:es)?|lost\s+circulation|loss\s+of\s+circulation|lost\s+returns|partial\s+loss(?:es)?|total\s+loss(?:es)?)\b", re.I)),
        (EventType.KICK, re.compile(r"\b(?:kick|well\s+kick|influx|unexpected\s+influx|flow\s+increase)\b", re.I)),
        (EventType.STUCK_PIPE, re.compile(r"\b(?:stuck\s+pipe|pipe\s+stuck|stuck\s+string|differential\s+sticking|mechanical\s+sticking)\b", re.I)),
        (EventType.FISHING, re.compile(r"\b(?:fishing|fish(?:ing)?\s+operation|fish\s+in\s+hole|fished\s+out|junk\s+in\s+hole)\b", re.I)),
        (EventType.NPT, re.compile(r"\b(?:non[-\s]?productive\s+time|NPT|lost\s+time|downtime)\b", re.I)),
        (EventType.CEMENTING_PROBLEM, re.compile(r"\b(?:cement(?:ing)?\s+(?:problem|failure|loss|channeling|shortfall)|poor\s+cement\s+bond|cement\s+loss|failed\s+cement(?:ing)?)\b", re.I)),
        (EventType.PRESSURE_OBSERVATION, re.compile(r"\b(?:pressure\s+(?:increase|decrease|drop|spike|observed|was|recorded)|(?:high|low|abnormal)\s+pressure|formation\s+pressure)\b", re.I)),
        (EventType.CASING_EVENT, re.compile(r"\b(?:casing\s+(?:run|running|set|stuck|failure|problem)|casing\s+shoe|liner\s+(?:run|set|stuck))\b", re.I)),
    ]

    SEVERITY = {
        "critical": Severity.CRITICAL, "severe": Severity.HIGH, "major": Severity.HIGH,
        "high": Severity.HIGH, "significant": Severity.HIGH, "moderate": Severity.MEDIUM,
        "medium": Severity.MEDIUM, "minor": Severity.LOW, "low": Severity.LOW,
    }

    EVENT_CONTEXT_CUES = re.compile(
        r"\b(?:occurred|experienced|encountered|observed|reported|resulted|developed|started|stopped|recorded|confirmed|detected|required|caused|led\s+to|due\s+to|while|during|after)\b",
        re.I,
    )

    MITIGATION_RE = re.compile(
        r"\b(?:mitigat(?:e|ed|ing)|control(?:led)?|remediat(?:e|ed)|resolved|circulat(?:ed|ion)|pumped|spotted|squeezed|increased|reduced|decreased|shut\s+in|closed|opened|wiper\s+tripped|reamed|backreamed|worked\s+the\s+pipe|fished|cemented|set\s+casing|lost\s+circulation\s+material|LCM)\b[^.;\n]*",
        re.I,
    )
    RECOMMENDATION_RE = re.compile(r"\b(?:recommend(?:ed|ation)?|advise[ds]?|should|shall|suggest(?:ed)?|next\s+time|to\s+avoid|lesson)\b[^.;\n]*", re.I)
    LESSON_RE = re.compile(r"\b(?:lesson\s+learned|lessons\s+learned|learning|takeaway|key\s+lesson)\s*[:\-]?\s*([^.;\n]+)", re.I)
    FORMATION_RE = re.compile(
        r"\b(?:formation|Fm\.?|member|reservoir)\s+(?:of\s+)?([A-Z][A-Za-z0-9&'()\-/ ]{2,60}?)(?=\s+(?:formation|Fm\.?|at|from|was|is|showed|observed|with|and|,|\.|;|\d)|$)",
        re.I,
    )
    WELL_RE = re.compile(r"\b(?:well\s*(?:name|no\.?|number|id)|well)\s*[:#-]?\s*([A-Z0-9][A-Z0-9._\-/]{2,30})\b", re.I)
    EQUIPMENT_RE = re.compile(r"\b(?:BHA|MWD|LWD|RSS|PDC|bit|mud\s+pump|top\s+drive|drawworks|shale\s+shaker|desander|desilter|centrifuge|cement\s+unit|choke\s+manifold|BOP|blowout\s+preventer|motor)\b", re.I)
    PARAM_RE = re.compile(
        r"\b(?P<name>ROP|WOB|RPM|SPP|ECD|MW|mud\s+weight|flow\s+rate|pump\s+rate|torque|standpipe\s+pressure|hookload|inclination|azimuth)\s*(?:=|:|was|of)?\s*(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>psi|ppg|klbf|rpm|ft/hr|m/hr|gpm|lpm|deg|°)?\b",
        re.I,
    )
    PRESSURE_RE = re.compile(r"\b(?:pressure|SPP|standpipe pressure)\s*(?:=|:|was|of|at)?\s*(-?\d+(?:\.\d+)?)\s*(psi|kPa|bar)?\b", re.I)
    CASING_RE = re.compile(r"\b(?P<size>\d+(?:\.\d+)?)\s*(?:in|inch|\")\s+casing\b", re.I)
    MUD_PROGRAM_RE = re.compile(r"\b(?:mud\s+(?:program|weight|system)|WBM|OBM|mud\s+properties|viscosity|funnel\s+viscosity)\b[^.;\n]*", re.I)

    def split_units(self, text: str) -> List[TextUnit]:
        """Split text into sentence-like units while preserving offsets."""
        units: List[TextUnit] = []
        for m in re.finditer(r"[^.!?\n]+(?:[.!?]+|$)", text):
            raw = m.group(0)
            left = len(raw) - len(raw.lstrip())
            right = len(raw.rstrip())
            if right <= left:
                continue
            start = m.start() + left
            end = m.start() + right
            units.append(TextUnit(text[start:end], start, end))
        return units

    @staticmethod
    def _prov(document_id: str, page: DocumentPage, page_text: str, start: int, end: int) -> Provenance:
        return Provenance(document_id=document_id, page_number=page.page_number,
                          text_span=[start, end], source_text=page_text[start:end])

    @staticmethod
    def _nearest_depth(text: str, anchor: int) -> Optional[float]:
        candidates = []
        for m in RuleBasedExtractor.DEPTH_RE.finditer(text):
            candidates.append((abs(m.start() - anchor), float(m.group(1))))
        if not candidates:
            for m in RuleBasedExtractor.DEPTH_BARE_RE.finditer(text):
                candidates.append((abs(m.start() - anchor), float(m.group(1))))
        if not candidates:
            return None
        distance, value = min(candidates, key=lambda x: x[0])
        return value if distance <= 250 else None

    @classmethod
    def _severity(cls, text: str) -> Severity:
        matches = [(m.start(), sev) for word, sev in cls.SEVERITY.items() for m in re.finditer(rf"\b{re.escape(word)}\b", text, re.I)]
        if not matches:
            return Severity.UNKNOWN
        return min(matches, key=lambda x: x[0])[1]

    def extract_entities(self, document_id: str, page: DocumentPage) -> List[ExtractedEntity]:
        out: List[ExtractedEntity] = []
        text = page.text
        for pattern, entity_type in [(self.WELL_RE, "WELL")]:
            for m in pattern.finditer(text):
                value = m.group(1).strip()
                out.append(ExtractedEntity(entity_type=entity_type, value=value,
                    normalized_value=value.upper(), confidence=0.88,
                    provenance=self._prov(document_id, page, text, m.start(), m.end())))
        for m in self.EQUIPMENT_RE.finditer(text):
            out.append(ExtractedEntity(entity_type="EQUIPMENT", value=m.group(0),
                normalized_value=m.group(0).upper(), confidence=0.82,
                provenance=self._prov(document_id, page, text, m.start(), m.end())))
        for m in self.PARAM_RE.finditer(text):
            value = m.group("value")
            unit = m.group("unit") or ""
            name = re.sub(r"\s+", "_", m.group("name").upper())
            out.append(ExtractedEntity(entity_type="DRILLING_PARAMETER", value=f"{value} {unit}".strip(),
                normalized_value=f"{name}={value}{unit}", confidence=0.94,
                provenance=self._prov(document_id, page, text, m.start(), m.end()),
                metadata={"parameter": name, "value": float(value), "unit": unit or None}))
        for m in self.PRESSURE_RE.finditer(text):
            out.append(ExtractedEntity(entity_type="PRESSURE", value=f"{m.group(1)} {m.group(2) or ''}".strip(),
                normalized_value=f"PRESSURE={m.group(1)}{m.group(2) or ''}", confidence=0.9,
                provenance=self._prov(document_id, page, text, m.start(), m.end())))
        for m in self.DEPTH_BARE_RE.finditer(text):
            out.append(ExtractedEntity(entity_type="DEPTH", value=f"{m.group(1)} m",
                normalized_value=f"DEPTH_M={float(m.group(1))}", confidence=0.92,
                provenance=self._prov(document_id, page, text, m.start(), m.end()),
                metadata={"depth_m": float(m.group(1))}))
        for m in self.CASING_RE.finditer(text):
            out.append(ExtractedEntity(entity_type="CASING", value=m.group(0),
                normalized_value=f"CASING_SIZE_IN={float(m.group('size'))}", confidence=0.9,
                provenance=self._prov(document_id, page, text, m.start(), m.end()),
                metadata={"size_in": float(m.group('size'))}))
        for m in self.MUD_PROGRAM_RE.finditer(text):
            out.append(ExtractedEntity(entity_type="MUD_PROGRAM", value=m.group(0).strip(),
                normalized_value=m.group(0).strip(), confidence=0.78,
                provenance=self._prov(document_id, page, text, m.start(), m.end())))
        for pattern in self.DATE_PATTERNS:
            for m in pattern.finditer(text):
                out.append(ExtractedEntity(entity_type="DATE", value=m.group(0), normalized_value=m.group(0), confidence=0.95,
                    provenance=self._prov(document_id, page, text, m.start(), m.end())))
        return out

    def extract_events(self, document_id: str, page: DocumentPage) -> List[DrillingEvent]:
        events: List[DrillingEvent] = []
        text = page.text
        units = self.split_units(text)
        for unit in units:
            for event_type, pattern in self.EVENT_RULES:
                match = pattern.search(unit.text)
                if not match:
                    continue
                # A bare noun such as "fishing tools" or "casing" is not enough.
                # Require incident/operation context for ambiguous event classes.
                ambiguous = event_type in {EventType.FISHING, EventType.NPT, EventType.PRESSURE_OBSERVATION, EventType.CASING_EVENT}
                if ambiguous and not self.EVENT_CONTEXT_CUES.search(unit.text):
                    # Still accept explicit incident phrases.
                    if not re.search(r"\b(?:operation|problem|issue|failure|stuck|occurred|experienced|required|recorded)\b", unit.text, re.I):
                        continue
                depth = self._nearest_depth(unit.text, match.start())
                severity = self._severity(unit.text)
                # Default severity only when the language itself supports it.
                description = unit.text.strip()
                events.append(DrillingEvent(
                    event_type=event_type, depth_m=depth, severity=severity,
                    confidence=0.91 if depth is not None else 0.84,
                    description=description,
                    date=self._first_date(unit.text),
                    provenance=self._prov(document_id, page, text, unit.start, unit.end),
                    metadata={"trigger": match.group(0)},
                ))
        return self._dedupe_events(events)

    @staticmethod
    def _first_date(text: str) -> Optional[str]:
        for pattern in RuleBasedExtractor.DATE_PATTERNS:
            m = pattern.search(text)
            if m:
                return m.group(0)
        return None

    @staticmethod
    def _dedupe_events(events: List[DrillingEvent]) -> List[DrillingEvent]:
        seen = set()
        result = []
        for e in events:
            key = (e.event_type, e.depth_m, e.provenance.page_number, e.provenance.text_span and tuple(e.provenance.text_span))
            if key not in seen:
                seen.add(key)
                result.append(e)
        return result

    def extract_formations(self, document_id: str, page: DocumentPage) -> List[FormationObservation]:
        out: List[FormationObservation] = []
        text = page.text
        for m in self.FORMATION_RE.finditer(text):
            name = re.sub(r"\s+", " ", m.group(1)).strip(" ,.-")
            if len(name) < 3 or name.lower() in {"pressure", "depth", "was", "is"}:
                continue
            out.append(FormationObservation(
                formation_name=name, depth_m=self._nearest_depth(text, m.start()),
                observation=m.group(0).strip(), confidence=0.78,
                provenance=self._prov(document_id, page, text, m.start(), m.end()),
            ))
        return out

    def extract_actions(self, document_id: str, page: DocumentPage) -> List[MitigationAction]:
        out: List[MitigationAction] = []
        text = page.text
        for pattern, recommendation in [(self.MITIGATION_RE, False), (self.RECOMMENDATION_RE, True)]:
            for m in pattern.finditer(text):
                action = m.group(0).strip(" .;:")
                if len(action) < 8:
                    continue
                out.append(MitigationAction(
                    action=action, action_type="RECOMMENDATION" if recommendation else "MITIGATION",
                    is_recommendation=recommendation, confidence=0.82,
                    provenance=self._prov(document_id, page, text, m.start(), m.end()),
                ))
        return self._dedupe_actions(out)

    @staticmethod
    def _dedupe_actions(actions: List[MitigationAction]) -> List[MitigationAction]:
        seen = set(); result = []
        for a in actions:
            key = (a.action.lower(), a.provenance.page_number, tuple(a.provenance.text_span or []))
            if key not in seen:
                seen.add(key); result.append(a)
        return result

    def extract_lessons(self, document_id: str, page: DocumentPage) -> List[LessonLearned]:
        out: List[LessonLearned] = []
        text = page.text
        for m in self.LESSON_RE.finditer(text):
            lesson = m.group(1).strip(" .;:")
            out.append(LessonLearned(lesson=lesson, confidence=0.9,
                provenance=self._prov(document_id, page, text, m.start(), m.end())))
        return out
