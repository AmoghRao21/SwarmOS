import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

export interface Workflow {
  id: string;
  title: string;
  status: string;
  tasks: Task[];
}

export interface Task {
  id: string;
  title: string;
  status: string;
  assigned_agent: string;
  output_payload?: { result: string };
}

export const createUser = async (email: string) => {
  const res = await api.post('/users/', null, { params: { email } });
  return res.data;
};

export const createWorkflow = async (userId: string, title: string, prompt: string) => {
  const res = await api.post('/workflows/', { title, initial_prompt: prompt }, { params: { user_id: userId } });
  return res.data;
};

export const getWorkflow = async (workflowId: string) => {
  const res = await api.get<Workflow>(`/workflows/${workflowId}`);
  return res.data;
};