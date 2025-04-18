import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import agentReducer from './agentSlice';
import taskReducer from './taskSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    agents: agentReducer,
    tasks: taskReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
