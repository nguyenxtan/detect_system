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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import Layout from '../components/layout/Layout';
import { customerAPI } from '../services/api';

function CustomerManagement() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [formData, setFormData] = useState({
    customer_code: '',
    customer_name: '',
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await customerAPI.getAll();
      setCustomers(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching customers:', err);
      setError('Không thể tải danh sách khách hàng');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (customer = null) => {
    if (customer) {
      setEditingCustomer(customer);
      setFormData({
        customer_code: customer.customer_code,
        customer_name: customer.customer_name,
      });
    } else {
      setEditingCustomer(null);
      setFormData({
        customer_code: '',
        customer_name: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCustomer(null);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingCustomer) {
        await customerAPI.update(editingCustomer.id, formData);
        toast.success('Cập nhật khách hàng thành công');
      } else {
        await customerAPI.create(formData);
        toast.success('Tạo khách hàng mới thành công');
      }
      handleCloseDialog();
      fetchCustomers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (customerId) => {
    if (!window.confirm('Bạn có chắc muốn xóa khách hàng này?')) return;

    try {
      await customerAPI.delete(customerId);
      toast.success('Xóa khách hàng thành công');
      fetchCustomers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể xóa khách hàng');
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
              Quản Lý Khách Hàng
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Quản lý thông tin khách hàng
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="large"
          >
            Thêm Khách Hàng
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Customers Table */}
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Mã khách hàng</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Tên khách hàng</strong>
                    </TableCell>
                    <TableCell align="center">
                      <strong>Thao tác</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {customers.map((customer) => (
                    <TableRow key={customer.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <BusinessIcon color="action" />
                          {customer.customer_code}
                        </Box>
                      </TableCell>
                      <TableCell>{customer.customer_name}</TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(customer)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(customer.id)}
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

            {customers.length === 0 && (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  Chưa có khách hàng nào. Nhấn "Thêm Khách Hàng" để tạo mới.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Create/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingCustomer ? 'Chỉnh sửa khách hàng' : 'Thêm khách hàng mới'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                margin="normal"
                label="Mã khách hàng *"
                name="customer_code"
                value={formData.customer_code}
                onChange={handleChange}
                required
                helperText="Mã duy nhất để định danh khách hàng"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tên khách hàng *"
                name="customer_name"
                value={formData.customer_name}
                onChange={handleChange}
                required
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Hủy</Button>
            <Button variant="contained" onClick={handleSubmit}>
              {editingCustomer ? 'Cập nhật' : 'Tạo mới'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default CustomerManagement;
