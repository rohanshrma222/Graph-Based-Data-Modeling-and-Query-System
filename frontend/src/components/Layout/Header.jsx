export function Header({ backendConnected }) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2">
      
        
          <img alt="Raw AI" className="h-12 w-16 object-contain" src="/RAI.png" />
       
      

      <div className="flex items-center gap-4">
        <span className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-500">
          v0.1
        </span>
        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600">
          <span className={`h-2 w-2 rounded-full ${backendConnected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          Backend {backendConnected ? 'Connected' : 'Offline'}
        </div>
      </div>
    </header>
  );
}
