import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Pages
import Login from './components/auth/Login';
import Dashboard from './pages/Dashboard';
import DefectList from './pages/DefectList';
import CreateDefect from './pages/CreateDefect';
import UserManagement from './pages/UserManagement';
import Incidents from './pages/Incidents';
import CustomerManagement from './pages/CustomerManagement';
import ProductManagement from './pages/ProductManagement';
import DefectTypeManagement from './pages/DefectTypeManagement';
import SeverityLevelManagement from './pages/SeverityLevelManagement';

// Utils
import { isAuthenticated } from './utils/auth';

// Create theme with gradient colors (light to dark)
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      light: '#4791db',     // Lighter blue
      main: '#1976d2',      // Main blue (giữ nguyên)
      dark: '#115293',      // Darker blue
      contrastText: '#fff',
    },
    secondary: {
      light: '#ff5983',
      main: '#dc004e',
      dark: '#9a0036',
      contrastText: '#fff',
    },
    background: {
      default: '#f5f7fa',   // Very light gray
      paper: '#ffffff',
    },
    text: {
      primary: '#2c3e50',   // Dark gray
      secondary: '#7f8c8d', // Medium gray
    },
    success: {
      light: '#81c784',
      main: '#4caf50',
      dark: '#388e3c',
    },
    warning: {
      light: '#ffb74d',
      main: '#ff9800',
      dark: '#f57c00',
    },
    error: {
      light: '#e57373',
      main: '#f44336',
      dark: '#d32f2f',
    },
    info: {
      light: '#64b5f6',
      main: '#2196f3',
      dark: '#1976d2',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
});

// Protected Route Component
function ProtectedRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/defects"
            element={
              <ProtectedRoute>
                <DefectList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/defects/create"
            element={
              <ProtectedRoute>
                <CreateDefect />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute>
                <UserManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/incidents"
            element={
              <ProtectedRoute>
                <Incidents />
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers"
            element={
              <ProtectedRoute>
                <CustomerManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/products"
            element={
              <ProtectedRoute>
                <ProductManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/defect-types"
            element={
              <ProtectedRoute>
                <DefectTypeManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/severity-levels"
            element={
              <ProtectedRoute>
                <SeverityLevelManagement />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
      <ToastContainer position="top-right" autoClose={3000} />
    </ThemeProvider>
  );
}

export default App;
