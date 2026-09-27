# NWIS Frontend — Industrial Drilling Dashboard

Standalone React/Vite/Tailwind frontend module for the AI-Powered Nearby Wells Intelligence System (NWIS), SIH problem statement 26121 / OIL.

## Scope

This module owns the presentation layer only. It does **not** modify or implement backend services, ML models, RAG pipelines, PostGIS repositories, OCR, NLP, or real-time eRTMAC ingestion.

Included pages:

1. Overview Dashboard
2. Nearby Wells Map
3. Active Well Monitoring
4. Historical Insights
5. Risk Dashboard
6. Well Comparison
7. Alerts & Recommendations
8. AI Assistant
9. Well Details
10. Document/Knowledge Explorer

The UI uses a service adapter (`src/api/index.js`) so pages do not contain direct `fetch` calls. Mock data is intentionally labeled throughout the interface and is never presented as live prediction output.

## Run

```bash
npm install
cp .env.example .env
npm run dev
```

Default configuration uses the mock API:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK_API=true
```

For backend integration:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK_API=false
```

The production adapter currently expects these endpoints:

- `GET /overview`
- `GET /wells`
- `GET /wells/{well_id}`
- `GET /wells/{well_id}/monitoring`
- `GET /wells/{well_id}/risks`
- `GET /wells/{well_id}/events`
- `GET /wells/{well_id}/compare`
- `GET /wells/{well_id}/trend`
- `GET /alerts`
- `GET /search?q=...`

If the final backend uses different paths or response envelopes, update **only** `src/api/index.js` (or add a mapper in `src/api/`) rather than changing page components.

## Architecture

```text
React pages
    ↓
UI components / charts / map
    ↓
NWIS API adapter (src/api/index.js)
    ├── mockApi (demo mode)
    └── Axios realApi (production integration)
             ↓
        NWIS FastAPI services
```

### Map

Leaflet renders:
- active well
- offset wells
- selected well
- 5 km demo radius
- active trajectory illustration
- well status markers

Replace the trajectory array in `src/components/NwisMap.jsx` with the production trajectory GeoJSON/coordinate contract when that API is finalized.

### Risk transparency

Risk cards display probability, severity, confidence, model version, and explanations. Demo values use `demo-risk-v0` and the global DEMO DATA banner. The UI does not imply that those values are real operational predictions.

## Tests

```bash
npm test
```

Tests cover the mock API contract and basic UI disclosure components.

## Integration

1. Copy `frontend/` into the root of the NWIS repository.
2. Install dependencies.
3. Set `VITE_API_BASE_URL` to the central FastAPI base URL.
4. Set `VITE_USE_MOCK_API=false` only after the corresponding endpoints are available.
5. Align the response mappers in `src/api/index.js` with the final shared API schemas.
6. Replace the demo map trajectory with the production GeoJSON trajectory contract.
7. Keep authentication/token handling in the API adapter/interceptor rather than page components.

## Files created

- `package.json`
- `vite.config.js`
- `index.html`
- `.env.example`
- `README.md`
- `src/index.css`
- `src/main.jsx`
- `src/types/index.js`
- `src/api/client.js`
- `src/api/mockApi.js`
- `src/api/index.js`
- `src/mocks/data.js`
- `src/components/ui.jsx`
- `src/components/NwisMap.jsx`
- `src/components/Charts.jsx`
- `src/layouts/AppShell.jsx`
- `src/pages/Overview.jsx`
- `src/pages/OperationalPages.jsx`
- `tests/setup.js`
- `tests/mockApi.test.js`
- `tests/ui.test.jsx`

No backend files are modified by this module.
