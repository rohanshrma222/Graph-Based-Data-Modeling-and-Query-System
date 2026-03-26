export const nodeTypeColors = {
  Customer: '#7AA7FF',
  Order: '#6F8CFF',
  OrderItem: '#8AA4FF',
  Product: '#7CCF9A',
  Delivery: '#FFB866',
  Invoice: '#FF8E8E',
  Payment: '#71D5CC',
  Plant: '#9AA8B8',
  Default: '#94A3B8',
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
      label: 'data(label)',
      'font-size': 8,
      'text-opacity': 0.18,
      color: '#475569',
      'text-wrap': 'wrap',
      'text-max-width': 80,
      'text-valign': 'bottom',
      'text-margin-y': 10,
      width: 8,
      height: 8,
      shape: 'ellipse',
      'background-color': 'data(color)',
      'border-width': 1,
      'border-color': 'data(borderColor)',
      'overlay-opacity': 0,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 1.5,
      'curve-style': 'bezier',
      'target-arrow-shape': 'triangle',
      'arrow-scale': 0.55,
      label: 'data(label)',
      'font-size': 7,
      'text-opacity': 0.06,
      color: '#9DBEF7',
      'line-color': 'rgba(147, 197, 253, 0.55)',
      'target-arrow-color': 'rgba(147, 197, 253, 0.55)',
    },
  },
  {
    selector: '.highlighted',
    style: {
      'border-color': '#1D4ED8',
      'border-width': 3,
      'background-color': 'data(highlightColor)',
      width: 16,
      height: 16,
      'shadow-blur': 14,
      'shadow-color': '#60A5FA',
      'shadow-opacity': 0.32,
      'text-opacity': 1,
    },
  },
  {
    selector: '.selected',
    style: {
      'border-color': '#0F172A',
      'border-width': 2,
      width: 14,
      height: 14,
      'text-opacity': 1,
      color: '#0F172A',
    },
  },
];

export const getNodeVisual = (type) => {
  const baseColor = nodeTypeColors[type] || nodeTypeColors.Default;
  return {
    color: baseColor,
    borderColor: lightenHex(baseColor, 0.05),
    highlightColor: lightenHex(baseColor, 0.22),
  };
};
