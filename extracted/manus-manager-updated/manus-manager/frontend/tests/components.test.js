import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../src/store/authSlice';
import agentReducer from '../src/store/agentSlice';
import taskReducer from '../src/store/taskSlice';
import Login from '../src/pages/Login';
import Dashboard from '../src/pages/Dashboard';
import AgentList from '../src/pages/AgentList';
import TaskList from '../src/pages/TaskList';
import { authService, analyticsService, agentService, taskService } from '../src/services/api';

// Mock the API services
jest.mock('../src/services/api', () => ({
  authService: {
    login: jest.fn(),
    logout: jest.fn(),
    getCurrentUser: jest.fn(),
  },
  analyticsService: {
    getDashboardData: jest.fn(),
    getAgentStats: jest.fn(),
    getTaskStats: jest.fn(),
    getAgentPerformance: jest.fn(),
  },
  agentService: {
    getAgents: jest.fn(),
    getAgent: jest.fn(),
    createAgent: jest.fn(),
    updateAgent: jest.fn(),
    deleteAgent: jest.fn(),
    startAgent: jest.fn(),
    stopAgent: jest.fn(),
    pauseAgent: jest.fn(),
  },
  taskService: {
    getTasks: jest.fn(),
    getTask: jest.fn(),
    createTask: jest.fn(),
    updateTask: jest.fn(),
    deleteTask: jest.fn(),
    assignTask: jest.fn(),
  },
  trackingService: {
    getAgentLogs: jest.fn(),
    getTaskLogs: jest.fn(),
    updateAgentStatus: jest.fn(),
    updateTaskProgress: jest.fn(),
    connectWebSocket: jest.fn(),
  },
}));

// Create a test store
const createTestStore = (preloadedState = {}) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      agents: agentReducer,
      tasks: taskReducer,
    },
    preloadedState,
  });
};

// Test wrapper component
const TestWrapper = ({ children, store }) => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </Provider>
  );
};

describe('Login Component', () => {
  let store;

  beforeEach(() => {
    store = createTestStore();
    authService.login.mockClear();
  });

  test('renders login form', () => {
    render(
      <TestWrapper store={store}>
        <Login />
      </TestWrapper>
    );

    expect(screen.getByText('Manus Manager')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('handles login submission', async () => {
    authService.login.mockResolvedValue({
      access_token: 'test-token',
      user: { id: 1, username: 'testuser', email: 'test@example.com' }
    });

    render(
      <TestWrapper store={store}>
        <Login />
      </TestWrapper>
    );

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('testuser', 'password123');
    });
  });

  test('displays error message on login failure', async () => {
    authService.login.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <TestWrapper store={store}>
        <Login />
      </TestWrapper>
    );

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpassword' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
    });
  });
});

describe('Dashboard Component', () => {
  let store;

  beforeEach(() => {
    store = createTestStore({
      auth: {
        isAuthenticated: true,
        user: { id: 1, username: 'testuser', email: 'test@example.com' },
        loading: false,
        error: null,
      }
    });
    
    analyticsService.getDashboardData.mockClear();
    analyticsService.getDashboardData.mockResolvedValue({
      data: {
        agent_count: 3,
        task_count: 10,
        agent_status_counts: {
          running: 1,
          idle: 1,
          paused: 1,
        },
        task_status_counts: {
          completed: 5,
          in_progress: 3,
          pending: 2,
        },
        overall_progress: 60,
        completed_tasks: 5,
        failed_tasks: 0,
        in_progress_tasks: 3,
        pending_tasks: 2,
      }
    });
  });

  test('renders dashboard with data', async () => {
    render(
      <TestWrapper store={store}>
        <Dashboard />
      </TestWrapper>
    );

    // Check for loading state first
    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(analyticsService.getDashboardData).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Welcome back, testuser!')).toBeInTheDocument();
    });
  });
});

describe('AgentList Component', () => {
  let store;

  beforeEach(() => {
    store = createTestStore({
      auth: {
        isAuthenticated: true,
        user: { id: 1, username: 'testuser', email: 'test@example.com' },
        loading: false,
        error: null,
      },
      agents: {
        agents: [],
        selectedAgent: null,
        loading: false,
        error: null,
      }
    });
    
    agentService.getAgents.mockClear();
    agentService.getAgents.mockResolvedValue({
      data: [
        {
          id: 1,
          name: 'Agent 1',
          description: 'Test agent 1',
          status: 'running',
          owner_id: 1,
          max_tasks: 5,
          created_at: '2025-04-13T12:00:00Z',
          last_active: '2025-04-13T12:30:00Z',
        },
        {
          id: 2,
          name: 'Agent 2',
          description: 'Test agent 2',
          status: 'idle',
          owner_id: 1,
          max_tasks: 3,
          created_at: '2025-04-12T10:00:00Z',
          last_active: '2025-04-12T11:00:00Z',
        }
      ]
    });
  });

  test('renders agent list with data', async () => {
    render(
      <TestWrapper store={store}>
        <AgentList />
      </TestWrapper>
    );

    // Check for loading state first
    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(agentService.getAgents).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText('Agents')).toBeInTheDocument();
      expect(screen.getByText('Agent 1')).toBeInTheDocument();
      expect(screen.getByText('Agent 2')).toBeInTheDocument();
    });
  });

  test('opens create agent dialog', async () => {
    render(
      <TestWrapper store={store}>
        <AgentList />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(agentService.getAgents).toHaveBeenCalled();
    });

    fireEvent.click(screen.getByRole('button', { name: /add agent/i }));

    await waitFor(() => {
      expect(screen.getByText('Create New Agent')).toBeInTheDocument();
    });
  });
});

describe('TaskList Component', () => {
  let store;

  beforeEach(() => {
    store = createTestStore({
      auth: {
        isAuthenticated: true,
        user: { id: 1, username: 'testuser', email: 'test@example.com' },
        loading: false,
        error: null,
      },
      tasks: {
        tasks: [],
        selectedTask: null,
        loading: false,
        error: null,
      },
      agents: {
        agents: [
          {
            id: 1,
            name: 'Agent 1',
            status: 'running',
          }
        ],
        selectedAgent: null,
        loading: false,
        error: null,
      }
    });
    
    taskService.getTasks.mockClear();
    taskService.getTasks.mockResolvedValue({
      data: [
        {
          id: 1,
          title: 'Task 1',
          description: 'Test task 1',
          status: 'in_progress',
          owner_id: 1,
          agent_id: 1,
          created_at: '2025-04-13T12:00:00Z',
          priority: 1,
          progress: 50,
        },
        {
          id: 2,
          title: 'Task 2',
          description: 'Test task 2',
          status: 'pending',
          owner_id: 1,
          agent_id: null,
          created_at: '2025-04-12T10:00:00Z',
          priority: 2,
          progress: 0,
        }
      ]
    });
  });

  test('renders task list with data', async () => {
    render(
      <TestWrapper store={store}>
        <TaskList />
      </TestWrapper>
    );

    // Check for loading state first
    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(taskService.getTasks).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText('Tasks')).toBeInTheDocument();
      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });
  });

  test('opens create task dialog', async () => {
    render(
      <TestWrapper store={store}>
        <TaskList />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(taskService.getTasks).toHaveBeenCalled();
    });

    fireEvent.click(screen.getByRole('button', { name: /add task/i }));

    await waitFor(() => {
      expect(screen.getByText('Create New Task')).toBeInTheDocument();
    });
  });
});
