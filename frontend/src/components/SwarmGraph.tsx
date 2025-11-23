"use client";

import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, Handle, Position, MarkerType, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { Bot, BrainCircuit } from 'lucide-react';
import { Task } from '@/lib/api';

const AgentNode = ({ data }: { data: { label: string; status: string; role: string } }) => {
  const isCompleted = data.status === 'completed';
  const isRunning = data.status === 'running';

  let borderColor = 'border-slate-700';
  let bgColor = 'bg-slate-900';
  let iconColor = 'text-slate-500';

  if (isCompleted) {
    borderColor = 'border-emerald-500';
    bgColor = 'bg-emerald-950/50';
    iconColor = 'text-emerald-400';
  } else if (isRunning) {
    borderColor = 'border-amber-500';
    bgColor = 'bg-amber-950/50';
    iconColor = 'text-amber-400';
  }

  return (
    <div className={`px-4 py-3 rounded-xl border-2 ${borderColor} ${bgColor} min-w-[180px] shadow-2xl`}>
      <Handle type="target" position={Position.Top} className="!bg-slate-500" />
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-black/50 ${iconColor}`}>
          {data.role === 'Supervisor' ? <BrainCircuit size={18} /> : <Bot size={18} />}
        </div>
        <div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">{data.role}</div>
          <div className="text-xs font-semibold text-slate-200">
            {data.label.length > 20 ? data.label.substring(0, 20) + '...' : data.label}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-slate-500" />
    </div>
  );
};

const nodeTypes = { agent: AgentNode };

export default function SwarmGraph({ tasks }: { tasks: Task[] }) {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    nodes.push({
      id: 'start',
      type: 'input',
      data: { label: 'User Request' },
      position: { x: 250, y: 0 },
      style: { background: '#0f172a', color: '#94a3b8', border: '1px solid #334155' }
    });

    tasks.forEach((task, index) => {
      nodes.push({
        id: task.id,
        type: 'agent',
        position: { x: 250, y: (index + 1) * 150 },
        data: { label: task.title, status: task.status, role: task.assigned_agent },
      });

      edges.push({
        id: `e-${index}`,
        source: index === 0 ? 'start' : tasks[index - 1].id,
        target: task.id,
        animated: task.status === 'running',
        style: { stroke: task.status === 'completed' ? '#10b981' : '#475569', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: task.status === 'completed' ? '#10b981' : '#475569' },
      });
    });

    return { nodes, edges };
  }, [tasks]);

  return (
    <div className="w-full h-[500px] bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView>
        <Background color="#334155" gap={20} size={1} />
        <Controls className="bg-slate-800 border-slate-700 text-slate-400" />
      </ReactFlow>
    </div>
  );
}