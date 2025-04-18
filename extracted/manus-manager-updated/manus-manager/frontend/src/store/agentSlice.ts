import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Agent {
  id: number;
  name: string;
  description?: string;
  status: string;
  owner_id: number;
  instance_url?: string;
  max_tasks: number;
  created_at: string;
  updated_at?: string;
  last_active?: string;
}

interface AgentState {
  agents: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
}

const initialState: AgentState = {
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,
};

const agentSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    fetchAgentsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchAgentsSuccess: (state, action: PayloadAction<Agent[]>) => {
      state.agents = action.payload;
      state.loading = false;
    },
    fetchAgentsFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    selectAgent: (state, action: PayloadAction<Agent>) => {
      state.selectedAgent = action.payload;
    },
    clearSelectedAgent: (state) => {
      state.selectedAgent = null;
    },
    updateAgentStatus: (state, action: PayloadAction<{ id: number; status: string }>) => {
      const { id, status } = action.payload;
      const agent = state.agents.find(a => a.id === id);
      if (agent) {
        agent.status = status;
        agent.last_active = new Date().toISOString();
      }
      if (state.selectedAgent && state.selectedAgent.id === id) {
        state.selectedAgent.status = status;
        state.selectedAgent.last_active = new Date().toISOString();
      }
    },
    addAgent: (state, action: PayloadAction<Agent>) => {
      state.agents.push(action.payload);
    },
    updateAgent: (state, action: PayloadAction<Agent>) => {
      const index = state.agents.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = action.payload;
      }
      if (state.selectedAgent && state.selectedAgent.id === action.payload.id) {
        state.selectedAgent = action.payload;
      }
    },
    removeAgent: (state, action: PayloadAction<number>) => {
      state.agents = state.agents.filter(a => a.id !== action.payload);
      if (state.selectedAgent && state.selectedAgent.id === action.payload) {
        state.selectedAgent = null;
      }
    },
  },
});

export const {
  fetchAgentsStart,
  fetchAgentsSuccess,
  fetchAgentsFailure,
  selectAgent,
  clearSelectedAgent,
  updateAgentStatus,
  addAgent,
  updateAgent,
  removeAgent,
} = agentSlice.actions;

export default agentSlice.reducer;
