import clsx from 'clsx';
import { Maximize2, Minimize2 } from 'lucide-react';

export function GraphControls({ isExpanded, onToggleExpand, onZoomIn, onZoomOut }) {
  const lightButton = clsx(
    'inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50'
  );

  return (
    <div className="absolute left-4 top-4 z-20 flex flex-wrap gap-2">
      <button aria-label={isExpanded ? 'Minimize graph' : 'Maximize graph'} className={lightButton} onClick={onToggleExpand} type="button">
        {isExpanded ? <Minimize2 size={14} strokeWidth={2} /> : <Maximize2 size={14} strokeWidth={2} />}
      </button>
      <button aria-label="Zoom in" className={lightButton} onClick={onZoomIn} type="button">
        +
      </button>
      <button aria-label="Zoom out" className={lightButton} onClick={onZoomOut} type="button">
        -
      </button>
    </div>
  );
}
