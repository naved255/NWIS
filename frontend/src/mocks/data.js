export const DEMO_LABEL = 'DEMO DATA — not a live prediction';

export const wells = [
  { id:'WELL-001', name:'OIL-NE-01', field:'Naharkatiya', operator:'OIL', status:'ACTIVE', latitude:27.432, longitude:95.338, totalDepth:3120, formation:'Tipam', spudDate:'2026-08-11' },
  { id:'WELL-014', name:'OIL-NE-14', field:'Naharkatiya', operator:'OIL', status:'COMPLETED', latitude:27.448, longitude:95.352, totalDepth:3380, formation:'Barail', spudDate:'2025-12-03' },
  { id:'WELL-021', name:'OIL-NE-21', field:'Naharkatiya', operator:'OIL', status:'COMPLETED', latitude:27.421, longitude:95.321, totalDepth:2965, formation:'Tipam', spudDate:'2025-06-19' },
  { id:'WELL-033', name:'OIL-NE-33', field:'Naharkatiya', operator:'OIL', status:'SUSPENDED', latitude:27.457, longitude:95.316, totalDepth:2750, formation:'Girujan', spudDate:'2024-09-27' },
  { id:'WELL-041', name:'OIL-NE-41', field:'Naharkatiya', operator:'OIL', status:'COMPLETED', latitude:27.409, longitude:95.349, totalDepth:3220, formation:'Tipam', spudDate:'2024-02-14' }
];

export const monitoring = { wellId:'WELL-001', depth:2874, rop:18.6, wob:11.8, rpm:112, torque:18.4, pressure:2840, mudWeight:1.16, mudFlow:2260, formation:'Tipam', timestamp:'2026-09-28T00:02:00+05:30' };

export const riskPredictions = [
  { riskType:'Mud loss', probability:0.21, severity:'LOW', confidence:0.74, modelVersion:'demo-risk-v0', explanation:['Current mud-flow trend is within the demo operating envelope','Historical offset events in this interval are infrequent'] },
  { riskType:'Stuck pipe', probability:0.47, severity:'MEDIUM', confidence:0.69, modelVersion:'demo-risk-v0', explanation:['Torque is trending above the recent baseline','Depth interval overlaps two historical stuck-pipe events in demo data'] },
  { riskType:'Kick', probability:0.12, severity:'LOW', confidence:0.81, modelVersion:'demo-risk-v0', explanation:['Pressure trend is stable in the demo stream','No demo kick indicators are currently active'] },
  { riskType:'Overpressure', probability:0.58, severity:'MEDIUM', confidence:0.63, modelVersion:'demo-risk-v0', explanation:['Pressure is elevated relative to the demo offset baseline','Formation context matches a higher-pressure historical interval'] }
];

export const recentEvents = [
  {id:'EV-1001',type:'DRILLING',title:'ROP increased',message:'ROP moved from 16.9 to 18.6 m/hr',timestamp:'00:02'},
  {id:'EV-1002',type:'PARAMETER',title:'Torque trend',message:'Torque crossed the demo watch threshold',timestamp:'23:56'},
  {id:'EV-1003',type:'FORMATION',title:'Formation confirmed',message:'Tipam interval confirmed from current interpretation',timestamp:'23:41'},
  {id:'EV-1004',type:'OFFSET',title:'Offset event match',message:'WELL-021 has a historical stuck-pipe event in this depth range',timestamp:'23:15'}
];

export const alerts = [
  {id:'AL-01',type:'RISK',severity:'MEDIUM',title:'Stuck-pipe risk watch',message:'Demo model indicates elevated risk in the current interval.',wellId:'WELL-001',timestamp:'00:02',status:'OPEN'},
  {id:'AL-02',type:'OFFSET',severity:'MEDIUM',title:'Offset incident match',message:'Two demo offset events share formation and depth context.',wellId:'WELL-001',timestamp:'23:15',status:'OPEN'},
  {id:'AL-03',type:'INFO',severity:'LOW',title:'Trajectory comparison ready',message:'Three offset wells have usable trajectory data.',wellId:'WELL-001',timestamp:'22:58',status:'ACKNOWLEDGED'}
];

export const depthTrend = Array.from({length:12}, (_,i) => ({depth:2760+i*10, rop:14+i*.4, torque:15+i*.28, pressure:2700+i*11}));

export const comparison = [
  {wellId:'WELL-001',name:'OIL-NE-01',distance:0,depth:2874,formation:'Tipam',rop:18.6,events:4,risk:'Medium'},
  {wellId:'WELL-021',name:'OIL-NE-21',distance:2.9,depth:2965,formation:'Tipam',rop:17.1,events:8,risk:'Medium'},
  {wellId:'WELL-041',name:'OIL-NE-41',distance:3.5,depth:3220,formation:'Tipam',rop:16.3,events:5,risk:'Low'},
  {wellId:'WELL-014',name:'OIL-NE-14',distance:4.2,depth:3380,formation:'Barail',rop:15.8,events:7,risk:'High'}
];
