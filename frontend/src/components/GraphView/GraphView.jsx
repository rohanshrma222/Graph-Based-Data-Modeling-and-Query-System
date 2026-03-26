import { useEffect, useMemo, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';

import { GraphControls } from './GraphControls';
import { NodePanel } from './NodePanel';
import { getNodeVisual, cytoscapeStyles } from '../../utils/cytoscapeStyles';

cytoscape.use(coseBilkent);

const layout = {
  name: 'cose-bilkent',
  animate: false,
  fit: true,
  padding: 32,
  randomize: true,
  nodeRepulsion: 4200,
  idealEdgeLength: 90,
};

function toElements(graphData) {
  const nodes = (graphData.nodes ?? []).map((node) => {
    const visual = getNodeVisual(node.type);
    return {
      data: {
        id: node.id,
        label: node.label || node.id,
        type: node.type,
        metadata: node.metadata || {},
        color: visual.color,
        borderColor: visual.borderColor,
        highlightColor: visual.highlightColor,
      },
    };
  });

  const edges = (graphData.edges ?? []).map((edge) => ({
    data: {
      id: `${edge.source}-${edge.target}-${edge.relationship}`,
      source: edge.source,
      target: edge.target,
      label: edge.relationship,
    },
  }));

  return [...nodes, ...edges];
}

export function GraphView({
  graphData,
  selectedNode,
  highlightedNodes,
  loading,
  error,
  onRetry,
  onSelectNode,
  onClearHighlights,
  onClosePanel,
}) {
  const cyRef = useRef(null);
  const clickTimeoutRef = useRef(null);

  const elements = useMemo(() => toElements(graphData), [graphData]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) {
      return;
    }

    cy.nodes().removeClass('highlighted selected');

    highlightedNodes.forEach((nodeId) => {
      cy.getElementById(nodeId).addClass('highlighted');
    });

    if (selectedNode?.node?.id) {
      cy.getElementById(selectedNode.node.id).addClass('selected');
    }
  }, [highlightedNodes, selectedNode, elements]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || elements.length === 0) {
      return;
    }

    cy.layout(layout).run();
    requestAnimationFrame(() => {
      cy.fit(cy.elements(), 36);
      cy.zoom(Math.min(cy.zoom(), 1));
    });
  }, [elements]);

  const attachCy = (cy) => {
    if (cyRef.current === cy) {
      return;
    }
    cyRef.current = cy;

    cy.minZoom(0.08);
    cy.maxZoom(3.5);

    cy.on('tap', 'node', (event) => {
      const nodeId = event.target.id();
      if (clickTimeoutRef.current) {
        clearTimeout(clickTimeoutRef.current);
        clickTimeoutRef.current = null;
        onSelectNode(nodeId, { expand: true });
        return;
      }

      clickTimeoutRef.current = setTimeout(() => {
        onSelectNode(nodeId);
        clickTimeoutRef.current = null;
      }, 220);
    });
  };

  const zoomIn = () => cyRef.current?.zoom({ level: (cyRef.current?.zoom() || 1) * 1.2, renderedPosition: { x: 300, y: 240 } });
  const zoomOut = () => cyRef.current?.zoom({ level: (cyRef.current?.zoom() || 1) * 0.8, renderedPosition: { x: 300, y: 240 } });
  const fit = () => cyRef.current?.fit(cyRef.current?.elements(), 36);

  return (
    <section className="relative flex h-full min-w-0 flex-1 flex-col border-r border-slate-200 bg-white">
      <GraphControls
        onFit={fit}
        onResetHighlights={onClearHighlights}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
      />

      {loading && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/75 backdrop-blur-sm">
          <div className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm text-slate-700 shadow-sm">
            Loading graph...
          </div>
        </div>
      )}

      {error && !loading && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/85 px-8">
          <div className="max-w-md rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Graph unavailable</h3>
            <p className="mt-2 text-sm text-slate-500">{error}</p>
            <button
              className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700 hover:border-slate-300"
              onClick={onRetry}
              type="button"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      <div className="graph-surface h-full min-h-0">
        <CytoscapeComponent
          className="h-full w-full"
          cy={attachCy}
          elements={elements}
          layout={layout}
          stylesheet={cytoscapeStyles}
        />
      </div>

      <NodePanel onClose={onClosePanel} onNodeClick={onSelectNode} selectedNode={selectedNode} />
    </section>
  );
}
