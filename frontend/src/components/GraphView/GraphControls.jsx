import clsx from 'clsx';

export function GraphControls({ onZoomIn, onZoomOut, onFit, onResetHighlights }) {
  const lightButton = clsx(
    'rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50'
  );
  const darkButton = clsx(
    'rounded-xl border border-black bg-black px-3 py-2 text-xs font-medium text-white transition hover:bg-slate-800'
  );

  return (
    <div className="absolute left-4 top-4 z-20 flex flex-wrap gap-2">
      <button className={lightButton} onClick={onFit} type="button">
        ? Minimize
      </button>
      <button className={darkButton} onClick={onResetHighlights} type="button">
        ? Hide Granular Overlay
      </button>
      <button className={lightButton} onClick={onZoomIn} type="button">
        +
      </button>
      <button className={lightButton} onClick={onZoomOut} type="button">
        -
      </button>
    </div>
  );
}
