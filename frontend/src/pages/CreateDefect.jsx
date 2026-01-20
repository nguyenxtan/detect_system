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
  const [allProducts, setAllProducts] = useState([]); // Store all products for filtering
  const [defectTypes, setDefectTypes] = useState([]);
  const [severityLevels, setSeverityLevels] = useState([]);

  const [formData, setFormData] = useState({
    customer_id: '',
    product_id: '',
    defect_type: '',
    defect_title: '',
    defect_description: '',
    keywords: '',
    severity: '',
  });

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
        setAllProducts(productsRes.data);
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

  const handleChange = (e) => {
    const { name, value } = e.target;

    // Filter products when customer changes
    if (name === 'customer_id') {
      const filtered = allProducts.filter((p) => p.customer_id === parseInt(value));
      setProducts(filtered);
      // Reset product selection when customer changes
      setFormData({
        ...formData,
        [name]: value,
        product_id: '',
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
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
      // Find selected customer and product
      const selectedCustomer = customers.find((c) => c.id === parseInt(formData.customer_id));
      const selectedProduct = allProducts.find((p) => p.id === parseInt(formData.product_id));

      if (!selectedCustomer) {
        setError('Vui lòng chọn khách hàng');
        setLoading(false);
        return;
      }

      if (!selectedProduct) {
        setError('Vui lòng chọn sản phẩm');
        setLoading(false);
        return;
      }

      const formDataToSend = new FormData();

      // Map to backend expected fields
      formDataToSend.append('customer', selectedCustomer.customer_name);
      formDataToSend.append('part_code', selectedProduct.product_code);
      formDataToSend.append('part_name', selectedProduct.product_name);
      formDataToSend.append('defect_type', formData.defect_type);
      formDataToSend.append('defect_title', formData.defect_title);
      formDataToSend.append('defect_description', formData.defect_description);
      formDataToSend.append('keywords', formData.keywords);
      formDataToSend.append('severity', formData.severity);

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
                select
                label="Khách Hàng"
                name="customer_id"
                value={formData.customer_id}
                onChange={handleChange}
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
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                required
                fullWidth
                select
                label="Sản Phẩm"
                name="product_id"
                value={formData.product_id}
                onChange={handleChange}
                disabled={!formData.customer_id}
                helperText={!formData.customer_id ? 'Vui lòng chọn khách hàng trước' : ''}
              >
                <MenuItem value="">
                  <em>-- Chọn sản phẩm --</em>
                </MenuItem>
                {products.map((product) => (
                  <MenuItem key={product.id} value={product.id}>
                    {product.product_name} ({product.product_code})
                  </MenuItem>
                ))}
              </TextField>
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
                <MenuItem value="">
                  <em>-- Chọn loại lỗi --</em>
                </MenuItem>
                {defectTypes.map((type) => (
                  <MenuItem key={type.id} value={type.defect_code}>
                    {type.display_name}
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
