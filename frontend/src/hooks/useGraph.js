import { useCallback, useEffect, useState } from 'react';

import { fetchGraph, fetchNode } from '../api/client';

const EMPTY_GRAPH = { nodes: [], edges: [] };

export function useGraph() {
  const [graphData, setGraphData] = useState(EMPTY_GRAPH);
  const [selectedNode, setSelectedNode] = useState(null);
  const [highlightedNodes, setHighlightedNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchGraph();
      setGraphData({
        nodes: data.nodes ?? [],
        edges: data.edges ?? [],
      });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load graph.');
    } finally {
      setLoading(false);
    }
  }, []);

  const selectNode = useCallback(async (nodeId) => {
    setError('');
    try {
      const data = await fetchNode(nodeId);
      setSelectedNode(data);
      return data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load node.');
      return null;
    }
  }, []);

  const highlightNodes = useCallback((nodeIds) => {
    setHighlightedNodes(Array.isArray(nodeIds) ? nodeIds : []);
  }, []);

  const clearHighlights = useCallback(() => {
    setHighlightedNodes([]);
  }, []);

  const clearSelectedNode = useCallback(() => {
    setSelectedNode(null);
  }, []);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  return {
    graphData,
    selectedNode,
    highlightedNodes,
    loading,
    error,
    loadGraph,
    selectNode,
    highlightNodes,
    clearHighlights,
    clearSelectedNode,
    setGraphData,
  };
}
