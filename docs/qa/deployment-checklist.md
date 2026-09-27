# NWIS Deployment Checklist

## Backend
- [ ] Set `NWIS_ENVIRONMENT=production`.
- [ ] Configure `NWIS_DATABASE_URL` for PostgreSQL/PostGIS.
- [ ] Run Alembic migrations.
- [ ] Verify `/api/v1/health`.
- [ ] Configure CORS for the deployed frontend.
- [ ] Enable real service adapters instead of mock services.

## Database/PostGIS
- [ ] Install PostGIS extension.
- [ ] Run spatial indexes.
- [ ] Load approved wells, trajectories, formations, drilling parameters, events and documents.
- [ ] Verify spatial queries with representative data.

## RAG
- [ ] Deploy Qdrant.
- [ ] Configure embedding provider/model.
- [ ] Create the configured collection.
- [ ] Index document chunks with provenance and metadata.
- [ ] Verify filtered retrieval by well, formation, depth and event.

## Document/OCR/NLP
- [ ] Install an approved OCR engine/model.
- [ ] Test scanned PDFs and image inputs.
- [ ] Preserve document/page provenance.
- [ ] Validate extracted entities/events before persistence.

## ML/SHAP
- [ ] Train and register the production risk model.
- [ ] Persist the complete preprocessing + model artifact.
- [ ] Verify feature schema/version.
- [ ] Verify SHAP explanations against the same engineered input.
- [ ] Configure model threshold and monitoring.

## Realtime
- [ ] Configure production eRTMAC adapter.
- [ ] Validate UTC timestamps and sequence numbers.
- [ ] Configure production parameter/anomaly limits.
- [ ] Connect realtime prediction/alert callbacks.
- [ ] Mount one canonical WebSocket route behind the API gateway.

## Frontend
- [ ] Set `VITE_USE_MOCK_API=false`.
- [ ] Set `VITE_API_BASE_URL` to `/api/v1` or the deployed API.
- [ ] Run `npm ci`.
- [ ] Run `npm test`.
- [ ] Run `npm run build`.
- [ ] Verify Leaflet/GeoJSON rendering and WebSocket reconnect behavior.

## Security / operations
- [ ] Configure secrets outside source control.
- [ ] Restrict CORS origins.
- [ ] Add authentication/authorization at deployment gateway/API.
- [ ] Configure logging and metrics.
- [ ] Back up database/vector store.
- [ ] Validate all operational recommendations against approved OIL procedures before production use.
