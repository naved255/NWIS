import React,{useState} from 'react';
import ReactDOM from 'react-dom/client';
import { AppShell } from './layouts/AppShell';
import { Overview } from './pages/Overview';
import { MapPage,Monitoring,History,Risk,Compare,Alerts,Assistant,Details,Knowledge } from './pages/OperationalPages';
import './index.css';

const pages={overview:Overview,map:MapPage,monitoring:Monitoring,history:History,risk:Risk,compare:Compare,alerts:Alerts,assistant:Assistant,details:Details,knowledge:Knowledge};
function App(){const [page,setPage]=useState('overview');const Page=pages[page]||Overview;return <AppShell page={page} setPage={setPage}><Page go={setPage}/></AppShell>}
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);
