import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assignment as AssignIcon
} from '@mui/icons-material';
import { RootState } from '../store';
import { 
  fetchTasksStart, 
  fetchTasksSuccess, 
  fetchTasksFailure,
  addTask,
  updateTask,
  removeTask,
  updateTaskProgress,
  assignTask
} from '../store/taskSlice';
import { taskService } from '../services/api';

const TaskList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { tasks, loading, error } = useSelector((state: RootState) => state.tasks);
  const { agents } = useSelector((state: RootState) => state.agents);
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openAssignDialog, setOpenAssignDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 0,
    status: 'pending'
  });
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        dispatch(fetchTasksStart());
        const response = await taskService.getTasks();
        dispatch(fetchTasksSuccess(response.data));
      } catch (err: any) {
        dispatch(fetchTasksFailure(err.message || 'Failed to fetch tasks'));
      }
    };
    
    fetchTasks();
  }, [dispatch]);
  
  const handleOpenCreateDialog = () => {
    setFormData({
      title: '',
      description: '',
      priority: 0,
      status: 'pending'
    });
    setOpenCreateDialog(true);
  };
  
  const handleOpenEditDialog = (task: any) => {
    setSelectedTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      status: task.status
    });
    setOpenEditDialog(true);
  };
  
  const handleOpenDeleteDialog = (task: any) => {
    setSelectedTask(task);
    setOpenDeleteDialog(true);
  };
  
  const handleOpenAssignDialog = (task: any) => {
    setSelectedTask(task);
    setSelectedAgentId(task.agent_id || null);
    setOpenAssignDialog(true);
  };
  
  const handleCloseDialogs = () => {
    setOpenCreateDialog(false);
    setOpenEditDialog(false);
    setOpenDeleteDialog(false);
    setOpenAssignDialog(false);
    setSelectedTask(null);
    setSelectedAgentId(null);
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
  
  const handleAgentSelectChange = (e: any) => {
    setSelectedAgentId(e.target.value);
  };
  
  const handleCreateTask = async () => {
    try {
      const taskData = {
        ...formData,
        owner_id: user?.id,
        progress: 0
      };
      
      const response = await taskService.createTask(taskData);
      dispatch(addTask(response.data));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to create task:', err);
    }
  };
  
  const handleUpdateTask = async () => {
    if (!selectedTask) return;
    
    try {
      const response = await taskService.updateTask(selectedTask.id, formData);
      dispatch(updateTask(response.data));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to update task:', err);
    }
  };
  
  const handleDeleteTask = async () => {
    if (!selectedTask) return;
    
    try {
      await taskService.deleteTask(selectedTask.id);
      dispatch(removeTask(selectedTask.id));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };
  
  const handleAssignTask = async () => {
    if (!selectedTask || selectedAgentId === null) return;
    
    try {
      const response = await taskService.assignTask(selectedTask.id, selectedAgentId);
      dispatch(assignTask({ taskId: selectedTask.id, agentId: selectedAgentId }));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to assign task:', err);
    }
  };
  
  const handleViewTask = (taskId: number) => {
    navigate(`/tasks/${taskId}`);
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
  
  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Tasks</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          Add Task
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Progress</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Assigned Agent</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No tasks found. Create your first task to get started.
                </TableCell>
              </TableRow>
            ) : (
              tasks.map((task) => (
                <TableRow key={task.id} hover onClick={() => handleViewTask(task.id)} style={{ cursor: 'pointer' }}>
                  <TableCell>{task.title}</TableCell>
                  <TableCell>
                    <Chip 
                      label={task.status} 
                      color={getStatusChipColor(task.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress variant="determinate" value={task.progress} />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">{`${task.progress}%`}</Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{task.priority}</TableCell>
                  <TableCell>
                    {task.agent_id ? (
                      agents.find(a => a.id === task.agent_id)?.name || `Agent #${task.agent_id}`
                    ) : (
                      <Typography variant="body2" color="text.secondary">Not assigned</Typography>
                    )}
                  </TableCell>
                  <TableCell>{new Date(task.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Box>
                      <IconButton 
                        size="small" 
                        color="primary" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenAssignDialog(task);
                        }}
                      >
                        <AssignIcon />
                      </IconButton>
                      
                      <IconButton 
                        size="small" 
                        color="primary" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenEditDialog(task);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      
                      <IconButton 
                        size="small" 
                        color="error" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDeleteDialog(task);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Create Task Dialog */}
      <Dialog open={openCreateDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Create New Task</DialogTitle>
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
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleCreateTask} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
      
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
      
      {/* Delete Task Dialog */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Delete Task</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the task "{selectedTask?.title}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleDeleteTask} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Assign Task Dialog */}
      <Dialog open={openAssignDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Assign Task to Agent</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Select an agent to assign the task "{selectedTask?.title}".
          </DialogContentText>
          <FormControl fullWidth margin="dense">
            <InputLabel>Agent</InputLabel>
            <Select
              value={selectedAgentId || ''}
              label="Agent"
              onChange={handleAgentSelectChange}
            >
              <MenuItem value="">
                <em>None (Unassign)</em>
              </MenuItem>
              {agents.map((agent) => (
                <MenuItem key={agent.id} value={agent.id}>
                  {agent.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleAssignTask} variant="contained" color="primary">
            Assign
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskList;
