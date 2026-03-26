import { useEffect, useRef, useState } from 'react';

export function ChatInput({ disabled, loading, onSend }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }
    textarea.style.height = '0px';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 112)}px`;
  }, [value]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSend(trimmed);
    setValue('');
  };

  return (
    <div className="border-t border-slate-200 p-3">
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-slate-100 px-3 py-2 text-xs text-slate-500">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          Raw AI is awaiting instructions
        </div>
        <textarea
          ref={textareaRef}
          className="max-h-28 min-h-[92px] w-full resize-none bg-transparent px-3 py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400"
          disabled={disabled}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="Analyze anything"
          rows={1}
          value={value}
        />
        <div className="flex items-center justify-end px-3 pb-3">
          <button
            className="inline-flex items-center gap-2 rounded-lg bg-slate-400 px-3.5 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={disabled || !value.trim()}
            onClick={handleSubmit}
            type="button"
          >
            {loading && <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
