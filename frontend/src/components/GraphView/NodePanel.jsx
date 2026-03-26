import clsx from 'clsx';

export function NodePanel({ selectedNode, onClose, onNodeClick }) {
  const node = selectedNode?.node;

  return (
    <aside
      className={clsx(
        'pointer-events-none absolute inset-x-0 top-16 z-30 flex justify-center px-4 transition-all duration-300',
        node ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
      )}
    >
      {node && (
        <div className="pointer-events-auto w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_20px_45px_rgba(15,23,42,0.12)]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-2xl font-semibold text-slate-800">{node.label}</h3>
              <p className="mt-1 text-sm text-slate-500">Entity: {node.type}</p>
              <p className="text-sm text-slate-500">ID: {node.id}</p>
            </div>
            <button
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-500 hover:border-slate-300 hover:text-slate-800"
              onClick={onClose}
              type="button"
            >
              Close
            </button>
          </div>

          <div className="mt-5 space-y-2 text-sm text-slate-700">
            {Object.entries(node.metadata ?? {}).slice(0, 12).map(([key, value]) => (
              <div key={key} className="flex gap-2 border-b border-slate-100 pb-2 last:border-b-0">
                <span className="min-w-[140px] font-medium text-slate-500">{key}:</span>
                <span className="break-words text-slate-700">{String(value ?? 'N/A')}</span>
              </div>
            ))}
          </div>

          <div className="mt-4 border-t border-slate-100 pt-4">
            <div className="mb-2 text-xs uppercase tracking-[0.2em] text-slate-400">Connections</div>
            <div className="flex flex-wrap gap-2">
              {(selectedNode.neighbors ?? []).slice(0, 12).map((neighbor) => (
                <button
                  key={neighbor.id}
                  className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-700 hover:border-blue-300 hover:text-blue-700"
                  onClick={() => onNodeClick(neighbor.id)}
                  type="button"
                >
                  {neighbor.label || neighbor.id}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
