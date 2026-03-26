export const nodeTypeColors = {
  Customer: '#5B8CFF',
  Order: '#5E6BFF',
  OrderItem: '#6D7DFF',
  Product: '#27B36A',
  Delivery: '#F59E0B',
  Invoice: '#EF4444',
  Payment: '#0FAF9D',
  Plant: '#7C8CA0',
  Default: '#64748B',
};

const lightenHex = (hex, amount = 0.18) => {
  const value = hex.replace('#', '');
  const parsed = Number.parseInt(value, 16);
  const r = Math.min(255, Math.round(((parsed >> 16) & 255) + (255 - ((parsed >> 16) & 255)) * amount));
  const g = Math.min(255, Math.round(((parsed >> 8) & 255) + (255 - ((parsed >> 8) & 255)) * amount));
  const b = Math.min(255, Math.round((parsed & 255) + (255 - (parsed & 255)) * amount));
  return `rgb(${r}, ${g}, ${b})`;
};

export const cytoscapeStyles = [
  {
    selector: 'node',
    style: {
      label: '',
      width: 16,
      height: 16,
      shape: 'ellipse',
      'background-color': 'data(color)',
      'border-width': 1.5,
      'border-color': 'data(borderColor)',
      'background-opacity': 0.92,
      'overlay-opacity': 0,
    },
  },
  {
    selector: 'edge',
    style: {
      label: '',
      width: 1.8,
      'curve-style': 'bezier',
      'target-arrow-shape': 'triangle',
      'arrow-scale': 0.7,
      opacity: 0.72,
      'line-color': 'rgba(96, 165, 250, 0.58)',
      'target-arrow-color': 'rgba(96, 165, 250, 0.58)',
    },
  },
  {
    selector: '.highlighted',
    style: {
      'border-color': '#1D4ED8',
      'border-width': 4,
      'background-color': 'data(highlightColor)',
      width: 24,
      height: 24,
      'shadow-blur': 16,
      'shadow-color': '#60A5FA',
      'shadow-opacity': 0.38,
    },
  },
  {
    selector: '.selected',
    style: {
      'border-color': '#0F172A',
      'border-width': 3,
      width: 22,
      height: 22,
    },
  },
];

export const getNodeVisual = (type) => {
  const baseColor = nodeTypeColors[type] || nodeTypeColors.Default;
  return {
    color: baseColor,
    borderColor: lightenHex(baseColor, 0.02),
    highlightColor: lightenHex(baseColor, 0.18),
  };
};
