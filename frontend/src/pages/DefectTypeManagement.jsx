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
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Category as CategoryIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import Layout from '../components/layout/Layout';
import { defectTypeAPI } from '../services/api';

function DefectTypeManagement() {
  const [defectTypes, setDefectTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingDefectType, setEditingDefectType] = useState(null);
  const [formData, setFormData] = useState({
    defect_code: '',
    name_vi: '',
    name_en: '',
  });

  useEffect(() => {
    fetchDefectTypes();
  }, []);

  const fetchDefectTypes = async () => {
    try {
      setLoading(true);
      const response = await defectTypeAPI.getAll();
      setDefectTypes(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching defect types:', err);
      setError('Không thể tải danh sách loại lỗi');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (defectType = null) => {
    if (defectType) {
      setEditingDefectType(defectType);
      setFormData({
        defect_code: defectType.defect_code,
        name_vi: defectType.name_vi,
        name_en: defectType.name_en,
      });
    } else {
      setEditingDefectType(null);
      setFormData({
        defect_code: '',
        name_vi: '',
        name_en: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingDefectType(null);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingDefectType) {
        await defectTypeAPI.update(editingDefectType.id, formData);
        toast.success('Cập nhật loại lỗi thành công');
      } else {
        await defectTypeAPI.create(formData);
        toast.success('Tạo loại lỗi mới thành công');
      }
      handleCloseDialog();
      fetchDefectTypes();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (defectTypeId) => {
    if (!window.confirm('Bạn có chắc muốn xóa loại lỗi này?')) return;

    try {
      await defectTypeAPI.delete(defectTypeId);
      toast.success('Xóa loại lỗi thành công');
      fetchDefectTypes();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể xóa loại lỗi');
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
              Quản Lý Loại Lỗi
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Quản lý danh mục các loại lỗi sản phẩm
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="large"
          >
            Thêm Loại Lỗi
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Defect Types Table */}
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Mã loại lỗi</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Tên hiển thị</strong>
                    </TableCell>
                    <TableCell align="center">
                      <strong>Thao tác</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {defectTypes.map((defectType) => (
                    <TableRow key={defectType.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <CategoryIcon color="action" />
                          {defectType.defect_code}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={defectType.display_name}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(defectType)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(defectType.id)}
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

            {defectTypes.length === 0 && (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  Chưa có loại lỗi nào. Nhấn "Thêm Loại Lỗi" để tạo mới.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Create/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingDefectType ? 'Chỉnh sửa loại lỗi' : 'Thêm loại lỗi mới'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                margin="normal"
                label="Mã loại lỗi *"
                name="defect_code"
                value={formData.defect_code}
                onChange={handleChange}
                required
                helperText="Mã duy nhất để định danh loại lỗi (ví dụ: CRACK, SCRATCH)"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tên tiếng Việt *"
                name="name_vi"
                value={formData.name_vi}
                onChange={handleChange}
                required
                helperText="Tên loại lỗi bằng tiếng Việt (ví dụ: Nứt, Trầy xước)"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tên tiếng Anh *"
                name="name_en"
                value={formData.name_en}
                onChange={handleChange}
                required
                helperText="Tên loại lỗi bằng tiếng Anh (ví dụ: Crack, Scratch)"
              />
              <Alert severity="info" sx={{ mt: 2 }}>
                Hiển thị: Tên tiếng Việt (Tên tiếng Anh)
              </Alert>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Hủy</Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={!formData.defect_code || !formData.name_vi || !formData.name_en}
            >
              {editingDefectType ? 'Cập nhật' : 'Tạo mới'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default DefectTypeManagement;
