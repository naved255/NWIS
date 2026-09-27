import { describe,expect,it } from 'vitest';
import { mockApi } from '../src/api/mockApi';

describe('NWIS mock API',()=>{
 it('returns the active well monitoring snapshot',async()=>{const m=await mockApi.getMonitoring();expect(m.wellId).toBe('WELL-001');expect(m.depth).toBeGreaterThan(0);});
 it('returns nearby wells with coordinates',async()=>{const wells=await mockApi.getWells();expect(wells.length).toBeGreaterThan(1);expect(wells.every(w=>Number.isFinite(w.latitude)&&Number.isFinite(w.longitude))).toBe(true);});
 it('marks search results as demo data',async()=>{const r=await mockApi.searchKnowledge('stuck pipe');expect(r.demo).toBe(true);expect(r.results.length).toBeGreaterThan(0);});
});
