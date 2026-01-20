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
  PriorityHigh as PriorityIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import Layout from '../components/layout/Layout';
import { severityLevelAPI } from '../services/api';

function SeverityLevelManagement() {
  const [severityLevels, setSeverityLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingSeverityLevel, setEditingSeverityLevel] = useState(null);
  const [formData, setFormData] = useState({
    severity_code: '',
    name_vi: '',
    name_en: '',
  });

  useEffect(() => {
    fetchSeverityLevels();
  }, []);

  const fetchSeverityLevels = async () => {
    try {
      setLoading(true);
      const response = await severityLevelAPI.getAll();
      setSeverityLevels(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching severity levels:', err);
      setError('Không thể tải danh sách mức độ nghiêm trọng');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (severityLevel = null) => {
    if (severityLevel) {
      setEditingSeverityLevel(severityLevel);
      setFormData({
        severity_code: severityLevel.severity_code,
        name_vi: severityLevel.name_vi,
        name_en: severityLevel.name_en,
      });
    } else {
      setEditingSeverityLevel(null);
      setFormData({
        severity_code: '',
        name_vi: '',
        name_en: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingSeverityLevel(null);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingSeverityLevel) {
        await severityLevelAPI.update(editingSeverityLevel.id, formData);
        toast.success('Cập nhật mức độ nghiêm trọng thành công');
      } else {
        await severityLevelAPI.create(formData);
        toast.success('Tạo mức độ nghiêm trọng mới thành công');
      }
      handleCloseDialog();
      fetchSeverityLevels();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (severityLevelId) => {
    if (!window.confirm('Bạn có chắc muốn xóa mức độ nghiêm trọng này?')) return;

    try {
      await severityLevelAPI.delete(severityLevelId);
      toast.success('Xóa mức độ nghiêm trọng thành công');
      fetchSeverityLevels();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể xóa mức độ nghiêm trọng');
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
              Quản Lý Mức Độ Nghiêm Trọng
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Quản lý danh mục mức độ nghiêm trọng của lỗi
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="large"
          >
            Thêm Mức Độ
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Severity Levels Table */}
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Mã mức độ</strong>
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
                  {severityLevels.map((severityLevel) => (
                    <TableRow key={severityLevel.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <PriorityIcon color="action" />
                          {severityLevel.severity_code}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={severityLevel.display_name}
                          size="small"
                          color="secondary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(severityLevel)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(severityLevel.id)}
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

            {severityLevels.length === 0 && (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  Chưa có mức độ nghiêm trọng nào. Nhấn "Thêm Mức Độ" để tạo mới.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Create/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingSeverityLevel ? 'Chỉnh sửa mức độ nghiêm trọng' : 'Thêm mức độ nghiêm trọng mới'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                margin="normal"
                label="Mã mức độ *"
                name="severity_code"
                value={formData.severity_code}
                onChange={handleChange}
                required
                helperText="Mã duy nhất để định danh mức độ (ví dụ: CRITICAL, MAJOR, MINOR)"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tên tiếng Việt *"
                name="name_vi"
                value={formData.name_vi}
                onChange={handleChange}
                required
                helperText="Tên mức độ bằng tiếng Việt (ví dụ: Nghiêm trọng, Vừa phải)"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tên tiếng Anh *"
                name="name_en"
                value={formData.name_en}
                onChange={handleChange}
                required
                helperText="Tên mức độ bằng tiếng Anh (ví dụ: Critical, Major, Minor)"
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
              disabled={!formData.severity_code || !formData.name_vi || !formData.name_en}
            >
              {editingSeverityLevel ? 'Cập nhật' : 'Tạo mới'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default SeverityLevelManagement;
