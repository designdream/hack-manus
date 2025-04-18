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
  CircularProgress
} from '@mui/material';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Pause as PauseIcon
} from '@mui/icons-material';
import { RootState } from '../store';
import { 
  fetchAgentsStart, 
  fetchAgentsSuccess, 
  fetchAgentsFailure,
  addAgent,
  updateAgent,
  removeAgent,
  updateAgentStatus
} from '../store/agentSlice';
import { agentService } from '../services/api';

const AgentList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { agents, loading, error } = useSelector((state: RootState) => state.agents);
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    api_key: '',
    max_tasks: 5
  });
  
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        dispatch(fetchAgentsStart());
        const response = await agentService.getAgents();
        dispatch(fetchAgentsSuccess(response.data));
      } catch (err: any) {
        dispatch(fetchAgentsFailure(err.message || 'Failed to fetch agents'));
      }
    };
    
    fetchAgents();
  }, [dispatch]);
  
  const handleOpenCreateDialog = () => {
    setFormData({
      name: '',
      description: '',
      api_key: '',
      max_tasks: 5
    });
    setOpenCreateDialog(true);
  };
  
  const handleOpenEditDialog = (agent: any) => {
    setSelectedAgent(agent);
    setFormData({
      name: agent.name,
      description: agent.description || '',
      api_key: agent.api_key || '',
      max_tasks: agent.max_tasks
    });
    setOpenEditDialog(true);
  };
  
  const handleOpenDeleteDialog = (agent: any) => {
    setSelectedAgent(agent);
    setOpenDeleteDialog(true);
  };
  
  const handleCloseDialogs = () => {
    setOpenCreateDialog(false);
    setOpenEditDialog(false);
    setOpenDeleteDialog(false);
    setSelectedAgent(null);
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
  
  const handleCreateAgent = async () => {
    try {
      const agentData = {
        ...formData,
        owner_id: user?.id
      };
      
      const response = await agentService.createAgent(agentData);
      dispatch(addAgent(response.data));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to create agent:', err);
    }
  };
  
  const handleUpdateAgent = async () => {
    if (!selectedAgent) return;
    
    try {
      const response = await agentService.updateAgent(selectedAgent.id, formData);
      dispatch(updateAgent(response.data));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to update agent:', err);
    }
  };
  
  const handleDeleteAgent = async () => {
    if (!selectedAgent) return;
    
    try {
      await agentService.deleteAgent(selectedAgent.id);
      dispatch(removeAgent(selectedAgent.id));
      handleCloseDialogs();
    } catch (err) {
      console.error('Failed to delete agent:', err);
    }
  };
  
  const handleStartAgent = async (agentId: number) => {
    try {
      const response = await agentService.startAgent(agentId);
      dispatch(updateAgentStatus({ id: agentId, status: 'running' }));
    } catch (err) {
      console.error('Failed to start agent:', err);
    }
  };
  
  const handleStopAgent = async (agentId: number) => {
    try {
      const response = await agentService.stopAgent(agentId);
      dispatch(updateAgentStatus({ id: agentId, status: 'idle' }));
    } catch (err) {
      console.error('Failed to stop agent:', err);
    }
  };
  
  const handlePauseAgent = async (agentId: number) => {
    try {
      const response = await agentService.pauseAgent(agentId);
      dispatch(updateAgentStatus({ id: agentId, status: 'paused' }));
    } catch (err) {
      console.error('Failed to pause agent:', err);
    }
  };
  
  const handleViewAgent = (agentId: number) => {
    navigate(`/agents/${agentId}`);
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
        <Typography variant="h4">Agents</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          Add Agent
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Max Tasks</TableCell>
              <TableCell>Last Active</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {agents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No agents found. Create your first agent to get started.
                </TableCell>
              </TableRow>
            ) : (
              agents.map((agent) => (
                <TableRow key={agent.id} hover onClick={() => handleViewAgent(agent.id)} style={{ cursor: 'pointer' }}>
                  <TableCell>{agent.name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={agent.status} 
                      color={getStatusChipColor(agent.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{agent.max_tasks}</TableCell>
                  <TableCell>{agent.last_active ? new Date(agent.last_active).toLocaleString() : 'Never'}</TableCell>
                  <TableCell>
                    <Box>
                      {agent.status !== 'running' && (
                        <IconButton 
                          size="small" 
                          color="success" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStartAgent(agent.id);
                          }}
                        >
                          <StartIcon />
                        </IconButton>
                      )}
                      
                      {agent.status === 'running' && (
                        <IconButton 
                          size="small" 
                          color="warning" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePauseAgent(agent.id);
                          }}
                        >
                          <PauseIcon />
                        </IconButton>
                      )}
                      
                      {(agent.status === 'running' || agent.status === 'paused') && (
                        <IconButton 
                          size="small" 
                          color="error" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStopAgent(agent.id);
                          }}
                        >
                          <StopIcon />
                        </IconButton>
                      )}
                      
                      <IconButton 
                        size="small" 
                        color="primary" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenEditDialog(agent);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      
                      <IconButton 
                        size="small" 
                        color="error" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDeleteDialog(agent);
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
      
      {/* Create Agent Dialog */}
      <Dialog open={openCreateDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Create New Agent</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Agent Name"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.name}
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
          <TextField
            margin="dense"
            name="api_key"
            label="API Key (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.api_key}
            onChange={handleInputChange}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Max Tasks</InputLabel>
            <Select
              name="max_tasks"
              value={formData.max_tasks}
              label="Max Tasks"
              onChange={handleSelectChange}
            >
              <MenuItem value={1}>1</MenuItem>
              <MenuItem value={2}>2</MenuItem>
              <MenuItem value={3}>3</MenuItem>
              <MenuItem value={4}>4</MenuItem>
              <MenuItem value={5}>5</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleCreateAgent} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Edit Agent Dialog */}
      <Dialog open={openEditDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Edit Agent</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Agent Name"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.name}
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
          <TextField
            margin="dense"
            name="api_key"
            label="API Key (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.api_key}
            onChange={handleInputChange}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Max Tasks</InputLabel>
            <Select
              name="max_tasks"
              value={formData.max_tasks}
              label="Max Tasks"
              onChange={handleSelectChange}
            >
              <MenuItem value={1}>1</MenuItem>
              <MenuItem value={2}>2</MenuItem>
              <MenuItem value={3}>3</MenuItem>
              <MenuItem value={4}>4</MenuItem>
              <MenuItem value={5}>5</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleUpdateAgent} variant="contained" color="primary">
            Update
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Agent Dialog */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Delete Agent</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the agent "{selectedAgent?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleDeleteAgent} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentList;
