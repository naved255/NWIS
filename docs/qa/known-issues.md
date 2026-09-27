# Known Issues / Follow-up

1. **Production adapters are not enabled by default.** Backend dependencies currently default to mock services for local/demo operation.
2. **Qdrant dependency is optional at runtime.** It was not started during this offline integration run.
3. **PostGIS was not exercised against a live database.** ORM and repository contracts were inspected; spatial behavior is covered by geo fake-repository tests.
4. **Production eRTMAC is unavailable in the package.** The adapter boundary and deterministic mock adapter are tested.
5. **Frontend npm build/test was not executed because dependency installation timed out in the QA environment.**
6. **ML inference emits feature-name warnings.** This does not currently break predictions, but the inference call should pass a DataFrame consistently.
7. **Realtime has two API surfaces.** The main backend mock WebSocket and dedicated realtime module should eventually be consolidated into one mounted production router.
8. **Database/ingestion field naming requires an explicit mapping adapter.** The differences are documented in `docs/data-contract.md`; they are not intended to be treated as identical field names.
