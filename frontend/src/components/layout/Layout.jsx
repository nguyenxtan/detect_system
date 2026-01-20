import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  BugReport as BugReportIcon,
  AddCircle as AddCircleIcon,
  History as HistoryIcon,
  People as PeopleIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  Business as BusinessIcon,
  Inventory as InventoryIcon,
  Category as CategoryIcon,
  PriorityHigh as PriorityIcon,
} from '@mui/icons-material';
import { removeAuthToken, getUser, isAdmin } from '../../utils/auth';

const drawerWidth = 260;

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser();
  const userIsAdmin = isAdmin();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    removeAuthToken();
    navigate('/login');
  };

  const getRoleLabel = (role) => {
    return role === 'admin' ? 'Quản Trị Viên' : 'Người Dùng';
  };

  const menuItems = [
    {
      title: 'Dashboard',
      path: '/dashboard',
      icon: <DashboardIcon />,
      adminOnly: false,
    },
    {
      title: 'Defect Profiles',
      path: '/defects',
      icon: <BugReportIcon />,
      adminOnly: false,
    },
    {
      title: 'Thêm Defect',
      path: '/defects/create',
      icon: <AddCircleIcon />,
      adminOnly: true,
    },
    {
      title: 'Lịch Sử',
      path: '/incidents',
      icon: <HistoryIcon />,
      adminOnly: false,
    },
    {
      title: 'Quản Lý User',
      path: '/users',
      icon: <PeopleIcon />,
      adminOnly: true,
    },
    {
      title: 'Khách Hàng',
      path: '/customers',
      icon: <BusinessIcon />,
      adminOnly: true,
    },
    {
      title: 'Sản Phẩm',
      path: '/products',
      icon: <InventoryIcon />,
      adminOnly: true,
    },
    {
      title: 'Loại Lỗi',
      path: '/defect-types',
      icon: <CategoryIcon />,
      adminOnly: true,
    },
    {
      title: 'Mức Độ',
      path: '/severity-levels',
      icon: <PriorityIcon />,
      adminOnly: true,
    },
  ];

  const drawer = (
    <Box>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          px: [1],
          py: 2,
          bgcolor: 'primary.main',
          color: 'white',
        }}
      >
        <BugReportIcon sx={{ fontSize: 32, mr: 1 }} />
        <Typography variant="h6" noWrap fontWeight="bold">
          QC System
        </Typography>
      </Toolbar>

      <Divider />

      <List sx={{ px: 1, py: 2 }}>
        {menuItems.map((item) => {
          if (item.adminOnly && !userIsAdmin) return null;

          const isActive = location.pathname === item.path;

          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={isActive}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'white' : 'action.active',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.title}
                  primaryTypographyProps={{
                    fontSize: '0.95rem',
                    fontWeight: isActive ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      <List sx={{ px: 1, py: 2 }}>
        <ListItem disablePadding>
          <ListItemButton
            onClick={handleLogout}
            sx={{
              borderRadius: 2,
              color: 'error.main',
            }}
          >
            <ListItemIcon sx={{ color: 'error.main', minWidth: 40 }}>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Đăng Xuất" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'grey.50' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: 'white',
          color: 'text.primary',
          boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find((item) => item.path === location.pathname)?.title || 'Dashboard'}
          </Typography>

          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={getRoleLabel(user.role)}
                color={user.role === 'admin' ? 'primary' : 'default'}
                size="small"
              />
              <IconButton onClick={handleProfileMenuOpen} size="small">
                <Avatar
                  sx={{
                    width: 36,
                    height: 36,
                    bgcolor: 'primary.main',
                    fontSize: '1rem',
                  }}
                >
                  {(user.full_name || user.username || 'U')[0].toUpperCase()}
                </Avatar>
              </IconButton>
            </Box>
          )}

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem disabled>
              <Typography variant="subtitle2">{user?.full_name || user?.username}</Typography>
            </MenuItem>
            <MenuItem disabled>
              <Typography variant="caption" color="text.secondary">
                {user?.email || 'No email'}
              </Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => navigate('/settings')}>
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              Cài Đặt
            </MenuItem>
            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" color="error" />
              </ListItemIcon>
              Đăng Xuất
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

export default Layout;
