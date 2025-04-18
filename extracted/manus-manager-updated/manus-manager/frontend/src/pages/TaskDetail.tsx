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
  IconButton,
  LinearProgress,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { RootState } from '../store';
import { selectTask, updateTask, updateTaskProgress } from '../store/taskSlice';
import { taskService, trackingService } from '../services/api';

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
      id={`task-tabpanel-${index}`}
      aria-labelledby={`task-tab-${index}`}
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

const TaskDetail = () => {
  const { id } = useParams<{ id: string }>();
  const taskId = parseInt(id || '0');
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const { tasks } = useSelector((state: RootState) => state.tasks);
  const { agents } = useSelector((state: RootState) => state.agents);
  const task = tasks.find(t => t.id === taskId);
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [logs, setLogs] = useState<any[]>([]);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openProgressDialog, setOpenProgressDialog] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 0,
    status: 'pending'
  });
  const [progressValue, setProgressValue] = useState(0);

  useEffect(() => {
    const fetchTaskDetails = async () => {
      try {
        setLoading(true);
        
        // Fetch task if not in store
        if (!task) {
          const taskResponse = await taskService.getTask(taskId);
          dispatch(selectTask(taskResponse.data));
        } else {
          // Initialize form data from task
          setFormData({
            title: task.title,
            description: task.description || '',
            priority: task.priority,
            status: task.status
          });
          setProgressValue(task.progress);
        }
        
        // Fetch logs
        const logsResponse = await trackingService.getTaskLogs(taskId);
        setLogs(logsResponse.data);
        
        setLoading(false);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch task details');
        setLoading(false);
      }
    };

    fetchTaskDetails();
  }, [taskId, task, dispatch]);

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        status: task.status
      });
      setProgressValue(task.progress);
    }
  }, [task]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenEditDialog = () => {
    setOpenEditDialog(true);
  };

  const handleOpenProgressDialog = () => {
    setOpenProgressDialog(true);
  };

  const handleCloseDialogs = () => {
    setOpenEditDialog(false);
    setOpenProgressDialog(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSelectChange = (e: any) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProgressValue(Number(e.target.value));
  };

  const handleUpdateTask = async () => {
    if (!task) return;
    
    try {
      const response = await taskService.updateTask(task.id, formData);
      dispatch(updateTask(response.data));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to update task:', err);
    }
  };

  const handleUpdateProgress = async () => {
    if (!task) return;
    
    try {
      await trackingService.updateTaskProgress(task.id, progressValue, formData.status);
      dispatch(updateTaskProgress({ 
        id: task.id, 
        progress: progressValue, 
        status: formData.status 
      }));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to update task progress:', err);
    }
  };

  const getStatusChipColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      case 'cancelled':
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

  if (error || !task) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <Typography color="error">{error || 'Task not found'}</Typography>
      </Box>
    );
  }

  const assignedAgent = agents.find(a => a.id === task.agent_id);

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/tasks')} sx={{ mr: 2 }}>
          <BackIcon />
        </IconButton>
        <Typography variant="h4">Task Details</Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h5">{task.title}</Typography>
            {task.description && (
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                {task.description}
              </Typography>
            )}
          </Grid>
          <Grid item xs={12} md={4} display="flex" justifyContent="flex-end" alignItems="center">
            <Box>
              <Chip
                label={task.status}
                color={getStatusChipColor(task.status) as any}
                sx={{ mr: 1 }}
              />
              
              <Button
                variant="outlined"
                color="primary"
                size="small"
                startIcon={<EditIcon />}
                onClick={handleOpenEditDialog}
                sx={{ mr: 1 }}
              >
                Edit
              </Button>
              
              <Button
                variant="contained"
                color="primary"
                size="small"
                onClick={handleOpenProgressDialog}
              >
                Update Progress
              </Button>
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
              {task.status}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Priority
            </Typography>
            <Typography variant="body1">
              {['Low', 'Medium', 'High', 'Critical'][task.priority] || 'Low'}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Assigned Agent
            </Typography>
            <Typography variant="body1">
              {assignedAgent ? assignedAgent.name : 'Not assigned'}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Created At
            </Typography>
            <Typography variant="body1">
              {new Date(task.created_at).toLocaleString()}
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Progress
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress variant="determinate" value={task.progress} />
            </Box>
            <Box sx={{ minWidth: 35 }}>
              <Typography variant="body2" color="text.secondary">{`${task.progress}%`}</Typography>
            </Box>
          </Box>
        </Box>
      </Paper>

      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="task tabs">
            <Tab label="Details" />
            <Tab label="Logs" />
            <Tab label="Timeline" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Task Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Started At
                      </Typography>
                      <Typography variant="body1">
                        {task.started_at ? new Date(task.started_at).toLocaleString() : 'Not started'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Completed At
                      </Typography>
                      <Typography variant="body1">
                        {task.completed_at ? new Date(task.completed_at).toLocaleString() : 'Not completed'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        Duration
                      </Typography>
                      <Typography variant="body1">
                        {task.started_at && task.completed_at ? 
                          `${Math.round((new Date(task.completed_at).getTime() - new Date(task.started_at).getTime()) / 1000 / 60)} minutes` : 
                          'N/A'}
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
                    Agent Information
                  </Typography>
                  {assignedAgent ? (
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Agent Name
                        </Typography>
                        <Typography variant="body1">
                          {assignedAgent.name}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Agent Status
                        </Typography>
                        <Typography variant="body1">
                          {assignedAgent.status}
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">
                          Last Active
                        </Typography>
                        <Typography variant="body1">
                          {assignedAgent.last_active ? new Date(assignedAgent.last_active).toLocaleString() : 'Never'}
                        </Typography>
                      </Grid>
                    </Grid>
                  ) : (
                    <Typography variant="body1" color="text.secondary">
                      No agent assigned to this task.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
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
              No logs available for this task.
            </Typography>
          )}
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <Typography variant="body1" color="text.secondary">
            Task timeline would be displayed here, showing the progression of the task through different states.
          </Typography>
        </TabPanel>
      </Box>

      {/* Edit Task Dialog */}
      <Dialog open={openEditDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Edit Task</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Task Title"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleInputChange}
            required
          />
          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.description}
            onChange={handleInputChange}
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Priority</InputLabel>
            <Select
              name="priority"
              value={formData.priority}
              label="Priority"
              onChange={handleSelectChange}
            >
              <MenuItem value={0}>Low</MenuItem>
              <MenuItem value={1}>Medium</MenuItem>
              <MenuItem value={2}>High</MenuItem>
              <MenuItem value={3}>Critical</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="dense">
            <InputLabel>Status</InputLabel>
            <Select
              name="status"
              value={formData.status}
              label="Status"
              onChange={handleSelectChange}
            >
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleUpdateTask} variant="contained" color="primary">
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Progress Dialog */}
      <Dialog open={openProgressDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Update Task Progress</DialogTitle>
        <DialogContent>
          <Typography variant="body2" gutterBottom>
            Current Progress: {task.progress}%
          </Typography>
          <TextField
            margin="dense"
            name="progress"
            label="Progress (%)"
            type="number"
            fullWidth
            variant="outlined"
            value={progressValue}
            onChange={handleProgressChange}
            inputProps={{ min: 0, max: 100 }}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Status</InputLabel>
            <Select
              name="status"
              value={formData.status}
              label="Status"
              onChange={handleSelectChange}
            >
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleUpdateProgress} variant="contained" color="primary">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskDetail;
