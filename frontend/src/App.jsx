import { useCallback, useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';

import { fetchHealth } from './api/client';
import { ChatPanel } from './components/ChatPanel/ChatPanel';
import { GraphView } from './components/GraphView/GraphView';
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Layout/Sidebar';
import { useChat } from './hooks/useChat';
import { useGraph } from './hooks/useGraph';

function formatTimestamp(date = new Date()) {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export default function App() {
  const {
    graphData,
    selectedNode,
    highlightedNodes,
    loading,
    error,
    loadGraph,
    selectNode,
    highlightNodes,
    clearSelectedNode,
    setGraphData,
  } = useGraph();
  const { messages, loading: chatLoading, sendMessage, clearChat } = useChat();

  const [backendConnected, setBackendConnected] = useState(false);
  const [backendBanner, setBackendBanner] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');
  const [isGraphExpanded, setIsGraphExpanded] = useState(false);

  useEffect(() => {
    const pingBackend = async () => {
      try {
        await fetchHealth();
        setBackendConnected(true);
        setBackendBanner('');
      } catch {
        setBackendConnected(false);
        setBackendBanner('Backend unavailable. Make sure the FastAPI server is running on port 8000.');
      }
    };

    pingBackend();
  }, []);

  useEffect(() => {
    if (graphData.nodes.length || graphData.edges.length) {
      setLastUpdated(formatTimestamp());
    }
  }, [graphData]);

  useEffect(() => {
    if (error) {
      setBackendBanner('Backend unavailable. Make sure the FastAPI server is running on port 8000.');
      setBackendConnected(false);
    }
  }, [error]);

  const handleSelectNode = useCallback(async (nodeId, options = {}) => {
    const detail = await selectNode(nodeId);
    if (!detail || !options.expand) {
      return;
    }

    const existingNodeIds = new Set(graphData.nodes.map((node) => node.id));
    const missingNodes = (detail.neighbors ?? []).filter((node) => !existingNodeIds.has(node.id));
    const missingEdges = (detail.edges ?? []).filter(
      (edge) => !graphData.edges.some((current) => current.source === edge.source && current.target === edge.target && current.relationship === edge.relationship)
    );

    if (missingNodes.length || missingEdges.length) {
      setGraphData({
        nodes: [...graphData.nodes, ...missingNodes.map(({ id, type, label, metadata }) => ({ id, type, label, metadata }))],
        edges: [...graphData.edges, ...missingEdges.map(({ source, target, relationship }) => ({ source, target, relationship }))],
      });
    }
  }, [graphData, selectNode, setGraphData]);

  const handleSendMessage = useCallback(async (question) => {
    const nodes = await sendMessage(question);
    if (nodes?.length) {
      highlightNodes(nodes);
    }
  }, [highlightNodes, sendMessage]);

  const memoizedGraphData = useMemo(() => graphData, [graphData]);

  return (
    <div className="h-screen overflow-hidden bg-[#f5f6f8] text-slate-900">
      <div className="flex h-full flex-col">
        <Header backendConnected={backendConnected} />

        {backendBanner && (
          <div className="border-b border-amber-200 bg-amber-50 px-6 py-3 text-sm text-amber-900">
            {backendBanner}
          </div>
        )}

        <div className="min-h-0 flex-1 p-3">
          <div className="flex h-full min-h-0 overflow-hidden rounded-none border border-slate-200 bg-white">
            <div
              className={clsx(
                'transition-all duration-300 ease-out',
                isGraphExpanded ? 'pointer-events-none w-0 -translate-x-4 opacity-0' : 'w-[20%] min-w-[230px] translate-x-0 opacity-100'
              )}
            >
              <Sidebar graphData={memoizedGraphData} lastUpdated={lastUpdated} />
            </div>

            <div className="min-w-0 flex-1 transition-all duration-300 ease-out">
              <GraphView
                error={error}
                graphData={memoizedGraphData}
                highlightedNodes={highlightedNodes}
                isExpanded={isGraphExpanded}
                loading={loading}
                onClosePanel={clearSelectedNode}
                onRetry={loadGraph}
                onSelectNode={handleSelectNode}
                onToggleExpand={() => setIsGraphExpanded((value) => !value)}
                selectedNode={selectedNode}
              />
            </div>

            <div
              className={clsx(
                'transition-all duration-300 ease-out',
                isGraphExpanded ? 'pointer-events-none w-0 translate-x-4 opacity-0' : 'w-[26%] min-w-[300px] translate-x-0 opacity-100'
              )}
            >
              <ChatPanel
                loading={chatLoading}
                messages={messages}
                onClearChat={clearChat}
                onHighlightNodes={highlightNodes}
                onSendMessage={handleSendMessage}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
