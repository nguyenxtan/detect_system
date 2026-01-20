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
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import Layout from '../components/layout/Layout';
import { productAPI, customerAPI } from '../services/api';

function ProductManagement() {
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    product_code: '',
    product_name: '',
    customer_id: '',
  });

  useEffect(() => {
    fetchProducts();
    fetchCustomers();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await productAPI.getAll();
      setProducts(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Không thể tải danh sách sản phẩm');
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await customerAPI.getAll();
      setCustomers(response.data);
    } catch (err) {
      console.error('Error fetching customers:', err);
      toast.error('Không thể tải danh sách khách hàng');
    }
  };

  const handleOpenDialog = (product = null) => {
    if (product) {
      setEditingProduct(product);
      setFormData({
        product_code: product.product_code,
        product_name: product.product_name,
        customer_id: product.customer_id,
      });
    } else {
      setEditingProduct(null);
      setFormData({
        product_code: '',
        product_name: '',
        customer_id: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingProduct(null);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingProduct) {
        await productAPI.update(editingProduct.id, formData);
        toast.success('Cập nhật sản phẩm thành công');
      } else {
        await productAPI.create(formData);
        toast.success('Tạo sản phẩm mới thành công');
      }
      handleCloseDialog();
      fetchProducts();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Bạn có chắc muốn xóa sản phẩm này?')) return;

    try {
      await productAPI.delete(productId);
      toast.success('Xóa sản phẩm thành công');
      fetchProducts();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể xóa sản phẩm');
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
              Quản Lý Sản Phẩm
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Quản lý thông tin sản phẩm và liên kết với khách hàng
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="large"
          >
            Thêm Sản Phẩm
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Products Table */}
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Mã sản phẩm</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Tên sản phẩm</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Khách hàng</strong>
                    </TableCell>
                    <TableCell align="center">
                      <strong>Thao tác</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {products.map((product) => (
                    <TableRow key={product.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <InventoryIcon color="action" />
                          {product.product_code}
                        </Box>
                      </TableCell>
                      <TableCell>{product.product_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${product.customer.customer_name} (${product.customer.customer_code})`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(product)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(product.id)}
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

            {products.length === 0 && (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  Chưa có sản phẩm nào. Nhấn "Thêm Sản Phẩm" để tạo mới.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Create/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingProduct ? 'Chỉnh sửa sản phẩm' : 'Thêm sản phẩm mới'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                margin="normal"
                label="Mã sản phẩm *"
                name="product_code"
                value={formData.product_code}
                onChange={handleChange}
                required
                helperText="Mã duy nhất để định danh sản phẩm"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tên sản phẩm *"
                name="product_name"
                value={formData.product_name}
                onChange={handleChange}
                required
              />
              <TextField
                fullWidth
                margin="normal"
                select
                label="Khách hàng *"
                name="customer_id"
                value={formData.customer_id}
                onChange={handleChange}
                required
                helperText="Chọn khách hàng sở hữu sản phẩm này"
              >
                <MenuItem value="">
                  <em>-- Chọn khách hàng --</em>
                </MenuItem>
                {customers.map((customer) => (
                  <MenuItem key={customer.id} value={customer.id}>
                    {customer.customer_name} ({customer.customer_code})
                  </MenuItem>
                ))}
              </TextField>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Hủy</Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={!formData.customer_id}
            >
              {editingProduct ? 'Cập nhật' : 'Tạo mới'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default ProductManagement;
