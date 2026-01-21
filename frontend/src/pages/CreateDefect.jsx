import React, { useState, useEffect } from 'react';
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
  Autocomplete,
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import Layout from '../components/layout/Layout';
import { defectAPI, customerAPI, productAPI, defectTypeAPI, severityLevelAPI } from '../services/api';

function CreateDefect() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  // Data from database
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [defectTypes, setDefectTypes] = useState([]);
  const [severityLevels, setSeverityLevels] = useState([]);

  const [formData, setFormData] = useState({
    customer: '',
    part_code: '',
    part_name: '',
    defect_type: '',
    defect_title: '',
    defect_description: '',
    keywords: '',
    severity: '',
    customer_id: null,
    product_id: null,
  });

  // Filtered products based on selected customer
  const [filteredProducts, setFilteredProducts] = useState([]);

  // Fetch data from APIs
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [customersRes, productsRes, defectTypesRes, severityLevelsRes] = await Promise.all([
          customerAPI.getAll(),
          productAPI.getAll(),
          defectTypeAPI.getAll(),
          severityLevelAPI.getAll(),
        ]);

        setCustomers(customersRes.data);
        setProducts(productsRes.data);
        setDefectTypes(defectTypesRes.data);
        setSeverityLevels(severityLevelsRes.data);

        // Set default values if available
        if (defectTypesRes.data.length > 0) {
          setFormData((prev) => ({ ...prev, defect_type: defectTypesRes.data[0].defect_code }));
        }
        if (severityLevelsRes.data.length > 0) {
          setFormData((prev) => ({ ...prev, severity: severityLevelsRes.data[0].severity_code }));
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Không thể tải dữ liệu. Vui lòng refresh trang.');
      }
    };

    fetchData();
  }, []);

  // Filter products when customer changes
  useEffect(() => {
    if (formData.customer_id) {
      const filtered = products.filter((p) => p.customer_id === formData.customer_id);
      setFilteredProducts(filtered);
    } else {
      setFilteredProducts(products);
    }
  }, [formData.customer_id, products]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
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
      formDataToSend.append('customer', formData.customer);
      formDataToSend.append('part_code', formData.part_code);
      formDataToSend.append('part_name', formData.part_name);
      formDataToSend.append('defect_type', formData.defect_type);
      formDataToSend.append('defect_title', formData.defect_title);
      formDataToSend.append('defect_description', formData.defect_description);
      formDataToSend.append('keywords', formData.keywords);
      formDataToSend.append('severity', formData.severity);

      // Append context IDs for context-based filtering
      if (formData.customer_id) {
        formDataToSend.append('customer_id', formData.customer_id);
      }
      if (formData.product_id) {
        formDataToSend.append('product_id', formData.product_id);
      }

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
              <Autocomplete
                options={customers}
                getOptionLabel={(option) => (typeof option === 'string' ? option : option.customer_name)}
                value={customers.find((c) => c.id === formData.customer_id) || null}
                onChange={(event, newValue) => {
                  if (newValue && typeof newValue === 'object') {
                    setFormData({
                      ...formData,
                      customer: newValue.customer_name,
                      customer_id: newValue.id,
                      // Reset product selection when customer changes
                      part_code: '',
                      part_name: '',
                      product_id: null,
                    });
                  } else {
                    setFormData({
                      ...formData,
                      customer: '',
                      customer_id: null,
                      part_code: '',
                      part_name: '',
                      product_id: null,
                    });
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    required
                    label="Khách Hàng"
                    placeholder="Chọn khách hàng"
                    helperText="Chọn khách hàng từ danh sách"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Autocomplete
                options={filteredProducts}
                getOptionLabel={(option) => (typeof option === 'string' ? option : option.product_code)}
                value={filteredProducts.find((p) => p.id === formData.product_id) || null}
                onChange={(event, newValue) => {
                  if (newValue && typeof newValue === 'object') {
                    setFormData({
                      ...formData,
                      part_code: newValue.product_code,
                      part_name: newValue.product_name,
                      product_id: newValue.id,
                    });
                  } else {
                    setFormData({
                      ...formData,
                      part_code: '',
                      part_name: '',
                      product_id: null,
                    });
                  }
                }}
                renderOption={(props, option) => (
                  <li {...props} key={option.id}>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {option.product_code}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {option.product_name}
                      </Typography>
                    </Box>
                  </li>
                )}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    required
                    label="Mã Sản Phẩm"
                    placeholder="Chọn sản phẩm"
                    helperText={
                      formData.customer_id
                        ? `Hiển thị ${filteredProducts.length} sản phẩm của khách hàng này`
                        : 'Vui lòng chọn khách hàng trước'
                    }
                    disabled={!formData.customer_id}
                  />
                )}
                disabled={!formData.customer_id}
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
                helperText={formData.part_code && !formData.part_name ? 'Không tìm thấy sản phẩm với mã này. Vui lòng nhập tên thủ công.' : 'Được tự động điền khi nhập mã sản phẩm'}
                error={formData.part_code && !formData.part_name}
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
                helperText={
                  formData.defect_type === 'OK'
                    ? '✅ OK / No Defect: Upload ảnh sản phẩm BÌNH THƯỜNG (không có lỗi) để hệ thống nhận biết'
                    : 'Chọn loại lỗi cần tạo profile'
                }
              >
                <MenuItem value="">
                  <em>-- Chọn loại lỗi --</em>
                </MenuItem>
                {defectTypes.map((type) => (
                  <MenuItem key={type.id} value={type.defect_code}>
                    {type.defect_code === 'OK' ? '✅ ' : ''}{type.display_name}
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
                <MenuItem value="">
                  <em>-- Chọn mức độ --</em>
                </MenuItem>
                {severityLevels.map((level) => (
                  <MenuItem key={level.id} value={level.severity_code}>
                    {level.display_name}
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
