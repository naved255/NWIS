import { apiClient } from './client';
import { mockApi } from './mockApi';

const useMock = String(import.meta.env.VITE_USE_MOCK_API ?? 'true').toLowerCase() !== 'false';
const ACTIVE_WELL = 'WELL-001';

const mapWell = (w) => ({
  id: w.well_id, name: w.well_name || w.well_id, field: w.field_name || '—',
  operator: w.operator || '—', status: w.status || 'UNKNOWN',
  latitude: Number(w.latitude), longitude: Number(w.longitude),
  totalDepth: Number(w.total_depth_m ?? 0),
  formation: w.metadata?.formation || w.metadata?.primary_formation || '—',
  spudDate: w.metadata?.spud_date || '—'
});

const mapPrediction = (p) => ({
  riskType: p.risk_type, probability: p.probability, severity: p.severity,
  confidence: p.confidence, modelVersion: p.model_version,
  explanation: p.explanation?.features?.map(x => `${x.feature}: ${x.contribution > 0 ? '+' : ''}${Number(x.contribution).toFixed(3)}`) || []
});

const mapEvent = (e) => ({ id:e.id, title:e.event_type, message:e.description || '', timestamp:e.event_time });

const realApi = {
  getOverview: async () => {
    const [well, monitoring, risks, alerts, events, nearby] = await Promise.all([
      realApi.getWell(ACTIVE_WELL), realApi.getMonitoring(ACTIVE_WELL),
      realApi.getRisks(ACTIVE_WELL), realApi.getAlerts(ACTIVE_WELL),
      realApi.getEvents(ACTIVE_WELL), realApi.getWellsNear(ACTIVE_WELL)
    ]);
    return { monitoring, riskPredictions: risks, alerts, recentEvents: events, nearbyCount: nearby.length, demo:false, well };
  },
  getWells: async () => (await apiClient.get('/wells')).data.items.map(mapWell),
  getWellsNear: async (id) => {
    const r = await apiClient.get('/wells/nearby', {params:{well_id:id, radius_km:25}});
    return r.data.items.map(mapWell);
  },
  getWell: async (id) => mapWell((await apiClient.get(`/wells/${id}`)).data),
  getMonitoring: async (id) => (await apiClient.get(`/wells/${id}/monitoring`)).data,
  getRisks: async (id) => (await apiClient.get('/predictions', {params:{well_id:id}})).data.items.map(mapPrediction),
  getEvents: async (id) => (await apiClient.get(`/wells/${id}/events`)).data.items.map(mapEvent),
  getAlerts: async (wellId) => (await apiClient.get('/alerts', {params:{well_id:wellId}})).data.items.map(a => ({id:a.id,type:a.alert_type,severity:a.severity,title:a.alert_type,message:a.message,wellId:a.well_id,timestamp:a.triggered_at,status:a.status})),
  getComparison: async (id) => (await apiClient.get('/wells/nearby', {params:{well_id:id, radius_km:25}})).data.items.map(w => ({wellId:w.well_id,name:w.well_name || w.well_id,distance:w.distance_km,depth:w.total_depth_m,formation:w.formation_matches?.[0] || '—',rop:'—',events:w.event_types?.length || 0,risk:'medium'})),
  getTrend: async (id) => (await apiClient.get(`/wells/${id}/trend`)).data,
  searchKnowledge: async (query) => {
    const r = await apiClient.post('/search', {query, limit:10});
    return {query, demo:false, results:r.data.items.map(x => ({id:x.result_id,title:x.title || x.document_id || 'Evidence',type:x.metadata?.event_type || 'DOCUMENT',score:x.score || 0,summary:x.text,source:x.source_uri}))};
  }
};

export const nwisApi = useMock ? mockApi : realApi;
export const apiMode = useMock ? 'mock' : 'live';
