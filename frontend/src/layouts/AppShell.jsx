import { Activity, Bell, Bot, ChevronRight, CircleHelp, FileSearch, Gauge, GitCompareArrows, Layers3, MapPinned, Menu, Search, Settings2, ShieldCheck, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Badge, DemoBanner } from '../components/ui';
import { apiMode } from '../api';

const nav = [
  ['Overview','overview',Gauge], ['Nearby Wells','map',MapPinned], ['Active Monitoring','monitoring',Activity],
  ['Historical Insights','history',FileSearch], ['Risk Dashboard','risk',ShieldCheck], ['Well Comparison','compare',GitCompareArrows],
  ['Alerts & Recommendations','alerts',Bell], ['AI Assistant','assistant',Bot], ['Well Details','details',Layers3], ['Knowledge Explorer','knowledge',Search]
];

export function AppShell({ page, setPage, children }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const closeOnEscape = (event) => event.key === 'Escape' && setOpen(false);
    document.addEventListener('keydown', closeOnEscape);
    document.body.classList.toggle('nav-open', open);
    return () => {
      document.removeEventListener('keydown', closeOnEscape);
      document.body.classList.remove('nav-open');
    };
  }, [open]);

  const navigate = (key) => {
    setPage(key);
    setOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen overflow-x-hidden text-slate-700">
      {open && <button aria-label="Close navigation" onClick={() => setOpen(false)} className="fixed inset-0 z-[900] bg-slate-900/30 backdrop-blur-[2px] lg:hidden" />}

      <aside className={`fixed inset-y-0 left-0 z-[1000] flex w-[280px] flex-col border-r border-slate-200 bg-white shadow-2xl shadow-slate-900/10 transition-transform duration-200 lg:translate-x-0 lg:shadow-none ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 px-5">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl border border-cyan-200 bg-cyan-50 text-cyan-700 shadow-sm"><Activity size={18}/></div>
            <div><div className="text-sm font-bold tracking-wide text-slate-900">NWIS</div><div className="text-[9px] uppercase tracking-[.18em] text-slate-400">Drilling Intelligence</div></div>
          </div>
          <button aria-label="Close navigation" onClick={() => setOpen(false)} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"><X size={18}/></button>
        </div>

        <nav className="nwis-scroll flex-1 overflow-y-auto px-3 py-4" aria-label="Primary navigation">
          <div className="mb-2 px-3 text-[9px] font-semibold uppercase tracking-[.2em] text-slate-400">Workspace</div>
          {nav.map(([label,key,Icon]) => (
            <button key={key} onClick={() => navigate(key)} className={`mb-1 flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left text-xs transition ${page===key ? 'border-cyan-200 bg-cyan-50 font-semibold text-cyan-800 shadow-sm' : 'border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50 hover:text-slate-900'}`}>
              <Icon size={16}/><span className="flex-1">{label}</span>{page===key && <ChevronRight size={13}/>} 
            </button>
          ))}
        </nav>

        <div className="shrink-0 border-t border-slate-200 bg-slate-50/80 p-4">
          <div className="flex items-center justify-between text-[10px] text-slate-500"><span>API mode</span><Badge tone={apiMode==='mock'?'amber':'green'}>{apiMode}</Badge></div>
          <div className="mt-3 flex items-center gap-2 text-[10px] text-slate-500"><CircleHelp size={13}/> SIH 2026 presentation build</div>
        </div>
      </aside>

      <div className="lg:pl-[280px]">
        <header className="sticky top-0 z-[800] flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 bg-white/95 px-4 shadow-sm backdrop-blur-xl sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <button aria-label="Open navigation" onClick={() => setOpen(true)} className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"><Menu size={20}/></button>
            <div className="min-w-0"><div className="truncate text-xs font-semibold text-slate-900">Operations Intelligence Console</div><div className="truncate text-[10px] text-slate-500">Nearby Wells Intelligence System · OIL</div></div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <div className="hidden items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-[10px] text-slate-500 md:flex"><Search size={13}/> Global well / event search</div>
            <button aria-label="Settings" className="grid h-9 w-9 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 shadow-sm hover:bg-slate-50"><Settings2 size={15}/></button>
          </div>
        </header>
        <DemoBanner/>
        <main className="mx-auto max-w-[1700px] p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
