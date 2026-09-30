import { Circle, CircleMarker, MapContainer, Polyline, Popup, TileLayer, useMap } from 'react-leaflet';
import { useEffect } from 'react';

function FitMap({wells}) { const map=useMap(); useEffect(()=>{ if(wells.length) map.fitBounds(wells.map(w=>[w.latitude,w.longitude]),{padding:[30,30]}); },[map,wells]); return null; }
const active=[27.432,95.338];
const trajectory=[[27.432,95.338],[27.434,95.341],[27.438,95.345],[27.443,95.348]];
export function NwisMap({wells,selectedId,onSelect,showTrajectory=true}){
 return <div className="relative isolate h-full min-h-[380px] overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 shadow-sm sm:min-h-[420px]">
   <MapContainer center={active} zoom={12} scrollWheelZoom className="h-full w-full">
     <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
     <FitMap wells={wells}/>
     <Circle center={active} radius={5000} pathOptions={{color:'#0891b2',weight:1,fillOpacity:.05}}/>
     {showTrajectory&&<Polyline positions={trajectory} pathOptions={{color:'#0891b2',weight:3,dashArray:'7 8'}}/>}
     {wells.map(w=><CircleMarker key={w.id} center={[w.latitude,w.longitude]} radius={w.id===selectedId?10:7} pathOptions={{color:w.id===selectedId?'#0891b2':w.status==='ACTIVE'?'#10b981':'#94a3b8',fillColor:w.id===selectedId?'#0891b2':w.status==='ACTIVE'?'#10b981':'#64748b',fillOpacity:.9}} eventHandlers={{click:()=>onSelect?.(w.id)}}><Popup><div className="min-w-[170px]"><strong>{w.name}</strong><div className="mt-1 text-xs">{w.field} · {w.status}</div><div className="mt-2 text-xs">Depth: {w.totalDepth} m</div><div className="text-xs">Formation: {w.formation}</div></div></Popup></CircleMarker>)}
   </MapContainer>
 </div>
}
