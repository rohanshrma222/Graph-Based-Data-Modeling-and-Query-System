import { useEffect, useRef } from 'react';

import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';

const suggestions = [
  'Which products have the most billing documents?',
  'Trace the flow of a billing document',
  'Show orders delivered but not billed',
  'Which customer has the most pending payments?',
];

export function ChatPanel({ messages, loading, onClearChat, onHighlightNodes, onSendMessage }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) {
      return;
    }
    container.scrollTop = container.scrollHeight;
  }, [messages, loading]);

  return (
    <aside className="flex h-full w-full flex-col border-l border-slate-200 bg-[#fbfbfb]">
      <div className="border-b border-slate-200 px-4 py-3">
        <div className="text-sm font-semibold text-slate-800">Chat with Graph</div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4" ref={scrollRef}>
        <div className="flex flex-col gap-5">
          {messages.length === 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-sm text-slate-600">Try one of these questions:</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700 hover:border-slate-300 hover:bg-white"
                    onClick={() => onSendMessage(suggestion)}
                    type="button"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} onHighlightNodes={onHighlightNodes} />
          ))}
        </div>
      </div>

      <div className="px-3 pb-3 text-right">
        <button className="text-xs text-slate-400 hover:text-slate-700" onClick={onClearChat} type="button">
          Clear chat
        </button>
      </div>
      <ChatInput disabled={loading} loading={loading} onSend={onSendMessage} />
    </aside>
  );
}
