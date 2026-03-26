import { nodeTypeColors } from '../../utils/cytoscapeStyles';

const legendOrder = ['Customer', 'Order', 'OrderItem', 'Product', 'Delivery', 'Invoice', 'Payment', 'Plant'];

export function Sidebar({ graphData, lastUpdated }) {
  const counts = (graphData.nodes ?? []).reduce((acc, node) => {
    acc[node.type] = (acc[node.type] || 0) + 1;
    return acc;
  }, {});

  const totalNodes = graphData.nodes?.length ?? 0;
  const totalEdges = graphData.edges?.length ?? 0;

  return (
    <aside className="flex h-full w-full flex-col border-r border-slate-200 bg-[#fafafa] text-slate-700">
      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Supply Chain Graph</p>
        </div>
        <div className="my-5 border-t border-slate-200" />
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Graph Stats</h2>
          <div className="mt-3 space-y-2.5">
            <div className="rounded-xl border border-slate-200 bg-white px-3 py-3">
              <div className="text-[11px] uppercase tracking-[0.22em] text-slate-400">Nodes</div>
              <div className="mt-1 text-2xl font-semibold text-slate-900">{totalNodes}</div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white px-3 py-3">
              <div className="text-[11px] uppercase tracking-[0.22em] text-slate-400">Edges</div>
              <div className="mt-1 text-2xl font-semibold text-slate-900">{totalEdges}</div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white px-3 py-3">
              <div className="text-[11px] uppercase tracking-[0.22em] text-slate-400">Updated</div>
              <div className="mt-1 text-sm text-slate-700">{lastUpdated || 'Waiting for sync'}</div>
            </div>
          </div>
        </section>

        <div className="my-5 border-t border-slate-200" />

        <section>
          <h2 className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Entity Breakdown</h2>
          <div className="mt-3 space-y-2">
            {legendOrder.map((type) => (
              <div key={type} className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-2.5">
                <div className="flex items-center gap-2.5 text-sm text-slate-700">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: nodeTypeColors[type] }} />
                  {type}
                </div>
                <span className="text-sm font-medium text-slate-900">{counts[type] || 0}</span>
              </div>
            ))}
          </div>
        </section>

        <div className="my-5 border-t border-slate-200" />

        <section>
          <h2 className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Legend</h2>
          <div className="mt-3 grid gap-2">
            {legendOrder.map((type) => (
              <div key={type} className="flex items-center gap-2.5 text-sm text-slate-600">
                <span className="h-3 w-3 rounded-full border border-slate-200" style={{ backgroundColor: nodeTypeColors[type] }} />
                {type}
              </div>
            ))}
          </div>
        </section>
      </div>
    </aside>
  );
}
