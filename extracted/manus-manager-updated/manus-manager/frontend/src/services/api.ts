import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth service
export const authService = {
  // Login with username and password
  login: async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },
  
  // Get Google auth URL
  getGoogleAuthUrl: async () => {
    try {
      const response = await api.get('/auth/google/auth-url');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get Google auth URL');
    }
  },
  
  // Login with Google token
  loginWithGoogle: async (token) => {
    try {
      const response = await api.post('/auth/google', { token });
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Google login failed');
    }
  },
  
  // Logout
  logout: () => {
    localStorage.removeItem('token');
  },
  
  // Get current user
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get user');
    }
  },
};

// Agent service
export const agentService = {
  // Get all agents
  getAgents: async () => {
    try {
      const response = await api.get('/agents');
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get agents');
    }
  },
  
  // Get agent by ID
  getAgent: async (id) => {
    try {
      const response = await api.get(`/agents/${id}`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get agent');
    }
  },
  
  // Create agent
  createAgent: async (agentData) => {
    try {
      const response = await api.post('/agents', agentData);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create agent');
    }
  },
  
  // Update agent
  updateAgent: async (id, agentData) => {
    try {
      const response = await api.put(`/agents/${id}`, agentData);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update agent');
    }
  },
  
  // Delete agent
  deleteAgent: async (id) => {
    try {
      await api.delete(`/agents/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete agent');
    }
  },
  
  // Start agent
  startAgent: async (id) => {
    try {
      const response = await api.post(`/agents/${id}/start`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to start agent');
    }
  },
  
  // Stop agent
  stopAgent: async (id) => {
    try {
      const response = await api.post(`/agents/${id}/stop`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to stop agent');
    }
  },
  
  // Pause agent
  pauseAgent: async (id) => {
    try {
      const response = await api.post(`/agents/${id}/pause`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to pause agent');
    }
  },
};

// Task service
export const taskService = {
  // Get all tasks
  getTasks: async () => {
    try {
      const response = await api.get('/tasks');
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get tasks');
    }
  },
  
  // Get task by ID
  getTask: async (id) => {
    try {
      const response = await api.get(`/tasks/${id}`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get task');
    }
  },
  
  // Create task
  createTask: async (taskData) => {
    try {
      const response = await api.post('/tasks', taskData);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create task');
    }
  },
  
  // Update task
  updateTask: async (id, taskData) => {
    try {
      const response = await api.put(`/tasks/${id}`, taskData);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update task');
    }
  },
  
  // Delete task
  deleteTask: async (id) => {
    try {
      await api.delete(`/tasks/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete task');
    }
  },
  
  // Assign task to agent
  assignTask: async (taskId, agentId) => {
    try {
      const response = await api.post(`/tasks/${taskId}/assign/${agentId}`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to assign task');
    }
  },
};

// Tracking service
export const trackingService = {
  // Get agent logs
  getAgentLogs: async (agentId) => {
    try {
      const response = await api.get(`/tracking/agents/${agentId}/logs`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get agent logs');
    }
  },
  
  // Get task logs
  getTaskLogs: async (taskId) => {
    try {
      const response = await api.get(`/tracking/tasks/${taskId}/logs`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get task logs');
    }
  },
  
  // Update agent status
  updateAgentStatus: async (agentId, status) => {
    try {
      const response = await api.post(`/tracking/agents/${agentId}/status`, { status });
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update agent status');
    }
  },
  
  // Update task progress
  updateTaskProgress: async (taskId, progress, taskStatus) => {
    try {
      const response = await api.post(`/tracking/tasks/${taskId}/progress/${progress}`, { task_status: taskStatus });
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update task progress');
    }
  },
  
  // Connect to WebSocket for real-time updates
  connectWebSocket: (onMessage) => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    const ws = new WebSocket(`${WS_URL}/tracking/ws?token=${token}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    return ws;
  },
};

// Analytics service
export const analyticsService = {
  // Get dashboard data
  getDashboardData: async () => {
    try {
      const response = await api.get('/analytics/dashboard');
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get dashboard data');
    }
  },
  
  // Get agent stats
  getAgentStats: async () => {
    try {
      const response = await api.get('/analytics/agents/stats');
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get agent stats');
    }
  },
  
  // Get task stats
  getTaskStats: async () => {
    try {
      const response = await api.get('/analytics/tasks/stats');
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get task stats');
    }
  },
  
  // Get agent performance
  getAgentPerformance: async (agentId) => {
    try {
      const response = await api.get(`/analytics/agents/${agentId}/performance`);
      return { data: response.data };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get agent performance');
    }
  },
};

export default api;
