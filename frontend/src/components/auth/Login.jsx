import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Avatar,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  LockOutlined,
  Visibility,
  VisibilityOff,
  Person,
} from '@mui/icons-material';
import { authAPI } from '../../services/api';
import { setAuthToken, setUser } from '../../utils/auth';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(formData.username, formData.password);
      const { access_token, user } = response.data;

      // Save token and user info
      setAuthToken(access_token);
      setUser(user);

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={24}
          sx={{
            padding: 5,
            borderRadius: 3,
            backdropFilter: 'blur(10px)',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Avatar
              sx={{
                width: 70,
                height: 70,
                bgcolor: 'primary.main',
                mb: 2,
              }}
            >
              <LockOutlined sx={{ fontSize: 40 }} />
            </Avatar>

            <Typography component="h1" variant="h4" fontWeight="bold" gutterBottom>
              Defect Recognition System
            </Typography>

            <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
              PU/PE Manufacturing Quality Control
            </Typography>

            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Tên đăng nhập"
                name="username"
                autoComplete="username"
                autoFocus
                value={formData.username}
                onChange={handleChange}
                disabled={loading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Mật khẩu"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockOutlined color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{
                  mt: 4,
                  mb: 2,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 'bold',
                  textTransform: 'none',
                  borderRadius: 2,
                }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Đăng Nhập'}
              </Button>

              <Box
                sx={{
                  mt: 3,
                  p: 2,
                  bgcolor: 'info.light',
                  borderRadius: 1,
                  textAlign: 'center',
                }}
              >
                <Typography variant="caption" color="info.dark" fontWeight="medium">
                  Demo Account: admin / admin123
                </Typography>
              </Box>
            </Box>
          </Box>
        </Paper>

        <Typography
          variant="body2"
          color="white"
          align="center"
          sx={{ mt: 3, opacity: 0.9 }}
        >
          © 2026 PU/PE Manufacturing - AI-Powered Quality Control
        </Typography>
      </Container>
    </Box>
  );
}

export default Login;
