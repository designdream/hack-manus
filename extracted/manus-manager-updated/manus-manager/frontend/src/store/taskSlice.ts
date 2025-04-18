import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  owner_id: number;
  agent_id?: number;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  priority: number;
  progress: number;
}

interface TaskState {
  tasks: Task[];
  selectedTask: Task | null;
  loading: boolean;
  error: string | null;
}

const initialState: TaskState = {
  tasks: [],
  selectedTask: null,
  loading: false,
  error: null,
};

const taskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    fetchTasksStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchTasksSuccess: (state, action: PayloadAction<Task[]>) => {
      state.tasks = action.payload;
      state.loading = false;
    },
    fetchTasksFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    selectTask: (state, action: PayloadAction<Task>) => {
      state.selectedTask = action.payload;
    },
    clearSelectedTask: (state) => {
      state.selectedTask = null;
    },
    updateTaskProgress: (state, action: PayloadAction<{ id: number; progress: number; status?: string }>) => {
      const { id, progress, status } = action.payload;
      const task = state.tasks.find(t => t.id === id);
      if (task) {
        task.progress = progress;
        if (status) {
          task.status = status;
        }
      }
      if (state.selectedTask && state.selectedTask.id === id) {
        state.selectedTask.progress = progress;
        if (status) {
          state.selectedTask.status = status;
        }
      }
    },
    addTask: (state, action: PayloadAction<Task>) => {
      state.tasks.push(action.payload);
    },
    updateTask: (state, action: PayloadAction<Task>) => {
      const index = state.tasks.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.tasks[index] = action.payload;
      }
      if (state.selectedTask && state.selectedTask.id === action.payload.id) {
        state.selectedTask = action.payload;
      }
    },
    removeTask: (state, action: PayloadAction<number>) => {
      state.tasks = state.tasks.filter(t => t.id !== action.payload);
      if (state.selectedTask && state.selectedTask.id === action.payload) {
        state.selectedTask = null;
      }
    },
    assignTask: (state, action: PayloadAction<{ taskId: number; agentId: number }>) => {
      const { taskId, agentId } = action.payload;
      const task = state.tasks.find(t => t.id === taskId);
      if (task) {
        task.agent_id = agentId;
        if (task.status === 'pending') {
          task.status = 'in_progress';
          task.started_at = new Date().toISOString();
        }
      }
      if (state.selectedTask && state.selectedTask.id === taskId) {
        state.selectedTask.agent_id = agentId;
        if (state.selectedTask.status === 'pending') {
          state.selectedTask.status = 'in_progress';
          state.selectedTask.started_at = new Date().toISOString();
        }
      }
    },
  },
});

export const {
  fetchTasksStart,
  fetchTasksSuccess,
  fetchTasksFailure,
  selectTask,
  clearSelectedTask,
  updateTaskProgress,
  addTask,
  updateTask,
  removeTask,
  assignTask,
} = taskSlice.actions;

export default taskSlice.reducer;
