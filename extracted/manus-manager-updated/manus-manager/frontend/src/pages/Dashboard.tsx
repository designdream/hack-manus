import React from 'react';
import { Box, Typography, Grid, Paper, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { useEffect, useState } from 'react';
import { analyticsService } from '../services/api';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale,
  LinearScale,
  BarElement,
  Title
} from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const StatCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
}));

const Dashboard = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await analyticsService.getDashboardData();
        setDashboardData(response.data);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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

  // Prepare chart data
  const agentStatusData = {
    labels: Object.keys(dashboardData?.agent_status_counts || {}),
    datasets: [
      {
        data: Object.values(dashboardData?.agent_status_counts || {}),
        backgroundColor: [
          '#4caf50', // running
          '#2196f3', // idle
          '#ff9800', // paused
          '#f44336', // error
          '#9e9e9e', // terminated
        ],
        borderWidth: 1,
      },
    ],
  };

  const taskStatusData = {
    labels: Object.keys(dashboardData?.task_status_counts || {}),
    datasets: [
      {
        data: Object.values(dashboardData?.task_status_counts || {}),
        backgroundColor: [
          '#4caf50', // completed
          '#f44336', // failed
          '#2196f3', // in_progress
          '#ff9800', // pending
          '#9e9e9e', // cancelled
        ],
        borderWidth: 1,
      },
    ],
  };

  const taskProgressData = {
    labels: ['Completed', 'In Progress', 'Pending', 'Failed'],
    datasets: [
      {
        label: 'Tasks',
        data: [
          dashboardData?.completed_tasks || 0,
          dashboardData?.in_progress_tasks || 0,
          dashboardData?.pending_tasks || 0,
          dashboardData?.failed_tasks || 0,
        ],
        backgroundColor: [
          'rgba(76, 175, 80, 0.6)',
          'rgba(33, 150, 243, 0.6)',
          'rgba(255, 152, 0, 0.6)',
          'rgba(244, 67, 54, 0.6)',
        ],
      },
    ],
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {user && (
        <Typography variant="subtitle1" gutterBottom>
          Welcome back, {user.username}!
        </Typography>
      )}
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard elevation={2}>
            <Typography variant="h6">Agents</Typography>
            <Typography variant="h3">{dashboardData?.agent_count || 0}</Typography>
          </StatCard>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard elevation={2}>
            <Typography variant="h6">Tasks</Typography>
            <Typography variant="h3">{dashboardData?.task_count || 0}</Typography>
          </StatCard>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard elevation={2}>
            <Typography variant="h6">Completed Tasks</Typography>
            <Typography variant="h3">{dashboardData?.completed_tasks || 0}</Typography>
          </StatCard>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard elevation={2}>
            <Typography variant="h6">Overall Progress</Typography>
            <Box display="flex" justifyContent="center" alignItems="center">
              <CircularProgress 
                variant="determinate" 
                value={dashboardData?.overall_progress || 0} 
                size={60}
                thickness={5}
                sx={{ color: '#4caf50' }}
              />
              <Typography 
                variant="h5" 
                component="div" 
                sx={{ 
                  position: 'absolute',
                  fontWeight: 'bold'
                }}
              >
                {dashboardData?.overall_progress || 0}%
              </Typography>
            </Box>
          </StatCard>
        </Grid>
      </Grid>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <StyledPaper elevation={3}>
            <Typography variant="h6" gutterBottom>
              Agent Status
            </Typography>
            <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
              <Pie data={agentStatusData} options={{ maintainAspectRatio: false }} />
            </Box>
          </StyledPaper>
        </Grid>
        <Grid item xs={12} md={6}>
          <StyledPaper elevation={3}>
            <Typography variant="h6" gutterBottom>
              Task Status
            </Typography>
            <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
              <Pie data={taskStatusData} options={{ maintainAspectRatio: false }} />
            </Box>
          </StyledPaper>
        </Grid>
        <Grid item xs={12}>
          <StyledPaper elevation={3}>
            <Typography variant="h6" gutterBottom>
              Task Progress
            </Typography>
            <Box sx={{ height: 300 }}>
              <Bar 
                data={taskProgressData} 
                options={{ 
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  }
                }} 
              />
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
