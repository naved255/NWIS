# NWIS Real-Time Module Contract

## Input contract

Adapters must yield `DrillingParameterUpdate` with:

- `well_id`
- UTC `timestamp`
- `depth`
- `rop`
- `wob`
- `rpm`
- `torque`
- `pressure`
- `mud_flow`
- `mud_weight`
- optional `sequence`
- `source`

## Output contract

`NormalizedRealtimeEvent` contains:

- `event_type`: `parameter_update`, `abnormal_parameter`, or `stream_status`
- `well_id`
- `timestamp`
- `parameters`
- `abnormal_fields`
- `issues`
- `source`

## Prediction interface

```python
class PredictionServiceAdapter(ABC):
    async def predict(self, update: DrillingParameterUpdate) -> Any:
        ...
```

The adapter intentionally accepts the canonical update rather than importing the ML module's internal classes.
