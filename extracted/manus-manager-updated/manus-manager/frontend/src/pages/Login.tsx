import React from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Container,
  Grid,
  CircularProgress,
  Alert,
  Link,
  Divider
} from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import { loginStart, loginSuccess, loginFailure } from '../store/authSlice';
import { authService } from '../services/api';

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  
  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      dispatch(loginStart());
      
      const response = await authService.login(username, password);
      dispatch(loginSuccess(response.user));
      
      setLoading(false);
      navigate('/');
    } catch (err) {
      setLoading(false);
      setError(err.message || 'Login failed. Please check your credentials.');
      dispatch(loginFailure(err.message || 'Login failed'));
    }
  };
  
  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get Google auth URL
      const { auth_url } = await authService.getGoogleAuthUrl();
      
      // Open Google auth in a new window
      const googleWindow = window.open(auth_url, '_blank', 'width=500,height=600');
      
      // Listen for messages from the popup window
      window.addEventListener('message', async (event) => {
        // Verify origin for security
        if (event.origin !== window.location.origin) return;
        
        // Check if the message contains a Google token
        if (event.data && event.data.token) {
          try {
            // Login with Google token
            const response = await authService.loginWithGoogle(event.data.token);
            dispatch(loginSuccess(response.user));
            
            // Close the popup window
            if (googleWindow) googleWindow.close();
            
            setLoading(false);
            navigate('/');
          } catch (err) {
            setLoading(false);
            setError(err.message || 'Google login failed.');
            dispatch(loginFailure(err.message || 'Google login failed'));
          }
        }
      });
    } catch (err) {
      setLoading(false);
      setError(err.message || 'Failed to initiate Google login.');
      dispatch(loginFailure(err.message || 'Failed to initiate Google login'));
    }
  };
  
  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h4" sx={{ mb: 3 }}>
          Manus Manager
        </Typography>
        
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h2" variant="h5" align="center" sx={{ mb: 3 }}>
            Sign In
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleLogin} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username or Email"
              name="username"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
            
            <Divider sx={{ my: 2 }}>OR</Divider>
            
            <Button
              fullWidth
              variant="outlined"
              startIcon={<GoogleIcon />}
              onClick={handleGoogleLogin}
              disabled={loading}
              sx={{ mb: 2 }}
            >
              Sign in with Google
            </Button>
            
            <Grid container>
              <Grid item xs>
                <Link href="#" variant="body2">
                  Forgot password?
                </Link>
              </Grid>
              <Grid item>
                <Link href="#" variant="body2">
                  {"Don't have an account? Contact admin"}
                </Link>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Box>
      <Box sx={{ mt: 8, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Manus Manager v0.1.0 - Manage your Manus AI agents efficiently
        </Typography>
      </Box>
    </Container>
  );
};

export default Login;
