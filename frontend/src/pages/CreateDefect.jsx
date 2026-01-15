import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import Layout from '../components/layout/Layout';
import { defectAPI } from '../services/api';

function CreateDefect() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const [formData, setFormData] = useState({
    customer: '',
    part_code: '',
    part_name: '',
    defect_type: 'can',
    defect_title: '',
    defect_description: '',
    keywords: '',
    severity: 'minor',
  });

  const defectTypes = [
    { value: 'can', label: 'Cấn (Dents)' },
    { value: 'rach', label: 'Rách (Tears)' },
    { value: 'nhan', label: 'Nhăn (Wrinkles)' },
    { value: 'phong', label: 'Phồng (Bubbles)' },
    { value: 'ok', label: 'OK (No Defect)' },
  ];

  const severityLevels = [
    { value: 'minor', label: 'Nhỏ (Minor)' },
    { value: 'major', label: 'Nghiêm Trọng (Major)' },
    { value: 'critical', label: 'Rất Nghiêm Trọng (Critical)' },
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      const formDataToSend = new FormData();

      // Append text fields
      Object.keys(formData).forEach((key) => {
        formDataToSend.append(key, formData[key]);
      });

      // Append images
      selectedFiles.forEach((file) => {
        formDataToSend.append('reference_images', file);
      });

      await defectAPI.createProfile(formDataToSend);

      setSuccess(true);
      setTimeout(() => {
        navigate('/defects');
      }, 2000);
    } catch (err) {
      console.error('Error creating defect:', err);
      setError(err.response?.data?.detail || 'Không thể tạo defect profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Tạo Defect Profile Mới
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Nhập thông tin lỗi sản phẩm và upload ảnh tham khảo
        </Typography>
      </Box>

      <Paper sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Tạo defect profile thành công! Đang chuyển hướng...
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                label="Khách Hàng"
                name="customer"
                value={formData.customer}
                onChange={handleChange}
                placeholder="VD: FAPV"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                label="Mã Sản Phẩm"
                name="part_code"
                value={formData.part_code}
                onChange={handleChange}
                placeholder="VD: GD3346"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                label="Tên Sản Phẩm"
                name="part_name"
                value={formData.part_name}
                onChange={handleChange}
                placeholder="VD: Grommet"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                select
                label="Loại Lỗi"
                name="defect_type"
                value={formData.defect_type}
                onChange={handleChange}
              >
                {defectTypes.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                label="Tiêu Đề Lỗi"
                name="defect_title"
                value={formData.defect_title}
                onChange={handleChange}
                placeholder="VD: Cấn"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                select
                label="Mức Độ Nghiêm Trọng"
                name="severity"
                value={formData.severity}
                onChange={handleChange}
              >
                {severityLevels.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                multiline
                rows={4}
                label="Mô Tả Lỗi (QC Standard)"
                name="defect_description"
                value={formData.defect_description}
                onChange={handleChange}
                placeholder="Mô tả chi tiết theo chuẩn QC..."
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Keywords (phân cách bằng dấu phẩy)"
                name="keywords"
                value={formData.keywords}
                onChange={handleChange}
                placeholder="VD: can, vet lom, ep, gap"
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="outlined"
                component="label"
                startIcon={<CloudUpload />}
                fullWidth
              >
                Upload Ảnh Tham Khảo (Tối Thiểu 1 Ảnh)
                <input
                  type="file"
                  hidden
                  multiple
                  accept="image/*"
                  onChange={handleFileChange}
                  required
                />
              </Button>
              {selectedFiles.length > 0 && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Đã chọn {selectedFiles.length} ảnh
                </Typography>
              )}
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={loading || selectedFiles.length === 0}
              >
                {loading ? <CircularProgress size={24} /> : 'Tạo Defect Profile'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Layout>
  );
}

export default CreateDefect;
