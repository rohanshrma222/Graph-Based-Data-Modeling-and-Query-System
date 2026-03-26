import { useEffect, useMemo, useState } from 'react';

function ResultsTable({ results }) {
  const columns = useMemo(() => {
    const firstRow = results?.[0] ?? {};
    return Object.keys(firstRow);
  }, [results]);

  if (!results?.length) {
    return <p className="text-xs text-slate-400">No rows returned.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full text-left text-xs text-slate-700">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((column) => (
              <th key={column} className="border-b border-slate-200 px-2 py-2 font-medium text-slate-500">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column} className="border-b border-slate-100 px-2 py-2 align-top text-slate-700">
                  {String(row[column] ?? 'null')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ChatMessage({ message, onHighlightNodes }) {
  const [showSql, setShowSql] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (message.role === 'assistant' && message.variant === 'error') {
      setShowSql(false);
      setShowResults(false);
    }
  }, [message]);

  const isUser = message.role === 'user';
  const bubbleClass = isUser
    ? 'ml-auto max-w-[88%] rounded-2xl rounded-tr-md bg-[#1f1f1f] text-white'
    : message.variant === 'guardrail'
      ? 'mr-auto max-w-[92%] rounded-2xl rounded-tl-md border border-amber-200 bg-amber-50 text-amber-900'
      : message.variant === 'error'
        ? 'mr-auto max-w-[92%] rounded-2xl rounded-tl-md border border-rose-200 bg-rose-50 text-rose-900'
        : 'mr-auto max-w-[92%] rounded-2xl rounded-tl-md bg-white text-slate-800';

  return (
    <div className="space-y-2">
      {!isUser && (
        <div className="flex items-center gap-3 px-1 text-slate-700">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#1f1f1f] text-sm font-semibold text-white">?</div>
          <div>
            <div className="text-sm font-semibold">Raw AI</div>
            <div className="text-xs text-slate-500">Graph Agent</div>
          </div>
        </div>
      )}
      {isUser && (
        <div className="px-1 text-right text-sm font-semibold text-slate-700">You</div>
      )}

      <div className={bubbleClass}>
        <div className="px-4 py-3 text-sm leading-7">{message.content}</div>

        {!isUser && message.sql && (
          <div className="border-t border-slate-100 px-4 py-3">
            <button className="text-xs font-medium text-slate-500 hover:text-slate-800" onClick={() => setShowSql((value) => !value)} type="button">
              {showSql ? 'Hide SQL' : 'View SQL'}
            </button>
            {showSql && (
              <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
                {message.sql}
              </pre>
            )}
          </div>
        )}

        {!isUser && Array.isArray(message.results) && message.results.length > 0 && (
          <div className="border-t border-slate-100 px-4 py-3">
            <button className="text-xs font-medium text-slate-500 hover:text-slate-800" onClick={() => setShowResults((value) => !value)} type="button">
              {showResults ? 'Hide Raw Results' : 'View Raw Results'}
            </button>
            {showResults && <div className="mt-3"><ResultsTable results={message.results} /></div>}
          </div>
        )}

        {!isUser && message.nodesReferenced?.length > 0 && (
          <div className="border-t border-slate-100 px-4 py-3">
            <button
              className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-blue-200 hover:text-blue-700"
              onClick={() => onHighlightNodes(message.nodesReferenced)}
              type="button"
            >
              Highlight on graph
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
