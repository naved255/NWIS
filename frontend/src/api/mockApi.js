import { alerts, comparison, depthTrend, monitoring, recentEvents, riskPredictions, wells } from '../mocks/data';

const delay = (value, ms=120) => new Promise(resolve => setTimeout(() => resolve(structuredClone(value)), ms));

export const mockApi = {
  getOverview: () => delay({ demo:true, monitoring, riskPredictions, recentEvents, alerts, nearbyCount:wells.length-1 }),
  getWells: () => delay(wells),
  getWell: (id) => delay(wells.find(w => w.id === id) || wells[0]),
  getMonitoring: () => delay(monitoring),
  getRisks: () => delay(riskPredictions),
  getEvents: () => delay(recentEvents),
  getAlerts: () => delay(alerts),
  getComparison: () => delay(comparison),
  getTrend: () => delay(depthTrend),
  searchKnowledge: (query) => delay({ query, demo:true, results:[
    {id:'DOC-017',title:'Historical drilling report — Tipam interval',type:'DDR',score:.89,summary:'Demo result showing how offset drilling knowledge can be surfaced.'},
    {id:'EV-221',title:'Stuck pipe event — OIL-NE-21',type:'EVENT',score:.84,summary:'Demo historical event matched on formation and depth.'}
  ]})
};
