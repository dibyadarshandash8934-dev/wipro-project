/** Network topology visualization using React Flow. */

import { useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  EdgeProps,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { VirtualDevice, Network } from '../../types';

interface NetworkTopologyProps {
  network: Network | null;
  devices: VirtualDevice[];
}

const nodeTypes = {
  device: (props: { data: { device: VirtualDevice; isGateway?: boolean; network?: Network } }) => {
    const { device, isGateway, network } = props.data;
    return (
      <div
        className={`p-3 rounded-lg border-2 shadow-lg transition-all ${
          isGateway
            ? 'bg-blue-600 border-blue-500 text-white'
            : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-600'
        }`}
        style={{ minWidth: 160 }}
      >
        <div className="flex items-center gap-2 mb-2">
          {isGateway ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {device.type === 'server' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              )}
              {device.type === 'laptop' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h-2l-1.5-4.5A2 2 0 0010.5 11H8.5a2 2 0 00-1.983 1.5L6 17H4a2 2 0 00-2 2v1h20v-1a2 2 0 00-2-2zM11 9v6m3-6v6m-9-2V7a2 2 0 012-2h2a2 2 0 012 2v2m-6 0h.01M13 14h.01M9 14h.01" />
              )}
              {device.type === 'phone' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              )}
              {device.type === 'iot' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              )}
              {device.type === 'pc' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              )}
            </svg>
          )}
          <span className="font-medium text-sm">{device.name}</span>
        </div>
        <div className="text-xs opacity-80">
          <div>{device.ip}</div>
          <div className="capitalize">{device.type}</div>
        </div>
        {isGateway && network && (
          <div className="mt-2 pt-2 border-t border-current/20 text-xs">
            <div>Public: {network.public_ip}</div>
          </div>
        )}
      </div>
    );
  },
  internet: () => (
    <div className="p-3 rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-600 text-white text-center shadow-lg">
      <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
      <div className="font-medium text-sm">Internet</div>
    </div>
  ),
};

// Use simple edge types - just use the default edge type with custom properties
const edgeTypes = {
  nat: (_props: EdgeProps) => <></>,
  forward: (_props: EdgeProps) => <></>,
};

export default function NetworkTopology({
  network,
  devices,
}: NetworkTopologyProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node[]>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge[]>([]);

  // Build nodes and edges from simulation state
  const buildTopology = useCallback(() => {
    if (!network) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    // Add LAN devices
    devices.forEach((device, index) => {
      newNodes.push({
        id: device.id,
        type: 'device',
        position: { x: 100 + (index % 3) * 200, y: 100 + Math.floor(index / 3) * 150 },
        data: { device },
      });
    });

    // Add NAT Gateway
    newNodes.push({
      id: 'nat-gateway',
      type: 'device',
      position: { x: 400, y: 300 },
      data: { device: { id: 'gateway', name: 'NAT Gateway', ip: network.gateway_ip, type: 'pc' }, isGateway: true, network },
    });

    // Add Internet node
    newNodes.push({
      id: 'internet',
      type: 'internet',
      position: { x: 700, y: 300 },
      data: {},
    });

    // Connect devices to NAT Gateway
    devices.forEach((device) => {
      newEdges.push({
        id: `edge-${device.id}-gateway`,
        source: device.id,
        target: 'nat-gateway',
        type: 'nat',
        animated: true,
      });
    });

    // Connect NAT Gateway to Internet
    newEdges.push({
      id: 'edge-gateway-internet',
      source: 'nat-gateway',
      target: 'internet',
      type: 'nat',
      animated: true,
      label: 'SNAT',
      style: { fontSize: 10 },
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [network, devices, setNodes, setEdges]);

  useEffect(() => {
    buildTopology();
  }, [buildTopology]);

  if (!network) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-12">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No Network Configured</h3>
          <p className="text-slate-500 dark:text-slate-400">Create a network to see the topology</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Network Topology</h2>
        <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-blue-500"></span>
            SNAT
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500" style={{ border: '2px dashed #22c55e', background: 'transparent' }}></span>
            Port Forward
          </span>
        </div>
      </div>
      <div className="h-96">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="#e2e8f0" gap={16} />
          <Controls />
          <MiniMap nodeColor={(node) => (node.type === 'internet' ? '#1e293b' : node.type === 'device' ? '#3b82f6' : '#64748b')} />
        </ReactFlow>
      </div>
    </div>
  );
}