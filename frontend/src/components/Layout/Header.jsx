export function Header({ backendConnected }) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-4">
      <div className="flex items-center gap-3 text-sm text-slate-400">
        <div className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-300 bg-slate-50 text-slate-700">
          <span className="text-[11px]">?</span>
        </div>
        <span>Mapping</span>
        <span>/</span>
        <span className="font-semibold text-slate-800">Order to Cash</span>
      </div>

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
