import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  IconButton
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';
import { RootState } from '../store';
import { selectAgent, updateAgentStatus } from '../store/agentSlice';
import { agentService, analyticsService, trackingService } from '../services/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`agent-tabpanel-${index}`}
      aria-labelledby={`agent-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AgentDetail = () => {
  const { id } = useParams<{ id: string }>();
  const agentId = parseInt(id || '0');
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const { agents } = useSelector((state: RootState) => state.agents);
  const agent = agents.find(a => a.id === agentId);
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [performance, setPerformance] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    const fetchAgentDetails = async () => {
      try {
        setLoading(true);
        
        // Fetch agent if not in store
        if (!agent) {
          const agentResponse = await agentService.getAgent(agentId);
          dispatch(selectAgent(agentResponse.data));
        }
        
        // Fetch performance data
        const performanceResponse = await analyticsService.getAgentPerformance(agentId);
        setPerformance(performanceResponse.data);
        
        // Fetch logs
        const logsResponse = await trackingService.getAgentLogs(agentId);
        setLogs(logsResponse.data);
        
        setLoading(false);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch agent details');
        setLoading(false);
      }
    };

    fetchAgentDetails();
  }, [agentId, agent, dispatch]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleStartAgent = async () => {
    try {
      await agentService.startAgent(agentId);
      dispatch(updateAgentStatus({ id: agentId, status: 'running' }));
    } catch (err) {
      console.error('Failed to start agent:', err);
    }
  };

  const handleStopAgent = async () => {
    try {
      await agentService.stopAgent(agentId);
      dispatch(updateAgentStatus({ id: agentId, status: 'idle' }));
    } catch (err) {
      console.error('Failed to stop agent:', err);
    }
  };

  const handlePauseAgent = async () => {
    try {
      await agentService.pauseAgent(agentId);
      dispatch(updateAgentStatus({ id: agentId, status: 'paused' }));
    } catch (err) {
      console.error('Failed to pause agent:', err);
    }
  };

  const getStatusChipColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'idle':
        return 'primary';
      case 'paused':
        return 'warning';
      case 'error':
        return 'error';
      case 'terminated':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !agent) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <Typography color="error">{error || 'Agent not found'}</Typography>
      </Box>
    );
  }

  // Prepare chart data for task completion times
  const taskCompletionData = {
    labels: performance?.task_completion_times?.map((t: any) => t.title.substring(0, 20) + '...') || [],
    datasets: [
      {
        label: 'Completion Time (seconds)',
        data: performance?.task_completion_times?.map((t: any) => t.completion_time_seconds) || [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
    ],
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/agents')} sx={{ mr: 2 }}>
          <BackIcon />
        </IconButton>
        <Typography variant="h4">Agent Details</Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h5">{agent.name}</Typography>
            {agent.description && (
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                {agent.description}
              </Typography>
            )}
          </Grid>
          <Grid item xs={12} md={4} display="flex" justifyContent="flex-end" alignItems="center">
            <Box>
              <Chip
                label={agent.status}
                color={getStatusChipColor(agent.status) as any}
                sx={{ mr: 1 }}
              />
              
              {agent.status !== 'running' && (
                <Button
                  variant="contained"
                  color="success"
                  size="small"
                  startIcon={<StartIcon />}
                  onClick={handleStartAgent}
                  sx={{ mr: 1 }}
                >
                  Start
                </Button>
              )}
              
              {agent.status === 'running' && (
                <Button
                  variant="contained"
                  color="warning"
                  size="small"
                  startIcon={<PauseIcon />}
                  onClick={handlePauseAgent}
                  sx={{ mr: 1 }}
                >
                  Pause
                </Button>
              )}
              
              {(agent.status === 'running' || agent.status === 'paused') && (
                <Button
                  variant="contained"
                  color="error"
                  size="small"
                  startIcon={<StopIcon />}
                  onClick={handleStopAgent}
                >
                  Stop
                </Button>
              )}
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Status
            </Typography>
            <Typography variant="body1">
              {agent.status}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Max Tasks
            </Typography>
            <Typography variant="body1">
              {agent.max_tasks}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Last Active
            </Typography>
            <Typography variant="body1">
              {agent.last_active ? new Date(agent.last_active).toLocaleString() : 'Never'}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Created At
            </Typography>
            <Typography variant="body1">
              {new Date(agent.created_at).toLocaleString()}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="agent tabs">
            <Tab label="Performance" />
            <Tab label="Tasks" />
            <Tab label="Logs" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Task Statistics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Total Tasks
                      </Typography>
                      <Typography variant="h6">
                        {performance?.total_tasks || 0}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Completed Tasks
                      </Typography>
                      <Typography variant="h6">
                        {performance?.completed_tasks || 0}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Failed Tasks
                      </Typography>
                      <Typography variant="h6">
                        {performance?.failed_tasks || 0}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        In Progress Tasks
                      </Typography>
                      <Typography variant="h6">
                        {performance?.in_progress_tasks || 0}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Task Completion Times
                  </Typography>
                  {performance?.task_completion_times?.length > 0 ? (
                    <Box sx={{ height: 300 }}>
                      <Line 
                        data={taskCompletionData} 
                        options={{ 
                          maintainAspectRatio: false,
                          scales: {
                            y: {
                              beginAtZero: true,
                              title: {
                                display: true,
                                text: 'Time (seconds)'
                              }
                            }
                          }
                        }} 
                      />
                    </Box>
                  ) : (
                    <Typography variant="body1" color="text.secondary">
                      No completed tasks yet.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          {performance?.total_tasks > 0 ? (
            <List>
              {/* This would be populated with actual task data */}
              <Typography variant="body1">
                Task list would be displayed here, fetched from the backend.
              </Typography>
            </List>
          ) : (
            <Typography variant="body1" color="text.secondary">
              No tasks assigned to this agent yet.
            </Typography>
          )}
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          {logs.length > 0 ? (
            <List>
              {logs.map((log) => (
                <ListItem key={log.id} divider>
                  <ListItemText
                    primary={log.message}
                    secondary={`${new Date(log.timestamp).toLocaleString()} - ${log.level}`}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body1" color="text.secondary">
              No logs available for this agent.
            </Typography>
          )}
        </TabPanel>
      </Box>
    </Box>
  );
};

export default AgentDetail;
