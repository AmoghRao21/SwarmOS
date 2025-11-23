"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Play, Terminal, Cpu, CheckCircle2, Loader2, ArrowRight, Network } from 'lucide-react';
import { createWorkflow, getWorkflow, Workflow } from '@/lib/api';
import SwarmGraph from '@/components/SwarmGraph';

// ⚠️ REPLACE THIS WITH YOUR ACTUAL USER ID FROM SWAGGER ⚠️
const USER_ID = "97b5e150-c022-43af-9a5c-821a578bb4b5"; 

type ViewMode = 'console' | 'graph';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [activeWorkflow, setActiveWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('console');
  
  // We use a ref to track the current workflow ID without triggering re-renders
  const activeWorkflowIdRef = useRef<string | null>(null);

  useEffect(() => {
    // 1. Connect ONCE on mount
    const wsUrl = process.env.NEXT_PUBLIC_API_URL 
      ? process.env.NEXT_PUBLIC_API_URL.replace('http', 'ws').replace('/api/v1', '/api/v1/ws') 
      : 'ws://localhost:8000/api/v1/ws';
      
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => setLogs(prev => [...prev, `⚡ Neural Link Established`]);
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'task_update') {
        const icon = data.status === 'completed' ? '✅' : '🔄';
        setLogs(prev => [...prev, `${icon} ${data.agent}: ${data.status}`]);
        
        // Only fetch update if this event belongs to our current workflow
        if (activeWorkflowIdRef.current && data.workflow_id === activeWorkflowIdRef.current) {
           getWorkflow(activeWorkflowIdRef.current).then(updated => {
             setActiveWorkflow(updated);
           });
        }
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      setLogs(prev => [...prev, `⚠️ Neural Link Unstable`]);
    };

    return () => {
      socket.close();
    };
  }, []); // 👈 Dependency Array is EMPTY. Runs once.

  const handleStart = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setLogs(prev => [...prev, `🚀 Initializing Swarm...`]);
    setViewMode('graph');
    
    try {
      const workflow = await createWorkflow(USER_ID, "New Mission", prompt);
      setActiveWorkflow(workflow);
      // Update the Ref so the WebSocket knows what to listen for
      activeWorkflowIdRef.current = workflow.id;
      setLogs(prev => [...prev, `🤖 Workflow ID: ${workflow.id} created.`]);
    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, `❌ Error connecting to backend.`]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 font-mono selection:bg-emerald-500/30">
      <header className="flex items-center gap-4 mb-12 border-b border-slate-800 pb-6">
        <div className="w-12 h-12 bg-emerald-600 rounded-lg flex items-center justify-center shadow-lg">
          <Cpu size={24} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">SwarmOS <span className="text-emerald-500">v1.0</span></h1>
          <p className="text-slate-500 text-sm">Autonomous Neural Orchestration Grid</p>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {/* Left Column */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <label className="block text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Mission Objective</label>
            <textarea 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the mission..."
              className="w-full h-48 bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm focus:ring-2 focus:ring-emerald-500/50 outline-none resize-none"
            />
            <button 
              onClick={handleStart}
              disabled={loading || !prompt}
              className="mt-4 w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Play size={18} />}
              {loading ? 'Deploying...' : 'Initialize Swarm'}
            </button>
          </div>

          <div className="bg-black/40 border border-slate-800 rounded-2xl p-4 h-64 overflow-y-auto text-xs">
            <div className="flex items-center gap-2 mb-3 text-slate-500 border-b border-slate-800/50 pb-2">
              <Terminal size={14} /> <span>System Stream</span>
            </div>
            <div className="space-y-2">
              {logs.map((log, i) => (
                <div key={i} className="text-emerald-400/80 break-words">
                  <span className="opacity-50 mr-2">[{new Date().toLocaleTimeString()}]</span>
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800 w-fit">
            <button onClick={() => setViewMode('console')} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${viewMode === 'console' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>
              <Terminal size={16} /> Output
            </button>
            <button onClick={() => setViewMode('graph')} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${viewMode === 'graph' ? 'bg-slate-800 text-emerald-400 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>
              <Network size={16} /> Neural Graph
            </button>
          </div>

          {viewMode === 'console' ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 min-h-[500px] relative flex flex-col">
              <div className="flex-1 bg-black/50 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-auto whitespace-pre-wrap border border-slate-800/50">
                {activeWorkflow?.tasks.map((task) => (
                  <div key={task.id} className="mb-8">
                    <div className="flex items-center gap-2 text-emerald-500 mb-2 text-xs uppercase tracking-widest font-bold">
                      <ArrowRight size={12} /> {task.assigned_agent}
                    </div>
                    <div className="pl-4 border-l-2 border-slate-800">
                      {task.output_payload?.result || <span className="animate-pulse text-slate-600">Thinking...</span>}
                    </div>
                  </div>
                ))}
                {!activeWorkflow && <div className="h-full flex items-center justify-center text-slate-700">System Standby...</div>}
              </div>
            </div>
          ) : (
            <SwarmGraph tasks={activeWorkflow?.tasks || []} />
          )}
        </div>
      </main>
    </div>
  );
}