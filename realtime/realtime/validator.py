from __future__ import annotations

from dataclasses import dataclass

from .models import DrillingParameterUpdate, ValidationIssue


@dataclass(frozen=True)
class ParameterLimits:
    """Engineering sanity/abnormality thresholds for the synthetic NWIS stream.

    These are development defaults, not OIL operational limits. Production
    limits must be supplied by the operating organization/configuration.
    """

    depth: tuple[float, float] = (0, 12000)
    rop: tuple[float, float] = (0, 80)
    wob: tuple[float, float] = (0, 80)
    rpm: tuple[float, float] = (0, 400)
    torque: tuple[float, float] = (0, 500)
    pressure: tuple[float, float] = (0, 1000)
    mud_flow: tuple[float, float] = (0, 600)
    mud_weight: tuple[float, float] = (0, 25)


PARAMETER_LIMITS = ParameterLimits()


def validate_update(update: DrillingParameterUpdate, limits: ParameterLimits = PARAMETER_LIMITS) -> list[ValidationIssue]:
    """Validate a canonical update and return non-fatal abnormality issues."""
    issues: list[ValidationIssue] = []
    for field, bounds in limits.__dict__.items():
        value = getattr(update, field)
        low, high = bounds
        if value < low or value > high:
            issues.append(
                ValidationIssue(
                    field=field,
                    code="OUT_OF_RANGE",
                    message=f"{field}={value} is outside configured development range [{low}, {high}]",
                    value=value,
                    severity="warning",
                )
            )
    return issues
