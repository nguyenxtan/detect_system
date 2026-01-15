import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import Layout from '../components/layout/Layout';
import { userAPI } from '../services/api';

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    email: '',
    role: 'user',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getAll();
      setUsers(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Không thể tải danh sách người dùng');
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role) => {
    return role === 'admin' ? 'Quản Trị Viên' : 'Người Dùng';
  };

  const handleOpenDialog = (user = null) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        password: '',
        full_name: user.full_name || '',
        email: user.email || '',
        role: user.role || 'user',
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        password: '',
        full_name: '',
        email: '',
        role: 'user',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingUser) {
        await userAPI.update(editingUser.id, formData);
        toast.success('Cập nhật người dùng thành công');
      } else {
        await userAPI.create(formData);
        toast.success('Tạo người dùng mới thành công');
      }
      handleCloseDialog();
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Bạn có chắc muốn xóa người dùng này?')) return;

    try {
      await userAPI.delete(userId);
      toast.success('Xóa người dùng thành công');
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể xóa người dùng');
    }
  };

  if (loading) {
    return (
      <Layout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight="bold">
              Quản Lý Người Dùng
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tạo và quản lý tài khoản người dùng hệ thống
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="large"
          >
            Thêm Người Dùng
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Users Table */}
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Tên đăng nhập</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Họ tên</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Email</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Vai trò</strong>
                    </TableCell>
                    <TableCell align="center">
                      <strong>Thao tác</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <PersonIcon color="action" />
                          {user.username}
                        </Box>
                      </TableCell>
                      <TableCell>{user.full_name || '-'}</TableCell>
                      <TableCell>{user.email || '-'}</TableCell>
                      <TableCell>
                        <Chip
                          label={getRoleLabel(user.role)}
                          color={user.role === 'admin' ? 'primary' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(user)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(user.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Create/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingUser ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                margin="normal"
                label="Tên đăng nhập"
                name="username"
                value={formData.username}
                onChange={handleChange}
                disabled={!!editingUser}
                required
              />
              <TextField
                fullWidth
                margin="normal"
                label="Mật khẩu"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required={!editingUser}
                helperText={editingUser ? 'Để trống nếu không muốn đổi mật khẩu' : ''}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Họ tên"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
              />
              <TextField
                fullWidth
                margin="normal"
                select
                label="Vai trò"
                name="role"
                value={formData.role}
                onChange={handleChange}
              >
                <MenuItem value="user">Người Dùng (User)</MenuItem>
                <MenuItem value="admin">Quản Trị Viên (Admin)</MenuItem>
              </TextField>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Hủy</Button>
            <Button variant="contained" onClick={handleSubmit}>
              {editingUser ? 'Cập nhật' : 'Tạo mới'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default UserManagement;
